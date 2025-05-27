"""
@file font_manager.py
@description Font management utility for Unicode text support
@author Assistant
@created 2024-01-20
@lastModified 2024-01-20
@dependencies PyQt6
"""

from typing import List, Optional

from loguru import logger
from PyQt6.QtGui import QFont, QFontDatabase


class FontManager:
    """Manages fonts for proper Unicode text display across different scripts."""

    def __init__(self):
        """Initialize the font manager."""
        self._unicode_fonts = {}
        self._fallback_fonts = {}
        self._system_fonts = []
        self._script_fonts = {
            "latin": [],
            "greek": [],
            "hebrew": [],
            "arabic": [],
            "cyrillic": [],
            "chinese": [],
            "japanese": [],
            "korean": [],
            "mixed": [],
        }

        # Initialize font detection
        self._detect_system_fonts()
        self._categorize_fonts_by_script()

        logger.info("FontManager initialized successfully")

    def _detect_system_fonts(self):
        """Detect available system fonts."""
        try:
            # Use static method to get font families
            self._system_fonts = QFontDatabase.families()
            logger.info(f"Detected {len(self._system_fonts)} system fonts")

            # Log some key Unicode fonts if available
            unicode_fonts_found = []
            key_fonts = [
                "Times New Roman",
                "Arial Unicode MS",
                "DejaVu Sans",
                "Noto Sans",
                "Liberation Serif",
                "Segoe UI",
            ]

            for font in key_fonts:
                if font in self._system_fonts:
                    unicode_fonts_found.append(font)

            if unicode_fonts_found:
                logger.info(
                    f"Found Unicode-capable fonts: {', '.join(unicode_fonts_found)}"
                )
            else:
                logger.warning(
                    "No common Unicode fonts detected - text rendering may be limited"
                )

        except Exception as e:
            logger.error(f"Error detecting system fonts: {e}")
            # Fallback fonts that are commonly available
            self._system_fonts = [
                "Arial",
                "Times New Roman",
                "Helvetica",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans",
                "Segoe UI",
                "Tahoma",
            ]

    def _categorize_fonts_by_script(self):
        """Categorize fonts by the scripts they support."""

        # Font preferences by script (in order of preference)
        script_preferences = {
            "greek": [
                "Times New Roman",
                "Arial Unicode MS",
                "Lucida Grande",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans",
                "Noto Serif",
                "Linux Libertine",
                "FreeSerif",
                "GNU FreeFont",
                "Segoe UI",
                "Tahoma",
                "Verdana",
                "Georgia",
                "Palatino",
                "Book Antiqua",
            ],
            "hebrew": [
                "Times New Roman",
                "Arial Unicode MS",
                "Lucida Grande",
                "David",
                "Miriam",
                "Narkisim",
                "Rod",
                "SBL Hebrew",
                "Ezra SIL",
                "Cardo",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans Hebrew",
                "Noto Serif Hebrew",
                "FreeSerif",
                "Segoe UI",
                "Tahoma",
                "Verdana",
            ],
            "arabic": [
                "Times New Roman",
                "Arial Unicode MS",
                "Lucida Grande",
                "Traditional Arabic",
                "Arabic Typesetting",
                "Simplified Arabic",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans Arabic",
                "Noto Serif Arabic",
                "Amiri",
                "Scheherazade",
                "FreeSerif",
                "Segoe UI",
                "Tahoma",
            ],
            "cyrillic": [
                "Times New Roman",
                "Arial Unicode MS",
                "Lucida Grande",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans",
                "Noto Serif",
                "PT Sans",
                "PT Serif",
                "Segoe UI",
                "Tahoma",
                "Verdana",
            ],
            "chinese": [
                "SimSun",
                "SimHei",
                "Microsoft YaHei",
                "Arial Unicode MS",
                "Noto Sans CJK SC",
                "Noto Serif CJK SC",
                "Source Han Sans",
                "Source Han Serif",
                "WenQuanYi Micro Hei",
                "DejaVu Sans",
            ],
            "japanese": [
                "MS Gothic",
                "MS Mincho",
                "Meiryo",
                "Arial Unicode MS",
                "Noto Sans CJK JP",
                "Noto Serif CJK JP",
                "Source Han Sans",
                "Source Han Serif",
                "DejaVu Sans",
            ],
            "korean": [
                "Malgun Gothic",
                "Batang",
                "Dotum",
                "Arial Unicode MS",
                "Noto Sans CJK KR",
                "Noto Serif CJK KR",
                "Source Han Sans",
                "Source Han Serif",
                "DejaVu Sans",
            ],
            "latin": [
                "Times New Roman",
                "Arial",
                "Helvetica",
                "Georgia",
                "Verdana",
                "Segoe UI",
                "DejaVu Sans",
                "Liberation Serif",
                "Noto Sans",
                "Noto Serif",
            ],
        }

        # Find available fonts for each script
        for script, preferred_fonts in script_preferences.items():
            available_fonts = []
            for font_name in preferred_fonts:
                if font_name in self._system_fonts:
                    available_fonts.append(font_name)

            # Add fallback fonts if none found
            if not available_fonts:
                fallback_fonts = [
                    "Arial",
                    "Times New Roman",
                    "DejaVu Sans",
                    "Liberation Serif",
                ]
                for font_name in fallback_fonts:
                    if font_name in self._system_fonts:
                        available_fonts.append(font_name)
                        break

                # Ultimate fallback
                if not available_fonts and self._system_fonts:
                    available_fonts.append(self._system_fonts[0])

            self._script_fonts[script] = available_fonts
            logger.debug(f"Script '{script}' fonts: {available_fonts[:3]}...")

        # Mixed script fonts (fonts that support multiple scripts)
        mixed_fonts = []
        universal_fonts = [
            "Arial Unicode MS",
            "Lucida Grande",
            "DejaVu Sans",
            "Noto Sans",
            "Times New Roman",
            "Segoe UI",
        ]

        for font_name in universal_fonts:
            if font_name in self._system_fonts:
                mixed_fonts.append(font_name)

        self._script_fonts["mixed"] = mixed_fonts or self._script_fonts["latin"]

    def get_best_font_for_script(
        self, script: str, size: int = 12, weight: QFont.Weight = QFont.Weight.Normal
    ) -> QFont:
        """Get the best available font for a script.

        Args:
            script: Script name
            size: Font size
            weight: Font weight

        Returns:
            QFont object
        """
        available_fonts = self._script_fonts.get(script, self._script_fonts["latin"])

        if available_fonts:
            font_family = available_fonts[0]
        else:
            font_family = "Arial"  # Ultimate fallback

        font = QFont(font_family, size, weight)
        return font

    def get_font_for_text(
        self, text: str, size: int = 12, weight: QFont.Weight = QFont.Weight.Normal
    ) -> QFont:
        """Get the best font for displaying specific text.

        Args:
            text: Text to display
            size: Font size
            weight: Font weight

        Returns:
            QFont object
        """
        script = self.detect_text_script(text)
        return self.get_best_font_for_script(script, size, weight)

    def get_mixed_script_font(
        self, size: int = 12, weight: QFont.Weight = QFont.Weight.Normal
    ) -> QFont:
        """Get a font that supports multiple scripts.

        Args:
            size: Font size
            weight: Font weight

        Returns:
            QFont object
        """
        mixed_fonts = self._script_fonts.get("mixed", self._script_fonts["latin"])
        font_family = mixed_fonts[0] if mixed_fonts else "Arial"

        font = QFont(font_family, size, weight)
        return font

    def detect_text_script(self, text: str) -> str:
        """Detect the primary script used in text.

        Args:
            text: Text to analyze

        Returns:
            Primary script name
        """
        if not text:
            return "latin"

        script_counts = {
            "greek": 0,
            "hebrew": 0,
            "arabic": 0,
            "cyrillic": 0,
            "chinese": 0,
            "japanese": 0,
            "korean": 0,
            "latin": 0,
        }

        for char in text:
            code_point = ord(char)

            # Greek (0370-03FF, 1F00-1FFF)
            if (0x0370 <= code_point <= 0x03FF) or (0x1F00 <= code_point <= 0x1FFF):
                script_counts["greek"] += 1
            # Hebrew (0590-05FF, FB1D-FB4F)
            elif (0x0590 <= code_point <= 0x05FF) or (0xFB1D <= code_point <= 0xFB4F):
                script_counts["hebrew"] += 1
            # Arabic (0600-06FF, 0750-077F, FB50-FDFF, FE70-FEFF)
            elif (
                (0x0600 <= code_point <= 0x06FF)
                or (0x0750 <= code_point <= 0x077F)
                or (0xFB50 <= code_point <= 0xFDFF)
                or (0xFE70 <= code_point <= 0xFEFF)
            ):
                script_counts["arabic"] += 1
            # Cyrillic (0400-04FF, 0500-052F, 2DE0-2DFF, A640-A69F)
            elif (
                (0x0400 <= code_point <= 0x04FF)
                or (0x0500 <= code_point <= 0x052F)
                or (0x2DE0 <= code_point <= 0x2DFF)
                or (0xA640 <= code_point <= 0xA69F)
            ):
                script_counts["cyrillic"] += 1
            # Chinese (4E00-9FFF, 3400-4DBF, 20000-2A6DF)
            elif (
                (0x4E00 <= code_point <= 0x9FFF)
                or (0x3400 <= code_point <= 0x4DBF)
                or (0x20000 <= code_point <= 0x2A6DF)
            ):
                script_counts["chinese"] += 1
            # Japanese Hiragana/Katakana (3040-309F, 30A0-30FF)
            elif (0x3040 <= code_point <= 0x309F) or (0x30A0 <= code_point <= 0x30FF):
                script_counts["japanese"] += 1
            # Korean (AC00-D7AF, 1100-11FF, 3130-318F)
            elif (
                (0xAC00 <= code_point <= 0xD7AF)
                or (0x1100 <= code_point <= 0x11FF)
                or (0x3130 <= code_point <= 0x318F)
            ):
                script_counts["korean"] += 1
            # Latin and other common scripts
            elif (0x0020 <= code_point <= 0x007F) or (0x00A0 <= code_point <= 0x00FF):
                script_counts["latin"] += 1

        # Find the script with the highest count
        max_script = max(script_counts, key=script_counts.get)
        max_count = script_counts[max_script]

        # If multiple scripts are present, return 'mixed'
        non_zero_scripts = [
            script for script, count in script_counts.items() if count > 0
        ]
        if len(non_zero_scripts) > 1 and max_count < len(text) * 0.7:
            return "mixed"

        return max_script if max_count > 0 else "latin"

    def get_available_fonts_for_script(self, script: str) -> List[str]:
        """Get list of available fonts for a script.

        Args:
            script: Script name

        Returns:
            List of font family names
        """
        return self._script_fonts.get(script, [])

    def apply_unicode_font_to_widget(
        self,
        widget,
        text: str = "",
        size: int = 12,
        weight: QFont.Weight = QFont.Weight.Normal,
    ):
        """Apply appropriate Unicode font to a widget.

        Args:
            widget: Qt widget
            text: Text that will be displayed
            size: Font size
            weight: Font weight
        """
        try:
            if text:
                font = self.get_font_for_text(text, size, weight)
            else:
                font = self.get_mixed_script_font(size, weight)

            widget.setFont(font)
            logger.debug(f"Applied font '{font.family()}' to widget")
        except Exception as e:
            logger.error(f"Error applying Unicode font to widget: {e}")

    @classmethod
    def get_instance(cls) -> "FontManager":
        """Get singleton instance of FontManager."""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


# Global font manager instance
_font_manager: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """Get the global font manager instance.

    Returns:
        FontManager instance
    """
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
