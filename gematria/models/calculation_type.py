"""
Purpose: Defines the enumeration of available gematria calculation methods

This file is part of the gematria pillar and serves as a model component.
It is responsible for providing a standardized enumeration of all supported
gematria calculation methods across Hebrew, Greek, and English systems.

Key components:
- CalculationType: Enumeration of all supported calculation methods
- get_calculation_type_name: Function to convert enum values to display names
- language_from_text: Function to detect language from text

Dependencies:
- enum: For creating enumeration types

Related files:
- gematria/services/gematria_service.py: Uses these calculation types
- gematria/ui/panels/word_abacus_panel.py: Offers these calculation types in UI
- gematria/models/calculation_result.py: Stores calculation type with results
"""

from enum import Enum, auto
from typing import Any, List, Optional, Union


class Language(str, Enum):
    """Supported languages for gematria calculations."""

    HEBREW = "hebrew"
    GREEK = "greek"
    ENGLISH = "english"
    UNKNOWN = "unknown"


class CalculationType(Enum):
    """Types of Gematria calculations."""

    # === HEBREW METHODS ===

    # Standard (Mispar Hechrachi) - ordinal value of each letter
    MISPAR_HECHRACHI = auto()

    # Ordinal (Mispar Siduri) - position in alphabet (alef=1, bet=2, etc.)
    MISPAR_SIDURI = auto()

    # Reduced (Mispar Katan) - reduced to single digit where possible
    MISPAR_KATAN = auto()

    # Integral Reduced (Mispar Katan Mispari) - convergence to a single digit
    MISPAR_KATAN_MISPARI = auto()

    # Absolute (Mispar HaAkhor) - value of the letter name
    MISPAR_HAAKHOR = auto()

    # Squared (Mispar HaMerubah HaKlali) - square of standard value
    MISPAR_HAMERUBAH_HAKLALI = auto()

    # Reversal (Mispar Meshupach) - letter values reversed (alef=400, tav=1)
    MISPAR_MESHUPACH = auto()

    # Albam - letter substitution cipher (alef↔lamed, bet↔mem, etc.)
    ALBAM = auto()

    # Atbash - letter substitution cipher (alef↔tav, bet↔shin, etc.)
    ATBASH = auto()

    # Full (Mispar HaPanim) - value of the full letter name
    MISPAR_HAPANIM = auto()

    # Large (Mispar Gadol) - final letters have values 500-900
    MISPAR_GADOL = auto()

    # Building (Mispar Bone'eh) - cumulative value of letters as word is spelled
    MISPAR_BONEH = auto()

    # Triangular (Mispar Kidmi) - sum of all letters up to the current one in alphabet
    MISPAR_KIDMI = auto()

    # Hidden (Mispar Ne'elam) - value of letter name without the letter itself
    MISPAR_NEELAM = auto()

    # Individual Square (Mispar Perati) - each letter value is squared
    MISPAR_PERATI = auto()

    # Full Name (Mispar Shemi) - value of the full letter name
    MISPAR_SHEMI = auto()

    # Additive (Mispar Musafi) - adds the number of letters to the value
    MISPAR_MUSAFI = auto()

    # === GREEK METHODS ===

    # Standard Greek Isopsophy - standard letter values
    GREEK_ISOPSOPHY = auto()

    # Greek Ordinal (Arithmos Taktikos) - position in Greek alphabet
    GREEK_ORDINAL = auto()

    # Greek Reduced (Arithmos Mikros) - reduced to single digit
    GREEK_REDUCED = auto()

    # Greek Integral Reduced (Arithmos Mikros Olistikos) - convergence to a single digit
    GREEK_INTEGRAL_REDUCED = auto()

    # Greek Squared (Arithmos Tetragonos) - square of standard value
    GREEK_SQUARED = auto()

    # Greek Reversal (Arithmos Antistrofos) - letter values reversed (alpha=800, omega=1)
    GREEK_REVERSAL = auto()

    # Greek Alpha-Mu Cipher (Kryptos Alpha-Mu) - similar to Hebrew Albam
    GREEK_ALPHA_MU = auto()

    # Greek Alpha-Omega Cipher (Kryptos Alpha-Omega) - similar to Hebrew Atbash
    GREEK_ALPHA_OMEGA = auto()

    # Greek Large Value (Arithmos Megalos) - uses extended values for additional letters
    GREEK_LARGE = auto()

    # Greek Building Value (Arithmos Oikodomikos) - cumulative value of letters
    GREEK_BUILDING = auto()

    # Greek Triangular Value (Arithmos Trigonikos) - sum of all previous letter values
    GREEK_TRIANGULAR = auto()

    # Greek Hidden Value (Arithmos Kryptos) - letter name value without the letter
    GREEK_HIDDEN = auto()

    # Greek Individual Square (Arithmos Atomikos) - square of each letter value
    GREEK_INDIVIDUAL_SQUARE = auto()

    # Greek Full Name Value (Arithmos Onomatos) - value of the full letter name
    GREEK_FULL_NAME = auto()

    # Greek Additive (Arithmos Prosthetikos) - adds number of letters to value
    GREEK_ADDITIVE = auto()

    # === ENGLISH METHODS ===

    # TQ English - specific English letter-number mapping system
    TQ_ENGLISH = auto()

    @classmethod
    def get_types_for_language(cls, language: Language) -> List["CalculationType"]:
        """Get all calculation types for a specific language.

        Args:
            language: The language to filter by

        Returns:
            List of calculation types for the specified language
        """
        if language == Language.HEBREW:
            return [
                cls.MISPAR_HECHRACHI,
                cls.MISPAR_SIDURI,
                cls.MISPAR_KATAN,
                cls.MISPAR_KATAN_MISPARI,
                cls.MISPAR_HAAKHOR,
                cls.MISPAR_HAMERUBAH_HAKLALI,
                cls.MISPAR_MESHUPACH,
                cls.ALBAM,
                cls.ATBASH,
                cls.MISPAR_HAPANIM,
                cls.MISPAR_GADOL,
                cls.MISPAR_BONEH,
                cls.MISPAR_KIDMI,
                cls.MISPAR_NEELAM,
                cls.MISPAR_PERATI,
                cls.MISPAR_SHEMI,
                cls.MISPAR_MUSAFI,
            ]
        elif language == Language.GREEK:
            return [
                cls.GREEK_ISOPSOPHY,
                cls.GREEK_ORDINAL,
                cls.GREEK_REDUCED,
                cls.GREEK_INTEGRAL_REDUCED,
                cls.GREEK_SQUARED,
                cls.GREEK_REVERSAL,
                cls.GREEK_ALPHA_MU,
                cls.GREEK_ALPHA_OMEGA,
                cls.GREEK_LARGE,
                cls.GREEK_BUILDING,
                cls.GREEK_TRIANGULAR,
                cls.GREEK_HIDDEN,
                cls.GREEK_INDIVIDUAL_SQUARE,
                cls.GREEK_FULL_NAME,
                cls.GREEK_ADDITIVE,
            ]
        elif language == Language.ENGLISH:
            return [cls.TQ_ENGLISH]
        else:
            return []

    @classmethod
    def get_default_for_language(
        cls, language: Language
    ) -> Optional["CalculationType"]:
        """Get the default calculation type for a language.

        Args:
            language: The language

        Returns:
            The default calculation type or None if language not supported
        """
        if language == Language.HEBREW:
            return cls.MISPAR_HECHRACHI
        elif language == Language.GREEK:
            return cls.GREEK_ISOPSOPHY
        elif language == Language.ENGLISH:
            return cls.TQ_ENGLISH
        else:
            return None

    @classmethod
    def get_all_types(cls) -> List["CalculationType"]:
        """Get all available calculation types across all languages.

        Returns:
            List of all calculation types
        """
        all_types = []
        for language in [Language.HEBREW, Language.GREEK, Language.ENGLISH]:
            all_types.extend(cls.get_types_for_language(language))
        return all_types

    @property
    def display_name(self) -> str:
        """Get a formatted display name for this calculation type.

        Returns:
            The formatted display name
        """
        return get_calculation_type_name(self)


def get_calculation_type_name(calc_type: Union[CalculationType, str, Any]) -> str:
    """Get the display name for a calculation type.

    Args:
        calc_type: The calculation type enum value, string name, or other value

    Returns:
        The formatted display name for the calculation type
    """
    # Convert string to enum if possible
    if isinstance(calc_type, str):
        try:
            # Try to get the enum by name
            calc_type = CalculationType[calc_type]
        except (KeyError, ValueError):
            # If it's not a valid enum name, just return it as a custom calculation
            return f"Custom: {calc_type}"

    # If we have a CalculationType enum instance
    if isinstance(calc_type, CalculationType):
        # Format the name for readability
        name = calc_type.name

        # Special case formatting
        if name.startswith("MISPAR"):
            parts = name.split("_")
            return " ".join(parts).title()

        # General formatting - replace underscores with spaces and title case
        return name.replace("_", " ").title()

    # For any other type, just convert to string
    return str(calc_type)


def language_from_text(text: str) -> Optional[Language]:
    """Detect the language of a given text.

    Args:
        text: Text to analyze

    Returns:
        Detected language or None if detection fails
    """
    if not text:
        return None

    # Hebrew detection - check for Hebrew Unicode range (U+0590 to U+05FF)
    hebrew_count = sum(1 for c in text if 0x0590 <= ord(c) <= 0x05FF)
    if hebrew_count > 0 and hebrew_count / len(text) > 0.3:
        return Language.HEBREW

    # Greek detection - check for Greek Unicode range (U+0370 to U+03FF)
    greek_count = sum(1 for c in text if 0x0370 <= ord(c) <= 0x03FF)
    if greek_count > 0 and greek_count / len(text) > 0.3:
        return Language.GREEK

    # English detection - default if mostly Latin characters
    latin_count = sum(1 for c in text if ord("a") <= ord(c.lower()) <= ord("z"))
    if latin_count > 0 and latin_count / len(text) > 0.3:
        return Language.ENGLISH

    # Couldn't detect with confidence
    return None
