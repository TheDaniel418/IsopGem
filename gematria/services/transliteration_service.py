"""
Purpose: Provides transliteration services between Latin script and other scripts
         like Hebrew, Greek, and Coptic for gematria calculations.

This file is part of the gematria pillar and serves as a service component.
It is responsible for converting user input from a familiar script (e.g., Latin)
to the target script required for specific gematria methods.

Key components:
- TransliterationService: Class containing transliteration logic and mappings.
- Language-specific transliteration maps.

Dependencies:
- gematria.models.calculation_type.Language (for Language enum)

Related files:
- gematria/services/gematria_service.py: Will use this service.
- gematria/ui/*: UI components will interact with this for input.
"""

from typing import Dict  # List might be needed for ordered digraph keys

from loguru import logger

from gematria.models.calculation_type import (
    Language,  # Assuming Language is in calculation_type
)


class TransliterationService:
    """Service for handling transliteration between scripts."""

    def __init__(self):
        """Initialize the transliteration service with script mappings."""
        # Hebrew to Latin
        self._hebrew_to_latin_map = {
            "א": "a",
            "ב": "b",
            "ג": "g",
            "ד": "d",
            "ה": "h",
            "ו": "v",
            "ז": "z",
            "ח": "ch",
            "ט": "t",
            "י": "y",
            "כ": "k",
            "ך": "kh",
            "ל": "l",
            "מ": "m",
            "ם": "M",
            "נ": "n",
            "ן": "N",
            "ס": "s",
            "ע": "'",
            "פ": "p",
            "ף": "ph",
            "צ": "tz",
            "ץ": "Tz",
            "ק": "q",
            "ר": "r",
            "ש": "sh",
            "ת": "th",
        }
        # Latin to Hebrew (Simplified)
        self._latin_to_hebrew_map = {v: k for k, v in self._hebrew_to_latin_map.items()}
        # Add specific cases for Latin to Hebrew if needed (e.g., 'v' vs 'w')
        self._latin_to_hebrew_map.update(
            {"v": "ו", "w": "ו", "x": "קס"}
        )  # 'x' often becomes קס

        # Greek to Latin
        self._greek_to_latin_map = {
            "α": "a",
            "β": "b",
            "γ": "g",
            "δ": "d",
            "ε": "e",
            "ζ": "z",
            "η": "e",
            "θ": "th",
            "ι": "i",
            "κ": "k",
            "λ": "l",
            "μ": "m",
            "ν": "n",
            "ξ": "x",
            "ο": "o",
            "π": "p",
            "ρ": "r",
            "σ": "s",
            "ς": "s",
            "τ": "t",
            "υ": "y",
            "φ": "ph",
            "χ": "ch",
            "ψ": "ps",
            "ω": "o",
            # Capitals if needed, assuming lowercase input mostly
            "Α": "A",
            "Β": "B",
            "Γ": "G",
            "Δ": "D",
            "Ε": "E",
            "Ζ": "Z",
            "Η": "E",
            "Θ": "Th",
            "Ι": "I",
            "Κ": "K",
            "Λ": "L",
            "Μ": "M",
            "Ν": "N",
            "Ξ": "X",
            "Ο": "O",
            "Π": "P",
            "Ρ": "R",
            "Σ": "S",
            "Τ": "T",
            "Υ": "Y",
            "Φ": "Ph",
            "Χ": "Ch",
            "Ψ": "Ps",
            "Ω": "O",
        }
        # Latin to Greek (Simplified)
        self._latin_to_greek_map = {
            v.lower(): k for k, v in self._greek_to_latin_map.items() if k.islower()
        }
        self._latin_to_greek_map.update(
            {"ph": "φ", "ch": "χ", "ps": "ψ", "th": "θ", "ks": "ξ"}  # often for x
        )

        # Coptic to Latin (using the values from user docs primarily)
        self._coptic_to_latin_map = {
            "ⲁ": "a",
            "ⲃ": "b",
            "ⲅ": "g",
            "ⲇ": "d",
            "ⲉ": "e",
            "ⲋ": "so",
            "ⲍ": "z",
            "ⲏ": "e",
            "ⲑ": "th",
            "ⲓ": "i",
            "ⲕ": "k",
            "ⲗ": "l",
            "ⲙ": "m",
            "ⲛ": "n",
            "ⲝ": "ks",
            "ⲟ": "o",
            "ⲡ": "p",
            "ⲣ": "r",
            "ⲥ": "s",
            "ⲧ": "t",
            "ⲩ": "u",
            "ⲫ": "ph",
            "ⲭ": "kh",
            "ⲯ": "ps",
            "ⲱ": "o",
            "ϣ": "sh",
            "ϥ": "f",
            "ϧ": "kh",
            "ϩ": "h",
            "ϫ": "j",
            "ϭ": "ch",
            "ϯ": "ti",
        }
        # Latin to Coptic (Simplified)
        self._latin_to_coptic_map = {v: k for k, v in self._coptic_to_latin_map.items()}
        # Add common digraphs or alternative spellings for Latin to Coptic, ensure longest match first
        self._latin_to_coptic_map.update(
            {
                "ps": "ⲯ",
                "ph": "ⲫ",
                "th": "ⲑ",
                "kh": "ⲭ",  # Could also be ϧ, context dependent. Default to chi.
                "sh": "ϣ",
                "ks": "ⲝ",
                "so": "ⲋ",
                "dj": "ϫ",  # Alternative for j
                "ch": "ϭ",
                "ti": "ϯ",
                "ou": "ⲟⲩ",
                "ei": "ⲉⲓ",
                "ai": "ⲁⲓ",
            }
        )

        # Arabic to Latin (Simplified)
        self._arabic_to_latin_map = {
            "ا": "a",
            "ب": "b",
            "ج": "j",
            "د": "d",
            "ه": "h",
            "و": "w",
            "ز": "z",
            "ح": "H",
            "ط": "T",
            "ي": "y",
            "ك": "k",
            "ل": "l",
            "م": "m",
            "ن": "n",
            "س": "s",
            "ع": "'",
            "ف": "f",
            "ص": "S",
            "ق": "q",
            "ر": "r",
            "ش": "sh",
            "ت": "t",
            "ث": "th",
            "خ": "kh",
            "ذ": "dh",
            "ض": "D",
            "ظ": "Z",
            "غ": "gh",
        }

        # Latin to Arabic (Simplified)
        self._latin_to_arabic_map = {
            "a": "ا",
            "b": "ب",
            "j": "ج",
            "d": "د",
            "h": "ه",
            "w": "و",
            "z": "ز",
            "H": "ح",
            "T": "ط",
            "y": "ي",
            "k": "ك",
            "l": "ل",
            "m": "م",
            "n": "ن",
            "s": "س",
            "'": "ع",
            "f": "ف",
            "S": "ص",
            "q": "ق",
            "r": "ر",
            "sh": "ش",
            "t": "ت",
            "th": "ث",
            "kh": "خ",
            "dh": "ذ",
            "D": "ض",
            "Z": "ظ",
            "gh": "غ",
        }
        # For multi-character Latin to single/multi script, order matters.
        # Store ordered keys for languages where multi-char input is common.
        self._latin_to_hebrew_ordered_keys = sorted(
            self._latin_to_hebrew_map.keys(), key=len, reverse=True
        )
        self._latin_to_greek_ordered_keys = sorted(
            self._latin_to_greek_map.keys(), key=len, reverse=True
        )
        self._latin_to_coptic_ordered_keys = sorted(
            self._latin_to_coptic_map.keys(), key=len, reverse=True
        )
        self._latin_to_arabic_ordered_keys = sorted(
            self._latin_to_arabic_map.keys(), key=len, reverse=True
        )

    def transliterate_to_latin(self, text: str, source_language: Language) -> str:
        """Transliterates text from the source script to Latin."""
        target_map = {}
        if source_language == Language.HEBREW:
            target_map = self._hebrew_to_latin_map
        elif source_language == Language.GREEK:
            target_map = self._greek_to_latin_map
        elif source_language == Language.COPTIC:
            target_map = self._coptic_to_latin_map
        elif source_language == Language.ARABIC:
            target_map = self._arabic_to_latin_map
        else:
            logger.warning(
                f"Transliteration from {source_language} to Latin not supported."
            )
            return text

        # Simple character-by-character mapping for now
        # For languages like Arabic, shadda/sukun might need context, but this is basic.
        output = []
        for char_in in text:
            output.append(target_map.get(char_in, char_in))
        return "".join(output)

    def transliterate_to_script(self, text: str, target_language: Language) -> str:
        """Transliterates Latin text to the target script (Hebrew, Greek, Coptic, Arabic)."""
        processed_text = text
        ordered_keys_map = []
        final_map_for_single_chars = {}

        if target_language == Language.HEBREW:
            ordered_keys_map = self._latin_to_hebrew_ordered_keys
            final_map_for_single_chars = self._latin_to_hebrew_map
            # Optional: Lowercase input if map keys are all lowercase
            # processed_text = processed_text.lower()
        elif target_language == Language.GREEK:
            ordered_keys_map = self._latin_to_greek_ordered_keys
            final_map_for_single_chars = self._latin_to_greek_map
            processed_text = (
                processed_text.lower()
            )  # Greek map uses lowercase Latin keys
        elif target_language == Language.COPTIC:
            ordered_keys_map = self._latin_to_coptic_ordered_keys
            final_map_for_single_chars = self._latin_to_coptic_map
            processed_text = (
                processed_text.lower()
            )  # Coptic map uses lowercase Latin keys
        elif target_language == Language.ARABIC:
            ordered_keys_map = self._latin_to_arabic_ordered_keys
            final_map_for_single_chars = self._latin_to_arabic_map
            # Arabic can be case-sensitive in our map (e.g. H for ح, h for ه)
            # So, don't lowercase all input here unless map is designed for it.
        else:
            logger.warning(f"Transliteration to {target_language} not supported.")
            return text

        # Process multi-character sequences first, using the ordered keys
        # This loop iterates through the input string to find matches for multi-char keys
        temp_output = []
        i = 0
        while i < len(processed_text):
            match_found = False
            for key in ordered_keys_map:  # These are sorted by length, longest first
                if processed_text.startswith(
                    key, i
                ):  # Check if current position starts with this key
                    temp_output.append(final_map_for_single_chars[key])
                    i += len(key)
                    match_found = True
                    break
            if not match_found:
                # If no multi-char key matched, append the character as is (or map if single)
                # This part is tricky if single char keys are also in ordered_keys_map.
                # The logic should be: try longest multi-char. If no match, try single char map for current char.
                # The current `ordered_keys_map` includes single chars too. Let's refine.
                # A better way: iterate multi-char keys, then single char keys for remaining characters.

                # Simpler refined logic: The `ordered_keys_map` approach should work if all keys from
                # `final_map_for_single_chars` are in `ordered_keys_map`, sorted by length.
                # The current `ordered_keys_map` is `sorted(self._latin_to_..._map.keys(), key=len, reverse=True)`
                # This means single characters are at the end. The loop should work.
                # If no key (multi or single) matches, append original character.
                char_to_append = processed_text[i]
                temp_output.append(
                    final_map_for_single_chars.get(char_to_append, char_to_append)
                )
                i += 1
        return "".join(temp_output)

    def _transliterate_char_by_char(self, text: str, trans_map: Dict[str, str]) -> str:
        """Helper for simple character-by-character transliteration (Hebrew, Greek)."""
        output = []
        for char_in in text:
            output.append(trans_map.get(char_in, char_in))
        return "".join(output)

    def _transliterate_coptic_from_latin(self, text: str) -> str:
        """
        Transliterates Latin text to Coptic, handling (potentially overlapping) digraphs correctly.
        Input text should be lowercased by the caller if the map keys are lowercase.
        """
        output = []
        i = 0
        text_len = len(text)
        while i < text_len:
            matched_key = None
            # Try to match the longest possible key from our ordered list
            for key in self._coptic_ordered_keys:
                if text.startswith(key, i):
                    matched_key = key
                    break

            if matched_key:
                output.append(self._coptic_trans_map[matched_key])
                i += len(matched_key)
            else:
                # If no known key (digraph or single) matches, append the character as is
                output.append(text[i])
                i += 1
        return "".join(output)
