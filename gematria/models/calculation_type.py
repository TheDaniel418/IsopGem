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

from enum import Enum
from typing import Any, List, Optional, Union


class Language(str, Enum):
    """Supported languages for gematria calculations."""

    HEBREW = "Hebrew"
    GREEK = "Greek"
    ENGLISH = "English"
    COPTIC = "Coptic"
    ARABIC = "Arabic"
    UNKNOWN = "Unknown"


class CalculationType(Enum):
    """Types of Gematria calculations."""

    # === HEBREW METHODS ===

    HEBREW_STANDARD_VALUE = (
        "Hebrew Standard Value",
        "Hebrew: Standard value (Mispar Hechrachi). Each letter has its numerical value.",
        Language.HEBREW,
    )
    HEBREW_ORDINAL_VALUE = (
        "Hebrew Ordinal Value",
        "Hebrew: Ordinal value (Mispar Siduri). Each letter is counted based on its position.",
        Language.HEBREW,
    )
    HEBREW_REVERSE_STANDARD_VALUES = (
        "Hebrew Reverse Standard Values",
        "Hebrew: Reverse Standard Values (Mispar Meshupach). Letter values are reversed (e.g., Alef=400).",
        Language.HEBREW,
    )
    HEBREW_ALBAM_SUBSTITUTION = (
        "Hebrew Albam Substitution",
        "Hebrew: Albam cipher. First letter is exchanged with 12th, 2nd with 13th, etc.",
        Language.HEBREW,
    )
    HEBREW_ATBASH_SUBSTITUTION = (
        "Hebrew Atbash Substitution",
        "Hebrew: Atbash cipher. First letter exchanged with last, second with second-to-last, etc.",
        Language.HEBREW,
    )
    HEBREW_BUILDING_VALUE_CUMULATIVE = (
        "Hebrew Building Value Cumulative",
        "Hebrew: Building Value (Mispar Bone\\'eh). Cumulative sum of letter values.",
        Language.HEBREW,
    )
    HEBREW_TRIANGULAR_VALUE = (
        "Hebrew Triangular Value",
        "Hebrew: Triangular Value (Mispar Kidmi). Sum of values from Alef to the letter.",
        Language.HEBREW,
    )
    HEBREW_INDIVIDUAL_SQUARE_VALUE = (
        "Hebrew Individual Square Value",
        "Hebrew: Individual Square Value (Mispar Perati/Bone\\'eh). Each letter\\'s value is squared.",
        Language.HEBREW,
    )
    HEBREW_SUM_OF_LETTER_NAMES_STANDARD = (
        "Hebrew Sum Of Letter Names Standard",
        "Hebrew: Sum of Letter Names - Standard (Mispar Shemi). Sums values of spelled-out letter names.",
        Language.HEBREW,
    )
    HEBREW_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS = (
        "Hebrew Collective Value Standard Plus Letters",
        "Hebrew: Collective Value (Mispar Kolel). Standard value plus number of letters.",
        Language.HEBREW,
    )
    HEBREW_SMALL_REDUCED_VALUE = (
        "Hebrew Small Reduced Value",
        "Hebrew: Small/Reduced Value (Mispar Katan). Reduces letter values to a single digit.",
        Language.HEBREW,
    )
    HEBREW_INTEGRAL_REDUCED_VALUE = (
        "Hebrew Integral Reduced Value",
        "Hebrew: Integral Reduced Value (Mispar Mispari). Sums the digits of each letter\\'s value.",
        Language.HEBREW,
    )
    HEBREW_CUBED_VALUE = (
        "Hebrew Cubed Value",
        "Hebrew: Cubed Value (Mispar Meshulash). Each letter\\'s value is cubed.",
        Language.HEBREW,
    )
    HEBREW_FINAL_LETTER_VALUES = (
        "Hebrew Final Letter Values",
        "Hebrew: Final Letter Values (Mispar Sofit/Gadol). Final letters have values 500-900.",
        Language.HEBREW,
    )
    HEBREW_SUM_OF_LETTER_NAMES_FINALS = (
        "Hebrew Sum Of Letter Names Finals",
        "Hebrew: Sum of Letter Names - Finals (Mispar Shemi Sofit). Uses final values in name spellings.",
        Language.HEBREW,
    )
    HEBREW_PRODUCT_OF_LETTER_NAMES_STANDARD = (
        "Hebrew Product Of Letter Names Standard",
        "Hebrew: Product of Letter Names - Standard. Multiplies values of spelled-out letter names.",
        Language.HEBREW,
    )
    HEBREW_PRODUCT_OF_LETTER_NAMES_FINALS = (
        "Hebrew Product Of Letter Names Finals",
        "Hebrew: Product of Letter Names - Finals. Multiplies using final values in name spellings.",
        Language.HEBREW,
    )
    HEBREW_HIDDEN_VALUE_STANDARD = (
        "Hebrew Hidden Value Standard",
        "Hebrew: Hidden Value - Standard (Mispar Ne\\'elam). Name value minus letter value.",
        Language.HEBREW,
    )
    HEBREW_HIDDEN_VALUE_FINALS = (
        "Hebrew Hidden Value Finals",
        "Hebrew: Hidden Value - Finals (Mispar Ne\\'elam Sofit). Name (finals) value minus letter value.",
        Language.HEBREW,
    )
    HEBREW_FACE_VALUE_STANDARD = (
        "Hebrew Face Value Standard",
        "Hebrew: Face Value - Standard (Mispar HaPanim). First letter name + rest standard.",
        Language.HEBREW,
    )
    HEBREW_FACE_VALUE_FINALS = (
        "Hebrew Face Value Finals",
        "Hebrew: Face Value - Finals (Mispar HaPanim Sofit). First letter name (finals) + rest standard.",
        Language.HEBREW,
    )
    HEBREW_BACK_VALUE_STANDARD = (
        "Hebrew Back Value Standard",
        "Hebrew: Back Value - Standard (Mispar HaAchor). Rest standard + last letter name.",
        Language.HEBREW,
    )
    HEBREW_BACK_VALUE_FINALS = (
        "Hebrew Back Value Finals",
        "Hebrew: Back Value - Finals (Mispar HaAchor Sofit). Rest standard + last letter name (finals).",
        Language.HEBREW,
    )
    HEBREW_SUM_OF_LETTER_NAMES_STANDARD_PLUS_LETTERS = (
        "Hebrew Sum Of Letter Names Standard Plus Letters",
        "Hebrew: Name Collective - Standard (Mispar Shemi Kolel). Sum of names + letters.",
        Language.HEBREW,
    )
    HEBREW_SUM_OF_LETTER_NAMES_FINALS_PLUS_LETTERS = (
        "Hebrew Sum Of Letter Names Finals Plus Letters",
        "Hebrew: Name Collective - Finals (Mispar Shemi Kolel Sofit). Sum of names (finals) + letters.",
        Language.HEBREW,
    )
    HEBREW_STANDARD_VALUE_PLUS_ONE = (
        "Hebrew Standard Value Plus One",
        "Hebrew: Standard Value + 1 (Ragil plus Kolel). Standard value plus one.",
        Language.HEBREW,
    )

    # === GREEK METHODS ===

    GREEK_STANDARD_VALUE = (
        "Greek Standard Value",
        "Greek: Standard Value (Isopsophy). Traditional Greek letter values.",
        Language.GREEK,
    )
    GREEK_ORDINAL_VALUE = (
        "Greek Ordinal Value",
        "Greek: Ordinal Value. Each letter numbered by position in alphabet.",
        Language.GREEK,
    )
    GREEK_SQUARE_VALUE = (
        "Greek Square Value",
        "Greek: Square Value. Square of standard Greek letter values.",
        Language.GREEK,
    )
    GREEK_REVERSE_STANDARD_VALUES = (
        "Greek Reverse Standard Values",
        "Greek: Reverse Standard Values. Letter values are reversed (α=800, ω=1).",
        Language.GREEK,
    )
    GREEK_ALPHAMU_SUBSTITUTION = (
        "Greek Alphamu Substitution",
        "Greek: Alpha-Mu Substitution. First half of alphabet exchanged with second.",
        Language.GREEK,
    )
    GREEK_ALPHAOMEGA_SUBSTITUTION = (
        "Greek Alphaomega Substitution",
        "Greek: Alpha-Omega Substitution (Values). Atbash-like value mapping.",
        Language.GREEK,
    )
    GREEK_BUILDING_VALUE_CUMULATIVE = (
        "Greek Building Value Cumulative",
        "Greek: Building Value. Cumulative value of letters as spelled out.",
        Language.GREEK,
    )
    GREEK_TRIANGULAR_VALUE = (
        "Greek Triangular Value",
        "Greek: Triangular Value. Triangular number of each letter\\'s standard value.",
        Language.GREEK,
    )
    GREEK_HIDDEN_LETTER_NAME_VALUE = (
        "Greek Hidden Letter Name Value",
        "Greek: Hidden Letter Name Value. Letter name value minus the letter itself.",
        Language.GREEK,
    )
    GREEK_SUM_OF_LETTER_NAMES = (
        "Greek Sum Of Letter Names",
        "Greek: Sum of Letter Names. Value of the full letter name.",
        Language.GREEK,
    )
    GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS = (
        "Greek Collective Value Standard Plus Letters",
        "Greek: Collective Value. Standard value plus number of letters.",
        Language.GREEK,
    )
    GREEK_CUBED_VALUE = (
        "Greek Cubed Value",
        "Greek: Cubed Value (Kyvos). Cube of standard Greek letter values.",
        Language.GREEK,
    )
    GREEK_NEXT_LETTER_VALUE = (
        "Greek Next Letter Value",
        "Greek: Next Letter Value (Epomenos). Value of the following letter.",
        Language.GREEK,
    )
    GREEK_CYCLICAL_PERMUTATION_VALUE = (
        "Greek Cyclical Permutation Value",
        "Greek: Cyclical Permutation. Text permuted (abc->bca) then valued.",
        Language.GREEK,
    )
    GREEK_SMALL_REDUCED_VALUE = (
        "Greek Small Reduced Value",
        "Greek: Small Reduced Value. Reduces standard letter values to a single digit.",
        Language.GREEK,
    )
    GREEK_DIGITAL_VALUE = (
        "Greek Digital Value",
        "Greek: Digital Value. Sums digits of each letter\\'s standard value.",
        Language.GREEK,
    )
    GREEK_DIGITAL_ORDINAL_VALUE = (
        "Greek Digital Ordinal Value",
        "Greek: Digital Ordinal Value. Sums digits of each letter\\'s ordinal value.",
        Language.GREEK,
    )
    GREEK_ORDINAL_SQUARE_VALUE = (
        "Greek Ordinal Square Value",
        "Greek: Ordinal Square Value. Each letter\\'s ordinal value is squared.",
        Language.GREEK,
    )
    GREEK_PRODUCT_OF_LETTER_NAMES = (
        "Greek Product Of Letter Names",
        "Greek: Product of Letter Names. Multiplies values of spelled-out letter names.",
        Language.GREEK,
    )
    GREEK_FACE_VALUE = (
        "Greek Face Value",
        "Greek: Face Value. First letter name value + rest standard values.",
        Language.GREEK,
    )
    GREEK_BACK_VALUE = (
        "Greek Back Value",
        "Greek: Back Value. Standard values of rest + last letter name value.",
        Language.GREEK,
    )
    GREEK_SUM_OF_LETTER_NAMES_PLUS_LETTERS = (
        "Greek Sum Of Letter Names Plus Letters",
        "Greek: Name Collective Value. Sum of letter names + number of letters.",
        Language.GREEK,
    )
    GREEK_STANDARD_VALUE_PLUS_ONE = (
        "Greek Standard Value Plus One",
        "Greek: Standard Value + 1. Standard value plus one.",
        Language.GREEK,
    )
    GREEK_ALPHABET_REVERSAL_SUBSTITUTION = (
        "Greek Alphabet Reversal Substitution",
        "Greek: Alphabet Reversal Substitution. True Atbash (α=ω letter swap).",
        Language.GREEK,
    )
    GREEK_PAIR_MATCHING_SUBSTITUTION = (
        "Greek Pair Matching Substitution",
        "Greek: Pair Matching Substitution (e.g. α=λ). Needs full cipher definition.",
        Language.GREEK,
    )

    # === ENGLISH METHODS ===

    ENGLISH_TQ_STANDARD_VALUE = (
        "English Tq Standard Value",
        "English: TQ Standard Value. Uses Trigrammaton Qabbalah letter values.",
        Language.ENGLISH,
    )
    ENGLISH_TQ_REDUCED_VALUE = (
        "English Tq Reduced Value",
        "English: TQ Reduced Value. Standard TQ sum reduced to a single digit.",
        Language.ENGLISH,
    )
    ENGLISH_TQ_SQUARE_VALUE = (
        "English Tq Square Value",
        "English: TQ Square Value. Each letter\\'s TQ value squared, then summed.",
        Language.ENGLISH,
    )
    ENGLISH_TQ_TRIANGULAR_VALUE = (
        "English Tq Triangular Value",
        "English: TQ Triangular Value. Triangular number of each letter\\'s TQ value.",
        Language.ENGLISH,
    )
    ENGLISH_TQ_LETTER_POSITION_VALUE = (
        "English Tq Letter Position Value",
        "English: TQ Letter Position. TQ value multiplied by its position in the word.",
        Language.ENGLISH,
    )

    # === COPTIC METHODS ===
    # Standard Value -> COPTIC_STANDARD_VALUE
    COPTIC_STANDARD_VALUE = (
        "Coptic Standard Value",
        "Standard Coptic numerology based on Greek system.",
        Language.COPTIC,
    )

    # Reduced Value -> COPTIC_REDUCED_VALUE
    COPTIC_REDUCED_VALUE = (
        "Coptic Reduced Value",
        "Reduces the standard Coptic sum to a single digit.",
        Language.COPTIC,
    )

    # === Arabic Methods ===
    ARABIC_STANDARD_ABJAD = (
        "Arabic Standard Abjad",
        "Standard Arabic numerology (Abjad Hawwaz).",
        Language.ARABIC,
    )

    CUSTOM_CIPHER = ("Custom Cipher", "User-defined custom cipher.", Language.UNKNOWN)

    def __init__(
        self, display_name_from_tuple: str, description: str, language: Language
    ):
        # The display_name_from_tuple is passed because it's part of the enum member's value tuple,
        # but self.display_name is handled by the @property below, which derives it from self.name.
        # So, we don't assign display_name_from_tuple to self.display_name here.
        self.description = description
        self.language = language

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
                cls.HEBREW_STANDARD_VALUE,
                cls.HEBREW_ORDINAL_VALUE,
                cls.HEBREW_REVERSE_STANDARD_VALUES,
                cls.HEBREW_ALBAM_SUBSTITUTION,
                cls.HEBREW_ATBASH_SUBSTITUTION,
                cls.HEBREW_BUILDING_VALUE_CUMULATIVE,
                cls.HEBREW_TRIANGULAR_VALUE,
                cls.HEBREW_INDIVIDUAL_SQUARE_VALUE,
                cls.HEBREW_SUM_OF_LETTER_NAMES_STANDARD,
                cls.HEBREW_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS,
                cls.HEBREW_FINAL_LETTER_VALUES,
                cls.HEBREW_SMALL_REDUCED_VALUE,
                cls.HEBREW_INTEGRAL_REDUCED_VALUE,
                cls.HEBREW_CUBED_VALUE,
                cls.HEBREW_SUM_OF_LETTER_NAMES_FINALS,
                cls.HEBREW_PRODUCT_OF_LETTER_NAMES_STANDARD,
                cls.HEBREW_PRODUCT_OF_LETTER_NAMES_FINALS,
                cls.HEBREW_HIDDEN_VALUE_STANDARD,
                cls.HEBREW_HIDDEN_VALUE_FINALS,
                cls.HEBREW_FACE_VALUE_STANDARD,
                cls.HEBREW_FACE_VALUE_FINALS,
                cls.HEBREW_BACK_VALUE_STANDARD,
                cls.HEBREW_BACK_VALUE_FINALS,
                cls.HEBREW_SUM_OF_LETTER_NAMES_STANDARD_PLUS_LETTERS,
                cls.HEBREW_SUM_OF_LETTER_NAMES_FINALS_PLUS_LETTERS,
                cls.HEBREW_STANDARD_VALUE_PLUS_ONE,
            ]
        elif language == Language.GREEK:
            return [
                cls.GREEK_STANDARD_VALUE,
                cls.GREEK_ORDINAL_VALUE,
                cls.GREEK_SQUARE_VALUE,
                cls.GREEK_REVERSE_STANDARD_VALUES,
                cls.GREEK_ALPHAMU_SUBSTITUTION,
                cls.GREEK_ALPHAOMEGA_SUBSTITUTION,
                cls.GREEK_BUILDING_VALUE_CUMULATIVE,
                cls.GREEK_TRIANGULAR_VALUE,
                cls.GREEK_HIDDEN_LETTER_NAME_VALUE,
                cls.GREEK_SUM_OF_LETTER_NAMES,
                cls.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS,
                cls.GREEK_CUBED_VALUE,
                cls.GREEK_NEXT_LETTER_VALUE,
                cls.GREEK_CYCLICAL_PERMUTATION_VALUE,
                cls.GREEK_SMALL_REDUCED_VALUE,
                cls.GREEK_DIGITAL_VALUE,
                cls.GREEK_DIGITAL_ORDINAL_VALUE,
                cls.GREEK_ORDINAL_SQUARE_VALUE,
                cls.GREEK_PRODUCT_OF_LETTER_NAMES,
                cls.GREEK_FACE_VALUE,
                cls.GREEK_BACK_VALUE,
                cls.GREEK_SUM_OF_LETTER_NAMES_PLUS_LETTERS,
                cls.GREEK_STANDARD_VALUE_PLUS_ONE,
                cls.GREEK_ALPHABET_REVERSAL_SUBSTITUTION,
                cls.GREEK_PAIR_MATCHING_SUBSTITUTION,
            ]
        elif language == Language.ENGLISH:
            return [
                cls.ENGLISH_TQ_STANDARD_VALUE,
                cls.ENGLISH_TQ_REDUCED_VALUE,
                cls.ENGLISH_TQ_SQUARE_VALUE,
                cls.ENGLISH_TQ_TRIANGULAR_VALUE,
                cls.ENGLISH_TQ_LETTER_POSITION_VALUE,
            ]
        elif language == Language.COPTIC:
            return [cls.COPTIC_STANDARD_VALUE, cls.COPTIC_REDUCED_VALUE]
        elif language == Language.ARABIC:
            return [cls.ARABIC_STANDARD_ABJAD]
        elif language == Language.UNKNOWN:
            return [cls.CUSTOM_CIPHER]
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
            return cls.HEBREW_STANDARD_VALUE
        elif language == Language.GREEK:
            return cls.GREEK_STANDARD_VALUE
        elif language == Language.ENGLISH:
            return cls.ENGLISH_TQ_STANDARD_VALUE
        elif language == Language.COPTIC:
            return cls.COPTIC_STANDARD_VALUE
        elif language == Language.ARABIC:
            return cls.ARABIC_STANDARD_ABJAD
        elif language == Language.UNKNOWN:
            # For UNKNOWN or if a direct default isn't sensible,
            return cls.CUSTOM_CIPHER
        else:
            return None

    @classmethod
    def get_all_types(cls) -> List["CalculationType"]:
        """Get all available calculation types across all languages.

        Returns:
            List of all calculation types
        """
        all_types = []
        for language in [
            Language.HEBREW,
            Language.GREEK,
            Language.ENGLISH,
            Language.COPTIC,
        ]:
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
