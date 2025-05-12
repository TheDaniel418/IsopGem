"""
@file style_mappings_utils.py
@description Shared style mappings for rich text editing components
@created 2024-05-05
@dependencies PyQt6

Provides centralized style mappings for text, table, and border styles.
These can be used by different components to ensure consistency.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextListFormat, QTextTableFormat


class StyleMappingsUtils:
    """Utility class for centralized style mappings."""

    # Table border style mappings (enum to string)
    @staticmethod
    def get_border_style_name(style: QTextTableFormat.BorderStyle) -> str:
        """Get the name of a border style from its enum value.

        Args:
            style: The border style enum

        Returns:
            The border style name
        """
        style_map = {
            QTextTableFormat.BorderStyle.BorderStyle_Solid: "Solid",
            QTextTableFormat.BorderStyle.BorderStyle_Dashed: "Dashed",
            QTextTableFormat.BorderStyle.BorderStyle_Dotted: "Dotted",
            QTextTableFormat.BorderStyle.BorderStyle_Double: "Double",
            QTextTableFormat.BorderStyle.BorderStyle_Groove: "Groove",
            QTextTableFormat.BorderStyle.BorderStyle_Ridge: "Ridge",
            QTextTableFormat.BorderStyle.BorderStyle_Inset: "Inset",
            QTextTableFormat.BorderStyle.BorderStyle_Outset: "Outset",
            QTextTableFormat.BorderStyle.BorderStyle_None: "None",
        }
        return style_map.get(style, "Solid")

    # Table border style mappings (string to enum)
    @staticmethod
    def get_border_style_enum(name: str) -> QTextTableFormat.BorderStyle:
        """Get the enum value for a border style from its name.

        Args:
            name: The border style name

        Returns:
            The border style enum
        """
        style_map_rev = {
            "Solid": QTextTableFormat.BorderStyle.BorderStyle_Solid,
            "Dashed": QTextTableFormat.BorderStyle.BorderStyle_Dashed,
            "Dotted": QTextTableFormat.BorderStyle.BorderStyle_Dotted,
            "Double": QTextTableFormat.BorderStyle.BorderStyle_Double,
            "Groove": QTextTableFormat.BorderStyle.BorderStyle_Groove,
            "Ridge": QTextTableFormat.BorderStyle.BorderStyle_Ridge,
            "Inset": QTextTableFormat.BorderStyle.BorderStyle_Inset,
            "Outset": QTextTableFormat.BorderStyle.BorderStyle_Outset,
            "None": QTextTableFormat.BorderStyle.BorderStyle_None,
        }
        return style_map_rev.get(name, QTextTableFormat.BorderStyle.BorderStyle_Solid)

    # List style mappings
    @staticmethod
    def get_list_style_name(style: QTextListFormat.Style) -> str:
        """Get the name of a list style from its enum value.

        Args:
            style: The list style enum

        Returns:
            The list style name
        """
        style_map = {
            QTextListFormat.Style.ListDisc: "Bullet",
            QTextListFormat.Style.ListCircle: "Circle",
            QTextListFormat.Style.ListSquare: "Square",
            QTextListFormat.Style.ListDecimal: "Numbered",
            QTextListFormat.Style.ListLowerAlpha: "Lowercase Alpha",
            QTextListFormat.Style.ListUpperAlpha: "Uppercase Alpha",
            QTextListFormat.Style.ListLowerRoman: "Lowercase Roman",
            QTextListFormat.Style.ListUpperRoman: "Uppercase Roman",
        }
        return style_map.get(style, "Bullet")

    @staticmethod
    def get_list_style_enum(name: str) -> QTextListFormat.Style:
        """Get the enum value for a list style from its name.

        Args:
            name: The list style name

        Returns:
            The list style enum
        """
        style_map_rev = {
            "Bullet": QTextListFormat.Style.ListDisc,
            "Circle": QTextListFormat.Style.ListCircle,
            "Square": QTextListFormat.Style.ListSquare,
            "Numbered": QTextListFormat.Style.ListDecimal,
            "Lowercase Alpha": QTextListFormat.Style.ListLowerAlpha,
            "Uppercase Alpha": QTextListFormat.Style.ListUpperAlpha,
            "Lowercase Roman": QTextListFormat.Style.ListLowerRoman,
            "Uppercase Roman": QTextListFormat.Style.ListUpperRoman,
        }
        return style_map_rev.get(name, QTextListFormat.Style.ListDisc)

    # Text alignment mappings
    @staticmethod
    def get_alignment_name(alignment: Qt.AlignmentFlag) -> str:
        """Get the name of an alignment from its enum value.

        Args:
            alignment: The alignment enum

        Returns:
            The alignment name
        """
        alignment_map = {
            Qt.AlignmentFlag.AlignLeft: "Left",
            Qt.AlignmentFlag.AlignCenter: "Center",
            Qt.AlignmentFlag.AlignRight: "Right",
            Qt.AlignmentFlag.AlignJustify: "Justify",
        }
        return alignment_map.get(alignment, "Left")

    @staticmethod
    def get_alignment_enum(name: str) -> Qt.AlignmentFlag:
        """Get the enum value for an alignment from its name.

        Args:
            name: The alignment name

        Returns:
            The alignment enum
        """
        alignment_map_rev = {
            "Left": Qt.AlignmentFlag.AlignLeft,
            "Center": Qt.AlignmentFlag.AlignCenter,
            "Right": Qt.AlignmentFlag.AlignRight,
            "Justify": Qt.AlignmentFlag.AlignJustify,
        }
        return alignment_map_rev.get(name, Qt.AlignmentFlag.AlignLeft)
