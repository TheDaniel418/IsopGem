"""Gematria calculation service.

This module provides functionality for calculating gematria values.
"""

import re
import unicodedata
from typing import List, Optional, Union

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.calculation_database_service import CalculationDatabaseService


class GematriaService:
    """Service for performing Gematria calculations."""

    def __init__(self) -> None:
        """Initialize the gematria service."""
        # Hebrew letter values for standard gematria
        self._letter_values = {
            # Alef to Tet (1-9)
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            # Yod to Tsadi (10-90)
            "י": 10,
            "כ": 20,
            "ל": 30,
            "מ": 40,
            "נ": 50,
            "ס": 60,
            "ע": 70,
            "פ": 80,
            "צ": 90,
            # Qof to Tav (100-400)
            "ק": 100,
            "ר": 200,
            "ש": 300,
            "ת": 400,
            # Final forms
            "ך": 20,
            "ם": 40,
            "ן": 50,
            "ף": 80,
            "ץ": 90,
        }

        # Hebrew letter positions for ordinal gematria
        self._letter_positions = {
            # Alef to Tet (1-9)
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            # Yod to Tsadi (10-18)
            "י": 10,
            "כ": 11,
            "ל": 12,
            "מ": 13,
            "נ": 14,
            "ס": 15,
            "ע": 16,
            "פ": 17,
            "צ": 18,
            # Qof to Tav (19-22)
            "ק": 19,
            "ר": 20,
            "ש": 21,
            "ת": 22,
            # Final forms (same as regular)
            "ך": 11,
            "ם": 13,
            "ן": 14,
            "ף": 17,
            "ץ": 18,
        }

        # Greek letter values for isopsophy
        self._greek_values = {
            # Alpha to Theta (1-9)
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ϝ": 6,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            # Iota to Pi (10-80)
            "ι": 10,
            "κ": 20,
            "λ": 30,
            "μ": 40,
            "ν": 50,
            "ξ": 60,
            "ο": 70,
            "π": 80,
            # Koppa to Omega (90-800)
            "ϙ": 90,
            "ρ": 100,
            "σ": 200,
            "τ": 300,
            "υ": 400,
            "φ": 500,
            "χ": 600,
            "ψ": 700,
            "ω": 800,
            # Variant forms
            "ς": 200,
            "ϲ": 200,  # Final sigma variants
        }

        # Greek letter positions for ordinal values
        self._greek_positions = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ϝ": 6,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 10,
            "κ": 11,
            "λ": 12,
            "μ": 13,
            "ν": 14,
            "ξ": 15,
            "ο": 16,
            "π": 17,
            "ϙ": 18,
            "ρ": 19,
            "σ": 20,
            "τ": 21,
            "υ": 22,
            "φ": 23,
            "χ": 24,
            "ψ": 25,
            "ω": 26,
            "ς": 20,
            "ϲ": 20,  # Final sigma variants
        }

        # Greek alpha-mu cipher (similar to Hebrew Albam)
        self._greek_alpha_mu_map = {
            # First half of alphabet maps to second half
            "α": "ν",
            "β": "ξ",
            "γ": "ο",
            "δ": "π",
            "ε": "ϙ",
            "ϝ": "ρ",
            "ζ": "σ",
            "η": "τ",
            "θ": "υ",
            "ι": "φ",
            "κ": "χ",
            "λ": "ψ",
            "μ": "ω",
            # Second half of alphabet maps to first half
            "ν": "α",
            "ξ": "β",
            "ο": "γ",
            "π": "δ",
            "ϙ": "ε",
            "ρ": "ϝ",
            "σ": "ζ",
            "τ": "η",
            "υ": "θ",
            "φ": "ι",
            "χ": "κ",
            "ψ": "λ",
            "ω": "μ",
            # Variant forms
            "ς": "ζ",
            "ϲ": "ζ",
        }

        # Greek alpha-omega cipher (similar to Hebrew Atbash)
        self._greek_alpha_omega_map = {
            # Reverse mapping (alpha->omega, beta->psi, etc.)
            "α": "ω",
            "β": "ψ",
            "γ": "χ",
            "δ": "φ",
            "ε": "υ",
            "ϝ": "τ",
            "ζ": "σ",
            "η": "ρ",
            "θ": "ϙ",
            "ι": "π",
            "κ": "ο",
            "λ": "ξ",
            "μ": "ν",
            "ν": "μ",
            "ξ": "λ",
            "ο": "κ",
            "π": "ι",
            "ϙ": "θ",
            "ρ": "η",
            "σ": "ζ",
            "τ": "ϝ",
            "υ": "ε",
            "φ": "δ",
            "χ": "γ",
            "ψ": "β",
            "ω": "α",
            # Variant forms
            "ς": "ζ",
            "ϲ": "ζ",
        }

        # TQ English letter values
        self._tq_values = {
            "i": 0,
            "I": 0,
            "l": 1,
            "L": 1,
            "c": 2,
            "C": 2,
            "h": 3,
            "H": 3,
            "p": 4,
            "P": 4,
            "a": 5,
            "A": 5,
            "x": 6,
            "X": 6,
            "j": 7,
            "J": 7,
            "w": 8,
            "W": 8,
            "t": 9,
            "T": 9,
            "o": 10,
            "O": 10,
            "g": 11,
            "G": 11,
            "f": 12,
            "F": 12,
            "e": 13,
            "E": 13,
            "r": 14,
            "R": 14,
            "s": 15,
            "S": 15,
            "q": 16,
            "Q": 16,
            "k": 17,
            "K": 17,
            "y": 18,
            "Y": 18,
            "z": 19,
            "Z": 19,
            "b": 20,
            "B": 20,
            "m": 21,
            "M": 21,
            "v": 22,
            "V": 22,
            "d": 23,
            "D": 23,
            "n": 24,
            "N": 24,
            "u": 25,
            "U": 25,
        }

        # Substitution ciphers
        self._albam_map = {
            # First half of alphabet maps to second half
            "א": "ל",
            "ב": "מ",
            "ג": "נ",
            "ד": "ס",
            "ה": "ע",
            "ו": "פ",
            "ז": "צ",
            "ח": "ק",
            "ט": "ר",
            "י": "ש",
            "כ": "ת",
            # Second half of alphabet maps to first half
            "ל": "א",
            "מ": "ב",
            "נ": "ג",
            "ס": "ד",
            "ע": "ה",
            "פ": "ו",
            "צ": "ז",
            "ק": "ח",
            "ר": "ט",
            "ש": "י",
            "ת": "כ",
            # Final forms
            "ך": "ת",
            "ם": "ב",
            "ן": "ג",
            "ף": "ו",
            "ץ": "ז",
        }

        self._atbash_map = {
            # Reverse mapping (alef->tav, bet->shin, etc.)
            "א": "ת",
            "ב": "ש",
            "ג": "ר",
            "ד": "ק",
            "ה": "צ",
            "ו": "פ",
            "ז": "ע",
            "ח": "ס",
            "ט": "נ",
            "י": "מ",
            "כ": "ל",
            "ל": "כ",
            "מ": "י",
            "נ": "ט",
            "ס": "ח",
            "ע": "ז",
            "פ": "ו",
            "צ": "ה",
            "ק": "ד",
            "ר": "ג",
            "ש": "ב",
            "ת": "א",
            # Final forms
            "ך": "ל",
            "ם": "י",
            "ן": "ט",
            "ף": "ו",
            "ץ": "ה",
        }

        # Hebrew final forms mapping (regular to final)
        self._hebrew_final_forms = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}

        # Initialize the database service
        self.db_service = CalculationDatabaseService()

        logger.debug("GematriaService initialized")

    def calculate(
        self,
        text: str,
        calculation_type: Union[
            CalculationType, str, CustomCipherConfig
        ] = CalculationType.MISPAR_HECHRACHI,
    ) -> int:
        """Calculate the gematria value for the given text.

        Args:
            text: The text to calculate
            calculation_type: The calculation type to use (enum, name, or custom config)

        Returns:
            The calculated gematria value
        """
        # Handle different input types for calculation_type
        if isinstance(calculation_type, str):
            # Special case for custom ciphers
            if calculation_type == "CUSTOM_CIPHER":
                # For custom ciphers, we need the custom_method_name to be set
                # This should be handled by the calling code
                logger.debug("Received CUSTOM_CIPHER as calculation type")
                # Return 0 as a fallback value since we can't calculate without the actual cipher
                return 0

            try:
                calculation_type = CalculationType(calculation_type)
            except ValueError:
                # If it's not a valid enum value, it might be a custom cipher ID
                # This would be handled by the calling code that would pass the CustomCipherConfig
                logger.error(f"Unknown calculation type: {calculation_type}")
                raise ValueError(f"Unknown calculation type: {calculation_type}")

        # Process based on calculation type
        if isinstance(calculation_type, CustomCipherConfig):
            return self._calculate_custom(text, calculation_type)

        # Use enum-based calculations
        # Strip any diacritical marks for Hebrew and Greek
        cleaned_text = self._strip_diacritical_marks(text)

        # Normalize Greek to lowercase for all standard (non-custom) calculations
        greek_types = [
            CalculationType.GREEK_ISOPSOPHY,
            CalculationType.GREEK_ORDINAL,
            CalculationType.GREEK_SQUARED,
            CalculationType.GREEK_REVERSAL,
            CalculationType.GREEK_ALPHA_MU,
            CalculationType.GREEK_ALPHA_OMEGA,
            CalculationType.GREEK_BUILDING,
            CalculationType.GREEK_TRIANGULAR,
            CalculationType.GREEK_HIDDEN,
            CalculationType.GREEK_FULL_NAME,
            CalculationType.GREEK_ADDITIVE,
        ]
        if calculation_type in greek_types:
            cleaned_text = cleaned_text.lower()

        # Handle Hebrew calculations
        if calculation_type == CalculationType.MISPAR_HECHRACHI:
            return self._calculate_standard(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_SIDURI:
            return self._calculate_ordinal(cleaned_text)
        elif calculation_type == CalculationType.ALBAM:
            return self._calculate_albam(cleaned_text)
        elif calculation_type == CalculationType.ATBASH:
            return self._calculate_atbash(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_GADOL:
            return self._calculate_large(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_BONEH:
            return self._calculate_building(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_KIDMI:
            return self._calculate_triangular(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_PERATI:
            return self._calculate_individual_square(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_SHEMI:
            return self._calculate_full_name(cleaned_text)
        elif calculation_type == CalculationType.MISPAR_MUSAFI:
            return self._calculate_additive(cleaned_text)

        # Handle Greek calculations
        elif calculation_type == CalculationType.GREEK_ISOPSOPHY:
            return self._calculate_greek_standard(cleaned_text)
        elif calculation_type == CalculationType.GREEK_ORDINAL:
            return self._calculate_greek_ordinal(cleaned_text)
        elif calculation_type == CalculationType.GREEK_SQUARED:
            return self._calculate_greek_squared(cleaned_text)
        elif calculation_type == CalculationType.GREEK_REVERSAL:
            return self._calculate_greek_reversal(cleaned_text)
        elif calculation_type == CalculationType.GREEK_ALPHA_MU:
            return self._calculate_greek_alpha_mu(cleaned_text)
        elif calculation_type == CalculationType.GREEK_ALPHA_OMEGA:
            return self._calculate_greek_alpha_omega(cleaned_text)
        elif calculation_type == CalculationType.GREEK_BUILDING:
            return self._calculate_greek_building(cleaned_text)
        elif calculation_type == CalculationType.GREEK_TRIANGULAR:
            return self._calculate_greek_triangular(cleaned_text)
        elif calculation_type == CalculationType.GREEK_HIDDEN:
            return self._calculate_greek_hidden(cleaned_text)
        elif calculation_type == CalculationType.GREEK_FULL_NAME:
            return self._calculate_greek_full_name(cleaned_text)
        elif calculation_type == CalculationType.GREEK_ADDITIVE:
            return self._calculate_greek_additive(cleaned_text)

        # Handle English calculations
        elif calculation_type == CalculationType.TQ_ENGLISH:
            return self._calculate_tq(text)  # No diacritical mark stripping for TQ

        raise ValueError(f"Unsupported calculation type: {calculation_type}")

    def _calculate_custom(self, text: str, config: CustomCipherConfig) -> int:
        """Calculate gematria value using a custom cipher configuration.

        Args:
            text: The text to calculate
            config: Custom cipher configuration

        Returns:
            The calculated gematria value
        """
        # Apply appropriate text preprocessing
        if config.language in [LanguageType.HEBREW, LanguageType.GREEK]:
            processed_text = self._strip_diacritical_marks(text)
        else:
            processed_text = text

        total = 0
        letter_values = config.letter_values

        for char in processed_text:
            # Handle case sensitivity
            lookup_char = char
            if not config.case_sensitive and config.language == LanguageType.ENGLISH:
                lookup_char = char.lower()

            # Handle Hebrew final forms
            if config.language == LanguageType.HEBREW and config.use_final_forms:
                # Check if it's a final form and if we have a special value for it
                if char in self._hebrew_final_forms and lookup_char in letter_values:
                    # If the final form has its own value, use that
                    if self._hebrew_final_forms[char] in letter_values:
                        lookup_char = self._hebrew_final_forms[char]

            # Add the value if the character is in our mapping
            if lookup_char in letter_values:
                total += letter_values[lookup_char]

        return total

    def _strip_diacritical_marks(self, text: str) -> str:
        """Strip diacritical marks from Hebrew or Greek text.

        This method removes all vowel points, cantillation marks, and other
        diacritical notations from the text, preserving only the base characters.

        Args:
            text: Text with potential diacritical marks

        Returns:
            Clean text with only base characters
        """
        # Normalize the text to separate base characters from combining marks
        normalized = unicodedata.normalize("NFD", text)

        # Filter out all combining diacritical marks
        # Unicode categories: Mn (Nonspacing Mark), Me (Enclosing Mark), Mc (Spacing Mark)
        clean_text = "".join(
            c for c in normalized if not unicodedata.category(c).startswith("M")
        )

        # Additional Hebrew-specific mark removal (these might not be categorized as marks)
        # Remove specific punctuation marks used in Hebrew text
        hebrew_marks = ["־", "׃", "׀", "׆", "׳", "״", "׏"]
        for mark in hebrew_marks:
            clean_text = clean_text.replace(mark, "")

        # Remove any remaining special punctuation
        clean_text = re.sub(r"[\u0591-\u05C7\u05F3\u05F4]", "", clean_text)

        # Additional Greek-specific mark removal
        greek_marks = [
            "ʹ",
            "·",
            "᾽",
            "᾿",
            "῀",
            "῁",
            "῍",
            "῎",
            "῏",
            "῝",
            "῞",
            "῟",
            "῭",
            "΄",
            "᾿",
            "῾",
        ]
        for mark in greek_marks:
            clean_text = clean_text.replace(mark, "")

        return clean_text

    def _preprocess_hebrew_text(self, text: str) -> str:
        """Preprocess Hebrew text for calculation.

        Args:
            text: Text to preprocess

        Returns:
            Preprocessed text
        """
        # Filter for just Hebrew characters
        hebrew_chars = [c for c in text if c in self._letter_values or c in " "]
        return "".join(hebrew_chars)

    def _preprocess_greek_text(self, text: str) -> str:
        """Preprocess Greek text for calculation.

        Args:
            text: Text to preprocess

        Returns:
            Preprocessed text
        """
        # Filter for just Greek characters
        greek_chars = [c for c in text if c in self._greek_values or c in " "]
        return "".join(greek_chars)

    def _preprocess_english_text(self, text: str) -> str:
        """Preprocess English text for TQ calculation.

        Args:
            text: Text to preprocess

        Returns:
            Preprocessed text
        """
        # Convert to lowercase and filter for just English characters
        english_chars = [c for c in text if c.lower() in self._tq_values or c in " "]
        return "".join(english_chars)

    # Rename the original function for backward compatibility
    def _preprocess_text(self, text: str) -> str:
        """Legacy method kept for backward compatibility."""
        return self._preprocess_hebrew_text(text)

    # ===== HEBREW CALCULATION METHODS =====

    def _calculate_standard(self, text: str) -> int:
        """Calculate standard gematria (Mispar Hechrachi).

        Args:
            text: Text to calculate

        Returns:
            Standard gematria value
        """
        total = 0
        for char in text:
            if char in self._letter_values:
                total += self._letter_values[char]
        return total

    def _calculate_ordinal(self, text: str) -> int:
        """Calculate ordinal gematria (Mispar Siduri).

        Args:
            text: Text to calculate

        Returns:
            Ordinal gematria value
        """
        total = 0
        for char in text:
            if char in self._letter_positions:
                total += self._letter_positions[char]
        return total

    def _calculate_albam(self, text: str) -> int:
        """Calculate Albam gematria.

        Args:
            text: Text to calculate

        Returns:
            Albam gematria value
        """
        # First substitute letters according to Albam cipher
        substituted = ""
        for char in text:
            if char in self._albam_map:
                substituted += self._albam_map[char]
            else:
                substituted += char

        # Then calculate standard value
        return self._calculate_standard(substituted)

    def _calculate_atbash(self, text: str) -> int:
        """Calculate Atbash gematria.

        Args:
            text: Text to calculate

        Returns:
            Atbash gematria value
        """
        # First substitute letters according to Atbash cipher
        substituted = ""
        for char in text:
            if char in self._atbash_map:
                substituted += self._atbash_map[char]
            else:
                substituted += char

        # Then calculate standard value
        return self._calculate_standard(substituted)

    def _calculate_reversal(self, text: str) -> int:
        """Calculate reversal gematria (Mispar Meshupach).

        Args:
            text: Text to calculate

        Returns:
            Reversal gematria value
        """
        # Reverse values (alef=400, bet=300, etc.)
        reversal_values = {
            "א": 400,
            "ב": 300,
            "ג": 200,
            "ד": 100,
            "ה": 90,
            "ו": 80,
            "ז": 70,
            "ח": 60,
            "ט": 50,
            "י": 40,
            "כ": 30,
            "ל": 20,
            "מ": 10,
            "נ": 9,
            "ס": 8,
            "ע": 7,
            "פ": 6,
            "צ": 5,
            "ק": 4,
            "ר": 3,
            "ש": 2,
            "ת": 1,
            # Final forms
            "ך": 30,
            "ם": 10,
            "ן": 9,
            "ף": 6,
            "ץ": 5,
        }

        total = 0
        for char in text:
            if char in reversal_values:
                total += reversal_values[char]
        return total

    def _calculate_large(self, text: str) -> int:
        """Calculate large gematria (Mispar Gadol) with final forms 500-900.

        Args:
            text: Text to calculate

        Returns:
            Large gematria value
        """
        # Values including final letters with extended values
        large_values = {
            # Standard letters
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            "י": 10,
            "כ": 20,
            "ל": 30,
            "מ": 40,
            "נ": 50,
            "ס": 60,
            "ע": 70,
            "פ": 80,
            "צ": 90,
            "ק": 100,
            "ר": 200,
            "ש": 300,
            "ת": 400,
            # Final forms with extended values
            "ך": 500,
            "ם": 600,
            "ן": 700,
            "ף": 800,
            "ץ": 900,
        }

        total = 0
        for char in text:
            if char in large_values:
                total += large_values[char]
        return total

    def _calculate_building(self, text: str) -> int:
        """Calculate building gematria (Mispar Bone'eh).

        For each letter, add the cumulative value of all previous letters plus current.

        Args:
            text: Text to calculate

        Returns:
            Building gematria value
        """
        filtered_text = "".join(char for char in text if char in self._letter_values)
        total = 0
        running_sum = 0

        for char in filtered_text:
            if char in self._letter_values:
                running_sum += self._letter_values[char]
                total += running_sum

        return total

    def _calculate_triangular(self, text: str) -> int:
        """Calculate triangular gematria (Mispar Kidmi).

        Each letter's value is the sum of all letters up to it in the alphabet.

        Args:
            text: Text to calculate

        Returns:
            Triangular gematria value
        """
        # Triangular values for each letter
        triangular_values = {
            "א": 1,
            "ב": 3,
            "ג": 6,
            "ד": 10,
            "ה": 15,
            "ו": 21,
            "ז": 28,
            "ח": 36,
            "ט": 45,
            "י": 55,
            "כ": 75,
            "ל": 105,
            "מ": 145,
            "נ": 195,
            "ס": 255,
            "ע": 325,
            "פ": 405,
            "צ": 495,
            "ק": 595,
            "ר": 795,
            "ש": 1095,
            "ת": 1495,
            # Final forms (same as regular forms)
            "ך": 75,
            "ם": 145,
            "ן": 195,
            "ף": 405,
            "ץ": 495,
        }

        total = 0
        for char in text:
            if char in triangular_values:
                total += triangular_values[char]
        return total

    # Hebrew letter names with their standard values
    _hebrew_letter_names = {
        "א": {"name": "אלף", "value": 111},  # alef = alef-lamed-peh
        "ב": {"name": "בית", "value": 412},  # bet = bet-yod-tav
        "ג": {"name": "גימל", "value": 83},  # gimel = gimel-yod-mem-lamed
        "ד": {"name": "דלת", "value": 434},  # dalet = dalet-lamed-tav
        "ה": {"name": "הא", "value": 6},  # heh = heh-alef
        "ו": {"name": "וו", "value": 12},  # vav = vav-vav
        "ז": {"name": "זין", "value": 67},  # zayin = zayin-yod-nun
        "ח": {"name": "חית", "value": 418},  # chet = chet-yod-tav
        "ט": {"name": "טית", "value": 419},  # tet = tet-yod-tav
        "י": {"name": "יוד", "value": 20},  # yod = yod-vav-dalet
        "כ": {"name": "כף", "value": 100},  # kaf = kaf-peh
        "ל": {"name": "למד", "value": 74},  # lamed = lamed-mem-dalet
        "מ": {"name": "מם", "value": 80},  # mem = mem-mem
        "נ": {"name": "נון", "value": 106},  # nun = nun-vav-nun
        "ס": {"name": "סמך", "value": 120},  # samech = samech-mem-kaf
        "ע": {"name": "עין", "value": 130},  # ayin = ayin-yod-nun
        "פ": {"name": "פא", "value": 81},  # peh = peh-alef
        "צ": {"name": "צדי", "value": 104},  # tsadi = tsadi-dalet-yod
        "ק": {"name": "קוף", "value": 186},  # qof = qof-vav-peh
        "ר": {"name": "ריש", "value": 510},  # resh = resh-yod-shin
        "ש": {"name": "שין", "value": 360},  # shin = shin-yod-nun
        "ת": {"name": "תו", "value": 406},  # tav = tav-vav
        # Final forms
        "ך": {"name": "כף סופית", "value": 100},
        "ם": {"name": "מם סופית", "value": 80},
        "ן": {"name": "נון סופית", "value": 106},
        "ף": {"name": "פא סופית", "value": 81},
        "ץ": {"name": "צדי סופית", "value": 104},
    }

    # Hebrew letter names without the letter itself
    _hebrew_letter_hidden_values = {
        "א": 110,  # alef without alef = lamed-peh (30+80)
        "ב": 410,  # bet without bet = yod-tav (10+400)
        "ג": 80,  # gimel without gimel = yod-mem-lamed (10+40+30)
        "ד": 430,  # dalet without dalet = lamed-tav (30+400)
        "ה": 1,  # heh without heh = alef (1)
        "ו": 6,  # vav without vav = vav (6)
        "ז": 60,  # zayin without zayin = yod-nun (10+50)
        "ח": 410,  # chet without chet = yod-tav (10+400)
        "ט": 410,  # tet without tet = yod-tav (10+400)
        "י": 10,  # yod without yod = vav-dalet (6+4)
        "כ": 80,  # kaf without kaf = peh (80)
        "ל": 44,  # lamed without lamed = mem-dalet (40+4)
        "מ": 40,  # mem without mem = mem (40)
        "נ": 56,  # nun without nun = vav-nun (6+50)
        "ס": 60,  # samech without samech = mem-kaf (40+20)
        "ע": 60,  # ayin without ayin = yod-nun (10+50)
        "פ": 1,  # peh without peh = alef (1)
        "צ": 14,  # tsadi without tsadi = dalet-yod (4+10)
        "ק": 86,  # qof without qof = vav-peh (6+80)
        "ר": 310,  # resh without resh = yod-shin (10+300)
        "ש": 60,  # shin without shin = yod-nun (10+50)
        "ת": 6,  # tav without tav = vav (6)
        # Final forms
        "ך": 80,
        "ם": 40,
        "ן": 56,
        "ף": 1,
        "ץ": 14,
    }

    def _calculate_individual_square(self, text: str) -> int:
        """Calculate the individual square gematria (Mispar Perati) value.

        In this method, each letter value is squared and then summed.

        Args:
            text: The text to calculate

        Returns:
            The calculated value
        """
        total = 0
        for char in text:
            if char in self._letter_values:
                total += self._letter_values[char] * self._letter_values[char]
        return total

    def _calculate_full_name(self, text: str) -> int:
        """Calculate the full name gematria (Mispar Shemi) value.

        This method calculates the value based on the spelling of each letter.

        Args:
            text: The text to calculate

        Returns:
            The calculated value
        """
        # Hebrew letter name values
        letter_names = {
            "א": 111,  # Alef (אלף)
            "ב": 412,  # Bet (בית)
            "ג": 83,  # Gimel (גימל)
            "ד": 434,  # Dalet (דלת)
            "ה": 6,  # He (הא)
            "ו": 12,  # Vav (וו)
            "ז": 67,  # Zayin (זין)
            "ח": 418,  # Chet (חית)
            "ט": 419,  # Tet (טית)
            "י": 20,  # Yod (יוד)
            "כ": 100,  # Kaf (כף)
            "ל": 74,  # Lamed (למד)
            "מ": 80,  # Mem (מם)
            "נ": 106,  # Nun (נון)
            "ס": 120,  # Samekh (סמך)
            "ע": 130,  # Ayin (עין)
            "פ": 85,  # Pe (פה)
            "צ": 104,  # Tsadi (צדי)
            "ק": 186,  # Qof (קוף)
            "ר": 510,  # Resh (ריש)
            "ש": 360,  # Shin (שין)
            "ת": 406,  # Tav (תו)
            # Final letters
            "ך": 100,  # Final Kaf (same as regular)
            "ם": 80,  # Final Mem (same as regular)
            "ן": 106,  # Final Nun (same as regular)
            "ף": 85,  # Final Pe (same as regular)
            "ץ": 104,  # Final Tsadi (same as regular)
        }

        total = 0
        for char in text:
            if char in letter_names:
                total += letter_names[char]
        return total

    def _calculate_additive(self, text: str) -> int:
        """Calculate the additive gematria (Mispar Musafi) value.

        In this method, the value of the word is combined with the number of letters.

        Args:
            text: The text to calculate

        Returns:
            The calculated value
        """
        # First calculate the standard value
        standard_value = self._calculate_standard(text)

        # Count the number of letters (excluding non-Hebrew characters)
        letter_count = sum(1 for char in text if char in self._letter_values)

        # Return the total
        return standard_value + letter_count

    # ===== GREEK CALCULATION METHODS =====

    def _calculate_greek_standard(self, text: str) -> int:
        """Calculate standard Greek isopsophy (Arithmos).

        Args:
            text: Greek text to calculate

        Returns:
            Standard isopsophy value
        """
        total = 0
        for char in text:
            if char in self._greek_values:
                total += self._greek_values[char]
        return total

    def _calculate_greek_ordinal(self, text: str) -> int:
        """Calculate ordinal Greek isopsophy (Arithmos Taktikos).

        Args:
            text: Greek text to calculate

        Returns:
            Ordinal isopsophy value
        """
        total = 0
        for char in text:
            if char in self._greek_positions:
                total += self._greek_positions[char]
        return total

    def _calculate_greek_squared(self, text: str) -> int:
        """Calculate squared Greek isopsophy (Arithmos Tetragonos).

        Args:
            text: Greek text to calculate

        Returns:
            Squared isopsophy value
        """
        total = 0
        for char in text:
            if char in self._greek_values:
                total += self._greek_values[char] ** 2
        return total

    def _calculate_greek_reversal(self, text: str) -> int:
        """Calculate reversal Greek isopsophy (Arithmos Antistrofos).

        Args:
            text: Greek text to calculate

        Returns:
            Reversal isopsophy value
        """
        # Create reversal values (alpha=800, beta=700, etc.)
        reversal_values = {
            "α": 800,
            "β": 700,
            "γ": 600,
            "δ": 500,
            "ε": 400,
            "ϝ": 300,
            "ζ": 200,
            "η": 100,
            "θ": 90,
            "ι": 80,
            "κ": 70,
            "λ": 60,
            "μ": 50,
            "ν": 40,
            "ξ": 30,
            "ο": 20,
            "π": 10,
            "ϙ": 9,
            "ρ": 8,
            "σ": 7,
            "τ": 6,
            "υ": 5,
            "φ": 4,
            "χ": 3,
            "ψ": 2,
            "ω": 1,
            # Variant forms
            "ς": 7,
            "ϲ": 7,
        }

        total = 0
        for char in text:
            if char in reversal_values:
                total += reversal_values[char]
        return total

    def _calculate_greek_alpha_mu(self, text: str) -> int:
        """Calculate Greek Alpha-Mu cipher (Kryptos Alpha-Mu).

        Similar to Hebrew Albam, this substitutes first half alphabet with second half.

        Args:
            text: Greek text to calculate

        Returns:
            Alpha-Mu cipher value
        """
        # First substitute letters according to Alpha-Mu cipher
        substituted = ""
        for char in text:
            if char in self._greek_alpha_mu_map:
                substituted += self._greek_alpha_mu_map[char]
            else:
                substituted += char

        # Then calculate standard value
        return self._calculate_greek_standard(substituted)

    def _calculate_greek_alpha_omega(self, text: str) -> int:
        """Calculate Greek Alpha-Omega cipher (Kryptos Alpha-Omega).

        Similar to Hebrew Atbash, this substitutes letters with their opposite from the end.

        Args:
            text: Greek text to calculate

        Returns:
            Alpha-Omega cipher value
        """
        # First substitute letters according to Alpha-Omega cipher
        substituted = ""
        for char in text:
            if char in self._greek_alpha_omega_map:
                substituted += self._greek_alpha_omega_map[char]
            else:
                substituted += char

        # Then calculate standard value
        return self._calculate_greek_standard(substituted)

    def _calculate_greek_building(self, text: str) -> int:
        """Calculate Greek building value (Arithmos Oikodomikos).

        For each letter, add the cumulative value of all previous letters plus current.

        Args:
            text: Greek text to calculate

        Returns:
            Greek building value
        """
        filtered_text = "".join(char for char in text if char in self._greek_values)
        total = 0
        running_sum = 0

        for char in filtered_text:
            if char in self._greek_values:
                running_sum += self._greek_values[char]
                total += running_sum

        return total

    def _calculate_greek_triangular(self, text: str) -> int:
        """Calculate Greek triangular value (Arithmos Trigonikos).

        Each letter's value is the sum of all letters up to it in the alphabet.

        Args:
            text: Greek text to calculate

        Returns:
            Greek triangular value
        """
        total = 0
        for char in text:
            if char in self._greek_triangular_values:
                total += self._greek_triangular_values[char]
        return total

    def _calculate_greek_hidden(self, text: str) -> int:
        """Calculate Greek hidden value (Arithmos Kryptos).

        Value of each letter's name without the letter itself.

        Args:
            text: Greek text to calculate

        Returns:
            Greek hidden value
        """
        total = 0
        for char in text:
            if char in self._greek_letter_hidden_values:
                total += self._greek_letter_hidden_values[char]
        return total

    def _calculate_greek_full_name(self, text: str) -> int:
        """Calculate Greek full name value (Arithmos Onomatos).

        Args:
            text: Greek text to calculate

        Returns:
            Greek full name value
        """
        total = 0
        for char in text:
            if char in self._greek_letter_names:
                letter_value = self._greek_letter_names[char]["value"]
                # Ensure we're adding an integer
                if isinstance(letter_value, int):
                    total += letter_value
                else:
                    try:
                        # Convert to int if it's a string or other type
                        total += int(str(letter_value))
                    except (ValueError, TypeError):
                        # Skip if not convertible to int
                        pass
        return total

    def _calculate_greek_additive(self, text: str) -> int:
        """Calculate Greek additive value (Arithmos Prosthetikos).

        Adds the number of letters to the standard value.

        Args:
            text: Greek text to calculate

        Returns:
            Greek additive value
        """
        # Calculate standard value
        standard = self._calculate_greek_standard(text)

        # Count letters (excluding spaces and non-Greek characters)
        letter_count = sum(1 for char in text if char in self._greek_values)

        return standard + letter_count

    # ===== ENGLISH CALCULATION METHODS =====

    def _calculate_tq(self, text: str) -> int:
        """Calculate TQ English gematria.

        Args:
            text: English text to calculate

        Returns:
            TQ English gematria value
        """
        total = 0
        for char in text:
            if char in self._tq_values:
                total += self._tq_values[char]
        return total

    def calculate_and_save(
        self,
        text: str,
        calculation_type: Union[
            CalculationType, str, CustomCipherConfig
        ] = CalculationType.MISPAR_HECHRACHI,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        favorite: bool = False,
        value: Optional[int] = None,
        custom_method_name: Optional[str] = None,
    ) -> CalculationResult:
        """Calculate the gematria value and save the result.

        Args:
            text: The text to calculate
            calculation_type: The calculation type to use (enum, name, or custom config)
            notes: Optional notes to attach to the calculation
            tags: Optional list of tag IDs to associate with the calculation
            favorite: Whether to mark the calculation as a favorite
            value: Optional explicit value to override the calculated result (for custom calculations)

        Returns:
            The saved calculation result
        """
        # Calculate the value if not explicitly provided
        result_value = (
            value if value is not None else self.calculate(text, calculation_type)
        )

        # Handle CustomCipherConfig as calculation type
        calc_type: Union[CalculationType, str] = CalculationType.MISPAR_HECHRACHI
        method_name: Optional[
            str
        ] = custom_method_name  # Use the provided custom_method_name if available

        if isinstance(calculation_type, CustomCipherConfig):
            # Use a special string type for custom ciphers and set the custom method name
            calc_type = "CUSTOM_CIPHER"
            method_name = calculation_type.name
        elif isinstance(calculation_type, str) and calculation_type == "CUSTOM_CIPHER":
            # If we're already using the CUSTOM_CIPHER string, make sure we have a custom_method_name
            if not method_name:
                logger.warning(
                    "Saving a CUSTOM_CIPHER calculation without a custom_method_name"
                )
        else:
            calc_type = calculation_type
            method_name = None  # Reset method_name for standard calculation types

        # Create a new calculation result
        result = CalculationResult(
            input_text=text,
            calculation_type=calc_type,
            result_value=result_value,
            notes=notes,
            tags=tags or [],
            favorite=favorite,
            custom_method_name=method_name,
        )

        # Save to database
        self.db_service.save_calculation(result)

        return result

    def get_calculation_history(self, limit: int = 50) -> List[CalculationResult]:
        """Get the calculation history.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent calculation results
        """
        return self.db_service.find_recent_calculations(limit)

    def find_calculations_with_value(self, value: int) -> List[CalculationResult]:
        """Find calculations with a specific value.

        Args:
            value: Value to search for

        Returns:
            List of calculation results with the specified value
        """
        return self.db_service.find_calculations_by_value(value)

    def find_calculations_with_text(self, text: str) -> List[CalculationResult]:
        """Find calculations containing specific text.

        Args:
            text: Text to search for

        Returns:
            List of calculation results containing the specified text
        """
        return self.db_service.find_calculations_by_text(text)

    def find_calculations_with_tag(self, tag_id: str) -> List[CalculationResult]:
        """Find calculations with a specific tag.

        Args:
            tag_id: ID of the tag to filter by

        Returns:
            List of calculation results with the specified tag
        """
        return self.db_service.find_calculations_by_tag(tag_id)

    def get_calculation_by_id(self, calculation_id: str) -> Optional[CalculationResult]:
        """Get a specific calculation by ID.

        Args:
            calculation_id: ID of the calculation to retrieve

        Returns:
            CalculationResult or None if not found
        """
        return self.db_service.get_calculation(calculation_id)

    def delete_calculation(self, calculation_id: str) -> bool:
        """Delete a calculation.

        Args:
            calculation_id: ID of the calculation to delete

        Returns:
            True if successful, False otherwise
        """
        return self.db_service.delete_calculation(calculation_id)

    def update_calculation_notes(self, calculation_id: str, notes: str) -> bool:
        """Update the notes for a calculation.

        Args:
            calculation_id: ID of the calculation
            notes: New notes content

        Returns:
            True if successful, False otherwise
        """
        return self.db_service.update_calculation_notes(calculation_id, notes)

    def add_tag_to_calculation(self, calculation_id: str, tag_id: str) -> bool:
        """Add a tag to a calculation.

        Args:
            calculation_id: ID of the calculation
            tag_id: ID of the tag to add

        Returns:
            True if successful, False otherwise
        """
        return self.db_service.add_tag_to_calculation(calculation_id, tag_id)

    def remove_tag_from_calculation(self, calculation_id: str, tag_id: str) -> bool:
        """Remove a tag from a calculation.

        Args:
            calculation_id: ID of the calculation
            tag_id: ID of the tag to remove

        Returns:
            True if successful, False otherwise
        """
        return self.db_service.remove_tag_from_calculation(calculation_id, tag_id)

    def toggle_favorite_calculation(self, calculation_id: str) -> bool:
        """Toggle the favorite status of a calculation.

        Args:
            calculation_id: ID of the calculation

        Returns:
            True if successful, False otherwise
        """
        return self.db_service.toggle_favorite_calculation(calculation_id)
