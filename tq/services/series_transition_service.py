"""
Purpose: Provides calculation services for series transitions between multiple numbers

This file is part of the tq pillar and serves as a service component.
It is responsible for calculating transitions between series of numbers,
including sum of transitions, closed loop sums, and amalgams.

Key components:
- SeriesTransitionService: Main service class for series transition calculations
- calculate_series_transitions: Core function for transition calculations
- calculate_closed_loop: Function for closed loop calculations

Dependencies:
- tq.utils.ternary_transition: For transition calculations
- tq.utils.ternary_converter: For ternary conversion
- shared.services.number_properties_service: For number analysis

Related files:
- tq/ui/widgets/series_transition_widget.py: UI that uses this service
- tq/ui/dialogs/series_transition_window.py: Window containing the widget
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

from loguru import logger
from PyQt6.QtCore import QObject, Qt, QTimer

from shared.services.number_properties_service import NumberPropertiesService
from shared.services.service_locator import ServiceLocator
from tq.ui.dialogs.series_transition_window import SeriesTransitionWindow
from tq.utils.ternary_converter import decimal_to_ternary
from tq.utils.ternary_transition import TernaryTransition


class NumberProperties(TypedDict):
    """Type definition for number properties dictionary."""

    factors: List[int]
    prime_factors: List[int]
    is_prime: bool
    is_perfect: bool
    is_abundant: bool
    is_deficient: bool
    aliquot_sum: int


@dataclass
class SeriesTransitionResult:
    """Result of a series transition calculation.

    Attributes:
        transitions: List of transitions between consecutive pairs in decimal
        transition_ternaries: List of transitions in ternary string form
        transition_sum: Sum of all transitions
        closed_loop_sum: Sum including transition from first to last number
        amalgam: Transition between sum of numbers and sum of differences
    """

    transitions: List[int]  # List of transitions between consecutive pairs (decimal)
    transition_ternaries: List[str]  # List of transitions in ternary form
    transition_sum: int  # Sum of all transitions
    closed_loop_sum: int  # Sum including transition from first to last number
    amalgam: int  # Transition between sum of numbers and sum of differences


class SeriesTransitionService(QObject):
    """Service for calculating series transitions."""

    _instance: Optional["SeriesTransitionService"] = None

    def __init__(self) -> None:
        """Initialize the service."""
        super().__init__()
        self.transition = TernaryTransition()
        self.number_service = NumberPropertiesService.get_instance()
        self.window: Optional[SeriesTransitionWindow] = None

    @classmethod
    def get_instance(cls) -> "SeriesTransitionService":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = SeriesTransitionService()
            # Register with ServiceLocator
            ServiceLocator.register(SeriesTransitionService, cls._instance)
            logger.debug("Registered SeriesTransitionService with ServiceLocator")
        return cls._instance

    def get_window(self) -> SeriesTransitionWindow:
        """Get or create the Series Transitions window.

        Returns:
            The SeriesTransitionWindow instance.
        """
        if self.window is None:
            self.window = SeriesTransitionWindow()
        return self.window

    def set_series_numbers(self, numbers: List[int]) -> None:
        """Set the series numbers and show the window.

        Args:
            numbers: List of numbers to set in pairs. Must be an even number of values
                    as they will be processed as pairs (a1,b1,a2,b2,...).

        Raises:
            ValueError: If the length of numbers is not even.
        """
        logger.debug(f"SeriesTransitionService: Setting series numbers {numbers}")

        if len(numbers) % 2 != 0:
            raise ValueError("Must provide an even number of values for pairs")

        # Create window if it doesn't exist
        if self.window is None:
            logger.debug("Creating new SeriesTransitionWindow")
            self.window = SeriesTransitionWindow()
        else:
            logger.debug("Using existing SeriesTransitionWindow")

        # Set the numbers and show
        logger.debug("Setting series numbers in window")
        self.window.set_series_numbers(numbers)
        logger.debug("Series numbers set successfully")

        # Ensure window is visible and focused using stronger focus methods
        self.window.show()

        # Use multiple methods to force the window to the front
        self.window.setWindowState(
            self.window.windowState() & ~Qt.WindowState.WindowMinimized
        )
        self.window.raise_()
        self.window.activateWindow()

        # If the window has an ensure_on_top method (inherits from AuxiliaryWindow), use it
        if hasattr(self.window, "ensure_on_top"):
            self.window.ensure_on_top()

        # Use timer to attempt focus again after event loop processes other events
        QTimer.singleShot(100, lambda: self._delayed_focus())

        logger.debug("Window visibility and focus operations complete")

    def _delayed_focus(self) -> None:
        """Apply delayed focus to ensure window is on top."""
        if self.window and self.window.isVisible():
            self.window.raise_()
            self.window.activateWindow()
            logger.debug("Applied delayed focus to series transition window")

    def calculate_series_transitions(
        self, numbers: List[int]
    ) -> Optional[SeriesTransitionResult]:
        """Calculate transitions for a series of numbers.

        Args:
            numbers: List of numbers to calculate transitions between.
                   Should be provided as pairs, e.g. [a1, b1, a2, b2, ...]
                   where transitions are calculated between a1→b1, a2→b2, etc.

        Returns:
            SeriesTransitionResult containing transitions and their properties,
            or None if an error occurs.

        Raises:
            ValueError: If less than 2 numbers are provided.
        """
        if len(numbers) < 2:
            logger.error("Need at least 2 numbers for series transitions")
            return None

        try:
            # Calculate transitions between pairs (not consecutive numbers)
            transitions: List[int] = []
            transition_ternaries: List[str] = []
            for i in range(0, len(numbers), 2):
                if i + 1 >= len(numbers):
                    break

                # Convert numbers to ternary
                first_ternary = decimal_to_ternary(numbers[i])
                second_ternary = decimal_to_ternary(numbers[i + 1])
                # Apply transition and convert back to decimal
                result_ternary = self.transition.apply_transition(
                    first_ternary, second_ternary
                )
                result_decimal = int(result_ternary, 3)
                transitions.append(result_decimal)
                transition_ternaries.append(result_ternary)

            # Calculate transition sum
            transition_sum = sum(transitions)

            # Calculate closed loop (transition from first number to last number)
            if len(numbers) >= 4:  # Need at least 2 pairs for closed loop
                first_ternary = decimal_to_ternary(numbers[0])  # Very first number
                last_ternary = decimal_to_ternary(numbers[-1])  # Very last number
                closed_loop_ternary = self.transition.apply_transition(
                    first_ternary, last_ternary
                )
                closed_loop_transition = int(closed_loop_ternary, 3)
                closed_loop_sum = transition_sum + closed_loop_transition
            else:
                closed_loop_sum = transition_sum

            # Calculate amalgam (transition between sum of numbers and sum of differences)
            # First calculate sum of all input numbers
            numbers_sum = sum(numbers)

            # Calculate sum of absolute differences between pairs
            differences_sum = 0
            for i in range(0, len(numbers), 2):
                if i + 1 >= len(numbers):
                    break
                differences_sum += abs(numbers[i] - numbers[i + 1])

            # Transition between the sums
            numbers_sum_ternary = decimal_to_ternary(numbers_sum)
            differences_sum_ternary = decimal_to_ternary(differences_sum)
            amalgam_ternary = self.transition.apply_transition(
                numbers_sum_ternary, differences_sum_ternary
            )
            amalgam = int(amalgam_ternary, 3)

            return SeriesTransitionResult(
                transitions=transitions,
                transition_ternaries=transition_ternaries,
                transition_sum=transition_sum,
                closed_loop_sum=closed_loop_sum,
                amalgam=amalgam,
            )

        except Exception as e:
            logger.error(f"Error calculating series transitions: {e}")
            return None

    def get_transition_properties(
        self, result: SeriesTransitionResult
    ) -> Dict[str, NumberProperties]:
        """Get number properties for all significant numbers in the result.

        Args:
            result: SeriesTransitionResult to analyze

        Returns:
            Dictionary mapping number types to their properties
        """
        return {
            "transition_sum": self.number_service.get_number_properties(
                result.transition_sum
            ),
            "closed_loop_sum": self.number_service.get_number_properties(
                result.closed_loop_sum
            ),
            "amalgam": self.number_service.get_number_properties(result.amalgam),
        }
