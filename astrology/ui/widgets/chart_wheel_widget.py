"""
Purpose: Provides a widget for displaying astrological chart wheels.

This file is part of the astrology pillar and serves as a UI component.
It provides a widget for rendering astrological chart wheels with
zodiac signs, houses, and planetary positions.

Key components:
- ChartWheelWidget: Widget for displaying astrological chart wheels

Dependencies:
- PyQt6: For UI components
- math: For mathematical calculations
- astrology.models: For astrological data models
"""

import math

from loguru import logger
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QWidget

from astrology.models.chart import Chart
from astrology.utils.astro_utils import (
    zodiac_to_chart_angle,
)


class ChartWheelWidget(QWidget):
    """Widget for displaying astrological chart wheels."""

    def __init__(self, parent=None):
        """Initialize the chart wheel widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Chart data
        self.chart = None

        # Wheel dimensions
        self.margin = 20
        self.outer_ring_width = 30  # Width of the degree markers ring
        self.house_ring_width = 30  # Width of the house ring - thinner to match design
        self.inner_circle_radius = 100  # Radius of the inner circle

        # Colors
        self.background_color = QColor(255, 255, 255)  # White background

        # Zodiac symbols
        self.zodiac_symbols = {
            "Aries": "♈",
            "Taurus": "♉",
            "Gemini": "♊",
            "Cancer": "♋",
            "Leo": "♌",
            "Virgo": "♍",
            "Libra": "♎",
            "Scorpio": "♏",
            "Sagittarius": "♐",
            "Capricorn": "♑",
            "Aquarius": "♒",
            "Pisces": "♓",
        }

        # Planet symbols
        self.planet_symbols = {
            "Sun": "☉",
            "Moon": "☽",
            "Mercury": "☿",
            "Venus": "♀",
            "Mars": "♂",
            "Jupiter": "♃",
            "Saturn": "♄",
            "Uranus": "♅",
            "Neptune": "♆",
            "Pluto": "♇",
            "North Node": "☊",
            "South Node": "☋",
            "Chiron": "⚷",
        }

        # Set minimum size
        self.setMinimumSize(400, 400)

        # Enable mouse tracking for tooltips
        self.setMouseTracking(True)

        logger.debug("ChartWheelWidget initialized")

    def set_chart(self, chart: Chart) -> None:
        """Set the chart to display.

        Args:
            chart: The chart to display
        """
        self.chart = chart

        # Debug logging for house positions
        if chart and chart.houses:
            logger.debug(f"Chart has {len(chart.houses)} houses")
            for house in sorted(chart.houses, key=lambda h: h.number):
                logger.debug(
                    f"House {house.number}: cusp at {house.cusp_degree:.2f}°, ends at {house.end_degree:.2f}°"
                )

            # Log the Ascendant position
            ascendant = chart.get_ascendant()
            if ascendant is not None:
                logger.debug(f"Ascendant is at {ascendant:.2f}°")

        self.update()

    def paintEvent(self, event):
        """Paint the chart wheel.

        Args:
            event: Paint event
        """
        if not self.chart:
            self._paint_empty_wheel(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the widget dimensions
        width = self.width()
        height = self.height()

        # Calculate the center and radius
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - self.margin

        # Draw background
        painter.fillRect(0, 0, width, height, self.background_color)

        # Calculate inner radii
        inner_radius = radius - self.outer_ring_width
        house_inner_radius = inner_radius - self.house_ring_width

        # Draw the outer circle (degree markers ring)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw the inner circle of the degree markers ring
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Draw the inner circle of the house ring
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(
            QPointF(center_x, center_y), house_inner_radius, house_inner_radius
        )

        # Draw the degree markers in the outer ring (tick marks)
        for i in range(360):  # Draw a marker every degree
            angle = math.radians(i)

            # Only draw markers in the outer ring
            outer_x = center_x + radius * math.cos(angle)
            outer_y = center_y + radius * math.sin(angle)

            # Determine tick length based on position
            tick_length = 3  # Default small tick
            line_width = 0.5  # Default thin line

            # Medium ticks for every 5 degrees
            if i % 5 == 0:
                tick_length = 6
                line_width = 0.7

            # Longer ticks for every 10 degrees
            if i % 10 == 0:
                tick_length = 10
                line_width = 1.0

            inner_x = center_x + (radius - tick_length) * math.cos(angle)
            inner_y = center_y + (radius - tick_length) * math.sin(angle)

            # Draw tick marks
            painter.setPen(QPen(Qt.GlobalColor.black, line_width))
            painter.drawLine(QPointF(inner_x, inner_y), QPointF(outer_x, outer_y))

        # Draw the cardinal cross lines (vertical and horizontal)
        painter.setPen(QPen(Qt.GlobalColor.black, 1.5))
        # Vertical line
        painter.drawLine(
            QPointF(center_x, center_y - radius), QPointF(center_x, center_y + radius)
        )
        # Horizontal line
        painter.drawLine(
            QPointF(center_x - radius, center_y), QPointF(center_x + radius, center_y)
        )

        # Get the Ascendant degree (1st house cusp)
        ascendant = None
        if self.chart and self.chart.houses:
            ascendant = self.chart.get_ascendant()
            logger.debug(f"Drawing chart with Ascendant at {ascendant:.2f}°")

            # Log all house cusps for debugging
            logger.debug("=== HOUSE POSITIONS FOR CHART DRAWING ===")
            logger.debug("-" * 50)
            logger.debug(
                f"{'House':<6} {'Cusp Degree':>12} {'End Degree':>12} {'Width':>8}"
            )
            logger.debug("-" * 50)

            houses = sorted(self.chart.houses, key=lambda h: h.number)
            for house in houses:
                width = (house.end_degree - house.cusp_degree) % 360
                logger.debug(
                    f"{house.number:<6} {house.cusp_degree:>12.2f}° {house.end_degree:>12.2f}° {width:>8.2f}°"
                )

        # If we have house data, use it; otherwise fall back to equal houses
        if self.chart and self.chart.houses and ascendant is not None:
            logger.debug("Using actual house positions for chart drawing")

            # SIMPLIFIED APPROACH:
            # 1. Extract house positions into an array
            # 2. Calculate rotation to place Ascendant at west (180 degrees)
            # 3. Draw each house cusp with proper rotation

            # Extract house positions (sorted by house number)
            houses = sorted(self.chart.houses, key=lambda h: h.number)

            # The Ascendant (1st house cusp) should be at 180 degrees (9 o'clock position/west)
            # Calculate the rotation needed to place the Ascendant at 180 degrees
            asc_chart_angle = self._zodiac_to_chart_angle(ascendant)
            rotation_offset = 180 - asc_chart_angle

            # Force the Ascendant to be at 180 degrees (west/9 o'clock)
            # This is a direct approach to ensure the Ascendant is at the correct position
            logger.debug("FORCING Ascendant to be at 180 degrees (west/9 o'clock)")

            logger.debug(
                f"Ascendant zodiac degree: {ascendant:.2f}°, chart angle: {asc_chart_angle:.2f}°"
            )
            logger.debug(
                f"Rotation offset: {rotation_offset:.2f}° to place Ascendant at 180° (9 o'clock/west)"
            )

            # Draw each house cusp
            for i in range(len(houses)):
                house = houses[i]
                next_house = houses[
                    (i + 1) % 12
                ]  # Get the next house (wrap around to 1st house after 12th)

                # Convert zodiacal degrees to chart angles
                house_chart_angle = self._zodiac_to_chart_angle(house.cusp_degree)

                # Apply rotation to place Ascendant at west (180 degrees)
                rotated_angle = (house_chart_angle + rotation_offset) % 360

                # Convert to radians for drawing
                chart_angle = math.radians(rotated_angle)

                logger.debug(
                    f"House {house.number}: zodiac {house.cusp_degree:.2f}°, chart angle {house_chart_angle:.2f}°, rotated {rotated_angle:.2f}°"
                )

                # Draw the house line
                # Use a thicker, red line for the first house to make it more visible
                if house.number == 1:
                    painter.setPen(
                        QPen(QColor(255, 0, 0), 2)
                    )  # Red, thicker line for first house
                else:
                    painter.setPen(QPen(Qt.GlobalColor.black, 1))

                line_x = center_x + inner_radius * math.cos(chart_angle)
                line_y = center_y + inner_radius * math.sin(chart_angle)
                painter.drawLine(
                    QPointF(
                        center_x + house_inner_radius * math.cos(chart_angle),
                        center_y + house_inner_radius * math.sin(chart_angle),
                    ),
                    QPointF(line_x, line_y),
                )

                # Calculate the middle angle between this house cusp and the next
                next_house_chart_angle = self._zodiac_to_chart_angle(
                    next_house.cusp_degree
                )
                next_rotated_angle = (next_house_chart_angle + rotation_offset) % 360
                next_chart_angle = math.radians(next_rotated_angle)

                # Handle the case where we cross 0/360
                if next_chart_angle < chart_angle:
                    next_chart_angle += math.radians(360)

                # Find the middle of the house for the number placement
                middle_angle = (chart_angle + next_chart_angle) / 2
                if middle_angle > math.radians(360):
                    middle_angle -= math.radians(360)

                # Log the middle angle for debugging
                middle_degrees = math.degrees(middle_angle) % 360
                logger.debug(
                    f"House {house.number} middle angle: {middle_degrees:.2f}°"
                )

                # Draw the house number
                number_radius = inner_radius - self.house_ring_width / 2
                number_x = center_x + number_radius * math.cos(middle_angle)
                number_y = center_y + number_radius * math.sin(middle_angle)

                # Log the house number position
                degrees_middle = math.degrees(middle_angle) % 360
                logger.debug(
                    f"House {house.number} number drawn at angle {degrees_middle:.2f}° (radius: {number_radius:.2f})"
                )

                font = QFont()

                # Make the first house number larger and bold
                if house.number == 1:
                    font.setPointSize(12)  # Larger font for the first house
                    font.setBold(True)  # Bold for emphasis
                    painter.setFont(font)
                    painter.setPen(QColor(255, 0, 0))  # Red text for first house
                else:
                    font.setPointSize(10)  # Smaller font for other houses
                    painter.setFont(font)
                    painter.setPen(Qt.GlobalColor.black)

                painter.drawText(
                    QRectF(number_x - 15, number_y - 15, 30, 30),
                    Qt.AlignmentFlag.AlignCenter,
                    str(house.number),
                )
        else:
            # Fall back to equal houses if no chart data
            for i in range(12):
                # Start with house 1 at the 180-degree mark (9 o'clock position/west) and proceed counterclockwise
                # Each house is 30 degrees, counterclockwise means NEGATIVE angle increment
                angle = math.radians(
                    180 - i * 30
                )  # This places house 1 at 180 degrees (west)

                # Draw the house line
                # Use a thicker, red line for the first house to make it more visible
                house_number = i + 1
                if house_number == 1:
                    painter.setPen(
                        QPen(QColor(255, 0, 0), 2)
                    )  # Red, thicker line for first house
                else:
                    painter.setPen(QPen(Qt.GlobalColor.black, 1))

                line_x = center_x + inner_radius * math.cos(angle)
                line_y = center_y + inner_radius * math.sin(angle)
                painter.drawLine(
                    QPointF(
                        center_x + house_inner_radius * math.cos(angle),
                        center_y + house_inner_radius * math.sin(angle),
                    ),
                    QPointF(line_x, line_y),
                )

                # Draw the house number
                house_number = (
                    i + 1
                )  # Start with 1 at 9 o'clock (left), then 2, 3, etc.
                number_radius = inner_radius - self.house_ring_width / 2
                # Position exactly in the middle of the house segment
                number_angle = angle + math.radians(
                    15
                )  # Middle of the house (15 degrees from house cusp)
                number_x = center_x + number_radius * math.cos(number_angle)
                number_y = center_y + number_radius * math.sin(number_angle)

                # Log the house number position
                degrees_angle = math.degrees(number_angle) % 360
                logger.debug(
                    f"Fallback: House {house_number} number drawn at angle {degrees_angle:.2f}° (radius: {number_radius:.2f})"
                )

                font = QFont()

                # Make the first house number larger and bold
                if house_number == 1:
                    font.setPointSize(12)  # Larger font for the first house
                    font.setBold(True)  # Bold for emphasis
                    painter.setFont(font)
                    painter.setPen(QColor(255, 0, 0))  # Red text for first house
                else:
                    font.setPointSize(10)  # Smaller font for other houses
                    painter.setFont(font)
                    painter.setPen(Qt.GlobalColor.black)

                painter.drawText(
                    QRectF(number_x - 15, number_y - 15, 30, 30),
                    Qt.AlignmentFlag.AlignCenter,
                    str(house_number),
                )

        # Draw the zodiac divisions (30 degree divisions in the outer ring)
        # Get the Ascendant degree if we haven't already
        if ascendant is None and self.chart and self.chart.houses:
            ascendant = self.chart.get_ascendant()

        if self.chart and ascendant is not None:
            # Calculate the rotation offset to place Ascendant at 180 degrees (9 o'clock/west)
            # Use the same rotation offset as for house cusps to ensure consistency
            asc_chart_angle = self._zodiac_to_chart_angle(ascendant)
            rotation_offset = 180 - asc_chart_angle
            logger.debug(
                f"Zodiac divisions: Using rotation offset {rotation_offset:.2f}° to place Ascendant at 180° (west)"
            )

            # Draw the 12 zodiac sign divisions (every 30 degrees)
            for i in range(12):
                # Calculate the zodiac sign starting degree
                zodiac_degree = i * 30  # 0, 30, 60, ..., 330

                # Convert to chart angle and apply rotation
                chart_angle = math.radians(
                    self._zodiac_to_chart_angle(zodiac_degree) + rotation_offset
                )

                # Draw the division line - only in the outer ring
                painter.setPen(QPen(Qt.GlobalColor.black, 2.0))
                painter.drawLine(
                    QPointF(
                        center_x + inner_radius * math.cos(chart_angle),
                        center_y + inner_radius * math.sin(chart_angle),
                    ),
                    QPointF(
                        center_x + radius * math.cos(chart_angle),
                        center_y + radius * math.sin(chart_angle),
                    ),
                )
        else:
            # Fall back to fixed positions if no chart data
            for i in range(12):
                # Align zodiac divisions with house divisions
                angle = math.radians(180 - i * 30)

                # Draw the division line - only in the outer ring
                painter.setPen(QPen(Qt.GlobalColor.black, 2.0))
                painter.drawLine(
                    QPointF(
                        center_x + inner_radius * math.cos(angle),
                        center_y + inner_radius * math.sin(angle),
                    ),
                    QPointF(
                        center_x + radius * math.cos(angle),
                        center_y + radius * math.sin(angle),
                    ),
                )

        # Draw center circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        center_circle_radius = house_inner_radius / 2
        painter.drawEllipse(
            QPointF(center_x, center_y), center_circle_radius, center_circle_radius
        )

        # Draw chart info in center if available
        if hasattr(self, "_draw_chart_info"):
            self._draw_chart_info(painter, center_x, center_y, center_circle_radius)

    def _zodiac_to_chart_angle(self, zodiac_degree):
        """Convert a zodiacal degree to a chart angle.

        This method is now a wrapper around the utility function zodiac_to_chart_angle.
        See astrology.utils.astro_utils for the implementation details.

        Args:
            zodiac_degree: Degree in the zodiac (0-360)

        Returns:
            Corresponding angle on the chart (0-360)
        """
        # We use the utility function to ensure consistency
        return zodiac_to_chart_angle(zodiac_degree)

    def _paint_empty_wheel(self, _):
        """Paint an empty wheel with a message."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the widget dimensions
        width = self.width()
        height = self.height()

        # Calculate the center and radius
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - self.margin

        # Draw background
        painter.fillRect(0, 0, width, height, self.background_color)

        # Calculate inner radii
        inner_radius = radius - self.outer_ring_width
        house_inner_radius = inner_radius - self.house_ring_width

        # Draw the outer circle (degree markers ring)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw the inner circle of the degree markers ring
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Draw the inner circle of the house ring
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(
            QPointF(center_x, center_y), house_inner_radius, house_inner_radius
        )

        # Draw the cardinal cross lines (vertical and horizontal)
        painter.setPen(QPen(Qt.GlobalColor.black, 1.5))
        # Vertical line
        painter.drawLine(
            QPointF(center_x, center_y - radius), QPointF(center_x, center_y + radius)
        )
        # Horizontal line
        painter.drawLine(
            QPointF(center_x - radius, center_y), QPointF(center_x + radius, center_y)
        )

        # Draw center circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        center_circle_radius = house_inner_radius / 2
        painter.drawEllipse(
            QPointF(center_x, center_y), center_circle_radius, center_circle_radius
        )

        # Draw message
        painter.setPen(QPen(Qt.GlobalColor.black))
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                center_x - center_circle_radius,
                center_y - 20,
                center_circle_radius * 2,
                40,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "No chart data available.\nCreate a chart to view it here.",
        )

    def _draw_zodiac_ring(self, painter, center_x, center_y, radius, rotation_angle):
        """Draw the zodiac ring.

        Args:
            painter: QPainter object
            center_x: X-coordinate of the center
            center_y: Y-coordinate of the center
            radius: Outer radius of the zodiac ring
            rotation_angle: Angle to rotate the chart to place Ascendant at 9 o'clock
        """
        # Draw zodiac signs
        inner_radius = radius - self.zodiac_ring_width

        # Draw the outer circle
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw the inner circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Draw each zodiac sign (30 degrees each)
        for i in range(12):
            # Get the sign name
            signs = list(self.zodiac_symbols.keys())
            sign = signs[i]

            # Calculate the start and end angles
            start_angle = i * 30
            end_angle = (i + 1) * 30

            # Draw the sign segment (only in the zodiac ring, not extending to center)
            path = QPainterPath()

            # Start at inner radius, not center
            inner_start_x = center_x + inner_radius * math.cos(
                math.radians(90 - start_angle)
            )
            inner_start_y = center_y - inner_radius * math.sin(
                math.radians(90 - start_angle)
            )
            path.moveTo(inner_start_x, inner_start_y)

            # Outer arc
            path.arcTo(
                center_x - radius,
                center_y - radius,
                radius * 2,
                radius * 2,
                90 - start_angle,
                -30,
            )

            # Line to inner radius
            path.lineTo(
                center_x + inner_radius * math.cos(math.radians(90 - end_angle)),
                center_y - inner_radius * math.sin(math.radians(90 - end_angle)),
            )

            # Inner arc
            path.arcTo(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2,
                inner_radius * 2,
                90 - end_angle,
                30,
            )

            path.closeSubpath()

            # Fill with the sign color
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setBrush(QBrush(self.zodiac_colors[sign]))
            painter.drawPath(path)

            # Draw the sign symbol
            symbol_radius = radius - self.zodiac_ring_width / 2
            symbol_angle = math.radians(
                90 - (start_angle + 15)
            )  # Middle of the segment
            symbol_x = center_x + symbol_radius * math.cos(symbol_angle)
            symbol_y = center_y - symbol_radius * math.sin(symbol_angle)

            font = QFont()
            font.setPointSize(14)
            painter.setFont(font)

            # Save the current state of the painter
            painter.save()

            # Translate to the text position
            painter.translate(symbol_x, symbol_y)

            # Rotate the text to be readable (counter-rotate by the same angle)
            painter.rotate(-rotation_angle)

            # Draw the symbol centered at the origin (0,0)
            painter.drawText(
                QRectF(-15, -15, 30, 30),
                Qt.AlignmentFlag.AlignCenter,
                self.zodiac_symbols[sign],
            )

            # Restore the painter state
            painter.restore()

            # Draw dividing lines between zodiac signs
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            # Note: The dividing lines are now naturally created by the path edges

    def _draw_house_ring(self, painter, center_x, center_y, radius, rotation_angle):
        """Draw the house ring.

        Args:
            painter: QPainter object
            center_x: X-coordinate of the center
            center_y: Y-coordinate of the center
            radius: Outer radius of the house ring
            rotation_angle: Angle to rotate the chart to place Ascendant at 9 o'clock
        """
        # Draw houses
        inner_radius = radius - self.house_ring_width

        # Draw the inner circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Draw each house
        for house in self.chart.houses:
            # Calculate the start and end angles
            start_angle = house.cusp_degree
            end_angle = house.end_degree

            # Handle houses that cross the 0° Aries point
            if end_angle < start_angle:
                end_angle += 360

            # Convert to painter angles (0° is at 3 o'clock, counterclockwise)
            start_painter_angle = 90 - start_angle
            sweep_angle = -(end_angle - start_angle)

            # Draw the house segment (only in the house ring, not extending to center)
            path = QPainterPath()

            # Start at inner radius, not center
            inner_start_x = center_x + inner_radius * math.cos(
                math.radians(start_painter_angle)
            )
            inner_start_y = center_y - inner_radius * math.sin(
                math.radians(start_painter_angle)
            )
            path.moveTo(inner_start_x, inner_start_y)

            # Outer arc
            path.arcTo(
                center_x - radius,
                center_y - radius,
                radius * 2,
                radius * 2,
                start_painter_angle,
                sweep_angle,
            )

            # Line to inner radius
            path.lineTo(
                center_x
                + inner_radius
                * math.cos(math.radians(start_painter_angle + sweep_angle)),
                center_y
                - inner_radius
                * math.sin(math.radians(start_painter_angle + sweep_angle)),
            )

            # Inner arc
            path.arcTo(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2,
                inner_radius * 2,
                start_painter_angle + sweep_angle,
                -sweep_angle,
            )

            path.closeSubpath()

            # Fill with a light color
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
            painter.drawPath(path)

            # Draw the house number
            number_radius = radius - self.house_ring_width / 2
            number_angle = math.radians(
                start_painter_angle + sweep_angle / 2
            )  # Middle of the segment
            number_x = center_x + number_radius * math.cos(number_angle)
            number_y = center_y - number_radius * math.sin(number_angle)

            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)

            # Save the current state of the painter
            painter.save()

            # Translate to the text position
            painter.translate(number_x, number_y)

            # Rotate the text to be readable (counter-rotate by the same angle)
            painter.rotate(-rotation_angle)

            # Draw the house number centered at the origin (0,0)
            painter.drawText(
                QRectF(-15, -15, 30, 30),
                Qt.AlignmentFlag.AlignCenter,
                str(house.number),
            )

            # Restore the painter state
            painter.restore()

            # Draw the house cusp line
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            cusp_angle = math.radians(start_painter_angle)
            painter.drawLine(
                QPointF(
                    center_x + inner_radius * math.cos(cusp_angle),
                    center_y - inner_radius * math.sin(cusp_angle),
                ),
                QPointF(
                    center_x + radius * math.cos(cusp_angle),
                    center_y - radius * math.sin(cusp_angle),
                ),
            )

    def _draw_planets(self, painter, center_x, center_y, radius, rotation_angle):
        """Draw the planets.

        Args:
            painter: QPainter object
            center_x: X-coordinate of the center
            center_y: Y-coordinate of the center
            radius: Outer radius of the planet ring
            rotation_angle: Angle to rotate the chart to place Ascendant at 9 o'clock
        """
        # Draw planets
        inner_radius = radius - self.planet_ring_width

        # Draw the inner circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Get the Ascendant degree
        ascendant = None
        if self.chart and self.chart.houses:
            ascendant = self.chart.get_ascendant()

        # Calculate rotation offset to place Ascendant at 180 degrees (9 o'clock/west)
        rotation_offset = 0
        if ascendant is not None:
            # Use the same rotation offset as for house cusps to ensure consistency
            asc_chart_angle = self._zodiac_to_chart_angle(ascendant)
            rotation_offset = 180 - asc_chart_angle
            logger.debug(
                f"Planets: Using rotation offset {rotation_offset:.2f}° to place Ascendant at 180° (west)"
            )

        # Group planets by position to avoid overlaps
        planet_positions = {}
        for name, body in self.chart.celestial_bodies.items():
            if body.longitude is not None:
                # Round to the nearest degree
                degree = round(body.longitude)
                if degree not in planet_positions:
                    planet_positions[degree] = []
                planet_positions[degree].append(body)

        # Draw each planet
        for degree, bodies in planet_positions.items():
            # Convert zodiacal degree to chart angle and apply rotation
            chart_angle = self._zodiac_to_chart_angle(degree) + rotation_offset
            angle = math.radians(chart_angle)

            # Calculate the base position
            planet_radius = radius * 0.8  # Position planets slightly inside the chart
            base_x = center_x + planet_radius * math.cos(angle)
            base_y = center_y + planet_radius * math.sin(angle)

            # Adjust for multiple planets at the same position
            num_bodies = len(bodies)
            offset = 15 if num_bodies > 1 else 0

            for i, body in enumerate(bodies):
                # Calculate offset position
                offset_angle = angle + math.radians(
                    (i - (num_bodies - 1) / 2) * offset / radius
                )
                planet_x = center_x + planet_radius * math.cos(offset_angle)
                planet_y = center_y + planet_radius * math.sin(offset_angle)

                # Draw the planet symbol
                font = QFont()
                font.setPointSize(12)
                painter.setFont(font)

                # Get the symbol
                symbol = self.planet_symbols.get(body.name, "?")

                # Draw a circle behind the symbol
                painter.setPen(QPen(Qt.GlobalColor.black, 1))
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawEllipse(QPointF(planet_x, planet_y), 12, 12)

                # Save the current state of the painter
                painter.save()

                # Translate to the text position
                painter.translate(planet_x, planet_y)

                # Rotate the text to be readable (counter-rotate by the same angle)
                painter.rotate(-rotation_angle)

                # Draw the symbol centered at the origin (0,0)
                painter.drawText(
                    QRectF(-12, -12, 24, 24), Qt.AlignmentFlag.AlignCenter, symbol
                )

                # Restore the painter state
                painter.restore()

                # Draw a line from the planet to its position on the zodiac wheel
                painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DotLine))
                zodiac_x = center_x + radius * math.cos(offset_angle)
                zodiac_y = center_y + radius * math.sin(offset_angle)
                painter.drawLine(
                    QPointF(planet_x, planet_y), QPointF(zodiac_x, zodiac_y)
                )

    def _draw_chart_info(self, painter, center_x, center_y, radius):
        """Draw chart information in the center.

        Args:
            painter: QPainter object
            center_x: X-coordinate of the center
            center_y: Y-coordinate of the center
            radius: Radius of the center circle
        """
        # Set up the font
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)

        # Draw the chart name
        painter.drawText(
            QRectF(center_x - radius * 0.8, center_y - radius * 0.5, radius * 1.6, 30),
            Qt.AlignmentFlag.AlignCenter,
            self.chart.name,
        )

        # Draw the chart date
        date_str = self.chart.date.strftime("%Y-%m-%d %H:%M")
        painter.drawText(
            QRectF(center_x - radius * 0.8, center_y - radius * 0.2, radius * 1.6, 30),
            Qt.AlignmentFlag.AlignCenter,
            date_str,
        )

        # Draw the location
        if self.chart.location_name:
            painter.drawText(
                QRectF(
                    center_x - radius * 0.8, center_y + radius * 0.1, radius * 1.6, 30
                ),
                Qt.AlignmentFlag.AlignCenter,
                self.chart.location_name,
            )

        # Draw the coordinates
        if self.chart.latitude is not None and self.chart.longitude is not None:
            lat_str = f"Lat: {self.chart.latitude:.4f}"
            lon_str = f"Lon: {self.chart.longitude:.4f}"
            painter.drawText(
                QRectF(
                    center_x - radius * 0.8, center_y + radius * 0.4, radius * 1.6, 30
                ),
                Qt.AlignmentFlag.AlignCenter,
                f"{lat_str}, {lon_str}",
            )

    def sizeHint(self):
        """Get the suggested size for the widget.

        Returns:
            Suggested size
        """
        return QSize(600, 600)

    def minimumSizeHint(self):
        """Get the minimum suggested size for the widget.

        Returns:
            Minimum suggested size
        """
        return QSize(400, 400)
