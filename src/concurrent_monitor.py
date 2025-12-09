import queue
import select
import sys
import threading
import time
from pathlib import Path

import cbor2
import crcmod
from bistmon.data_storage import DeviceDataCollector
from bistmon.logger import log
from serial import Serial

# Protocol identifiers (4 bytes each, little endian)
HEADER_START: bytes = bytes([0x0C, 0x0B, 0x0A, 0x09])
HEADER_END: bytes = bytes([0x10, 0x0F, 0x0E, 0x0D])
CHUNK_START: bytes = bytes([0x04, 0x03, 0x02, 0x01])
CHUNK_END: bytes = bytes([0x08, 0x07, 0x06, 0x05])

# CRC calculation
calculate_crc = crcmod.predefined.mkPredefinedCrcFun("crc-32")

# ACK protocol
ACK_START: int = 0x191A1B1C
ACK_END: int = 0x1D1E1F20

ACK_REQUESTED: int = 8


def send_ack(serial: Serial, received_hash):
    """Send simple ACK with crc"""
    try:
        ack_data = bytearray()
        ack_data.extend(ACK_START.to_bytes(4, "little"))
        ack_data.extend(received_hash.to_bytes(4, "little"))
        ack_data.extend(ACK_END.to_bytes(4, "little"))

        serial.write(ack_data)
        log.debug(f"ACK sent for crc: 0x{received_hash:08X}")
    except Exception as e:
        log.exception("ACK send failed", exc_info=e)


def parse_packet(hex_data, *, has_packet_id=False):
    """Parse CBOR packet: [PACKET_ID?][LENGTH][CBOR][CRC]"""
    try:
        offset = 0
        packet_id = -1

        if has_packet_id:
            packet_id = int.from_bytes(bytes.fromhex(hex_data[:8]), "little")
            offset = 4

        # Extract length (2 bytes, little endian)
        length = int.from_bytes(bytes.fromhex(hex_data[offset * 2 : offset * 2 + 4]), "little")

        # Extract CBOR data
        cbor_start = offset * 2 + 4
        cbor_end = cbor_start + length * 2
        cbor_hex = hex_data[cbor_start:cbor_end]
        cbor_bytes = bytes.fromhex(cbor_hex)

        # Extract hash (4 bytes at end)
        hash_hex = hex_data[cbor_end : cbor_end + 8]
        received_hash = int.from_bytes(bytes.fromhex(hash_hex), "little")

        # Verify hash
        calculated_hash = calculate_crc(cbor_bytes)
        hash_valid = received_hash == calculated_hash

        # Decode CBOR
        try:
            decoded = cbor2.loads(cbor_bytes)
        except:
            decoded = {"error": "cbor decode failed"}

        return {
            "ack_requested": decoded.get(ACK_REQUESTED, 0),
            "packet_id": packet_id,
            "data": decoded,
            "hash_valid": hash_valid,
            "received_hash": received_hash,
            "calculated_hash": calculated_hash,
            "raw_bytes": cbor_bytes,
        }
    except Exception as e:
        log.exception("Parse packet error", exc_info=e)
    return None


def serial_reader(serial: Serial, data_queue, stop_event):
    log.debug("Serial reader thread started")

    while not stop_event.is_set():
        try:
            if serial.in_waiting:
                new_data = serial.read(serial.in_waiting)
                if new_data:
                    data_queue.put(new_data)
            else:
                time.sleep(0.001)  # Very small delay when no data

        except Exception as e:
            log.exception("Reader error", exc_info=e)
            break

    log.debug("Serial reader stopped")


def packet_processor(serial: Serial, data_queue, stop_event, collector):
    """Process 2: Process incoming data and handle protocol"""
    log.debug("Packet processor thread started")

    buffer = bytearray()
    packet_data = bytearray()
    debug_buffer = bytearray()
    receiving_header = False
    receiving_chunk = False

    while not stop_event.is_set():
        try:
            # Get data from queue (non-blocking)
            try:
                new_data = data_queue.get_nowait()

                # Extract DEBUG messages
                for byte in new_data:
                    debug_buffer.append(byte)

                    # Check if we have a complete line ending with \n
                    if byte == ord("\n"):
                        try:
                            line_text = debug_buffer.decode("utf-8", errors="ignore").strip()
                            # Only print if it starts with DEBUG:
                            if line_text.startswith("DEBUG:"):
                                log.debug(line_text)
                        except:
                            pass
                        debug_buffer.clear()  # Clear for next line

                    # Prevent memory leak - clear if buffer gets too large
                    elif len(debug_buffer) > 1000:
                        debug_buffer.clear()

                # Add all data to binary protocol buffer (unmodified)
                buffer.extend(new_data)

            except queue.Empty:
                time.sleep(0.0001)
                continue

            # Look for protocol markers (binary protocol handling)
            while len(buffer) >= 4:
                if buffer[:4] == HEADER_START:
                    log.debug("=== Header Start ===")
                    receiving_header = True
                    packet_data = bytearray()
                    buffer = buffer[4:]

                elif buffer[:4] == HEADER_END:
                    log.debug("=== Header End ===")
                    receiving_header = False
                    if packet_data:
                        result = parse_packet(packet_data.hex(), has_packet_id=False)

                        # Debug: Print CBOR structure with keys
                        data = result.get("data", {})
                        log.debug(
                            f"CBOR Header: Device Family {data.get(1)}, Total Chunks {data.get(2)}"
                        )
                        log.debug(f"📦 CBOR Header Data: {data}")

                        # Process header in collector
                        collector.process_header(result)

                        if result.get("ack_requested", 1):
                            # Send ACK if hash is valid
                            if result["hash_valid"]:
                                send_ack(serial, result["received_hash"])
                            else:
                                log.warning("Hash invalid, no ACK sent")
                        else:
                            log.debug("ACK not requested, no ACK sent")
                    packet_data = bytearray()
                    buffer = buffer[4:]

                elif buffer[:4] == CHUNK_START:
                    receiving_chunk = True
                    packet_data = bytearray()
                    buffer = buffer[4:]

                elif buffer[:4] == CHUNK_END:
                    receiving_chunk = False
                    if packet_data:
                        result = parse_packet(packet_data.hex(), has_packet_id=True)
                        if result:
                            # Debug: Print CBOR structure with keys
                            data = result.get("data", {})
                            log.debug(
                                f"Received Chunk {data.get(0)} (Packet ID: {result['packet_id']})"
                            )
                            log.debug(f"CBOR Data: {data}")

                            # Process chunk in collector
                            collector.process_chunk(result)

                            # Check if collection is complete and export CBOR
                            collector.is_complete()

                            if result.get("ack_requested", 1):
                                # Send ACK if hash is valid
                                if result["hash_valid"]:
                                    send_ack(serial, result["received_hash"])
                                else:
                                    log.warning("Hash invalid, no ACK sent")
                            else:
                                log.debug("ACK not requested, no ACK sent")
                    packet_data = bytearray()
                    buffer = buffer[4:]

                elif receiving_header or receiving_chunk:
                    # Collect packet data
                    packet_data.append(buffer[0])
                    buffer = buffer[1:]
                else:
                    # Skip unknown byte
                    buffer = buffer[1:]

        except Exception as e:
            log.exception("Processor error", exc_info=e)

    log.debug("Packet processor stopped")


def offline_mode(file: Path):
    """Run in offline mode loading data from XML"""
    collector = DeviceDataCollector()
    if collector.load_from_xml(file):
        log.info("Data loaded. Entering offline command mode.")
        log.info("Press 'v' to visualize, 's' to save report, 'q' to quit")
        # TODO: replace by pre mode selection

        while True:
            try:
                cmd = input("Command (v/s/q): ").strip().lower()
                if cmd == "v":
                    collector.visualize_matrices()
                elif cmd == "s":
                    collector.manual_save()
                elif cmd == "q":
                    break
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    else:
        log.error("Failed to load data.")


def monitor_serial(serial_port: str, baudrate: int = 9600):
    """Concurrent serial monitor with two threads"""
    log.debug(f"Opening {serial_port} at {baudrate} baud...")

    collector = DeviceDataCollector()

    with Serial(serial_port, baudrate, timeout=1) as serial:
        data_queue = queue.Queue(maxsize=1000)
        stop_event = threading.Event()

        log.info("Starting concurrent monitoring...")
        log.info("Press 's' to save, 'r' to save raw XML, 'v' to visualize")

        reader_thread = threading.Thread(
            target=serial_reader, args=(serial, data_queue, stop_event), name="SerialReader"
        )

        processor_thread = threading.Thread(
            target=packet_processor,
            args=(serial, data_queue, stop_event, collector),
            name="PacketProcessor",
        )

        reader_thread.daemon = True
        processor_thread.daemon = True

        reader_thread.start()
        processor_thread.start()

        try:
            while True:
                if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                    cmd = sys.stdin.read(1)  # TODO: why?
                    if cmd == "s":
                        collector.manual_save()
                    elif cmd == "r":
                        collector.save_raw_xml()  # TODO: always save
                    elif cmd == "v":
                        collector.visualize_matrices()
                    elif cmd == "q":
                        break

                if not reader_thread.is_alive() or not processor_thread.is_alive():
                    log.warning("Thread died")
                    break

        except KeyboardInterrupt:
            log.info("\nStopping...")

        finally:
            # Stop threads gracefully
            stop_event.set()

            # Wait for threads to finish (with timeout)
            reader_thread.join(
                timeout=2
            )  # TODO: this does not kill the process, could survive as zombie
            processor_thread.join(timeout=2)

            log.debug("Monitor stopped")
