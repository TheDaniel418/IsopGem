"""Test script for checking the calculation database functionality."""

import os
import shutil
from pathlib import Path

from gematria.repositories.tag_repository import TagRepository
from gematria.repositories.calculation_repository import CalculationRepository
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.models.tag import Tag
from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType

def test_tag_repository():
    """Test the TagRepository functionality."""
    print("\n--- Testing TagRepository ---")
    
    # Create a temporary directory for testing
    test_dir = Path("./test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Initialize repository
        repo = TagRepository(str(test_dir))
        print("TagRepository initialized successfully")
        
        # Create a tag
        tag = Tag(name="Test Tag", color="#ff0000")
        result = repo.create_tag(tag)
        print(f"Create tag result: {result}")
        
        # Verify tag was created
        all_tags = repo.get_all_tags()
        print(f"Total tags: {len(all_tags)}")
        
        if all_tags:
            # Get the first tag
            first_tag = all_tags[0]
            print(f"First tag: {first_tag.name}, ID: {first_tag.id}")
            
            # Update the tag
            first_tag.name = "Updated Tag"
            result = repo.update_tag(first_tag)
            print(f"Update tag result: {result}")
            
            # Verify update
            updated_tag = repo.get_tag(first_tag.id)
            print(f"Updated tag name: {updated_tag.name}")
            
            # Test delete
            result = repo.delete_tag(first_tag.id)
            print(f"Delete tag result: {result}")
            
            # Verify deletion
            all_tags_after = repo.get_all_tags()
            print(f"Total tags after deletion: {len(all_tags_after)}")
        
        # Test default tags
        default_tags = repo.create_default_tags()
        print(f"Created {len(default_tags)} default tags")
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir)
        print("Test cleanup completed")

def test_calculation_repository():
    """Test the CalculationRepository functionality."""
    print("\n--- Testing CalculationRepository ---")
    
    # Create a temporary directory for testing
    test_dir = Path("./test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Initialize repository
        repo = CalculationRepository(str(test_dir))
        print("CalculationRepository initialized successfully")
        
        # Create a calculation result
        calc = CalculationResult(
            input_text="Test",
            calculation_type=CalculationType.MISPAR_HECHRACHI,
            result_value=123,
            notes="Test notes"
        )
        result = repo.save_calculation(calc)
        print(f"Save calculation result: {result}")
        
        # Verify calculation was saved
        all_calcs = repo.get_all_calculations()
        print(f"Total calculations: {len(all_calcs)}")
        
        if all_calcs:
            # Get the first calculation
            first_calc = all_calcs[0]
            print(f"First calculation: {first_calc.input_text}, Value: {first_calc.result_value}")
            
            # Update the calculation
            first_calc.notes = "Updated notes"
            result = repo.save_calculation(first_calc)
            print(f"Update calculation result: {result}")
            
            # Verify update
            updated_calc = repo.get_calculation(first_calc.id)
            print(f"Updated calculation notes: {updated_calc.notes}")
            
            # Test delete
            result = repo.delete_calculation(first_calc.id)
            print(f"Delete calculation result: {result}")
            
            # Verify deletion
            all_calcs_after = repo.get_all_calculations()
            print(f"Total calculations after deletion: {len(all_calcs_after)}")
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir)
        print("Test cleanup completed")

def test_database_service():
    """Test the CalculationDatabaseService functionality."""
    print("\n--- Testing CalculationDatabaseService ---")
    
    # Create a temporary directory for testing
    test_dir = Path("./test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Initialize service
        service = CalculationDatabaseService(str(test_dir))
        print("CalculationDatabaseService initialized successfully")
        
        # Check default tags were created
        tags = service.get_all_tags()
        print(f"Default tags created: {len(tags)}")
        
        # Create a calculation
        calc = CalculationResult(
            input_text="Test",
            calculation_type=CalculationType.MISPAR_HECHRACHI,
            result_value=123,
            notes="Test notes"
        )
        result = service.save_calculation(calc)
        print(f"Save calculation result: {result}")
        
        # Add tag to calculation
        if tags and result:
            result = service.add_tag_to_calculation(calc.id, tags[0].id)
            print(f"Add tag to calculation result: {result}")
            
            # Get calculation and verify tag
            updated_calc = service.get_calculation(calc.id)
            print(f"Tags on calculation: {len(updated_calc.tags)}")
            
            # Test favorite toggle
            result = service.toggle_favorite_calculation(calc.id)
            print(f"Toggle favorite result: {result}")
            
            # Verify favorite status
            updated_calc = service.get_calculation(calc.id)
            print(f"Favorite status: {updated_calc.favorite}")
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir)
        print("Test cleanup completed")

if __name__ == "__main__":
    test_tag_repository()
    test_calculation_repository()
    test_database_service()
    print("\nAll tests completed successfully!") 