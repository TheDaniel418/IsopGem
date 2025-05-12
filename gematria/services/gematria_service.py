"""Gematria calculation service.

This module provides functionality for calculating gematria values.
"""

import re
import unicodedata
from typing import Callable, Dict, List, Optional, Union

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.transliteration_service import TransliterationService


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

        # Greek alphabet reversal substitution (True Atbash: α=ω, etc.)
        self._greek_alphabet_reversal_map = {
            "α": "ω",
            "β": "ψ",
            "γ": "χ",
            "δ": "φ",
            "ε": "υ",
            "ζ": "τ",
            "η": "σ",
            "θ": "ρ",
            "ι": "π",
            "κ": "ο",
            "λ": "ξ",
            "μ": "ν",
            "ν": "μ",
            "ξ": "λ",
            "ο": "κ",
            "π": "ι",
            "ρ": "θ",
            "σ": "η",
            "τ": "ζ",
            "υ": "ε",
            "φ": "δ",
            "χ": "γ",
            "ψ": "β",
            "ω": "α",
            # Note: ϝ (Digamma), ϙ (Koppa), ϡ (Sampi) are tricky for a pure 24-letter reversal.
            # The user doc implies a 24-letter reversal. For now, not including archaic letters here.
            # Variants should map to the reversal of their standard form if needed, e.g. ς (sigma) -> η (eta)
            "ς": "η",
            "ϲ": "η",
        }

        # Greek pair matching substitution (α=λ, β=κ, etc. - needs full definition from doc)
        # Example from doc: αβγ → λκι means α->λ, β->κ, γ->ι. This is a specific pairing.
        # The doc's example is short. A full 24-letter scheme would be needed.
        # Assuming a scheme like first half maps to second, second to first (like Albam/AlphaMu):
        # α-μ (13 letters) map to ν-ω and then some (if alphabet is >26 or has variants)
        # For now, let's use the existing _greek_alpha_mu_map for GREEK_ALPHAMU_SUBSTITUTION
        # and define a new one if GREEK_PAIR_MATCHING_SUBSTITUTION is meant to be different.
        # The doc's example α->λ, β->κ, γ->ι is specific. Let's assume a 12-letter shift or a defined list.
        # Placeholder - this needs the actual pairing scheme from the user doc example if it's a fixed cipher.
        # If it means general pairing (like Albam), _greek_alpha_mu_map is it.
        # Let's assume GREEK_PAIR_MATCHING_SUBSTITUTION is for the specific α->λ example from doc.
        # The doc gives: α->λ, β->κ, γ->ι. Then λ->α, κ->β, ι->γ (symmetric?)
        # This implies a specific set of pairs, not a systematic cipher on halves.
        self._greek_pair_matching_map = {
            "α": "λ",
            "λ": "α",
            "β": "κ",
            "κ": "β",
            "γ": "ι",
            "ι": "γ",
            "δ": "θ",
            "θ": "δ",  # Assuming symmetry for next pairs
            "ε": "η",
            "η": "ε",
            "ζ": "None",  # What does Zeta pair with? Needs full list.
            # ... This needs to be fully defined based on the intended cipher from docs.
            # For now, this is a very incomplete placeholder based on the example.
            # If the intent was the _greek_alpha_mu_map, then GREEK_PAIR_MATCHING_SUBSTITUTION is redundant with GREEK_ALPHAMU_SUBSTITUTION.
            # We will treat GREEK_PAIR_MATCHING_SUBSTITUTION as needing a unique map. For now, incomplete.
            # And GREEK_ALPHAMU_SUBSTITUTION uses _greek_alpha_mu_map.
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
        self._hebrew_standard_from_final_forms = {
            v: k for k, v in self._hebrew_final_forms.items()
        }

        # Extended letter values including true final forms for specific calculations
        self._large_letter_values = {
            **self._letter_values,  # Standard values first
            "ך": 500,
            "ם": 600,
            "ן": 700,
            "ף": 800,
            "ץ": 900,  # Override final forms
        }
        # Ensure standard forms of final letters point to their standard values if not overridden by large
        for final, regular in self._hebrew_standard_from_final_forms.items():
            if final not in self._large_letter_values:  # if ך was 20 in letter_values
                pass  # it is already set
            # elif regular in self._letter_values and final not in self._large_letter_values.keys():
            #     self._large_letter_values[final] = self._letter_values[regular]

        # Hebrew letter names with their standard values
        # The 'name' is the spelling. We will calculate 'value_standard' and 'value_final'
        self._hebrew_letter_names_data = {
            "א": {"name": "אלף"},
            "ב": {"name": "בית"},
            "ג": {"name": "גימל"},
            "ד": {"name": "דלת"},
            "ה": {"name": "הא"},
            "ו": {"name": "וו"},
            "ז": {"name": "זין"},
            "ח": {"name": "חית"},
            "ט": {"name": "טית"},
            "י": {"name": "יוד"},
            "כ": {"name": "כף"},
            "ל": {"name": "למד"},
            "מ": {"name": "מם"},
            "נ": {"name": "נון"},
            "ס": {"name": "סמך"},
            "ע": {"name": "עין"},
            "פ": {"name": "פא"},  # Docs had פה, but פא is more common for 81
            "צ": {"name": "צדי"},
            "ק": {"name": "קוף"},
            "ר": {"name": "ריש"},
            "ש": {"name": "שין"},
            "ת": {"name": "תו"},
            # Final forms - their names are typically descriptive, not used for value usually
            # but if needed, they could be: ך: כף סופית, ם: מם סופית etc.
            # For now, calculations will use the primary letter's name data.
        }

        for letter_char, data in self._hebrew_letter_names_data.items():
            name_spelling = data["name"]

            # Calculate value_standard for the name
            current_sum_standard = 0
            for i, char_in_name in enumerate(name_spelling):
                # Use _letter_values (which includes final forms with their non-final values)
                current_sum_standard += self._letter_values.get(char_in_name, 0)
            data["value_standard"] = current_sum_standard

            # Calculate value_final for the name (uses _large_letter_values for final letters *within the name spelling*)
            current_sum_final = 0
            for i, char_in_name in enumerate(name_spelling):
                is_last_char_in_name = i == len(name_spelling) - 1
                val_to_add = 0
                if (
                    is_last_char_in_name
                    and char_in_name in self._hebrew_final_forms.values()
                ):  # e.g. is ף, ץ, ם, ן, ך
                    val_to_add = self._large_letter_values.get(
                        char_in_name, 0
                    )  # Use its large value e.g. ף=800
                elif (
                    char_in_name in self._hebrew_final_forms.values()
                ):  # It's a final letter but not at end of name word
                    # Use its standard (non-final) value. _letter_values has ך as 20, not 500.
                    # Or, more correctly, use the value of its non-final equivalent from _letter_values
                    regular_form = self._hebrew_standard_from_final_forms.get(
                        char_in_name
                    )
                    if regular_form:
                        val_to_add = self._letter_values.get(regular_form, 0)
                    else:  # Should not happen if maps are correct
                        val_to_add = self._letter_values.get(char_in_name, 0)
                else:  # It's a regular letter
                    val_to_add = self._letter_values.get(char_in_name, 0)
                current_sum_final += val_to_add
            data["value_final"] = current_sum_final

        # For Hidden Value methods
        self._hebrew_hidden_value_standard_map: Dict[str, int] = {}
        self._hebrew_hidden_value_final_map: Dict[str, int] = {}
        for letter_char, data in self._hebrew_letter_names_data.items():
            standard_letter_val = self._letter_values.get(letter_char, 0)
            self._hebrew_hidden_value_standard_map[letter_char] = (
                data.get("value_standard", 0) - standard_letter_val
            )
            self._hebrew_hidden_value_final_map[letter_char] = (
                data.get("value_final", 0) - standard_letter_val
            )

        # Triangular values for Hebrew (Mispar Kidmi)
        self._triangular_values = {...}  # Keep existing map

        # Coptic letter values (placeholder)
        self._coptic_values = {
            "ⲁ": 1,
            "ⲃ": 2,
            "ⲅ": 3,
            "ⲇ": 4,
            "ⲉ": 5,
            "ⲋ": 6,
            "ⲍ": 7,
            "ⲏ": 8,
            "ⲑ": 9,
            "ⲓ": 10,
            "ⲕ": 20,
            "ⲗ": 30,
            "ⲙ": 40,
            "ⲛ": 50,
            "ⲝ": 60,
            "ⲟ": 70,
            "ⲡ": 80,
            "ⲣ": 100,
            "ⲥ": 200,
            "ⲧ": 300,
            "ⲩ": 400,
            "ⲫ": 500,
            "ⲭ": 600,
            "ⲯ": 700,
            "ⲱ": 800,
            "ϣ": 900,
            "ϥ": 90,
            "ϧ": 900,  # Note: Conflicting values for ϧ, ϩ, ϫ, ϭ based on doc. Using one for now.
            "ϩ": 900,
            "ϫ": 90,
            "ϭ": 90,
            "ϯ": 300,
        }
        # Coptic letter positions (placeholder if needed for ordinal)
        self._coptic_positions = {
            k: i + 1 for i, k in enumerate(self._coptic_values.keys())
        }

        # Helper for Greek Epomenos (next letter value)
        # Create a mapping from position to unique Greek letter for sequential lookup
        # Filter out variants like 'ς' and 'ϲ' if they share positions with a main form like 'σ'
        # to ensure a clean sequence for "next letter".
        unique_greek_letters_by_pos = {}
        for letter, pos in sorted(
            self._greek_positions.items(), key=lambda item: item[1]
        ):
            if (
                pos not in unique_greek_letters_by_pos
            ):  # Keep the first encountered letter for a given position
                if letter not in [
                    "ς",
                    "ϲ",
                ]:  # Prioritize non-variant forms if possible, though sort might handle this
                    unique_greek_letters_by_pos[pos] = letter
            # If main form already there, ensure variants don't overwrite, but ensure all positions are covered if variants are only ones at a pos.
            # A simpler way might be to just build the list from primary forms if they are defined or known.
            # For now, this tries to get one letter per position. Standard 24-letter sequence is ideal.
        # A more direct way: base it on a defined ordered list of the 24/27 main letters
        # self._ordered_greek_alphabet = ['α', 'β', ..., 'ω'] # Ideally defined
        # For now, let's use the positions we have, ensuring it respects the order from _greek_positions
        self._greek_pos_to_letter: Dict[int, str] = {}
        temp_letter_to_pos = {
            k: v for k, v in self._greek_positions.items() if k not in ["ς", "ϲ"]
        }
        self._greek_letter_to_pos: Dict[str, int] = temp_letter_to_pos
        self._greek_pos_to_letter = {v: k for k, v in temp_letter_to_pos.items()}
        self._max_greek_pos = 0
        if self._greek_pos_to_letter:
            self._max_greek_pos = max(self._greek_pos_to_letter.keys())

        # Arabic Abjad letter values
        self._arabic_values = {
            "ا": 1,
            "ب": 2,
            "ج": 3,
            "د": 4,
            "ه": 5,
            "و": 6,
            "ز": 7,
            "ح": 8,
            "ط": 9,
            "ي": 10,
            "ك": 20,
            "ل": 30,
            "م": 40,
            "ن": 50,
            "س": 60,
            "ع": 70,
            "ف": 80,
            "ص": 90,
            "ق": 100,
            "ر": 200,
            "ش": 300,
            "ت": 400,
            "ث": 500,
            "خ": 600,
            "ذ": 700,
            "ض": 800,
            "ظ": 900,
            "غ": 1000,
            "ة": 400,  # Tāʾ marbūṭah, often valued as Tāʾ
        }
        # Arabic letter positions (placeholder if needed for ordinal in the future)
        self._arabic_positions = {
            k: i + 1 for i, k in enumerate(self._arabic_values.keys())
        }  # Basic sequential

        # --- Define missing Greek value maps for existing methods ---
        self._greek_triangular_values: Dict[str, int] = {}
        for char, value in self._greek_values.items():
            self._greek_triangular_values[char] = (value * (value + 1)) // 2

        # For _calculate_greek_hidden and _calculate_greek_full_name
        # Names from https://en.wikipedia.org/wiki/Greek_alphabet
        self._greek_letter_names: Dict[str, Dict[str, Union[str, int]]] = {
            "α": {"name": "άλφα"},
            "β": {"name": "βήτα"},
            "γ": {"name": "γάμμα"},  # Wikipedia also lists γάμα
            "δ": {"name": "δέλτα"},
            "ε": {"name": "έψιλον"},  # Properly ἒ ψιλόν
            "ζ": {"name": "ζήτα"},
            "η": {"name": "ήτα"},
            "θ": {"name": "θήτα"},
            "ι": {"name": "ιώτα"},  # Wikipedia also lists γιώτα
            "κ": {"name": "κάππα"},
            "λ": {
                "name": "λάμβδα"
            },  # User specified λάμβδα (standard is λάμδα or λάμβδα)
            "μ": {"name": "μυ"},  # Changed to match Wikipedia's name for mu
            "ν": {"name": "νυ"},  # Changed to match Wikipedia's name for nu
            "ξ": {"name": "ξι"},  # Wikipedia lists ξι (xi) or ξεί
            "ο": {"name": "όμικρον"},  # Properly ὂ μικρόν
            "π": {"name": "πι"},  # Wikipedia lists πι (pi) or πεί
            "ρ": {"name": "ρω"},
            "σ": {"name": "σίγμα"},
            "τ": {"name": "ταυ"},
            "υ": {"name": "ύψιλον"},  # Properly ὖ ψιλόν
            "φ": {"name": "φι"},
            "χ": {"name": "χι"},
            "ψ": {"name": "ψι"},
            "ω": {"name": "ωμέγα"}  # Properly ὦ μέγα
            # Note: Archaic letters like ϝ, ϙ, ϡ are not included here as their "names" for this purpose are less standard.
        }

        # Calculate value_of_name for each entry in _greek_letter_names
        for char_key in list(
            self._greek_letter_names.keys()
        ):  # Iterate over keys as dict might change
            data = self._greek_letter_names[char_key]
            name_spelling = data["name"]  # This is already a string

            # Process this 'name_spelling' like any other Greek text passed to calculation
            # 1. Lowercase (as our _greek_values keys are lowercase)
            # 2. Strip diacritics (though Greek names might not have many beyond accents on first letter)
            processed_name_for_calc = self._strip_diacritical_marks(
                name_spelling.lower()
            )

            current_sum = 0
            for letter_in_name in processed_name_for_calc:
                current_sum += self._greek_values.get(letter_in_name, 0)

            if current_sum > 0:
                data["value_of_name"] = current_sum
            else:
                logger.warning(
                    f"Could not calculate value for Greek letter name: '{name_spelling}' (for '{char_key}'). This entry might be ignored by dependent calculations."
                )
                # We can choose to remove it or leave it without a value_of_name for debugging
                # data["value_of_name"] = 0 # Or None, or pop it

        self._greek_letter_hidden_values: Dict[str, int] = {}
        for char, data in self._greek_letter_names.items():
            value_of_name = data.get("value_of_name")
            standard_value = self._greek_values.get(char)
            if isinstance(value_of_name, int) and isinstance(standard_value, int):
                self._greek_letter_hidden_values[char] = value_of_name - standard_value
            else:
                logger.warning(
                    f"Could not calculate hidden value for Greek letter '{char}'. Name value: {value_of_name}, Standard value: {standard_value}"
                )

        # Initialize the database service
        self.db_service = CalculationDatabaseService()
        # Initialize the transliteration service
        self.transliteration_service = TransliterationService()

        logger.debug("GematriaService initialized")

    def calculate(
        self,
        text: str,
        calculation_type: Union[
            CalculationType, str, CustomCipherConfig
        ] = CalculationType.HEBREW_STANDARD_VALUE,
        transliterate_input: bool = False,
    ) -> int:
        """Calculate the gematria value for the given text.

        Args:
            text: The text to calculate
            calculation_type: The calculation type to use (enum, name, or custom config)
            transliterate_input: If True, attempts to transliterate Latin input to target script.

        Returns:
            The calculated gematria value
        """
        actual_text_to_process = text

        # Determine target script language for potential transliteration
        target_script_language: Optional[Language] = None
        original_calc_type = (
            calculation_type  # Keep a copy for CustomCipherConfig checks
        )

        if isinstance(calculation_type, str) and calculation_type != "CUSTOM_CIPHER":
            try:
                calculation_type = CalculationType[
                    calculation_type.upper()
                ]  # Ensure it matches enum member names
            except KeyError:
                logger.error(f"Unknown calculation type string: {calculation_type}")
                raise ValueError(f"Unknown calculation type string: {calculation_type}")

        # Determine target script based on calculation_type
        if isinstance(calculation_type, CustomCipherConfig):
            # Map CustomCipherConfig.language (which is LanguageType) to our Language enum
            if calculation_type.language == LanguageType.HEBREW:
                target_script_language = Language.HEBREW
            elif calculation_type.language == LanguageType.GREEK:
                target_script_language = Language.GREEK
            # English custom ciphers typically don't need Latin-to-English script transliteration from Latin input
            elif calculation_type.language == LanguageType.ENGLISH:
                target_script_language = Language.ENGLISH
        elif isinstance(calculation_type, CalculationType):
            name = calculation_type.name
            if (
                name.startswith("HEBREW_")
                or name.startswith("MISPAR_")
                or name in ["ALBAM", "ATBASH"]
            ):
                target_script_language = Language.HEBREW
            elif name.startswith("GREEK_"):
                target_script_language = Language.GREEK
            elif name.startswith("COPTIC_"):
                target_script_language = Language.COPTIC
            elif name.startswith("ARABIC_"):
                target_script_language = Language.ARABIC
            elif name.startswith("TQ_ENGLISH"):
                target_script_language = Language.ENGLISH

        if transliterate_input:
            if target_script_language and target_script_language not in [
                Language.ENGLISH,
                Language.UNKNOWN,
            ]:
                logger.debug(
                    f"Attempting to transliterate input '{text}' to {target_script_language.value} script."
                )
                actual_text_to_process = (
                    self.transliteration_service.transliterate_to_script(
                        text, target_script_language
                    )
                )
                logger.debug(
                    f"Transliterated text for processing: '{actual_text_to_process}'"
                )  # Log after translit
            elif target_script_language == Language.ENGLISH:
                logger.debug(
                    "Input is Latin for an English-based method, no script transliteration needed."
                )
            elif (
                not target_script_language and original_calc_type != "CUSTOM_CIPHER"
            ):  # Avoid warning if it was a custom cipher string
                logger.warning(
                    f"Could not determine target script for transliteration with calc_type: {calculation_type}. Original input: '{text}'. Skipping transliteration."
                )

        # Handle different input types for calculation_type (if it was a string and got converted)
        # This block was originally at the top, moved after transliteration logic so translit can use original calc_type info
        if isinstance(original_calc_type, str):  # Use original_calc_type for this check
            if original_calc_type == "CUSTOM_CIPHER":
                logger.debug("Received CUSTOM_CIPHER as calculation type string.")
                # This case should now be handled if calculation_type is a CustomCipherConfig instance
                # If it's still a string here, it means a CustomCipherConfig object wasn't passed.
                # The `isinstance(calculation_type, CustomCipherConfig)` check below will handle it if it IS an object.
                # If it truly is just the string "CUSTOM_CIPHER" without a config, it's problematic.
                if not isinstance(calculation_type, CustomCipherConfig):
                    logger.error(
                        "CUSTOM_CIPHER string received but no CustomCipherConfig object provided."
                    )
                    return 0  # Or raise error
            # If it was a string and got converted to CalculationType enum, calculation_type is now an enum.
            # If it was a string and NOT converted (e.g. unknown), error was raised earlier.

        # Process based on calculation type
        if isinstance(calculation_type, CustomCipherConfig):
            # Pass the (potentially transliterated) text to custom calculation
            return self._calculate_custom(actual_text_to_process, calculation_type)

        # Ensure calculation_type is an enum for the main dispatch logic if it started as a resolvable string
        if not isinstance(calculation_type, CalculationType):
            if original_calc_type == "CUSTOM_CIPHER" and not isinstance(
                calculation_type, CustomCipherConfig
            ):
                return 0
            logger.error(
                f"Calculation type is not a valid Enum or CustomCipherConfig: {calculation_type}"
            )
            raise ValueError(
                f"Invalid calculation type for dispatch: {calculation_type}"
            )

        logger.debug(f"Text before stripping diacritics: '{actual_text_to_process}'")
        cleaned_text = self._strip_diacritical_marks(actual_text_to_process)
        logger.debug(f"Text after stripping diacritics: '{cleaned_text}'")

        if (
            target_script_language == Language.GREEK
            and isinstance(calculation_type, CalculationType)
            and not transliterate_input
        ):
            cleaned_text = cleaned_text.lower()
            logger.debug(f"Greek text lowercased (non-translit path): '{cleaned_text}'")

        # Dispatch based on the CalculationType enum
        # HEBREW (Basic)
        if calculation_type == CalculationType.HEBREW_STANDARD_VALUE:
            return self._calculate_standard(cleaned_text, self._letter_values)
        elif calculation_type == CalculationType.HEBREW_ORDINAL_VALUE:
            return self._calculate_ordinal(cleaned_text, self._letter_positions)
        elif calculation_type == CalculationType.HEBREW_REVERSE_STANDARD_VALUES:
            return self._calculate_reversal(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_ALBAM_SUBSTITUTION:
            return self._calculate_albam(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_ATBASH_SUBSTITUTION:
            return self._calculate_atbash(cleaned_text)
        elif (
            calculation_type == CalculationType.HEBREW_BUILDING_VALUE_CUMULATIVE
        ):  # Was MISPAR_BONEH
            return self._calculate_building(cleaned_text)  # Corrected call
        elif (
            calculation_type == CalculationType.HEBREW_TRIANGULAR_VALUE
        ):  # Was MISPAR_KIDMI
            return self._calculate_triangular(
                cleaned_text
            )  # Uses self._triangular_values
        elif (
            calculation_type == CalculationType.HEBREW_INDIVIDUAL_SQUARE_VALUE
        ):  # Was MISPAR_PERATI
            return self._calculate_individual_square(
                cleaned_text
            )  # Uses self._letter_values
        elif (
            calculation_type == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD
        ):  # Corrected from MISPAR_SHEMI
            return self._calculate_full_name(
                cleaned_text
            )  # Uses self._hebrew_letter_names_data[char].get("value_standard")
        elif (
            calculation_type
            == CalculationType.HEBREW_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS
        ):  # Was MISPAR_MUSAFI
            return self._calculate_additive(cleaned_text)  # Uses self._letter_values
        elif (
            calculation_type == CalculationType.HEBREW_FINAL_LETTER_VALUES
        ):  # Corrected from MISPAR_SOFIT
            return self._calculate_mispar_sofit(
                cleaned_text
            )  # Uses self._large_letter_values (via _calculate_large)
        elif (
            calculation_type == CalculationType.HEBREW_SMALL_REDUCED_VALUE
        ):  # Was MISPAR_KATAN
            return self._calculate_mispar_katan(
                cleaned_text
            )  # Uses self._letter_values and self._final_letter_values_map_for_katan
        elif (
            calculation_type == CalculationType.HEBREW_INTEGRAL_REDUCED_VALUE
        ):  # Was MISPAR_MISPARI
            return self._calculate_mispar_mispari(
                cleaned_text
            )  # Uses self._letter_values
        # elif calculation_type == CalculationType.MISPAR_MESHULASH: # This is the old name for HEBREW_CUBED_VALUE
        #     return self._calculate_mispar_meshulash(cleaned_text)
        elif (
            calculation_type == CalculationType.HEBREW_CUBED_VALUE
        ):  # Was MISPAR_MESHULASH
            return self._calculate_mispar_meshulash(
                cleaned_text
            )  # Uses self._letter_values

        # HEBREW - FULL SPELLING & COLLECTIVE METHODS
        elif calculation_type == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS:
            return self._calculate_hebrew_sum_of_letter_names_finals(cleaned_text)
        elif (
            calculation_type == CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_STANDARD
        ):
            return self._calculate_hebrew_product_of_letter_names_standard(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_FINALS:
            return self._calculate_hebrew_product_of_letter_names_finals(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_HIDDEN_VALUE_STANDARD:
            return self._calculate_hebrew_hidden_value_standard(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_HIDDEN_VALUE_FINALS:
            return self._calculate_hebrew_hidden_value_finals(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_FACE_VALUE_STANDARD:
            return self._calculate_hebrew_face_value_standard(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_FACE_VALUE_FINALS:
            return self._calculate_hebrew_face_value_finals(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_BACK_VALUE_STANDARD:
            return self._calculate_hebrew_back_value_standard(cleaned_text)
        elif calculation_type == CalculationType.HEBREW_BACK_VALUE_FINALS:
            return self._calculate_hebrew_back_value_finals(cleaned_text)
        elif (
            calculation_type
            == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD_PLUS_LETTERS
        ):
            return self._calculate_hebrew_sum_of_letter_names_standard_plus_letters(
                cleaned_text
            )
        elif (
            calculation_type
            == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS_PLUS_LETTERS
        ):
            return self._calculate_hebrew_sum_of_letter_names_finals_plus_letters(
                cleaned_text
            )
        elif calculation_type == CalculationType.HEBREW_STANDARD_VALUE_PLUS_ONE:
            return self._calculate_hebrew_standard_value_plus_one(cleaned_text)

        # Handle Greek calculations
        elif calculation_type == CalculationType.GREEK_STANDARD_VALUE:  # Correct
            logger.debug(
                f"Calling _calculate_greek_standard with: '{cleaned_text}'"
            )  # Log before specific call
            return self._calculate_greek_standard(cleaned_text)
        elif calculation_type == CalculationType.GREEK_ORDINAL_VALUE:  # Correct
            return self._calculate_greek_ordinal(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_SQUARE_VALUE
        ):  # Correct (was GREEK_SQUARED)
            return self._calculate_greek_squared(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_REVERSE_STANDARD_VALUES
        ):  # Correct (was GREEK_REVERSAL)
            return self._calculate_greek_reversal(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_ALPHAMU_SUBSTITUTION
        ):  # Was GREEK_ALPHA_MU
            return self._calculate_greek_alpha_mu(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION
        ):  # Was GREEK_ALPHA_OMEGA
            return self._calculate_greek_alpha_omega(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_BUILDING_VALUE_CUMULATIVE
        ):  # Was GREEK_BUILDING
            return self._calculate_greek_building(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_TRIANGULAR_VALUE
        ):  # Was GREEK_TRIANGULAR
            return self._calculate_greek_triangular(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_HIDDEN_LETTER_NAME_VALUE
        ):  # Was GREEK_HIDDEN
            return self._calculate_greek_hidden(cleaned_text)
        elif (
            calculation_type == CalculationType.GREEK_SUM_OF_LETTER_NAMES
        ):  # Was GREEK_FULL_NAME
            return self._calculate_greek_full_name(cleaned_text)
        elif (
            calculation_type
            == CalculationType.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS
        ):  # Was GREEK_ADDITIVE
            return self._calculate_greek_additive(cleaned_text)
        elif calculation_type == CalculationType.GREEK_CUBED_VALUE:  # Was GREEK_KYVOS
            return self._calculate_greek_kyvos(text)
        elif (
            calculation_type == CalculationType.GREEK_NEXT_LETTER_VALUE
        ):  # Was GREEK_EPOMENOS
            return self._calculate_greek_epomenos(text)
        # GREEK_KYKLIKI was an old name, GREEK_CYCLICAL_PERMUTATION_VALUE is the new one from CalculationType
        elif (
            calculation_type == CalculationType.GREEK_CYCLICAL_PERMUTATION_VALUE
        ):  # Was GREEK_KYKLIKI
            return self._calculate_greek_kykliki(text)

        # GREEK - ADDITIONAL METHODS (These should already be using new names from when we added them)
        elif calculation_type == CalculationType.GREEK_SMALL_REDUCED_VALUE:
            return self._calculate_greek_small_reduced_value(text)
        # ... (ensure all other GREEK_ADDITIONAL methods listed are using correct new CalculationType names)
        elif calculation_type == CalculationType.GREEK_DIGITAL_VALUE:
            return self._calculate_greek_digital_value(text)
        elif calculation_type == CalculationType.GREEK_DIGITAL_ORDINAL_VALUE:
            return self._calculate_greek_digital_ordinal_value(text)
        elif calculation_type == CalculationType.GREEK_ORDINAL_SQUARE_VALUE:
            return self._calculate_greek_ordinal_square_value(text)
        elif calculation_type == CalculationType.GREEK_PRODUCT_OF_LETTER_NAMES:
            return self._calculate_greek_product_of_letter_names(text)
        elif calculation_type == CalculationType.GREEK_FACE_VALUE:
            return self._calculate_greek_face_value(text)
        elif calculation_type == CalculationType.GREEK_BACK_VALUE:
            return self._calculate_greek_back_value(text)
        elif calculation_type == CalculationType.GREEK_SUM_OF_LETTER_NAMES_PLUS_LETTERS:
            return self._calculate_greek_sum_of_letter_names_plus_letters(text)
        elif calculation_type == CalculationType.GREEK_STANDARD_VALUE_PLUS_ONE:
            return self._calculate_greek_standard_value_plus_one(text)
        elif calculation_type == CalculationType.GREEK_ALPHABET_REVERSAL_SUBSTITUTION:
            return self._calculate_greek_alphabet_reversal_substitution(text)
        elif calculation_type == CalculationType.GREEK_PAIR_MATCHING_SUBSTITUTION:
            return self._calculate_greek_pair_matching_substitution(text)

        # Handle English calculations
        elif (
            calculation_type == CalculationType.ENGLISH_TQ_STANDARD_VALUE
        ):  # Was TQ_ENGLISH
            return self._calculate_tq(cleaned_text)
        elif (
            calculation_type == CalculationType.ENGLISH_TQ_REDUCED_VALUE
        ):  # Was TQ_ENGLISH_REDUCTION
            return self._calculate_tq_english_reduction(cleaned_text)
        elif (
            calculation_type == CalculationType.ENGLISH_TQ_SQUARE_VALUE
        ):  # Was TQ_ENGLISH_SQUARE
            return self._calculate_tq_english_square(cleaned_text)
        elif (
            calculation_type == CalculationType.ENGLISH_TQ_TRIANGULAR_VALUE
        ):  # Was TQ_ENGLISH_TRIANGULAR
            return self._calculate_tq_english_triangular(cleaned_text)
        elif (
            calculation_type == CalculationType.ENGLISH_TQ_LETTER_POSITION_VALUE
        ):  # Was TQ_ENGLISH_LETTER_POSITION
            return self._calculate_tq_english_letter_position(cleaned_text)

        # === COPTIC METHODS ===
        elif (
            calculation_type == CalculationType.COPTIC_STANDARD_VALUE
        ):  # Was COPTIC_STANDARD
            return self._calculate_coptic_standard(cleaned_text)
        elif (
            calculation_type == CalculationType.COPTIC_REDUCED_VALUE
        ):  # Was COPTIC_REDUCED
            return self._calculate_coptic_reduced(cleaned_text)

        # === ARABIC METHODS ===
        elif calculation_type == CalculationType.ARABIC_STANDARD_ABJAD:
            return self._calculate_arabic_standard_abjad(cleaned_text)

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

    def _calculate_standard(self, text: str, values: Dict[str, int]) -> int:
        """Calculate standard gematria (Mispar Hechrachi).

        Args:
            text: Text to calculate
            values: Dictionary of letter values

        Returns:
            Standard gematria value
        """
        total = 0
        for char in text:
            if char in values:
                total += values[char]
        return total

    def _calculate_ordinal(self, text: str, positions: Dict[str, int]) -> int:
        """Calculate ordinal gematria (Mispar Siduri).

        Args:
            text: Text to calculate
            positions: Dictionary of letter positions

        Returns:
            Ordinal gematria value
        """
        total = 0
        for char in text:
            if char in positions:
                total += positions[char]
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
        return self._calculate_standard(substituted, self._letter_values)

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
        return self._calculate_standard(substituted, self._letter_values)

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

    def _calculate_building(self, text: str) -> int:  # Reverted signature
        """Calculate building gematria (Mispar Bone'eh).

        For each letter, add the cumulative value of all previous letters plus current.

        Args:
            text: Text to calculate

        Returns:
            Building gematria value
        """
        filtered_text = "".join(
            char for char in text if char in self._letter_values
        )  # Reverted to use self._letter_values
        total = 0
        running_sum = 0

        for char in filtered_text:
            if char in self._letter_values:  # Reverted to use self._letter_values
                running_sum += self._letter_values[
                    char
                ]  # Reverted to use self._letter_values
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
        logger.info(f"Calculating Hebrew Triangular (Kidmi) for: {text}")
        # This method uses a precomputed map (_triangular_values) which is based on standard Hebrew values.
        # The current _triangular_values map IS the result of n(n+1)/2 for each letter, so it is simpler to use it directly.
        total = 0
        for char in text:
            if (
                char in self._triangular_values
            ):  # This 'triangular_values' should be self._triangular_values if it's a class member
                # or passed in. Assuming it refers to the one in __init__ for Hebrew.
                # The _triangular_values map for hebrew is already populated with final sums.
                # Let's make sure this refers to the correct map.
                # The original code for this method was:
                # if char in self._triangular_values: total += self._triangular_values[char]
                # This implies _triangular_values is a member. It is defined in __init__.
                if (
                    char in self._triangular_values
                ):  # Corrected to self._triangular_values
                    total += self._triangular_values[char]
        return total

    def _calculate_individual_square(self, text: str) -> int:
        """Calculate the individual square gematria (Mispar Perati) value.

        In this method, each letter value is squared and then summed.

        Args:
            text: The text to calculate

        Returns:
            The calculated value
        """
        logger.info(f"Calculating Hebrew Individual Square (Perati) for: {text}")
        return self._apply_char_operation_and_sum(
            text, self._letter_values, lambda x: x**2
        )

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
        standard_value = self._calculate_standard(text, self._letter_values)

        # Count the number of letters (excluding non-Hebrew characters)
        letter_count = sum(1 for char in text if char in self._letter_values)

        # Return the total
        return standard_value + letter_count

    # === STUBS FOR NEW HEBREW METHODS ===
    def _calculate_mispar_sofit(self, text: str) -> int:
        """Calculate Hebrew Final Letter Values (Mispar Sofit).
        This uses specific values for final forms (e.g., Final Kaf = 500).
        It is equivalent to the existing _calculate_large method.
        """
        logger.info(f"Calculating Mispar Sofit for: {text}")
        return self._calculate_large(text)  # Implemented by _calculate_large

    def _calculate_mispar_katan(self, text: str) -> int:
        """Calculate Hebrew Small/Reduced Value (Mispar Katan).
        Each letter's standard value is reduced to a single digit by summing its digits.
        """
        logger.info(f"Calculating Mispar Katan for: {text}")
        total = 0
        for char in text:
            if char in self._letter_values:
                value = self._letter_values[char]
                # Reduce each letter's value to a single digit iteratively.
                total += self._reduce_to_single_digit(value)
        return total

    def _calculate_mispar_mispari(self, text: str) -> int:
        """Calculate Hebrew Integral Reduced Value (Mispar Mispari).
        Sums the digits of each letter's standard value.
        """
        logger.info(f"Calculating Mispar Mispari for: {text}")
        total = 0
        for char in text:
            if char in self._letter_values:
                value = self._letter_values[char]
                # Summing digits of each letter's value (once, not iteratively to single digit)
                total += self._sum_digits_of_value(value)
        return total

    def _calculate_mispar_meshulash(self, text: str) -> int:
        """Calculate Hebrew Cubed Value (Mispar Meshulash).
        Each letter's standard value is cubed.
        """
        logger.info(f"Calculating Mispar Meshulash for: {text}")
        total = 0
        for char in text:
            if char in self._letter_values:
                total += self._letter_values[char] ** 3
        return total
        return self._apply_char_operation_and_sum(
            text, self._letter_values, lambda x: x**3
        )

    # === ADVANCED HEBREW - FULL SPELLING & COLLECTIVE METHODS ===

    def _calculate_hebrew_sum_of_letter_names_finals(self, text: str) -> int:
        """Calculates Mispar Shemi Sofit (Sum of letter names using final values where applicable in the name)."""
        logger.info(f"Calculating Hebrew Sum of Letter Names (Finals) for: {text}")
        total = 0
        for char_in_word in text:
            if char_in_word in self._hebrew_letter_names_data:
                total += self._hebrew_letter_names_data[char_in_word].get(
                    "value_final", 0
                )
        return total

    def _calculate_hebrew_product_of_letter_names_standard(self, text: str) -> int:
        """Calculates Name Value (Mispar Shemi - Product of standard letter name values)."""
        logger.info(
            f"Calculating Hebrew Product of Letter Names (Standard) for: {text}"
        )
        product = 1
        has_multiplied = False
        for char_in_word in text:
            if char_in_word in self._hebrew_letter_names_data:
                product *= self._hebrew_letter_names_data[char_in_word].get(
                    "value_standard", 1
                )  # Multiply by 1 if missing
                has_multiplied = True
        return (
            product if has_multiplied else 0
        )  # Return 0 if no letters found, consistent with sum returning 0

    def _calculate_hebrew_product_of_letter_names_finals(self, text: str) -> int:
        """Calculates Name Value with Finals (Mispar Shemi Sofit - Product of final letter name values)."""
        logger.info(f"Calculating Hebrew Product of Letter Names (Finals) for: {text}")
        product = 1
        has_multiplied = False
        for char_in_word in text:
            if char_in_word in self._hebrew_letter_names_data:
                product *= self._hebrew_letter_names_data[char_in_word].get(
                    "value_final", 1
                )
                has_multiplied = True
        return product if has_multiplied else 0

    def _calculate_hebrew_hidden_value_standard(self, text: str) -> int:
        """Calculates Hidden Value (Mispar Ne'elam - Standard name value minus letter value)."""
        logger.info(f"Calculating Hebrew Hidden Value (Standard) for: {text}")
        total = 0
        for char_in_word in text:
            total += self._hebrew_hidden_value_standard_map.get(char_in_word, 0)
        return total

    def _calculate_hebrew_hidden_value_finals(self, text: str) -> int:
        """Calculates Hidden Value with Finals (Mispar Ne'elam Sofit - Final name value minus letter value)."""
        logger.info(f"Calculating Hebrew Hidden Value (Finals) for: {text}")
        total = 0
        for char_in_word in text:
            total += self._hebrew_hidden_value_final_map.get(char_in_word, 0)
        return total

    def _calculate_hebrew_face_value_standard(self, text: str) -> int:
        """Calculates Face Value (Mispar HaPanim - Standard name value of first letter + standard values of rest)."""
        logger.info(f"Calculating Hebrew Face Value (Standard) for: {text}")
        if not text:
            return 0
        total = 0
        first_letter = text[0]
        if first_letter in self._hebrew_letter_names_data:
            total += self._hebrew_letter_names_data[first_letter].get(
                "value_standard", 0
            )
        else:  # Fallback if first letter not in names_data, use its standard value
            total += self._letter_values.get(first_letter, 0)

        for char_in_word in text[1:]:
            total += self._letter_values.get(char_in_word, 0)
        return total

    def _calculate_hebrew_face_value_finals(self, text: str) -> int:
        """Calculates Face Value with Finals (Mispar HaPanim Sofit - Final name value of first letter + standard values of rest)."""
        logger.info(f"Calculating Hebrew Face Value (Finals) for: {text}")
        if not text:
            return 0
        total = 0
        first_letter = text[0]
        if first_letter in self._hebrew_letter_names_data:
            total += self._hebrew_letter_names_data[first_letter].get("value_final", 0)
        else:  # Fallback
            total += self._large_letter_values.get(
                first_letter, self._letter_values.get(first_letter, 0)
            )

        for char_in_word in text[1:]:
            # Standard values for the rest, but consider if they are final letters for _large_letter_values context
            # The doc implies standard values for rest. So, _letter_values is correct.
            total += self._letter_values.get(char_in_word, 0)
        return total

    def _calculate_hebrew_back_value_standard(self, text: str) -> int:
        """Calculates Back Value (Mispar HaAchor - Standard values of all but last + standard name value of last)."""
        logger.info(f"Calculating Hebrew Back Value (Standard) for: {text}")
        if not text:
            return 0
        total = 0
        last_letter = text[-1]

        for char_in_word in text[:-1]:
            total += self._letter_values.get(char_in_word, 0)

        if last_letter in self._hebrew_letter_names_data:
            total += self._hebrew_letter_names_data[last_letter].get(
                "value_standard", 0
            )
        else:  # Fallback
            total += self._letter_values.get(last_letter, 0)
        return total

    def _calculate_hebrew_back_value_finals(self, text: str) -> int:
        """Calculates Back Value with Finals (Mispar HaAchor Sofit - Standard values of all but last + final name value of last)."""
        logger.info(f"Calculating Hebrew Back Value (Finals) for: {text}")
        if not text:
            return 0
        total = 0
        last_letter = text[-1]

        for char_in_word in text[:-1]:
            total += self._letter_values.get(char_in_word, 0)

        if last_letter in self._hebrew_letter_names_data:
            total += self._hebrew_letter_names_data[last_letter].get("value_final", 0)
        else:  # Fallback
            total += self._large_letter_values.get(
                last_letter, self._letter_values.get(last_letter, 0)
            )
        return total

    def _calculate_hebrew_sum_of_letter_names_standard_plus_letters(
        self, text: str
    ) -> int:
        """Calculates Name Collective Value (Mispar Shemi Kolel - Standard name sum + number of letters)."""
        logger.info(
            f"Calculating Hebrew Sum of Letter Names (Standard) + Letters for: {text}"
        )
        name_sum_standard = 0
        letter_count = 0
        for char_in_word in text:
            if char_in_word in self._hebrew_letter_names_data:
                name_sum_standard += self._hebrew_letter_names_data[char_in_word].get(
                    "value_standard", 0
                )
            if char_in_word in self._letter_values:  # Count valid Hebrew letters
                letter_count += 1
        return name_sum_standard + letter_count

    def _calculate_hebrew_sum_of_letter_names_finals_plus_letters(
        self, text: str
    ) -> int:
        """Calculates Name Collective Value with Finals (Mispar Shemi Kolel Sofit - Final name sum + number of letters)."""
        logger.info(
            f"Calculating Hebrew Sum of Letter Names (Finals) + Letters for: {text}"
        )
        name_sum_final = 0
        letter_count = 0
        for char_in_word in text:
            if char_in_word in self._hebrew_letter_names_data:
                name_sum_final += self._hebrew_letter_names_data[char_in_word].get(
                    "value_final", 0
                )
            if char_in_word in self._letter_values:
                letter_count += 1
        return name_sum_final + letter_count

    def _calculate_hebrew_standard_value_plus_one(self, text: str) -> int:
        """Calculates Regular plus Collective (Standard value + 1)."""
        logger.info(f"Calculating Hebrew Standard Value + 1 for: {text}")
        standard_val = self._calculate_standard(
            text, self._letter_values
        )  # Uses _letter_values
        return standard_val + 1

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
        logger.info(f"Calculating Greek Squared for: {text}")
        return self._apply_char_operation_and_sum(
            text, self._greek_values, lambda x: x**2
        )

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
        logger.info(f"Calculating Greek Triangular for: {text}")
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
        logger.info(f"Calculating Greek Hidden for: {text}")
        total = 0
        for char in text:
            if char in self._greek_letter_hidden_values:
                total += self._greek_letter_hidden_values[char]
            elif (
                char in self._greek_letter_names
                and isinstance(self._greek_letter_names[char].get("value_of_name"), int)
                and char in self._greek_values
            ):
                # Fallback if _greek_letter_hidden_values wasn't fully populated but names are
                hidden_val = (
                    self._greek_letter_names[char]["value_of_name"]
                    - self._greek_values[char]
                )
                total += hidden_val
                self._greek_letter_hidden_values[char] = hidden_val  # Cache it
            else:
                logger.warning(
                    f"No hidden value or name definition for Greek letter '{char}'."
                )
        return total

    def _calculate_greek_full_name(self, text: str) -> int:
        """Calculate Greek full name value (Arithmos Onomatos).

        Args:
            text: Greek text to calculate

        Returns:
            Greek full name value
        """
        logger.info(f"Calculating Greek Full Name for: {text}")
        total = 0
        for original_char in text:  # Renamed char to original_char for clarity
            char_for_lookup = original_char
            if original_char == "ς":  # If it's the final sigma
                char_for_lookup = "σ"  # Treat it as standard sigma for this lookup

            if char_for_lookup in self._greek_letter_names:
                name_data = self._greek_letter_names[char_for_lookup]
                letter_value = name_data.get("value_of_name")  # Use .get() for safety
                if isinstance(letter_value, int):
                    total += letter_value
                else:
                    # This warning was in the previous apply, it's good to keep
                    logger.warning(
                        f"No valid 'value_of_name' for Greek letter '{char_for_lookup}' in _greek_letter_names."
                    )
            else:
                logger.warning(
                    f"Greek letter '{original_char}' not found in _greek_letter_names for Full Name calculation."
                )
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

    # === STUBS FOR NEW GREEK METHODS ===
    def _calculate_greek_kyvos(self, text: str) -> int:
        """Calculate Greek Cubed Value (Arithmos Kyvos).
        Each letter's standard Greek value is cubed.
        """
        logger.info(f"Calculating Greek Kyvos for: {text}")
        total = 0
        for char in text:
            if char in self._greek_values:
                total += self._greek_values[char] ** 3
        return total
        return self._apply_char_operation_and_sum(
            text, self._greek_values, lambda x: x**3
        )

    def _calculate_greek_epomenos(self, text: str) -> int:
        """Calculate Greek Next Letter Value (Arithmos Epomenos).
        Value of the following letter in the Greek alphabet.
        """
        logger.info(f"Calculating Greek Epomenos for: {text}")
        total = 0
        if (
            not self._greek_pos_to_letter or not self._greek_letter_to_pos
        ):  # Ensure helper maps are initialized
            logger.error("Greek position/letter maps not initialized for Epomenos.")
            return 0

        for char in text:
            current_pos = self._greek_letter_to_pos.get(char)
            if current_pos is not None:
                next_pos = current_pos + 1
                if (
                    next_pos <= self._max_greek_pos
                    and next_pos in self._greek_pos_to_letter
                ):
                    next_char = self._greek_pos_to_letter[next_pos]
                    total += self._greek_values.get(next_char, 0)
                else:
                    # No next letter (e.g., for Omega if it's the last defined position)
                    # Or if next_pos maps to a variant not in _greek_values directly
                    logger.debug(
                        f"No defined next letter or value for position after '{char}' (pos {current_pos})."
                    )
                    pass  # Add 0 if no next letter value
            else:
                # Character not in defined Greek alphabet positions
                logger.debug(
                    f"Character '{char}' not found in Greek letter positions for Epomenos."
                )
        return total

    def _calculate_greek_kykliki(self, text: str) -> int:
        """Calculate Greek Cyclical Permutation (Kyklikē Metathesē).
        Text is cyclically permuted (e.g., "αβγδ" -> "βγδα") then standard value is taken.
        """
        logger.info(f"Calculating Greek Kykliki for: {text}")
        if not text:
            return 0
        permuted_text = text[1:] + text[0]
        logger.debug(f"Permuted text for Kykliki: {permuted_text}")
        return self._calculate_greek_standard(permuted_text)

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

    # === STUBS FOR NEW TQ ENGLISH METHODS ===
    def _calculate_tq_english_reduction(self, text: str) -> int:
        """Calculate TQ English Reduction.
        The standard TQ sum is reduced to a single digit.
        """
        logger.info(f"Calculating TQ English Reduction for: {text}")
        standard_tq_value = self._calculate_tq(text)
        return self._reduce_to_single_digit(standard_tq_value)

    def _calculate_tq_english_square(self, text: str) -> int:
        """Calculate TQ English Square Value.
        Each letter's TQ value is squared, then summed.
        """
        logger.info(f"Calculating TQ English Square for: {text}")
        total = 0
        # Text for TQ methods is passed as `cleaned_text` from `calculate` method
        # which means it's the result of `_strip_diacritical_marks(actual_text_to_process)`.
        # `_calculate_tq` itself does not preprocess further.
        for char in text:
            if char in self._tq_values:
                total += self._tq_values[char] ** 2
        return total
        return self._apply_char_operation_and_sum(
            text, self._tq_values, lambda x: x**2
        )

    def _calculate_tq_english_triangular(self, text: str) -> int:
        """Calculate TQ English Triangular Value. Placeholder."""
        # The following logger line (commented or uncommented) should be removed:
        # logger.warning(f"Calculation method TQ English Triangular not fully implemented for text: {text}")
        total = 0
        for char in text:
            if char in self._tq_values:
                n = self._tq_values[char]
                total += n * (n + 1) // 2  # Triangular number formula
        return total  # Placeholder

    def _calculate_tq_english_letter_position(self, text: str) -> int:
        """Calculate TQ English Letter Position."""  # Removed Placeholder from docstring
        # logger.warning(f"Calculation method TQ English Letter Position not fully implemented for text: {text}") # Ensure this line is removed
        total = 0
        for i, char in enumerate(text):
            if char in self._tq_values:
                total += self._tq_values[char] * (i + 1)  # Position is 1-indexed
        return total  # Removed Placeholder comment

    # ===== COPTIC CALCULATION METHODS =====
    def _calculate_coptic_standard(self, text: str) -> int:
        """Calculate standard Coptic gematria. Placeholder."""
        logger.warning(
            f"Calculation method Coptic Standard not fully implemented for text: {text}"
        )
        total = 0
        # Assuming Coptic text might need specific preprocessing if not handled by _strip_diacritical_marks
        # cleaned_text = self._preprocess_coptic_text(text) # If needed
        cleaned_text = text  # For now
        for char in cleaned_text:
            if char in self._coptic_values:
                total += self._coptic_values[char]
        return total  # Placeholder

    def _calculate_coptic_reduced(self, text: str) -> int:
        """Calculate reduced Coptic gematria. Placeholder."""
        logger.info(f"Calculating Coptic Reduced for: {text}")
        standard_coptic_value = self._calculate_coptic_standard(text)
        return self._reduce_to_single_digit(standard_coptic_value)

    # ===== ARABIC CALCULATION METHODS =====
    def _calculate_arabic_standard_abjad(self, text: str) -> int:
        """Calculate standard Arabic Abjad numerology."""
        logger.info(f"Calculating Arabic Standard Abjad for: {text}")
        total = 0
        for char in text:
            total += self._arabic_values.get(char, 0)
        return total

    def calculate_and_save(
        self,
        text: str,
        calculation_type: Union[
            CalculationType, str, CustomCipherConfig
        ] = CalculationType.HEBREW_STANDARD_VALUE,
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
        calc_type: Union[CalculationType, str] = CalculationType.HEBREW_STANDARD_VALUE
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

    # --- Helper Methods for Calculation Logic ---
    def _reduce_to_single_digit(self, value: int) -> int:
        """Reduces a number to a single digit by iteratively summing its digits."""
        # Check for negative numbers - reduction typically applies to positive values in gematria
        if value < 0:
            # Decide on handling: return as is, take abs, or raise error
            # For now, let's assume reduction applies to magnitude, then reapply sign if needed, or just work with positive.
            # Given gematria values are usually positive, this is less of an issue.
            pass  # Or handle negative sign explicitly if reduction should be sign-aware

        reduced = abs(value)  # Work with positive value for reduction
        while reduced > 9:
            reduced = sum(int(d) for d in str(reduced))
        return reduced

    def _sum_digits_of_value(self, value: int) -> int:
        """Sums the digits of a given number (e.g., 345 -> 3+4+5=12)."""
        return sum(
            int(d) for d in str(abs(value))
        )  # Use abs in case of negative inputs, though unlikely for gematria

    def _apply_char_operation_and_sum(
        self, text: str, value_map: Dict[str, int], operation: Callable[[int], int]
    ) -> int:
        """Applies a given operation to each character's value and sums the results."""
        total = 0
        for char in text:
            if char in value_map:
                total += operation(value_map[char])
        return total

    # === STUBS FOR ADDITIONAL GREEK METHODS (from Gematria_Methods.md) ===

    def _calculate_greek_small_reduced_value(self, text: str) -> int:
        """Calculates Greek Small Value (Arithmos Mikros - Reduces standard values to single digit)."""
        logger.info(f"Calculating Greek Small Reduced Value for: {text}")
        total = 0
        for char in text:
            if char in self._greek_values:
                total += self._reduce_to_single_digit(self._greek_values[char])
        return total

    def _calculate_greek_digital_value(self, text: str) -> int:
        """Calculates Greek Digital Value (Arithmos Psephiakos - Sums digits of each letter's standard value)."""
        logger.info(f"Calculating Greek Digital Value for: {text}")
        total = 0
        for char in text:
            if char in self._greek_values:
                total += self._sum_digits_of_value(self._greek_values[char])
        return total

    def _calculate_greek_digital_ordinal_value(self, text: str) -> int:
        """Calculates Greek Digital Ordinal Value (Arithmos Taktikos Psephiakos - Sums digits of ordinal value)."""
        logger.info(f"Calculating Greek Digital Ordinal Value for: {text}")
        total = 0
        for char in text:
            if char in self._greek_positions:
                total += self._sum_digits_of_value(self._greek_positions[char])
        return total

    def _calculate_greek_ordinal_square_value(self, text: str) -> int:
        """Calculates Greek Ordinal Square Value (Arithmos Taktikos Tetragonos)."""
        logger.info(f"Calculating Greek Ordinal Square Value for: {text}")
        return self._apply_char_operation_and_sum(
            text, self._greek_positions, lambda x: x**2
        )

    def _calculate_greek_product_of_letter_names(self, text: str) -> int:
        """Calculates Greek Name Value (Arithmos Onomatikos - Product of letter name values)."""
        logger.info(f"Calculating Greek Product of Letter Names for: {text}")
        product = 1
        has_multiplied = False
        for char in text:
            if char in self._greek_letter_names:
                name_data = self._greek_letter_names[char]
                value_of_name = name_data.get("value_of_name")
                if isinstance(value_of_name, int):
                    product *= (
                        value_of_name if value_of_name != 0 else 1
                    )  # Avoid multiplying by 0 if a name value is 0
                    has_multiplied = True
        return product if has_multiplied else 0

    def _calculate_greek_face_value(self, text: str) -> int:
        """Calculates Greek Face Value (Arithmos Prosopeio)."""
        logger.info(f"Calculating Greek Face Value for: {text}")
        if not text:
            return 0
        total = 0
        first_letter = text[0]
        if first_letter in self._greek_letter_names and isinstance(
            self._greek_letter_names[first_letter].get("value_of_name"), int
        ):
            total += self._greek_letter_names[first_letter]["value_of_name"]
        else:  # Fallback to standard value if name or name value not found
            total += self._greek_values.get(first_letter, 0)
        for char_in_word in text[1:]:
            total += self._greek_values.get(char_in_word, 0)
        return total

    def _calculate_greek_back_value(self, text: str) -> int:
        """Calculates Greek Back Value (Arithmos Opisthios)."""
        logger.info(f"Calculating Greek Back Value for: {text}")
        if not text:
            return 0
        total = 0
        last_letter = text[-1]
        for char_in_word in text[:-1]:
            total += self._greek_values.get(char_in_word, 0)
        if last_letter in self._greek_letter_names and isinstance(
            self._greek_letter_names[last_letter].get("value_of_name"), int
        ):
            total += self._greek_letter_names[last_letter]["value_of_name"]
        else:  # Fallback
            total += self._greek_values.get(last_letter, 0)
        return total

    def _calculate_greek_sum_of_letter_names_plus_letters(self, text: str) -> int:
        """Calculates Greek Name Collective Value (Arithmos Onomatikos Syllogikos)."""
        logger.info(f"Calculating Greek Sum of Letter Names + Letters for: {text}")
        name_sum = self._calculate_greek_full_name(
            text
        )  # Reuses existing full name sum
        letter_count = sum(1 for char in text if char in self._greek_values)
        return name_sum + letter_count

    def _calculate_greek_standard_value_plus_one(self, text: str) -> int:
        """Calculates Greek Regular plus Collective (Kanonikos Syn Syllogikos)."""
        logger.info(f"Calculating Greek Standard Value + 1 for: {text}")
        standard_val = self._calculate_greek_standard(text)
        return standard_val + 1

    def _calculate_greek_alphabet_reversal_substitution(self, text: str) -> int:
        """Calculates Greek using true Atbash-like letter substitution (α=ω)."""
        logger.info(f"Calculating Greek Alphabet Reversal Substitution for: {text}")
        substituted_text = "".join(
            [self._greek_alphabet_reversal_map.get(char, char) for char in text]
        )
        return self._calculate_greek_standard(substituted_text)

    def _calculate_greek_pair_matching_substitution(self, text: str) -> int:
        """Calculates Greek using specific pair matching substitution (e.g., α=λ)."""
        logger.info(f"Calculating Greek Pair Matching Substitution for: {text}")
        if not self._greek_pair_matching_map or list(
            self._greek_pair_matching_map.values()
        ) == [
            "None"
        ]:  # Check if map is effectively empty/placeholder
            logger.warning("Greek Pair Matching map is not fully defined. Returning 0.")
            return 0
        substituted_text = "".join(
            [self._greek_pair_matching_map.get(char, char) for char in text]
        )
        return self._calculate_greek_standard(substituted_text)
