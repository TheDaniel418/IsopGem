"""Gematria panel components.

This package provides panel widgets for the Gematria functionality.
"""

from typing import List

from .calculation_history_panel import CalculationHistoryPanel
from .main_panel import MainPanel
from .tag_management_panel import TagManagementPanel

__all__: List[str] = [
    'MainPanel',
    'CalculationHistoryPanel',
    'TagManagementPanel'
]
