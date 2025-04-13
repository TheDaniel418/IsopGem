"""
Purpose: Package initialization for TQ UI components

This file is part of the tq pillar and serves as a package initializer.
It makes UI components available for import and defines package-level constants.

Key components:
- Import statements making key modules available at the package level

Dependencies:
- None (package initialization only)

Related files:
- tq/ui/tq_tab.py: Main tab UI for TQ functionality
- shared/ui/window_management.py: Core window management system used by TQ components
"""

# Make window_management available for import
try:
    # First check if the module exists before trying to import it
    import importlib.util
    import os
    
    spec = importlib.util.find_spec('tq.ui.window_management')
    if spec is not None:
        from . import window_management
        
        # Explicitly export the functions
        __all__ = ['window_management']
except (ImportError, ModuleNotFoundError):
    # The module might not exist during initial imports
    pass
