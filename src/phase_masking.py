"""
Phase Masking - Centralized phase filtering logic for connections and matrices
"""


class PhaseMasking:
    """Class to handle phase masking/filtering logic for connections and matrices"""

    MASK_VALUE = 3  # Value to use for masked phases

    @staticmethod
    def should_keep_phase(phase, existing_phases):
        """Apply phase filtering rules based on existing phases"""
        # If phase 4 does not exist, remove phases 2 and 0
        if 4 not in existing_phases:
            if phase in (2, 0):
                return False

        # If phase 5 does not exist, remove phases 3 and 1
        if 5 not in existing_phases:
            if phase in (3, 1):
                return False

        # If phase 2 does not exist, remove phase 0
        if 2 not in existing_phases:
            if phase == 0:
                return False

        # If phase 3 does not exist, remove phase 1
        if 3 not in existing_phases:
            if phase == 1:
                return False

        return True

    @staticmethod
    def mask_matrix_values(matrix_data, existing_phases):
        """Mask matrix values based on phase filtering rules"""
        masked_matrix = matrix_data.copy()

        for phase in range(6):  # Phases 0-5
            if not PhaseMasking.should_keep_phase(phase, existing_phases):
                # Set masked phase values to MASK_VALUE
                if phase in masked_matrix:
                    masked_matrix[phase] = PhaseMasking.MASK_VALUE

        return masked_matrix

    @staticmethod
    def get_filtered_phases(all_phases):
        """Get list of phases that should be kept after filtering"""
        return [
            phase for phase in all_phases if PhaseMasking.should_keep_phase(phase, set(all_phases))
        ]
