"""Gematria widget components.

This package provides reusable widget components for the Gematria functionality.
"""

from typing import List

from gematria.ui.widgets.calculation_detail_widget import CalculationDetailWidget
from gematria.ui.widgets.word_abacus_widget import WordAbacusWidget

__all__: List[str] = ["WordAbacusWidget", "CalculationDetailWidget"]
