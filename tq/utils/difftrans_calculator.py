"""
Purpose: Utility for calculating the Differential Transition (DiffTrans) for a quadset

This file is part of the tq pillar and serves as a utility component.
It provides a single source of truth for the DiffTrans calculation logic,
ensuring consistency across all usages (UI, analysis, tests, etc.).

Key components:
- DiffTransCalculator: Class with static method to compute DiffTrans

Dependencies:
- tq.utils.ternary_converter: For ternary conversion
- tq.utils.ternary_transition: For ternary transition logic

Usage Example:
    from tq.utils.difftrans_calculator import DiffTransCalculator
    result = DiffTransCalculator.compute_difftrans([A, B, C, D])
    print(result['decimal'], result['padded_ternary'])
"""

from typing import Dict, List, Tuple, Union

from tq.utils.ternary_converter import (
    TernaryString,
    decimal_to_ternary,
    ternary_to_decimal,
)
from tq.utils.ternary_transition import TernaryTransition


class DiffTransCalculator:
    """
    Calculates the Differential Transition (DiffTrans) for a quadset.

    Example:
        result = DiffTransCalculator.compute_difftrans([A, B, C, D])
        print(result['decimal'], result['padded_ternary'])
    """

    @staticmethod
    def compute_difftrans(
        values: Union[List[int], Tuple[int, int, int, int]]
    ) -> Dict[str, Union[int, str]]:
        """
        Compute the DiffTrans for a quadset.

        Args:
            values: List or tuple of four decimal values (A, B, C, D)

        Returns:
            dict with keys:
                - 'decimal': int, the DiffTrans as decimal
                - 'ternary': str, the DiffTrans as ternary string
                - 'padded_ternary': str, the DiffTrans as 6-digit ternary string
        """
        if not (isinstance(values, (list, tuple)) and len(values) == 4):
            raise ValueError(
                "Input must be a list or tuple of four decimal values (A, B, C, D)"
            )
        A, B, C, D = values
        diff1 = abs(A - B)
        diff2 = abs(C - D)
        diff1_tern = decimal_to_ternary(int(diff1), pad_length=6)
        diff2_tern = decimal_to_ternary(int(diff2), pad_length=6)
        t = TernaryTransition()
        result_tern = t.apply_transition(diff1_tern, diff2_tern)
        # Convert to TernaryString for type safety
        result_tern_typed = TernaryString(result_tern)
        result_dec = ternary_to_decimal(result_tern_typed)
        result_tern_padded = str(result_tern).zfill(6)
        return {
            "decimal": result_dec,
            "ternary": result_tern,
            "padded_ternary": result_tern_padded,
        }
