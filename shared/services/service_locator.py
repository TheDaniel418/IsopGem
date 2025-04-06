"""
Purpose: Implements the Service Locator pattern for dependency management

This file is part of the shared services layer, providing a central registry
for all application services. It enables loose coupling between components
by allowing them to retrieve service instances without directly constructing them.

Key components:
- ServiceLocator: A static class that maintains a registry of services

Dependencies:
- Python typing: For type hint annotations

Related files:
- All service implementations that need to be registered and accessed
"""

from typing import Dict, Type, TypeVar, Any, Optional, cast

T = TypeVar('T')


class ServiceLocator:
    """
    Service locator for managing application-wide services.
    Provides a central registry to register, retrieve, and manage service instances.
    """
    
    _services: Dict[Type, Any] = {}
    
    @classmethod
    def register(cls, service_type: Type[T], instance: T) -> None:
        """
        Register a service instance with the locator.
        
        Args:
            service_type: The type/class of the service
            instance: The service instance to register
        """
        cls._services[service_type] = instance
    
    @classmethod
    def get(cls, service_type: Type[T]) -> T:
        """
        Get a service instance by its type.
        
        Args:
            service_type: The type/class of the service to retrieve
            
        Returns:
            The registered service instance
            
        Raises:
            KeyError: If the requested service type is not registered
        """
        if service_type not in cls._services:
            raise KeyError(f"Service of type {service_type.__name__} not registered")
        
        return cast(T, cls._services[service_type])
    
    @classmethod
    def has(cls, service_type: Type[T]) -> bool:
        """
        Check if a service type is registered.
        
        Args:
            service_type: The type/class to check
            
        Returns:
            True if the service is registered, False otherwise
        """
        return service_type in cls._services
    
    @classmethod
    def remove(cls, service_type: Type[T]) -> None:
        """
        Remove a service from the registry.
        
        Args:
            service_type: The type/class of the service to remove
            
        Raises:
            KeyError: If the service type is not registered
        """
        if service_type in cls._services:
            del cls._services[service_type]
        else:
            raise KeyError(f"Cannot remove: Service of type {service_type.__name__} not registered")
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered services."""
        cls._services.clear() 