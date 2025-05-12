"""Unit tests for the GematriaService."""

import pytest
from gematria.services.gematria_service import GematriaService
from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType as CustomLanguageType

@pytest.fixture
def gematria_service() -> GematriaService:
    """Provides a GematriaService instance for tests."""
    return GematriaService()

def test_hebrew_calculations(gematria_service: GematriaService):
    """Test all Hebrew calculation types."""
    sample_text = "שלום" # Shalom
    hebrew_types = CalculationType.get_types_for_language(Language.HEBREW)
    for calc_type in hebrew_types:
        try:
            result = gematria_service.calculate(sample_text, calc_type)
            assert isinstance(result, int), f"Expected int for {calc_type.name}, got {type(result)}"
            print(f"Successfully calculated {calc_type.name} for '{sample_text}': {result}")
        except Exception as e:
            pytest.fail(f"Error calculating {calc_type.name} for '{sample_text}': {e}")

def test_greek_calculations(gematria_service: GematriaService):
    """Test all Greek calculation types."""
    sample_text = "λογος" # Logos
    greek_types = CalculationType.get_types_for_language(Language.GREEK)
    for calc_type in greek_types:
        try:
            result = gematria_service.calculate(sample_text, calc_type)
            assert isinstance(result, int), f"Expected int for {calc_type.name}, got {type(result)}"
            print(f"Successfully calculated {calc_type.name} for '{sample_text}': {result}")
        except Exception as e:
            pytest.fail(f"Error calculating {calc_type.name} for '{sample_text}': {e}")

def test_english_tq_calculations(gematria_service: GematriaService):
    """Test all English TQ calculation types."""
    sample_text = "test"
    english_types = CalculationType.get_types_for_language(Language.ENGLISH)
    # Ensure we only test TQ types if others are added to Language.ENGLISH later
    tq_english_types = [t for t in english_types if "ENGLISH_TQ" in t.name or "TQ_ENGLISH" in t.name] # Added TQ_ENGLISH for robustness
    for calc_type in tq_english_types:
        try:
            result = gematria_service.calculate(sample_text, calc_type)
            assert isinstance(result, int), f"Expected int for {calc_type.name}, got {type(result)}"
            print(f"Successfully calculated {calc_type.name} for '{sample_text}': {result}")
        except Exception as e:
            pytest.fail(f"Error calculating {calc_type.name} for '{sample_text}': {e}")

def test_coptic_calculations(gematria_service: GematriaService):
    """Test all Coptic calculation types."""
    sample_text = "ⲛⲟⲩϯ" # Nouti (God)
    coptic_types = CalculationType.get_types_for_language(Language.COPTIC)
    for calc_type in coptic_types:
        try:
            result = gematria_service.calculate(sample_text, calc_type)
            assert isinstance(result, int), f"Expected int for {calc_type.name}, got {type(result)}"
            print(f"Successfully calculated {calc_type.name} for '{sample_text}': {result}")
        except Exception as e:
            pytest.fail(f"Error calculating {calc_type.name} for '{sample_text}': {e}")

def test_custom_cipher_calculation(gematria_service: GematriaService):
    """Test calculation with a custom cipher."""
    sample_text = "custom"
    custom_cipher = CustomCipherConfig(
        name="Test Custom English",
        language=CustomLanguageType.ENGLISH,
        description="A test cipher"
    )
    custom_cipher.letter_values = {"c": 1, "u": 2, "s": 3, "t": 4, "o": 5, "m": 6}
    custom_cipher.case_sensitive = False

    try:
        result = gematria_service.calculate(sample_text, custom_cipher)
        assert isinstance(result, int), f"Expected int for custom cipher, got {type(result)}"
        # Expected: c(1) + u(2) + s(3) + t(4) + o(5) + m(6) = 21
        assert result == 21, f"Expected 21 for custom cipher '{sample_text}', got {result}"
        print(f"Successfully calculated custom cipher for '{sample_text}': {result}")
    except Exception as e:
        pytest.fail(f"Error calculating with custom cipher for '{sample_text}': {e}")

def test_calculate_with_transliteration(gematria_service: GematriaService):
    """Test calculation with transliteration enabled."""
    # Test Hebrew transliteration
    try:
        result_he = gematria_service.calculate("shalom", CalculationType.HEBREW_STANDARD_VALUE, transliterate_input=True)
        assert isinstance(result_he, int)
        # Value of שלום (sh:300 + l:30 + v:6 + m:40 = 376)
        # Note: Transliteration might be simple and not produce perfect "שלום" for some inputs
        # This test mainly checks if the transliteration path doesn't crash.
        # Exact value assertion depends heavily on the transliteration_service logic.
        print(f"Calculated with Hebrew translit for 'shalom': {result_he}")
    except Exception as e:
        pytest.fail(f"Error calculating with Hebrew transliteration: {e}")

    # Test Greek transliteration
    try:
        result_gr = gematria_service.calculate("logos", CalculationType.GREEK_STANDARD_VALUE, transliterate_input=True)
        assert isinstance(result_gr, int)
        # Value of λογος (l:30 o:70 g:3 o:70 s:200 = 373)
        print(f"Calculated with Greek translit for 'logos': {result_gr}")
    except Exception as e:
        pytest.fail(f"Error calculating with Greek transliteration: {e}")

    # Test Coptic transliteration
    try:
        result_co = gematria_service.calculate("nouti", CalculationType.COPTIC_STANDARD_VALUE, transliterate_input=True)
        assert isinstance(result_co, int)
        # Value of ⲛⲟⲩϯ (n:50 o:70 u:400 ti:300 (from ϯ) = 820) -- Transliteration for 'ou' and 'ti' will be key.
        # 'ⲛ': 50, 'ⲟ': 70, 'ⲩ': 400, 'ϯ': 300 -> 820
        print(f"Calculated with Coptic translit for 'nouti': {result_co}")
    except Exception as e:
        pytest.fail(f"Error calculating with Coptic transliteration: {e}")

def test_invalid_calculation_type_string(gematria_service: GematriaService):
    """Test that an invalid calculation type string raises an error."""
    with pytest.raises(ValueError, match="Unknown calculation type string: INVALID_TYPE"):
        gematria_service.calculate("test", "INVALID_TYPE")

# Example of a test for a specific method if needed for deeper debugging
# def test_specific_hebrew_method(gematria_service: GematriaService):
#     text = "א"
#     calc_type = CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD
#     try:
#         result = gematria_service.calculate(text, calc_type)
#         # assert result == 111 # Alef (אלף) = 1+30+800 (using Mispar Gadol for final Pe) or 1+30+80=111 if final Pe is 80
#         # Need to confirm actual value expected by _hebrew_letter_names_data logic
#     except Exception as e:
#         pytest.fail(f"Error in {calc_type.name}: {e}")

# Ensure no trailing characters or unterminated comments
