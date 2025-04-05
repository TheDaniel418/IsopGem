"""
Purpose: Demonstrates the implementation of file documentation and tracking rules

This file is part of the shared pillar and serves as a utility component.
It is responsible for testing the automatic file documentation and tracking system 
within the IsopGem application.

Key components:
- TestDocumentClass: Example class that demonstrates proper documentation
- demonstrate_file_tracking: Function that shows file tracking behavior

Dependencies:
- None: This is a standalone test file

Related files:
- docs/FILE_TRACKER.md: The file tracker that should be updated with this file
"""

import datetime
from typing import Dict, List, Optional


class TestDocumentClass:
    """
    Example class to demonstrate proper class-level documentation.
    
    This class has no real functionality but serves as an example of
    how to document classes according to project standards.
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a new TestDocumentClass instance.
        
        Args:
            name: Identifying name for this instance
            description: Optional description of this instance
        """
        self.name = name
        self.description = description
        self.creation_date = datetime.datetime.now()
    
    def get_info(self) -> Dict[str, any]:
        """
        Return information about this instance.
        
        Returns:
            Dictionary containing the instance information
        """
        return {
            "name": self.name,
            "description": self.description,
            "creation_date": self.creation_date
        }


def demonstrate_file_tracking(message: str = "Hello, file tracking!") -> str:
    """
    Demonstrate the file tracking functionality.
    
    Args:
        message: Message to include in the demonstration
        
    Returns:
        A string confirming the demonstration
    """
    print(f"Demonstrating file tracking: {message}")
    return f"Demonstration complete: {message}"


if __name__ == "__main__":
    # Create a test instance
    test_instance = TestDocumentClass(
        name="Test Document", 
        description="Testing file documentation and tracking"
    )
    
    # Demonstrate functionality
    print(test_instance.get_info())
    demonstrate_file_tracking()
    
    print("\nThis file should now be automatically added to docs/FILE_TRACKER.md") 