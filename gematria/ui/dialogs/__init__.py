"""
Purpose: Provides initialization for dialog components within the Gematria pillar

This file is part of the gematria pillar and serves as a UI component.
It is responsible for exposing dialog components used for user interactions
within the gematria functionality of the application.

Key components:
- Import statements for all dialog classes
- __all__ list defining public exports

Dependencies:
- Various dialog implementations within the gematria.ui.dialogs package

Related files:
- All dialog implementation files in this directory
- gematria/ui/__init__.py: Imports from this module
"""

from gematria.ui.dialogs.create_tag_dialog import CreateTagDialog
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog
from gematria.ui.dialogs.edit_tags_window import EditTagsWindow
from gematria.ui.dialogs.gematria_help_dialog import GematriaHelpDialog
from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog
from gematria.ui.dialogs.save_calculation_dialog import SaveCalculationDialog
from gematria.ui.dialogs.tag_selection_dialog import TagSelectionDialog

__all__ = [
    "CreateTagDialog",
    "CustomCipherDialog",
    "EditTagsWindow",
    "GematriaHelpDialog",
    "ImportWordListDialog",
    "SaveCalculationDialog",
    "TagSelectionDialog",
]
