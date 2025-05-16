"""
Defines the Marker class for the Stonehenge Eclipse Predictor simulation.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-07-29
Dependencies: None
"""

class Marker:
    """
    Represents a single marker (Sun, Moon, Node) in the Stonehenge simulation.

    Attributes:
        name (str): The name of the marker (e.g., 'S', 'M', 'N', 'N_prime').
        current_position (int): The current position of the marker on the 
                                56-hole circle (indexed 0-55).
    """
    def __init__(self, name: str, initial_position: int):
        """
        Initializes a new Marker.

        Args:
            name (str): The name of the marker.
            initial_position (int): The starting position of the marker (0-55).
        
        Raises:
            ValueError: If initial_position is outside the valid range of 0-55.
        """
        if not 0 <= initial_position < 56:
            raise ValueError("Initial position must be between 0 and 55.")
            
        self.name: str = name
        self.current_position: int = initial_position

    def __repr__(self) -> str:
        """
        Returns a string representation of the Marker.

        Returns:
            str: A string like "Marker(Name: S, Position: 0)".
        """
        return f"Marker(Name: {self.name}, Position: {self.current_position})"

    def move(self, steps: int, num_holes: int = 56, clockwise: bool = False) -> None:
        """
        Moves the marker a specified number of steps around the circle.

        Args:
            steps (int): The number of steps to move.
            num_holes (int): The total number of holes in the circle (default 56).
            clockwise (bool): If True, moves clockwise (decreasing position index);
                              If False (default), moves anticlockwise (increasing position index).
        """
        if clockwise:
            self.current_position = (self.current_position - steps + num_holes) % num_holes
        else:
            self.current_position = (self.current_position + steps) % num_holes

# Example Usage (can be removed or moved to a test file):
if __name__ == '__main__':
    sun_marker = Marker(name="S", initial_position=0)
    print(sun_marker)
    sun_marker.move(steps=2)
    print(f"Moved 2 steps anticlockwise: {sun_marker}")
    sun_marker.move(steps=3, clockwise=True)
    print(f"Moved 3 steps clockwise: {sun_marker}")

    moon_marker = Marker(name="M", initial_position=28)
    print(moon_marker)

    # Test invalid position
    try:
        invalid_marker = Marker(name="Invalid", initial_position=60)
    except ValueError as e:
        print(f"Error creating marker: {e}") 