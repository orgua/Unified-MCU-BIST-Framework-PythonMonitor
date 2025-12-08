"""Analyze single pin measurements to determine external drive strength."""

from collections.abc import Mapping
from collections.abc import Sequence

STRENGTH_2_PATTERN: Mapping[int, tuple] = {
    6: (1, 1, 1, 1, 1, 1),
    5: (1, 1, 1, 1, "U", 1),
    4: (1, 1, 1, 1, 0, 1),
    3: (1, 1, "U", 1, 0, 1),
    2: (1, 1, 0, 1, 0, 1),
    1: ("U", 1, 0, 1, 0, 1),
    0: (0, 1, 0, 1, 0, 1),
    -1: (0, "U", 0, 1, 0, 1),
    -2: (0, 0, 0, 1, 0, 1),
    -3: (0, 0, "U", 1, 0, 1),
    -4: (0, 0, 0, 0, 0, 1),
    -5: (0, 0, 0, 0, "U", 1),
    -6: (0, 0, 0, 0, 0, 0),
}
PATTERN_2_STRENGTH = {v: k for k, v in STRENGTH_2_PATTERN.items()}

# Order: Stage 1 N/P, Stage 2 N/P, Stage 3 N/P
CHECKS: set[str] = {"STEP_1_A", "STEP_1_B", "STEP_2_A", "STEP_2_B", "STEP_3_A", "STEP_3_B"}


def get_value_of_stage(stage: str, events: Sequence) -> int | str:
    """Convert sting-results of stages into integer data."""
    if f"{stage}_HIGH" in events:
        return 1
    if f"{stage}_LOW" in events:
        return 0
    return "U"


def analyze_pin(pin_events: Sequence) -> int | None:
    """Analyze events of a single pin."""
    pattern = tuple(get_value_of_stage(stage, pin_events) for stage in CHECKS)
    return PATTERN_2_STRENGTH.get(pattern)


def analyze_pins(device_pins: Mapping) -> list[int | None]:
    """Analyze events of multiple pins."""
    return [analyze_pin(p.get("events", [])) for p in device_pins]
