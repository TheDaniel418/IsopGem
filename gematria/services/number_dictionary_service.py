"""
Service for managing the Number Dictionary functionality.

This service coordinates between the repository layer and UI components,
providing a clean interface for number note operations and integrating
with other services for number properties and quadset analysis.
"""

import os
from typing import List, Optional

from loguru import logger

from gematria.models.number_note import NumberNote
from gematria.repositories.number_note_repository import NumberNoteRepository
from shared.services.number_properties_service import NumberPropertiesService
from tq.services.tq_grid_service import TQGridService


class NumberDictionaryService:
    """Service for managing Number Dictionary operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize the service.
        
        Args:
            db_path: Path to the database file. If None, uses default location.
        """
        if db_path is None:
            # Use default database path in the data directory
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "number_dictionary.db")
        
        self.repository = NumberNoteRepository(db_path)
        self.number_properties_service = NumberPropertiesService.get_instance()
        self.tq_grid_service = TQGridService.get_instance()
        
        logger.debug(f"NumberDictionaryService initialized with database: {db_path}")
    
    def get_or_create_note(self, number: int) -> NumberNote:
        """Get an existing note for a number or create a new one.
        
        Args:
            number: The number to get/create a note for
            
        Returns:
            The note for the number
        """
        note = self.repository.get_note_by_number(number)
        if note is None:
            # Create a new note with default title
            note = NumberNote(
                number=number,
                title=f"Notes for {number}",
                content=""
            )
        return note
    
    def save_note(self, note: NumberNote) -> NumberNote:
        """Save a note to the database.
        
        Args:
            note: The note to save
            
        Returns:
            The saved note with updated timestamps
        """
        return self.repository.save_note(note)
    
    def delete_note(self, number: int) -> bool:
        """Delete a note for a number.
        
        Args:
            number: The number whose note to delete
            
        Returns:
            True if deleted, False otherwise
        """
        return self.repository.delete_note(number)
    
    def get_number_properties(self, number: int) -> dict:
        """Get comprehensive properties for a number.
        
        Args:
            number: The number to analyze
            
        Returns:
            Dictionary of number properties
        """
        return self.number_properties_service.get_number_properties(number)
    
    def get_quadset_analysis(self, number: int) -> dict:
        """Get quadset analysis for a number.
        
        Args:
            number: The number to analyze
            
        Returns:
            Dictionary containing quadset analysis
        """
        try:
            # Get the quadset properties from the number properties service
            quadset_props = self.number_properties_service.get_quadset_properties(number)
            
            # Get the current TQ grid for context
            current_grid = self.tq_grid_service.get_current_grid()
            
            # Combine the information
            analysis = {
                "base_number": number,
                "quadset_properties": quadset_props,
                "current_tq_grid": {
                    "base": current_grid.base_number,
                    "conrune": current_grid.conrune,
                    "reversal": current_grid.reversal,
                    "reversal_conrune": current_grid.reversal_conrune
                }
            }
            
            # Calculate the other numbers in the quadset
            if "conrune" in quadset_props:
                analysis["conrune"] = quadset_props["conrune"]
            if "reversal" in quadset_props:
                analysis["reversal"] = quadset_props["reversal"]
            if "reversal_conrune" in quadset_props:
                analysis["reversal_conrune"] = quadset_props["reversal_conrune"]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting quadset analysis for {number}: {e}")
            return {
                "base_number": number,
                "error": str(e)
            }
    
    def search_notes(self, query: str) -> List[NumberNote]:
        """Search notes by title or content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching notes
        """
        return self.repository.search_notes(query)
    
    def get_all_notes(self) -> List[NumberNote]:
        """Get all notes.
        
        Returns:
            List of all notes
        """
        return self.repository.get_all_notes()
    
    def get_linked_numbers(self, number: int) -> List[int]:
        """Get numbers that are linked to the given number.
        
        Args:
            number: The number to find links for
            
        Returns:
            List of linked numbers
        """
        note = self.repository.get_note_by_number(number)
        if note:
            return note.linked_numbers
        return []
    
    def add_number_link(self, from_number: int, to_number: int) -> bool:
        """Add a link from one number to another.
        
        Args:
            from_number: The source number
            to_number: The target number
            
        Returns:
            True if link was added, False otherwise
        """
        try:
            note = self.get_or_create_note(from_number)
            if to_number not in note.linked_numbers:
                note.linked_numbers.append(to_number)
                self.save_note(note)
                logger.debug(f"Added link from {from_number} to {to_number}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding number link: {e}")
            return False
    
    def remove_number_link(self, from_number: int, to_number: int) -> bool:
        """Remove a link from one number to another.
        
        Args:
            from_number: The source number
            to_number: The target number to unlink
            
        Returns:
            True if link was removed, False otherwise
        """
        try:
            note = self.repository.get_note_by_number(from_number)
            if note and to_number in note.linked_numbers:
                note.linked_numbers.remove(to_number)
                self.save_note(note)
                logger.debug(f"Removed link from {from_number} to {to_number}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing number link: {e}")
            return False 