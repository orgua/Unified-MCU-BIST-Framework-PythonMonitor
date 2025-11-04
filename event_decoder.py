#!/usr/bin/env python3
"""
Event Decoder for CBOR Serial Monitor
Decodes 31-bit event types using one-hot encoding
"""

# Pin Event Type definitions
PIN_EVENT_TYPES = {
    0: "HANDSHAKE_OK_INITIATOR",
    1: "HANDSHAKE_OK_RESPONDER",
    2: "HANDSHAKE_FAILURE",
    3: "DATA_HANDSHAKE_OK",
    4: "DATA_HANDSHAKE_FAILURE",
    5: "PIN_IS_CONNECTED_WITH_INTERNAL_PIN",
    6: "PIN_IS_NOT_LOW_WHEN_PULLED_DOWN",
    7: "PIN_IS_NOT_HIGH_WHEN_PULLED_UP",
    8: "PIN_IS_NOT_LOW_WHEN_DRIVEN_LOW",
    9: "PIN_IS_NOT_HIGH_WHEN_DRIVEN_HIGH",
    10: "UART_RX_IS_NOT_WORKING",
    11: "EXPECTS_TO_WORK_IN_ONE_DIRECTION",
    12: "EXCEEDS_CONNECTION_LIMIT"
}

def decode_event_type_one_hot(event_bits):
    events = []
    
    # Check each bit position (0-15, since we have 16 bits)
    for bit_position in range(16):
        # Check if this bit is set
        if event_bits & (1 << bit_position):
            event_name = PIN_EVENT_TYPES.get(bit_position, f"UNKNOWN_EVENT_{bit_position}")
            events.append(event_name)
    
    return events

def merge_handshake_events(events):
    merged = []
    has_initiator = "HANDSHAKE_OK_INITIATOR" in events
    has_responder = "HANDSHAKE_OK_RESPONDER" in events
    
    # Add HANDSHAKE_OK if both initiator and responder are present
    if has_initiator and has_responder:
        merged.append("HANDSHAKE_OK")
    
    # Add all other events (excluding the individual handshake events)
    for event in events:
        if event not in ["HANDSHAKE_OK_INITIATOR", "HANDSHAKE_OK_RESPONDER"]:
            merged.append(event)
        elif has_initiator and not has_responder and event == "HANDSHAKE_OK_INITIATOR":
            # Keep initiator if responder is not present
            merged.append(event)
        elif has_responder and not has_initiator and event == "HANDSHAKE_OK_RESPONDER":
            # Keep responder if initiator is not present
            merged.append(event)
    
    return merged
def encode_event_list(events):
    """Encode a list of event names back into one-hot encoded integer."""
    event_bits = 0
    reverse_event_map = {v: k for k, v in PIN_EVENT_TYPES.items()}
    
    for event in events:
        bit_position = reverse_event_map.get(event)
        if bit_position is not None:
            event_bits |= (1 << bit_position)
    
    return event_bits

def decode_result(result):
    if not result or not result.get('hash_valid'):
        print("⚠️ Invalid or corrupted result")
        return []
    
    data = result.get('data', {})
    
    # Look for event_type field (adjust key name as needed)
    event_bits = data.get('event_type', 0)
    
    if event_bits == 0:
        return []
    
    # Decode one-hot encoded events
    events = decode_event_type_one_hot(event_bits)
    
    # Merge handshake events
    merged_events = merge_handshake_events(events)
    
    return merged_events


def format_event_list(events):
    """Format event list for pretty printing."""
    if not events:
        return "No events"
    
    return ", ".join(events)