"""Shared repositories package initialization."""

from shared.repositories.database import Database

# Remove circular imports
# from shared.repositories.sqlite_calculation_repository import SQLiteCalculationRepository
# from shared.repositories.sqlite_tag_repository import SQLiteTagRepository

# Only include non-circular imports
__all__ = ["Database"]
# "SQLiteCalculationRepository" and "SQLiteTagRepository" removed to avoid circular dependencies
