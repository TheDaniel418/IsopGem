"""
Purpose: Provides type hints for Tag model to break circular imports.

This file is only for type definitions to support type checking and prevent
circular import issues. It doesn't contain any actual implementations.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from gematria.models.tag import Tag

# Type aliases used by SQLiteTagRepository and other files
TagType = Union[Dict[str, Any], "Tag"]
TagList = List["Tag"]
