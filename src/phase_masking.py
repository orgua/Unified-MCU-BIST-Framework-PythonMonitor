"""Phase Masking

Centralized phase filtering logic for connections and matrices.
"""

from collections.abc import Sequence

from typing_extensions import deprecated

MASK_VALUE: int = 3  # Value to use for masked phases


def keep_phase(phase: int, existing_phases: Sequence) -> bool:
    """Apply phase filtering rules based on existing phases."""
    # If phase 2 does not exist, remove phase 0
    if (2 not in existing_phases) and (phase == 0):
        return False

    # If phase 3 does not exist, remove phase 1
    if (3 not in existing_phases) and (phase == 1):
        return False

    # If phase 4 does not exist, remove phases 2 and 0
    if (4 not in existing_phases) and (phase in (2, 0)):
        return False

    # If phase 5 does not exist, remove phases 3 and 1
    if (5 not in existing_phases) and (phase in (3, 1)):
        return False

    return True


@deprecated("not used ATM")
def mask_matrix_values(matrix_data, existing_phases: Sequence):
    """Mask matrix values based on phase filtering rules."""
    masked_matrix = matrix_data.copy()

    for phase in range(6):  # Phases 0-5
        if not keep_phase(phase, existing_phases) and (phase in masked_matrix):
            masked_matrix[phase] = MASK_VALUE

    return masked_matrix


@deprecated("not used ATM")
def get_filtered_phases(all_phases: Sequence) -> list[int]:
    """Get list of phases that should be kept after filtering."""
    return [phase for phase in all_phases if keep_phase(phase, all_phases)]
