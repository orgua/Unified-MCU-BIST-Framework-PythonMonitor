import re
import serial
import cbor2
import xxhash

PORT = "/dev/cu.usbmodem0010502825871"
BAUDRATE = 9600

# Header keys
HEADER_KEY_DEVICE_UUID   = 0
HEADER_KEY_DEVICE_FAMILY = 1
HEADER_KEY_TOTAL_CHUNKS  = 2
HEADER_KEY_TOTAL_PINS    = 3
HEADER_KEY_ACTIVE_PINS   = 4
HEADER_KEY_HEADER_CRC    = 5

# Chunk keys
KEY_CHUNK_ID    = 0
KEY_NUM_ENTRIES = 1
KEY_PINS        = 2
KEY_CRC         = 3

# Pin keys
KEY_PIN         = 4
KEY_EVENTS      = 5
KEY_CONNECTIONS = 6
KEY_OTHER_PIN   = 7
KEY_DEVICE_ID   = 8

CBORSEED = 0

packet_buffer = []
last_header_info = None


def _xxhash32(data: bytes) -> int:
    return xxhash.xxh32(data, seed=CBORSEED).intdigest()


def calc_header_hash(hdr: dict):
    if not isinstance(hdr, dict):
        return None
    d = {}
    for k in [HEADER_KEY_DEVICE_UUID, HEADER_KEY_DEVICE_FAMILY,
              HEADER_KEY_TOTAL_CHUNKS, HEADER_KEY_TOTAL_PINS,
              HEADER_KEY_ACTIVE_PINS]:
        if k in hdr:
            d[k] = hdr[k]
    return _xxhash32(cbor2.dumps(d))


def calc_chunk_hash(chunk: dict):
    if not isinstance(chunk, dict):
        return None
    d = {}
    for k in [KEY_CHUNK_ID, KEY_NUM_ENTRIES, KEY_PINS]:
        if k in chunk:
            d[k] = chunk[k]
    return _xxhash32(cbor2.dumps(d))


def parse_pkt(line: str):
    m = re.match(r"PKT_(\d+):(.*)", line)
    if not m:
        return None, None
    pkt_num = int(m.group(1))
    hexdata = m.group(2).strip()

    try:
        if len(hexdata) < 12:
            return None, None
        cbor_size = int.from_bytes(bytes.fromhex(hexdata[:4]), "little")
        exp_len = (2 + cbor_size + 4) * 2
        if len(hexdata) < exp_len:
            return None, None

        cbor_hex = hexdata[4:4 + cbor_size * 2]
        hash_hex = hexdata[4 + cbor_size * 2: 4 + cbor_size * 2 + 8]

        decoded = cbor2.loads(bytes.fromhex(cbor_hex))
        recv_hash = int.from_bytes(bytes.fromhex(hash_hex), "little")
        calc_hash = _xxhash32(bytes.fromhex(cbor_hex))

        decoded["_received_hash"] = recv_hash
        decoded["_calculated_hash"] = calc_hash
        decoded["_hash_valid"] = recv_hash == calc_hash

        return pkt_num, decoded
    except Exception as e:
        print(f"PKT_{pkt_num} decode error: {e}")
        return None, None


def parse_header(line: str):
    if "HEADER_PKT:" not in line:
        return None
    hexdata = line.split("HEADER_PKT:")[1].strip()
    try:
        if len(hexdata) < 12:
            return None
        cbor_size = int.from_bytes(bytes.fromhex(hexdata[:4]), "little")
        exp_len = (2 + cbor_size + 4) * 2
        if len(hexdata) < exp_len:
            return None

        cbor_hex = hexdata[4:4 + cbor_size * 2]
        hash_hex = hexdata[4 + cbor_size * 2: 4 + cbor_size * 2 + 8]

        decoded = cbor2.loads(bytes.fromhex(cbor_hex))
        recv_hash = int.from_bytes(bytes.fromhex(hash_hex), "little")
        calc_hash = _xxhash32(bytes.fromhex(cbor_hex))

        decoded["_received_hash"] = recv_hash
        decoded["_calculated_hash"] = calc_hash
        decoded["_hash_valid"] = recv_hash == calc_hash
        return decoded
    except Exception as e:
        print(f"Header decode error: {e}")
        return None


def dump_header(hdr: dict):
    if not hdr:
        return "Invalid header"

    names = {
        HEADER_KEY_DEVICE_UUID:   "Device UUID",
        HEADER_KEY_DEVICE_FAMILY: "Device Family",
        HEADER_KEY_TOTAL_CHUNKS:  "Total Chunks",
        HEADER_KEY_TOTAL_PINS:    "Total Pins",
        HEADER_KEY_ACTIVE_PINS:   "Active Pins",
        HEADER_KEY_HEADER_CRC:    "Header CRC",
    }

    out = ["Header:"]
    for k, v in hdr.items():
        if isinstance(k, str) and k.startswith("_"):
            continue
        label = names.get(k, f"Key {k}")
        if k == HEADER_KEY_DEVICE_UUID:
            out.append(f"{label}: 0x{v:016X}")
        else:
            out.append(f"{label}: {v}")

    if "_received_hash" in hdr:
        out.append(f"XXHash32: 0x{hdr['_received_hash']:08X}")
        ok = hdr["_received_hash"] == hdr["_calculated_hash"]
        out.append(f"Hash Valid: {ok} (Calc: 0x{hdr['_calculated_hash']:08X})")
    return "\n".join(out)


def tx_end():
    global packet_buffer, last_header_info
    if not packet_buffer:
        print("TX_END but no data")
        return

    print("\nTX COMPLETE")
    if last_header_info:
        exp_chunks = last_header_info.get(HEADER_KEY_TOTAL_CHUNKS, 0)
        exp_pins = last_header_info.get(HEADER_KEY_TOTAL_PINS, 0)
        got_chunks = len(packet_buffer)
        got_pins = sum(len(d.get(KEY_PINS, [])) for _, d in packet_buffer if isinstance(d, dict))

        print(f"Chunks: {got_chunks}/{exp_chunks} {'OK' if got_chunks==exp_chunks else 'MISMATCH'}")
        print(f"Pins:   {got_pins}/{exp_pins} {'OK' if got_pins==exp_pins else 'MISMATCH'}")

    for n, d in sorted(packet_buffer):
        print(f"Packet {n}:")
        if isinstance(d, dict):
            print(f"  Chunk ID: {d.get(KEY_CHUNK_ID)}")
            print(f"  Entries : {d.get(KEY_NUM_ENTRIES)}")
            if "_received_hash" in d:
                print(f"  XXHash32: 0x{d['_received_hash']:08X} (valid={d['_hash_valid']})")
            for pin in d.get(KEY_PINS, []):
                if isinstance(pin, dict):
                    print(f"    Pin {pin.get(KEY_PIN)} -> Events {pin.get(KEY_EVENTS, [])}")
                else:
                    print(f"    Pin: {pin}")
        else:
            print("  Raw:", d)
        print("-" * 30)

    packet_buffer.clear()


if __name__ == "__main__":
    print(f"Opening {PORT} @ {BAUDRATE}")
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    buf = ""
    try:
        while True:
            if ser.in_waiting:
                buf += ser.read(ser.in_waiting).decode(errors="ignore")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("HEADER_PKT:"):
                        hdr = parse_header(line)
                        if hdr:
                            last_header_info = hdr
                            print(dump_header(hdr))
                    elif line.startswith("PKT_"):
                        n, d = parse_pkt(line)
                        if n is not None:
                            packet_buffer.append((n, d))
                            print(f"Stored packet {n}")
                    elif line == "TX_END":
                        tx_end()
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        ser.close()