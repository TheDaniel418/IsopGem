"""Document Manager tab implementation.

This module provides the main tab for the Document Manager pillar.
"""

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from shared.ui.window_management import TabManager, WindowManager


class DocumentTab(QWidget):
    """Main tab for the Document Manager pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Document Manager tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager
        self._init_ui()
        logger.debug("DocumentTab initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        # Document Browser button
        doc_browser_btn = QPushButton("Document Browser")
        doc_browser_btn.setToolTip("Open Document Browser")
        doc_browser_btn.clicked.connect(self._open_document_browser)
        button_layout.addWidget(doc_browser_btn)

        # Document Analysis button
        analysis_btn = QPushButton("Document Analysis")
        analysis_btn.setToolTip("Analyze documents from a gematric perspective")
        analysis_btn.clicked.connect(self._open_document_analysis)
        button_layout.addWidget(analysis_btn)

        # RTF Editor button
        rtf_btn = QPushButton("RTF Editor")
        rtf_btn.setToolTip("Open Rich Text Editor")
        rtf_btn.clicked.connect(self._open_rtf_editor)
        button_layout.addWidget(rtf_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Add button bar to main layout
        layout.addWidget(button_bar)

        # Title and welcome message
        title = QLabel("Document Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        welcome = QLabel(
            "Welcome to the Document Manager pillar. Please select a tool from the buttons above."
        )
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(welcome)
        layout.addStretch()

    def _open_document_browser(self) -> None:
        """Open the Document Browser window."""
        from document_manager.ui.panels.document_manager_panel import (
            DocumentManagerPanel,
        )

        # Create and open the document browser window
        self.window_manager.open_window(
            "document_browser", DocumentManagerPanel(), "Document Browser"
        )

        logger.debug("Opened Document Browser window")

    def _open_document_analysis(self) -> None:
        """Open the Document Analysis window."""
        from document_manager.ui.panels.document_analysis_panel import (
            DocumentAnalysisPanel,
        )

        # Create and open the document analysis window
        self.window_manager.open_window(
            "document_analysis", DocumentAnalysisPanel(), "Document Analysis"
        )

        logger.debug("Opened Document Analysis window")

    def _open_rtf_editor(self) -> None:
        """Open the RTF Editor window."""
        from loguru import logger

        from shared.ui.widgets.rtf_editor.rtf_editor_window import RTFEditorWindow

        logger.debug("Opening RTF Editor window directly...")

        # Create the RTF editor window
        editor = RTFEditorWindow()

        # Open the window using the window manager
        self.window_manager.open_window("rtf_editor", editor, "Rich Text Editor")

        logger.debug("RTF Editor window opened")
