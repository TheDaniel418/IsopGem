"""
Cosmic Force Interpreter Service.

This module provides functionality for interpreting ternary digits and patterns
according to the cosmic force framework, assigning meanings to digits and
identifying significant patterns in ternary numbers.
"""

from typing import Dict, List, Union


class CosmicForceInterpreter:
    """Interprets ternary representations as cosmic forces."""

    # Dictionary mapping ternary digits to their cosmic force meanings
    DIGIT_MEANINGS = {
        0: {
            "name": "Void",
            "energy": "Neutral",
            "quality": "Receptive",
            "description": "Represents emptiness, potential, and the unmanifested.",
        },
        1: {
            "name": "Light",
            "energy": "Expansive",
            "quality": "Active",
            "description": "Represents growth, creation, and forward movement.",
        },
        2: {
            "name": "Form",
            "energy": "Contractive",
            "quality": "Solidifying",
            "description": "Represents structure, boundaries, and manifestation.",
        },
    }

    # Position modifiers affect the interpretation based on digit position
    POSITION_MODIFIERS = [
        "Foundation",
        "Core",
        "Expression",
        "Projection",
        "Potential",
        "Higher Mind",
        "Spirit",
        "Cosmic Connection",
        "Divine Spark",
    ]

    # Pattern interpretations
    SEQUENCE_MEANINGS = {
        0: "Void sequences represent periods of gestation, emptiness that precedes creation.",
        1: "Light sequences indicate periods of rapid growth, expansion, and creative breakthrough.",
        2: "Form sequences show consolidation, structure-building, and manifestation of ideas.",
    }

    BALANCE_INTERPRETATIONS = {
        "balanced": "The forces are in harmony, indicating balance between expansion and contraction.",
        "expansive": "The forces favor growth and expansion, suggesting creative periods and new beginnings.",
        "contractive": "The forces favor form and structure, suggesting manifestation and concretization of ideas.",
    }

    def __init__(self):
        """Initialize the cosmic force interpreter."""
        pass

    def interpret_digit(self, digit: int, position: int = 0) -> Dict[str, str]:
        """
        Interpret a single ternary digit with position context.

        Args:
            digit: The ternary digit (0, 1, or 2)
            position: The position of the digit (0-based, right-to-left)

        Returns:
            Dictionary with the interpretation
        """
        if digit not in (0, 1, 2):
            raise ValueError(f"Invalid ternary digit: {digit}")

        interpretation = self.DIGIT_MEANINGS[digit].copy()

        # Add position context if within range
        pos_modifier = self.POSITION_MODIFIERS[
            min(position, len(self.POSITION_MODIFIERS) - 1)
        ]
        interpretation["position"] = pos_modifier
        interpretation["context"] = f"{pos_modifier} {interpretation['name']}"

        return interpretation

    def analyze_ternary(
        self, ternary_digits: List[int]
    ) -> Dict[str, Union[List, Dict, str]]:
        """
        Analyze a full ternary number and interpret its cosmic forces.

        Args:
            ternary_digits: List of ternary digits (0, 1, 2)

        Returns:
            Dictionary with comprehensive analysis
        """
        if not ternary_digits:
            return {"error": "Empty ternary input"}

        result = {
            "digits": [],
            "overall": {},
            "patterns": [],
            "balance": "",
            "dominant_force": "",
        }

        # Interpret each digit
        for i, digit in enumerate(reversed(ternary_digits)):
            interpretation = self.interpret_digit(digit, i)
            result["digits"].append(interpretation)

        # Analyze patterns
        counts = {0: 0, 1: 0, 2: 0}
        for digit in ternary_digits:
            counts[digit] += 1

        # Determine dominant force
        max_count = max(counts.values())
        dominant_digits = [d for d, count in counts.items() if count == max_count]

        if len(dominant_digits) == 1:
            dominant = dominant_digits[0]
            result[
                "dominant_force"
            ] = f"{self.DIGIT_MEANINGS[dominant]['name']} ({self.DIGIT_MEANINGS[dominant]['energy']})"
        else:
            result["dominant_force"] = "Mixed (No clear dominance)"

        # Calculate balance
        balance_score = counts[1] - counts[2]
        if balance_score > 0:
            result["balance"] = self.BALANCE_INTERPRETATIONS["expansive"]
        elif balance_score < 0:
            result["balance"] = self.BALANCE_INTERPRETATIONS["contractive"]
        else:
            result["balance"] = self.BALANCE_INTERPRETATIONS["balanced"]

        # Find sequences
        self.analyze_patterns(ternary_digits, result)

        # Overall interpretation
        result["overall"]["summary"] = self._generate_overall_summary(
            ternary_digits, counts, balance_score
        )

        return result

    def analyze_patterns(self, ternary_digits: List[int], result: Dict = None) -> Dict:
        """
        Analyze patterns in the ternary digits.

        Args:
            ternary_digits: List of ternary digits
            result: Optional existing result dictionary to add to

        Returns:
            Dictionary with pattern analysis
        """
        if result is None:
            result = {"patterns": []}

        if not ternary_digits:
            return result

        # Find sequences
        current_sequence = []
        current_digit = None

        for digit in ternary_digits:
            if digit == current_digit:
                current_sequence.append(digit)
            else:
                if len(current_sequence) >= 3:
                    result["patterns"].append(
                        {
                            "digit": current_digit,
                            "length": len(current_sequence),
                            "meaning": self.SEQUENCE_MEANINGS[current_digit],
                        }
                    )
                current_digit = digit
                current_sequence = [digit]

        # Check last sequence
        if len(current_sequence) >= 3:
            result["patterns"].append(
                {
                    "digit": current_digit,
                    "length": len(current_sequence),
                    "meaning": self.SEQUENCE_MEANINGS[current_digit],
                }
            )

        return result

    def _generate_overall_summary(
        self, digits: List[int], counts: Dict[int, int], balance_score: int
    ) -> str:
        """
        Generate an overall summary of the ternary number's cosmic forces.

        Args:
            digits: The ternary digits
            counts: Counts of each digit
            balance_score: The balance score between Light and Form

        Returns:
            A string summary
        """
        total_digits = len(digits)

        # Determine nature of the number
        dominant = (
            max(counts, key=counts.get) if len(set(counts.values())) > 1 else None
        )

        if dominant == 0:
            nature = "primarily receptive and potential-filled"
        elif dominant == 1:
            nature = "predominantly expansive and growth-oriented"
        elif dominant == 2:
            nature = "mainly structured and form-based"
        else:
            if balance_score > 0:
                nature = "balanced with expansive tendencies"
            elif balance_score < 0:
                nature = "balanced with form-building tendencies"
            else:
                nature = "perfectly balanced between forces"

        # Check for special patterns
        has_sequences = any(counts[d] >= 3 for d in counts)
        sequence_desc = ""
        if has_sequences:
            sequence_types = []
            for digit, count in counts.items():
                if count >= 3:
                    if digit == 0:
                        sequence_types.append("periods of gestation")
                    elif digit == 1:
                        sequence_types.append("creative breakthroughs")
                    elif digit == 2:
                        sequence_types.append("manifestation phases")

            if sequence_types:
                sequence_desc = f" Notable for its {', '.join(sequence_types)}."

        return f"This ternary number is {nature}.{sequence_desc} It contains {counts[0]} Void, {counts[1]} Light, and {counts[2]} Form forces."
