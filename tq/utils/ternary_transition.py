"""
Purpose: Implements the Ternary Transition System for qualitative transformation

This file is part of the tq pillar and serves as a utility component.
It is responsible for transforming ternary numbers using a specialized digit-pair
mapping that follows Taoist principles of transformation and motion.

Key components:
- TernaryTransition: Main class for applying ternary transitions
- TransitionMap: Type definition for the transition mapping dictionary
- apply_transition: Core method that transitions two ternary strings
- apply_multiple: Method for applying multiple transitions in sequence

Dependencies:
- tq.utils.ternary_converter: For ternary number validation and formatting

Related files:
- tq/utils/ternary_converter.py: Provides base-10 to base-3 conversion utilities
- tq/models/tq_grid.py: Will use this for TQ grid analysis
"""

import re
from typing import Dict, List, Literal, Optional, Tuple, cast

# Type aliases for clarity and type safety
TernaryDigit = Literal[0, 1, 2]
TernaryPair = Tuple[TernaryDigit, TernaryDigit]
TransitionMap = Dict[TernaryPair, TernaryDigit]


class TernaryTransition:
    """
    Implements the Ternary Transition System for transforming ternary numbers.

    This system uses a digit-pair mapping to transform two ternary numbers into
    a new ternary number, based on Taoist principles of transformation. Each
    digit represents a force of motion: 0 (equilibrium), 1 (outward/expansion),
    and 2 (inward/contraction).
    """

    # Default transition map based on Taoist principles
    DEFAULT_MAP: TransitionMap = {
        (0, 0): 0,
        (0, 1): 2,
        (0, 2): 1,
        (1, 0): 2,
        (1, 1): 1,
        (1, 2): 0,
        (2, 0): 1,
        (2, 1): 0,
        (2, 2): 2,
    }

    # Conrune transformation mapping: 0→0, 1→2, 2→1
    CONRUNE_MAP: Dict[str, str] = {"0": "0", "1": "2", "2": "1"}

    def __init__(self, transition_map: Optional[TransitionMap] = None) -> None:
        """
        Initialize the TernaryTransition with a transition map.

        Args:
            transition_map: Custom transition map (defaults to the standard Taoist map)

        Raises:
            ValueError: If the transition map is invalid
        """
        self.transition_map = transition_map or self.DEFAULT_MAP
        self._validate_transition_map()

    def _validate_transition_map(self) -> None:
        """
        Validate that the transition map contains all required transitions
        and only valid ternary digits.

        Raises:
            ValueError: If the transition map is invalid
        """
        required_pairs: List[TernaryPair] = [
            cast(TernaryPair, (i, j)) for i in range(3) for j in range(3)
        ]

        # Check that all required pairs are in the map
        for pair in required_pairs:
            if pair not in self.transition_map:
                raise ValueError(f"Transition map missing pair: {pair}")

        # Check that all values are valid ternary digits
        for pair, value in self.transition_map.items():
            if not isinstance(value, int) or value not in (0, 1, 2):
                raise ValueError(
                    f"Invalid transition value for {pair}: {value} "
                    f"(must be 0, 1, or 2)"
                )

    @classmethod
    def from_rule_string(cls, rule_string: str) -> "TernaryTransition":
        """
        Create a TernaryTransition from a rule string.

        Rule string format: "00:0,01:2,02:1,10:2,11:1,12:0,20:1,21:0,22:2"

        Args:
            rule_string: String defining the transition rules

        Returns:
            A new TernaryTransition instance with the specified rules

        Raises:
            ValueError: If the rule string is invalid
        """
        transition_map: TransitionMap = {}
        rules = rule_string.split(",")

        pattern = re.compile(r"([0-2])([0-2]):([0-2])")

        for rule in rules:
            match = pattern.match(rule.strip())
            if not match:
                raise ValueError(
                    f"Invalid rule format: {rule} "
                    f"(expected format: 'xy:z' where x,y,z are 0,1,2)"
                )

            x, y, z = match.groups()
            x_int = int(x)
            y_int = int(y)
            z_int = int(z)
            # Ensure the key is a valid TernaryPair
            if 0 <= x_int <= 2 and 0 <= y_int <= 2 and 0 <= z_int <= 2:
                pair = cast(TernaryPair, (x_int, y_int))
                transition_map[pair] = cast(TernaryDigit, z_int)
            else:
                raise ValueError(f"Invalid ternary digits in rule: {rule}")

        return cls(transition_map)

    def apply_transition(self, first: str, second: str) -> str:
        """
        Apply a transition between two ternary strings.

        Args:
            first: First ternary string
            second: Second ternary string

        Returns:
            The resulting ternary string after transition

        Raises:
            ValueError: If inputs are not valid ternary strings
            KeyError: If a digit pair is not found in the transition map
        """
        self._validate_ternary_input(first)
        self._validate_ternary_input(second)

        # Pad the shorter number with leading zeros
        max_length = max(len(first), len(second))
        first_padded = first.zfill(max_length)
        second_padded = second.zfill(max_length)

        # Apply transitions for each digit pair
        result_digits: List[str] = []
        for a, b in zip(first_padded, second_padded):
            try:
                a_int = int(a)
                b_int = int(b)
                if not (0 <= a_int <= 2 and 0 <= b_int <= 2):
                    raise ValueError(f"Digit pair out of range: ({a_int}, {b_int})")
                pair = cast(TernaryPair, (a_int, b_int))
                result_digits.append(str(self.transition_map[pair]))
            except KeyError:
                raise KeyError(
                    f"Transition pair ({a_int}, {b_int}) not found in transition map. This may indicate an incomplete transition map."
                )

        return "".join(result_digits)

    def apply_multiple(
        self, first: str, second: str, iterations: int
    ) -> List[Tuple[str, str, str]]:
        """
        Apply multiple transitions between two ternary strings.

        Args:
            first: Initial first ternary string
            second: Initial second ternary string
            iterations: Number of transitions to apply

        Returns:
            List of tuples (first, second, result) for each iteration

        Raises:
            ValueError: If inputs are not valid ternary strings or iterations < 1
            KeyError: If a digit pair is not found in the transition map
        """
        if iterations < 1:
            raise ValueError("Iterations must be a positive integer")

        results: List[Tuple[str, str, str]] = []
        current_first = first
        current_second = second

        for _ in range(iterations):
            try:
                result = self.apply_transition(current_first, current_second)
                results.append((current_first, current_second, result))

                # For the next iteration, the result becomes the first input
                # and the previous first input becomes the second input
                current_first, current_second = result, current_first
            except KeyError:
                # Include what we have so far and re-raise the error
                if results:
                    return results
                raise

        return results

    def find_cycle(
        self, first: str, second: str, max_iterations: int = 100
    ) -> List[Tuple[str, str, str]]:
        """
        Find a cycle in the transition sequence.

        Args:
            first: Initial first ternary string
            second: Initial second ternary string
            max_iterations: Maximum number of transitions to try

        Returns:
            List of tuples (first, second, result) in the cycle

        Raises:
            ValueError: If inputs are not valid ternary strings
            KeyError: If a digit pair is not found in the transition map
            RuntimeError: If no cycle is found within max_iterations
        """
        seen_states: Dict[Tuple[str, str], int] = {}
        current_first = first
        current_second = second

        for i in range(max_iterations):
            # The state is defined by the pair of inputs
            state = (current_first, current_second)

            if state in seen_states:
                # Found a cycle
                cycle_start = seen_states[state]
                cycle_length = i - cycle_start

                # Reconstruct the cycle
                cycle: List[Tuple[str, str, str]] = []
                temp_first, temp_second = first, second

                # Run to the start of the cycle
                try:
                    for _ in range(cycle_start):
                        result = self.apply_transition(temp_first, temp_second)
                        temp_first, temp_second = result, temp_first

                    # Capture the cycle
                    for _ in range(cycle_length):
                        result = self.apply_transition(temp_first, temp_second)
                        cycle.append((temp_first, temp_second, result))
                        temp_first, temp_second = result, temp_first

                    return cycle
                except KeyError as e:
                    # This shouldn't happen if we've already processed these states,
                    # but handle it gracefully anyway
                    raise KeyError(f"Unexpected error reconstructing cycle: {e}")

            seen_states[state] = i

            try:
                result = self.apply_transition(current_first, current_second)
                current_first, current_second = result, current_first
            except KeyError as e:
                # We can't continue finding cycles if we hit a KeyError
                raise KeyError(f"Cannot find cycle: {e}")

        raise RuntimeError(f"No cycle found within {max_iterations} iterations")

    def _validate_ternary_input(self, ternary_str: str) -> None:
        """
        Validate that a string contains only valid ternary digits.

        Args:
            ternary_str: String to validate

        Raises:
            ValueError: If the string contains non-ternary characters
        """
        if not all(digit in "012" for digit in ternary_str):
            raise ValueError(
                f"Invalid ternary string: '{ternary_str}' "
                f"(must contain only digits 0, 1, 2)"
            )

    def apply_conrune(self, ternary_str: str) -> str:
        """
        Apply Conrune transformation to a ternary string.

        The Conrune transformation swaps 1s and 2s while keeping 0s the same.
        This is a digit-wise operation on a single ternary number.

        Args:
            ternary_str: Ternary string to transform

        Returns:
            The transformed ternary string

        Raises:
            ValueError: If input is not a valid ternary string
            KeyError: If a digit is not found in the CONRUNE_MAP
        """
        self._validate_ternary_input(ternary_str)

        transformed_digits: List[str] = []
        for digit in ternary_str:
            try:
                transformed_digits.append(self.CONRUNE_MAP[digit])
            except KeyError:
                raise KeyError(f"Conrune mapping not defined for digit: {digit}")

        return "".join(transformed_digits)


def main() -> None:
    """Simple demonstration of the TernaryTransition system."""
    transition = TernaryTransition()

    # Example from the documentation
    first = "220"
    second = "111"
    result = transition.apply_transition(first, second)

    print(f"First number:  {first}")
    print(f"Second number: {second}")
    print(f"Result:        {result}")

    # Find a cycle
    print("\nFinding cycle for the same inputs:")
    cycle = transition.find_cycle(first, second)

    print(f"Cycle length: {len(cycle)}")
    for i, (a, b, c) in enumerate(cycle):
        print(f"Step {i+1}: ({a}, {b}) → {c}")

    # Demonstrate Conrune transformation
    print("\nConrune transformation examples:")
    conrune_examples = ["11220", "0", "12", "222", "111"]
    for example in conrune_examples:
        transformed = transition.apply_conrune(example)
        print(f"{example} → {transformed}")


if __name__ == "__main__":
    main()
