"""Custom Cipher Configuration model.

This module defines the data model for custom gematria cipher configurations.
"""

import hashlib
import re
from enum import Enum
from typing import Dict, Optional, Any, Set

from pydantic import BaseModel, Field, validator


class LanguageType(str, Enum):
    """Supported languages for custom ciphers."""
    
    HEBREW = "hebrew"
    GREEK = "greek"
    ENGLISH = "english"


class CustomCipherConfig(BaseModel):
    """Configuration for a custom gematria cipher."""
    
    id: str = Field(
        default="",
        description="Unique identifier for the cipher configuration"
    )
    name: str = Field(
        description="Display name for the cipher"
    )
    language: LanguageType = Field(
        description="Language this cipher applies to"
    )
    description: str = Field(
        default="",
        description="Description of the cipher and its significance"
    )
    letter_values: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of letters to their numerical values"
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether letter case matters for this cipher"
    )
    use_final_forms: bool = Field(
        default=False,
        description="Whether to use special values for Hebrew final forms"
    )
    
    class Config:
        """Pydantic model configuration."""
        
        arbitrary_types_allowed = True
    
    def __init__(self, name: str, language: LanguageType, description: str = "") -> None:
        """Initialize a new custom cipher configuration.
        
        Args:
            name: Name for the cipher
            language: Language type for this cipher
            description: Optional description
        """
        # Generate ID based on name
        cipher_id = self._generate_id(name)
        
        # Initialize with default empty letter values
        super().__init__(
            id=cipher_id,
            name=name,
            language=language,
            description=description,
            letter_values={},
            case_sensitive=False,
            use_final_forms=False
        )
    
    def _generate_id(self, name: str) -> str:
        """Generate a unique ID based on the cipher name.
        
        Args:
            name: Cipher name
            
        Returns:
            Unique ID string
        """
        # Create a slug from the name
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[\s-]+', '_', slug)
        
        # Add a hash for uniqueness
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        
        return f"{slug}_{name_hash}"
    
    def is_valid(self) -> bool:
        """Check if the cipher configuration is valid.
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not self.name or not self.id:
            return False
            
        # Check for at least one letter value
        if not self.letter_values:
            return False
            
        # Check language-specific requirements
        if self.language == LanguageType.HEBREW:
            # Hebrew should have values for primary letters
            hebrew_primary = {'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 
                             'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 
                             'ק', 'ר', 'ש', 'ת'}
            # Check if at least half of the primary letters have values
            found = set(self.letter_values.keys()) & hebrew_primary
            if len(found) < len(hebrew_primary) / 2:
                return False
                
        elif self.language == LanguageType.GREEK:
            # Greek should have values for primary letters
            greek_primary = {'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 
                            'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 
                            'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'}
            # Check if at least half of the primary letters have values
            found = set(self.letter_values.keys()) & greek_primary
            if len(found) < len(greek_primary) / 2:
                return False
                
        elif self.language == LanguageType.ENGLISH:
            # English should have values for primary letters
            english_primary = set("abcdefghijklmnopqrstuvwxyz")
            # Allow either lowercase or uppercase or both
            english_upper = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            
            found_lower = set(self.letter_values.keys()) & english_primary
            found_upper = set(self.letter_values.keys()) & english_upper
            
            # Check if we have at least half of either lowercase or uppercase
            if (len(found_lower) < len(english_primary) / 2 and 
                len(found_upper) < len(english_upper) / 2):
                return False
                
        # All checks passed
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomCipherConfig':
        """Create a CustomCipherConfig from a dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            New CustomCipherConfig instance
        """
        # Convert language string to enum if needed
        if isinstance(data.get('language'), str):
            data['language'] = LanguageType(data['language'])
            
        # Create instance with required fields
        instance = cls(
            name=data['name'],
            language=data['language'],
            description=data.get('description', '')
        )
        
        # Set other fields from data
        instance.id = data.get('id', instance.id)
        instance.letter_values = data.get('letter_values', {})
        instance.case_sensitive = data.get('case_sensitive', False)
        instance.use_final_forms = data.get('use_final_forms', False)
            
        return instance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        data: Dict[str, Any] = self.dict()
        
        # Convert enum to string
        if isinstance(data['language'], LanguageType):
            data['language'] = data['language'].value
            
        return data
    
    def get_empty_template(self) -> Dict[str, int]:
        """Get an empty template with all relevant letters for the language.
        
        Returns:
            Dictionary mapping letters to zero values
        """
        template = {}
        
        if self.language == LanguageType.HEBREW:
            # Regular Hebrew letters
            letters = [
                'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט',
                'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ',
                'ק', 'ר', 'ש', 'ת'
            ]
            
            # Add final forms if needed
            if self.use_final_forms:
                letters.extend(['ך', 'ם', 'ן', 'ף', 'ץ'])
                
            for letter in letters:
                template[letter] = 0
                
        elif self.language == LanguageType.GREEK:
            letters = [
                'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι',
                'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ',
                'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'
            ]
            
            for letter in letters:
                template[letter] = 0
                
        elif self.language == LanguageType.ENGLISH:
            # Add lowercase letters
            for letter in "abcdefghijklmnopqrstuvwxyz":
                template[letter] = 0
                
            # Add uppercase if case-sensitive
            if self.case_sensitive:
                for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    template[letter] = 0
                    
        return template
    
    def __str__(self) -> str:
        """String representation of the cipher.
        
        Returns:
            String representation
        """
        return f"{self.name} ({self.language.name})" 