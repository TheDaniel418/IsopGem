"""Custom Cipher Service.

This module provides services for managing custom gematria ciphers.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType


class CustomCipherService:
    """Service for managing custom gematria ciphers."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the custom cipher service.

        Args:
            data_dir: Optional directory path for storing cipher configurations
        """
        # Default data directory is under the user's home directory
        if data_dir is None:
            self.data_dir = os.path.join(
                os.path.expanduser("~"), ".isopgem", "custom_ciphers"
            )
        else:
            self.data_dir = data_dir

        # Ensure the directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Load all custom ciphers
        self._ciphers: Dict[str, CustomCipherConfig] = {}
        self._load_ciphers()

    def _load_ciphers(self) -> None:
        """Load all custom cipher configurations from the data directory."""
        if not os.path.exists(self.data_dir):
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                try:
                    file_path = os.path.join(self.data_dir, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cipher = CustomCipherConfig.from_dict(data)
                        self._ciphers[cipher.id] = cipher
                        logger.debug(f"Loaded custom cipher: {cipher.name}")
                except Exception as e:
                    logger.error(f"Error loading custom cipher {filename}: {e}")

    def get_ciphers(
        self, language: Optional[Union[LanguageType, str]] = None
    ) -> List[CustomCipherConfig]:
        """Get all custom ciphers or filter by language.

        Args:
            language: Optional language to filter by

        Returns:
            List of custom cipher configurations
        """
        if language is None:
            return list(self._ciphers.values())

        lang_enum = (
            language if isinstance(language, LanguageType) else LanguageType(language)
        )
        return [c for c in self._ciphers.values() if c.language == lang_enum]

    def get_cipher(self, cipher_id: str) -> Optional[CustomCipherConfig]:
        """Get a specific custom cipher by ID.

        Args:
            cipher_id: ID of the cipher to retrieve

        Returns:
            Custom cipher configuration or None if not found
        """
        return self._ciphers.get(cipher_id)

    def save_cipher(self, cipher: CustomCipherConfig) -> bool:
        """Save a custom cipher configuration.

        Args:
            cipher: Custom cipher configuration to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify the cipher is valid
            if not cipher.is_valid():
                logger.error(f"Invalid cipher configuration: {cipher.name}")
                return False

            # Generate file path
            file_path = os.path.join(self.data_dir, f"{cipher.id}.json")

            # Save to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cipher.to_dict(), f, indent=2, ensure_ascii=False)

            # Update in-memory collection
            self._ciphers[cipher.id] = cipher
            logger.debug(f"Saved custom cipher: {cipher.name}")
            return True

        except Exception as e:
            logger.error(f"Error saving custom cipher {cipher.name}: {e}")
            return False

    def delete_cipher(self, cipher_id: str) -> bool:
        """Delete a custom cipher configuration.

        Args:
            cipher_id: ID of the cipher to delete

        Returns:
            True if successful, False otherwise
        """
        if cipher_id not in self._ciphers:
            logger.warning(f"Custom cipher not found for deletion: {cipher_id}")
            return False

        try:
            # Remove file
            file_path = os.path.join(self.data_dir, f"{cipher_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

            # Remove from in-memory collection
            name = self._ciphers[cipher_id].name
            del self._ciphers[cipher_id]
            logger.debug(f"Deleted custom cipher: {name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting custom cipher {cipher_id}: {e}")
            return False

    def create_default_templates(self) -> List[str]:
        """Create default template ciphers for each language.

        Returns:
            List of IDs for the created templates
        """
        template_ids = []

        # Hebrew template with standard values
        hebrew_template = CustomCipherConfig(
            "Hebrew Template",
            LanguageType.HEBREW,
            "Template with Hebrew standard values",
        )
        hebrew_template.letter_values = {
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
        }

        # Greek template with standard values
        greek_template = CustomCipherConfig(
            "Greek Template", LanguageType.GREEK, "Template with Greek standard values"
        )
        greek_template.letter_values = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 10,
            "κ": 20,
            "λ": 30,
            "μ": 40,
            "ν": 50,
            "ξ": 60,
            "ο": 70,
            "π": 80,
            "ρ": 100,
            "σ": 200,
            "τ": 300,
            "υ": 400,
            "φ": 500,
            "χ": 600,
            "ψ": 700,
            "ω": 800,
        }

        # English template with standard values
        english_template = CustomCipherConfig(
            "English Template",
            LanguageType.ENGLISH,
            "Template with English A=1 through Z=26",
        )
        values = {}
        for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            values[letter] = i + 1
        english_template.letter_values = values

        # Save templates
        templates = [hebrew_template, greek_template, english_template]
        for template in templates:
            if self.save_cipher(template):
                template_ids.append(template.id)

        return template_ids

    def get_methods_for_language(
        self, language: Union[str, "LanguageType", Any]
    ) -> List[CustomCipherConfig]:
        """Get all custom cipher methods for a specific language.

        Args:
            language: Language to get methods for (can be string, enum, or Language enum)

        Returns:
            List of custom cipher configurations for the language
        """
        # Convert from models.calculation_type.Language to LanguageType if needed
        if hasattr(language, "value") and isinstance(language.value, str):
            lang_str = language.value.lower()
        elif isinstance(language, str):
            lang_str = language.lower()
        else:
            # Default to empty list for unknown language type
            return []

        # Map Language enum to LanguageType
        lang_map = {
            "hebrew": LanguageType.HEBREW,
            "greek": LanguageType.GREEK,
            "english": LanguageType.ENGLISH,
        }

        if lang_str in lang_map:
            return self.get_ciphers(lang_map[lang_str])

        return []
