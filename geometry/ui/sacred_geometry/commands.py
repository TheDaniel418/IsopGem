"""Command system for the Sacred Geometry Explorer.

This module contains the command system for the Sacred Geometry Explorer,
which provides undo/redo functionality for all operations.
"""

from copy import deepcopy
from typing import Any, List, Optional

from loguru import logger

from geometry.ui.sacred_geometry.model import Circle, GeometricObject, Line


class GeometryCommand:
    """Base class for all geometry commands.

    This class provides the interface for commands that can be executed,
    undone, and redone.
    """

    def __init__(self, name: str) -> None:
        """Initialize a geometry command.

        Args:
            name: Name of the command
        """
        self.name = name

    def execute(self) -> None:
        """Execute the command."""
        pass

    def undo(self) -> None:
        """Undo the command."""
        pass

    def redo(self) -> None:
        """Redo the command."""
        pass

    def __str__(self) -> str:
        """Get string representation of the command."""
        return self.name


class CommandHistory:
    """History of executed commands.

    This class manages the history of executed commands and provides
    undo/redo functionality.
    """

    def __init__(self) -> None:
        """Initialize the command history."""
        self.history: List[GeometryCommand] = []
        self.current_index = -1

    def execute(self, command: GeometryCommand) -> None:
        """Execute a command and add it to the history.

        Args:
            command: Command to execute
        """
        # Execute the command
        command.execute()

        # If we're not at the end of the history, remove all commands after the current index
        if self.current_index < len(self.history) - 1:
            self.history = self.history[: self.current_index + 1]

        # Add the command to the history
        self.history.append(command)
        self.current_index = len(self.history) - 1

        logger.debug(f"Executed command: {command}")

    def undo(self) -> bool:
        """Undo the last executed command.

        Returns:
            True if a command was undone, False otherwise
        """
        if self.current_index >= 0:
            # Undo the current command
            self.history[self.current_index].undo()
            self.current_index -= 1
            logger.debug(f"Undid command: {self.history[self.current_index + 1]}")
            return True
        return False

    def redo(self) -> bool:
        """Redo the last undone command.

        Returns:
            True if a command was redone, False otherwise
        """
        if self.current_index < len(self.history) - 1:
            # Redo the next command
            self.current_index += 1
            self.history[self.current_index].redo()
            logger.debug(f"Redid command: {self.history[self.current_index]}")
            return True
        return False

    def can_undo(self) -> bool:
        """Check if undo is possible.

        Returns:
            True if undo is possible, False otherwise
        """
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is possible.

        Returns:
            True if redo is possible, False otherwise
        """
        return self.current_index < len(self.history) - 1

    def get_undo_name(self) -> str:
        """Get the name of the command that would be undone.

        Returns:
            Name of the command that would be undone, or an empty string if none
        """
        if self.can_undo():
            return self.history[self.current_index].name
        return ""

    def get_redo_name(self) -> str:
        """Get the name of the command that would be redone.

        Returns:
            Name of the command that would be redone, or an empty string if none
        """
        if self.can_redo():
            return self.history[self.current_index + 1].name
        return ""

    def clear(self) -> None:
        """Clear the command history."""
        self.history = []
        self.current_index = -1
        logger.debug("Command history cleared")


class CreateObjectCommand(GeometryCommand):
    """Command for creating a geometric object."""

    def __init__(self, explorer, obj: GeometricObject) -> None:
        """Initialize a create object command.

        Args:
            explorer: Explorer instance
            obj: Object to create
        """
        super().__init__(f"Create {obj.__class__.__name__}")
        self.explorer = explorer
        self.obj = deepcopy(obj)  # Store a copy of the object
        self.created = False

    def execute(self) -> None:
        """Execute the command."""
        # Add object to canvas
        if hasattr(self.explorer, "canvas") and self.explorer.canvas:
            # Check if object already exists
            for existing_obj in self.explorer.canvas.objects:
                if existing_obj.id == self.obj.id:
                    # Object already exists, nothing to do
                    self.created = True
                    return

            # Add object to canvas
            self.explorer.canvas.add_object(self.obj)
            self.created = True
            logger.debug(f"Created {self.obj.__class__.__name__} with ID {self.obj.id}")

    def undo(self) -> None:
        """Undo the command."""
        if self.created and hasattr(self.explorer, "canvas") and self.explorer.canvas:
            # Remove object from canvas
            for obj in self.explorer.canvas.objects:
                if obj.id == self.obj.id:
                    self.explorer.canvas.remove_object(obj)
                    self.created = False
                    logger.debug(
                        f"Undid creation of {self.obj.__class__.__name__} with ID {self.obj.id}"
                    )
                    break

    def redo(self) -> None:
        """Redo the command."""
        # Just execute again
        self.execute()


class DeleteObjectCommand(GeometryCommand):
    """Command for deleting a geometric object."""

    def __init__(self, explorer, obj: GeometricObject) -> None:
        """Initialize a delete object command.

        Args:
            explorer: Explorer instance
            obj: Object to delete
        """
        super().__init__(f"Delete {obj.__class__.__name__}")
        self.explorer = explorer
        self.obj = deepcopy(obj)  # Store a copy of the object
        self.deleted = False

    def execute(self) -> None:
        """Execute the command."""
        # Remove object from canvas
        if hasattr(self.explorer, "canvas") and self.explorer.canvas:
            # Find object by ID
            for obj in self.explorer.canvas.objects:
                if obj.id == self.obj.id:
                    # Remove object from canvas
                    self.explorer.canvas.remove_object(obj)
                    self.deleted = True
                    logger.debug(
                        f"Deleted {self.obj.__class__.__name__} with ID {self.obj.id}"
                    )
                    break

    def undo(self) -> None:
        """Undo the command."""
        if self.deleted and hasattr(self.explorer, "canvas") and self.explorer.canvas:
            # Add object back to canvas
            self.explorer.canvas.add_object(self.obj)
            self.deleted = False
            logger.debug(
                f"Undid deletion of {self.obj.__class__.__name__} with ID {self.obj.id}"
            )

    def redo(self) -> None:
        """Redo the command."""
        # Just execute again
        self.execute()


class ModifyObjectCommand(GeometryCommand):
    """Command for modifying a geometric object."""

    def __init__(
        self,
        explorer,
        obj: GeometricObject,
        property_name: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Initialize a modify object command.

        Args:
            explorer: Explorer instance
            obj: Object to modify
            property_name: Name of the property to modify
            old_value: Old value of the property
            new_value: New value of the property
        """
        super().__init__(f"Modify {obj.__class__.__name__}.{property_name}")
        self.explorer = explorer
        self.obj_id = obj.id
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.modified = False

    def execute(self) -> None:
        """Execute the command."""
        # Find object by ID
        obj = self._find_object()
        if obj:
            # Set property value
            self._set_property_value(obj, self.property_name, self.new_value)
            self.modified = True
            logger.debug(
                f"Modified {obj.__class__.__name__}.{self.property_name} from {self.old_value} to {self.new_value}"
            )

    def undo(self) -> None:
        """Undo the command."""
        if self.modified:
            # Find object by ID
            obj = self._find_object()
            if obj:
                # Restore old value
                self._set_property_value(obj, self.property_name, self.old_value)
                logger.debug(
                    f"Undid modification of {obj.__class__.__name__}.{self.property_name} back to {self.old_value}"
                )

    def redo(self) -> None:
        """Redo the command."""
        # Just execute again
        self.execute()

    def _find_object(self) -> Optional[GeometricObject]:
        """Find the object by ID.

        Returns:
            Object with the given ID, or None if not found
        """
        if hasattr(self.explorer, "canvas") and self.explorer.canvas:
            for obj in self.explorer.canvas.objects:
                if obj.id == self.obj_id:
                    return obj
        return None

    def _set_property_value(
        self, obj: GeometricObject, property_name: str, value: Any
    ) -> None:
        """Set a property value on an object.

        Args:
            obj: Object to modify
            property_name: Name of the property to modify
            value: New value for the property
        """
        logger.debug(
            f"DEBUG: ModifyObjectCommand._set_property_value({obj.__class__.__name__} {obj.id}, {property_name}, {value})"
        )

        # For Line objects, store original endpoint values for debugging
        if isinstance(obj, Line):
            orig_x1, orig_y1 = obj.x1, obj.y1
            orig_x2, orig_y2 = obj.x2, obj.y2
            logger.debug(
                f"DEBUG: Before property change: P1=({orig_x1}, {orig_y1}), P2=({orig_x2}, {orig_y2})"
            )

        if "." in property_name:
            # Handle nested properties (e.g., 'center.x')
            parts = property_name.split(".")
            parent_obj = obj
            for part in parts[:-1]:
                if hasattr(parent_obj, part):
                    parent_obj = getattr(parent_obj, part)
                    logger.debug(
                        f"  Navigating to nested attribute {part} -> {parent_obj.__class__.__name__}"
                    )
                else:
                    logger.warning(
                        f"Object {obj.__class__.__name__} has no attribute {part}"
                    )
                    return

            # Set property on parent object
            if hasattr(parent_obj, parts[-1]):
                old_value = getattr(parent_obj, parts[-1])
                logger.debug(
                    f"  Setting nested property {parts[-1]} from {old_value} to {value}"
                )
                setattr(parent_obj, parts[-1], value)

                # Special handling for Circle center point properties
                if isinstance(obj, Circle) and parts[0] == "center":
                    logger.debug(
                        "  Special handling for Circle center property change"
                    )
            else:
                logger.warning(
                    f"Object {parent_obj.__class__.__name__} has no attribute {parts[-1]}"
                )
        else:
            # Set property directly on object
            if hasattr(obj, property_name):
                old_value = getattr(obj, property_name)
                logger.debug(
                    f"  Setting direct property {property_name} from {old_value} to {value}"
                )

                # For Line objects, check if we're modifying an endpoint property
                if isinstance(obj, Line) and property_name.startswith("endpoint"):
                    logger.debug(
                        f"DEBUG: Modifying Line endpoint property {property_name}"
                    )

                    # Determine which endpoint we're modifying
                    endpoint_num = int(
                        property_name[8:9]
                    )  # Extract the endpoint number (1 or 2)
                    coord = property_name[-1]  # Extract the coordinate (x or y)

                    # Store the original values of the other endpoint
                    if endpoint_num == 1:
                        other_x, other_y = obj.x2, obj.y2
                    else:  # endpoint_num == 2
                        other_x, other_y = obj.x1, obj.y1

                    # Set the property
                    setattr(obj, property_name, value)

                    # Verify the other endpoint hasn't changed
                    if endpoint_num == 1 and (obj.x2 != other_x or obj.y2 != other_y):
                        logger.error(
                            f"ERROR: Endpoint 2 changed unexpectedly from ({other_x}, {other_y}) to ({obj.x2}, {obj.y2})"
                        )
                        # Force it back to the original value
                        obj.x2 = other_x
                        obj.y2 = other_y
                    elif endpoint_num == 2 and (obj.x1 != other_x or obj.y1 != other_y):
                        logger.error(
                            f"ERROR: Endpoint 1 changed unexpectedly from ({other_x}, {other_y}) to ({obj.x1}, {obj.y1})"
                        )
                        # Force it back to the original value
                        obj.x1 = other_x
                        obj.y1 = other_y
                else:
                    # For non-endpoint properties, just set the value normally
                    setattr(obj, property_name, value)
            else:
                logger.warning(
                    f"Object {obj.__class__.__name__} has no attribute {property_name}"
                )

        # For Line objects, log the endpoint values after the change
        if isinstance(obj, Line):
            logger.debug(
                f"DEBUG: After property change: P1=({obj.x1}, {obj.y1}), P2=({obj.x2}, {obj.y2})"
            )

            # Check if both endpoints changed
            if obj.x1 != orig_x1 or obj.y1 != orig_y1:
                if obj.x2 != orig_x2 or obj.y2 != orig_y2:
                    logger.warning(
                        "WARNING: Both endpoints changed during property update!"
                    )

        # Update object on canvas
        if hasattr(self.explorer, "canvas") and self.explorer.canvas:
            logger.debug(
                f"  Updating object {obj.__class__.__name__} {obj.id} on canvas"
            )
            self.explorer.canvas.update_object(obj)


class CompoundCommand(GeometryCommand):
    """Command that combines multiple commands into one."""

    def __init__(self, name: str, commands: List[GeometryCommand]) -> None:
        """Initialize a compound command.

        Args:
            name: Name of the command
            commands: List of commands to execute
        """
        super().__init__(name)
        self.commands = commands

    def execute(self) -> None:
        """Execute the command."""
        for command in self.commands:
            command.execute()

    def undo(self) -> None:
        """Undo the command."""
        # Undo in reverse order
        for command in reversed(self.commands):
            command.undo()

    def redo(self) -> None:
        """Redo the command."""
        for command in self.commands:
            command.redo()
