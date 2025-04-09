"""
Purpose: Provides a base class for implementing the Singleton pattern

This file is part of the shared pillar and serves as a service component.
It provides a base class that ensures only one instance of a service exists
throughout the application lifecycle.

Key components:
- SingletonService: Base class for implementing singleton pattern in services

Dependencies:
- None

Related files:
- shared/services/number_properties_service.py: Uses singleton pattern
- gematria/services/search_service.py: Uses singleton pattern
"""

from typing import Optional, Type, TypeVar

T = TypeVar("T", bound="SingletonService")


class SingletonService:
    """Base class for implementing the Singleton pattern.

    This class provides a base implementation for services that should only
    have one instance throughout the application lifecycle. It implements
    the Singleton pattern using class variables and class methods.

    Example:
        class MyService(SingletonService):
            def __init__(self):
                super().__init__()
                self.data = {}

            @classmethod
            def get_instance(cls) -> 'MyService':
                return super().get_instance()
    """

    _instance: Optional[T] = None

    def __init__(self) -> None:
        """Initialize the singleton service."""
        if self.__class__._instance is not None:
            raise RuntimeError(
                f"Attempt to create second instance of {self.__class__.__name__}"
            )
        self.__class__._instance = self

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        """Get the singleton instance of the service.

        Returns:
            The singleton instance

        Raises:
            RuntimeError: If the service has not been initialized
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def has_instance(cls) -> bool:
        """Check if the singleton instance exists.

        Returns:
            True if the instance exists, False otherwise
        """
        return cls._instance is not None
