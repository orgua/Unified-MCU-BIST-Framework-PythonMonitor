from collections.abc import Mapping
from enum import Enum


class FW_KEY(int, Enum):  # TODO: find better name
    CHUNK_ID = 0
    PINS = 2
    PIN = 4
    EVENTS = 5
    CONNECTIONS = 6
    OTHER_PIN = 7
    CONNECTION_PARAMETER = 8  # Device ID (external) or Phase (internal)
    CONNECTION_TYPE = 9
    STREAM_NUMBER = 10


class HEADER_KEY(int, Enum):
    DEVICE_UUID = 0
    DEVICE_FAMILY = 1
    TOTAL_CHUNKS = 2
    TOTAL_PINS = 3
    ACTIVE_PINS = 4
    HEADER_HASH = 5
    NUMBER_SEEN_DEVICES = 6
    SEEN_DEVICE_IDS = 7
    ACK_REQUESTED = 8
    VERSION = 9
    EXPECTED_SESSIONS = 10


class CONNECTION_TYPE(int, Enum):
    INTERNAL = 0
    EXTERNAL = 1


# Internal Connection Phases
class PHASE(int, Enum):
    PULLDOWN = 0
    PULLUP = 1
    DRIVE_LOW = 2
    DRIVE_HIGH = 3
    ALLPULLUP_LOW = 4
    ALLPULLDOWN_HIGH = 5


PHASE_NAMES: Mapping[int, str] = {
    0: "ONE_SET_PULLDOWN",
    1: "ONE_SET_PULLUP",
    2: "DRIVE_LOW",
    3: "DRIVE_HIGH",
    4: "ALLPULLUP_LOW",
    5: "ALLPULLDOWN_HIGH",
}

PHASE_VECTORS: Mapping[int, Mapping[str, tuple]] = {
    0: {"A_to_B": (-1, 1), "B_to_A": (1, 1)},
    1: {"A_to_B": (-1, -1), "B_to_A": (1, -1)},
    2: {"A_to_B": (-2, 2), "B_to_A": (2, 2)},
    3: {"A_to_B": (-2, -2), "B_to_A": (2, -2)},
    4: {"A_to_B": (-3, 3), "B_to_A": (3, 3)},
    5: {"A_to_B": (-3, -3), "B_to_A": (3, -3)},
}
