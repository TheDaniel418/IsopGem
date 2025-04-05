"""Gematria panel components.

This package provides panel widgets for the Gematria functionality.
"""

from typing import List

from .calculation_history_panel import CalculationHistoryPanel
from .main_panel import MainPanel
from .search_panel import SearchPanel
from .tag_management_panel import TagManagementPanel
from .word_abacus_panel import WordAbacusPanel

__all__: List[str] = [
    "MainPanel",
    "CalculationHistoryPanel",
    "TagManagementPanel",
    "SearchPanel",
    "WordAbacusPanel",
]
