"""
Concordance Creation Dialog for Document Manager.

This dialog allows users to create new KWIC concordances by selecting
keywords, documents, and configuring generation settings.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.kwic_concordance import ConcordanceSettings
from document_manager.services.concordance_service import ConcordanceService
from document_manager.services.document_service import DocumentService


class ConcordanceCreationDialog(QDialog):
    """Dialog for creating new KWIC concordances."""
    
    concordanceCreated = pyqtSignal(str)  # Emits concordance table ID
    
    def __init__(
        self, 
        concordance_service: ConcordanceService,
        document_service: DocumentService,
        parent=None
    ):
        """Initialize the concordance creation dialog.
        
        Args:
            concordance_service: Service for concordance operations
            document_service: Service for document operations
            parent: Parent widget
        """
        super().__init__(parent)
        self.concordance_service = concordance_service
        self.document_service = document_service
        
        self.setWindowTitle("Create KWIC Concordance")
        self.setModal(True)
        self.resize(800, 600)
        
        self._setup_ui()
        self._load_documents()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Basic Info Tab
        self._create_basic_info_tab()
        
        # Keywords Tab
        self._create_keywords_tab()
        
        # Documents Tab
        self._create_documents_tab()
        
        # Settings Tab
        self._create_settings_tab()
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.button_box)
        
        # Update OK button state
        self._update_ok_button()
    
    def _create_basic_info_tab(self):
        """Create the basic information tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a name for this concordance")
        layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Optional description")
        layout.addRow("Description:", self.description_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas")
        layout.addRow("Tags:", self.tags_edit)
        
        # Created by
        self.created_by_edit = QLineEdit()
        self.created_by_edit.setPlaceholderText("Your name or identifier")
        layout.addRow("Created by:", self.created_by_edit)
        
        self.tab_widget.addTab(widget, "Basic Info")
    
    def _create_keywords_tab(self):
        """Create the keywords selection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Manual keyword entry
        keyword_group = QGroupBox("Keywords")
        keyword_layout = QVBoxLayout(keyword_group)
        
        # Keyword input
        input_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keywords separated by commas or one per line")
        self.add_keyword_button = QPushButton("Add Keywords")
        input_layout.addWidget(self.keyword_input)
        input_layout.addWidget(self.add_keyword_button)
        keyword_layout.addLayout(input_layout)
        
        # Multi-line keyword input
        self.keywords_text = QTextEdit()
        self.keywords_text.setMaximumHeight(100)
        self.keywords_text.setPlaceholderText("Or enter keywords here, one per line")
        keyword_layout.addWidget(QLabel("Multi-line keyword entry:"))
        keyword_layout.addWidget(self.keywords_text)
        
        # Keyword list
        self.keywords_list = QListWidget()
        self.keywords_list.setMaximumHeight(150)
        keyword_layout.addWidget(QLabel("Selected keywords:"))
        keyword_layout.addWidget(self.keywords_list)
        
        # Keyword management buttons
        button_layout = QHBoxLayout()
        self.remove_keyword_button = QPushButton("Remove Selected")
        self.clear_keywords_button = QPushButton("Clear All")
        self.extract_keywords_button = QPushButton("Extract from Documents")
        button_layout.addWidget(self.remove_keyword_button)
        button_layout.addWidget(self.clear_keywords_button)
        button_layout.addWidget(self.extract_keywords_button)
        keyword_layout.addLayout(button_layout)
        
        layout.addWidget(keyword_group)
        
        # Keyword extraction settings
        extraction_group = QGroupBox("Keyword Extraction Settings")
        extraction_layout = QFormLayout(extraction_group)
        
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setRange(1, 50)
        self.min_length_spin.setValue(3)
        extraction_layout.addRow("Minimum length:", self.min_length_spin)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(1, 100)
        self.max_length_spin.setValue(20)
        extraction_layout.addRow("Maximum length:", self.max_length_spin)
        
        self.min_frequency_spin = QSpinBox()
        self.min_frequency_spin.setRange(1, 100)
        self.min_frequency_spin.setValue(2)
        extraction_layout.addRow("Minimum frequency:", self.min_frequency_spin)
        
        self.exclude_stop_words_check = QCheckBox("Exclude common stop words")
        self.exclude_stop_words_check.setChecked(True)
        extraction_layout.addRow(self.exclude_stop_words_check)
        
        layout.addWidget(extraction_group)
        
        self.tab_widget.addTab(widget, "Keywords")
    
    def _create_documents_tab(self):
        """Create the documents selection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Document selection
        doc_group = QGroupBox("Select Documents")
        doc_layout = QVBoxLayout(doc_group)
        
        # Selection buttons
        button_layout = QHBoxLayout()
        self.select_all_docs_button = QPushButton("Select All")
        self.deselect_all_docs_button = QPushButton("Deselect All")
        self.select_text_docs_button = QPushButton("Select Text Documents Only")
        button_layout.addWidget(self.select_all_docs_button)
        button_layout.addWidget(self.deselect_all_docs_button)
        button_layout.addWidget(self.select_text_docs_button)
        doc_layout.addLayout(button_layout)
        
        # Document list
        self.documents_list = QListWidget()
        self.documents_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        doc_layout.addWidget(self.documents_list)
        
        # Selected count label
        self.selected_docs_label = QLabel("Selected: 0 documents")
        doc_layout.addWidget(self.selected_docs_label)
        
        layout.addWidget(doc_group)
        
        self.tab_widget.addTab(widget, "Documents")
    
    def _create_settings_tab(self):
        """Create the concordance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Context settings
        context_group = QGroupBox("Context Settings")
        context_layout = QFormLayout(context_group)
        
        self.context_window_spin = QSpinBox()
        self.context_window_spin.setRange(10, 500)
        self.context_window_spin.setValue(50)
        self.context_window_spin.setSuffix(" characters")
        context_layout.addRow("Context window:", self.context_window_spin)
        
        self.include_punctuation_check = QCheckBox("Include punctuation in context")
        self.include_punctuation_check.setChecked(True)
        context_layout.addRow(self.include_punctuation_check)
        
        layout.addWidget(context_group)
        
        # Matching settings
        matching_group = QGroupBox("Matching Settings")
        matching_layout = QFormLayout(matching_group)
        
        self.case_sensitive_check = QCheckBox("Case sensitive matching")
        self.case_sensitive_check.setChecked(False)
        matching_layout.addRow(self.case_sensitive_check)
        
        self.whole_words_only_check = QCheckBox("Match whole words only")
        self.whole_words_only_check.setChecked(True)
        matching_layout.addRow(self.whole_words_only_check)
        
        self.exclude_common_words_check = QCheckBox("Exclude common stop words")
        self.exclude_common_words_check.setChecked(False)
        matching_layout.addRow(self.exclude_common_words_check)
        
        layout.addWidget(matching_group)
        
        # Keyword length settings
        length_group = QGroupBox("Keyword Length Limits")
        length_layout = QFormLayout(length_group)
        
        self.min_keyword_length_spin = QSpinBox()
        self.min_keyword_length_spin.setRange(1, 50)
        self.min_keyword_length_spin.setValue(1)
        length_layout.addRow("Minimum keyword length:", self.min_keyword_length_spin)
        
        self.max_keyword_length_spin = QSpinBox()
        self.max_keyword_length_spin.setRange(1, 200)
        self.max_keyword_length_spin.setValue(100)
        length_layout.addRow("Maximum keyword length:", self.max_keyword_length_spin)
        
        layout.addWidget(length_group)
        
        # Sorting settings
        sort_group = QGroupBox("Sorting Settings")
        sort_layout = QFormLayout(sort_group)
        
        self.sort_by_combo = QComboBox()
        self.sort_by_combo.addItems([
            "keyword", "position", "document", "left_context", "right_context"
        ])
        sort_layout.addRow("Sort by:", self.sort_by_combo)
        
        self.group_by_document_check = QCheckBox("Group results by document")
        self.group_by_document_check.setChecked(False)
        sort_layout.addRow(self.group_by_document_check)
        
        layout.addWidget(sort_group)
        
        self.tab_widget.addTab(widget, "Settings")
    
    def _load_documents(self):
        """Load available documents into the list."""
        try:
            documents = self.document_service.list_documents()
            
            for doc in documents:
                # Only show documents with extracted text content
                if hasattr(doc, 'extracted_text') and doc.extracted_text:
                    item = QListWidgetItem()
                    item.setText(f"{doc.name} ({len(doc.extracted_text)} chars)")
                    item.setData(Qt.ItemDataRole.UserRole, doc.id)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.documents_list.addItem(item)
                # Also include documents with content field (for compatibility)
                elif hasattr(doc, 'content') and doc.content:
                    item = QListWidgetItem()
                    item.setText(f"{doc.name} ({len(doc.content)} chars)")
                    item.setData(Qt.ItemDataRole.UserRole, doc.id)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.documents_list.addItem(item)
            
            self._update_selected_docs_count()
            
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Basic info
        self.name_edit.textChanged.connect(self._update_ok_button)
        
        # Keywords
        self.add_keyword_button.clicked.connect(self._add_keywords)
        self.remove_keyword_button.clicked.connect(self._remove_selected_keywords)
        self.clear_keywords_button.clicked.connect(self._clear_keywords)
        self.extract_keywords_button.clicked.connect(self._extract_keywords)
        self.keyword_input.returnPressed.connect(self._add_keywords)
        self.keywords_text.textChanged.connect(self._on_keywords_text_changed)
        
        # Documents
        self.select_all_docs_button.clicked.connect(self._select_all_documents)
        self.deselect_all_docs_button.clicked.connect(self._deselect_all_documents)
        self.select_text_docs_button.clicked.connect(self._select_text_documents)
        self.documents_list.itemChanged.connect(self._update_selected_docs_count)
        
        # Dialog buttons
        self.button_box.accepted.connect(self._create_concordance)
        self.button_box.rejected.connect(self.reject)
    
    def _add_keywords(self):
        """Add keywords from the input field."""
        text = self.keyword_input.text().strip()
        if text:
            keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
            for keyword in keywords:
                if not self._keyword_exists(keyword):
                    item = QListWidgetItem(keyword)
                    self.keywords_list.addItem(item)
            
            self.keyword_input.clear()
            self._update_ok_button()
    
    def _on_keywords_text_changed(self):
        """Handle changes in the multi-line keywords text."""
        text = self.keywords_text.toPlainText().strip()
        if text:
            keywords = [kw.strip() for kw in text.split('\n') if kw.strip()]
            
            # Clear existing keywords
            self.keywords_list.clear()
            
            # Add new keywords
            for keyword in keywords:
                if keyword:
                    item = QListWidgetItem(keyword)
                    self.keywords_list.addItem(item)
            
            self._update_ok_button()
    
    def _keyword_exists(self, keyword: str) -> bool:
        """Check if a keyword already exists in the list."""
        for i in range(self.keywords_list.count()):
            if self.keywords_list.item(i).text().lower() == keyword.lower():
                return True
        return False
    
    def _remove_selected_keywords(self):
        """Remove selected keywords from the list."""
        for item in self.keywords_list.selectedItems():
            row = self.keywords_list.row(item)
            self.keywords_list.takeItem(row)
        self._update_ok_button()
    
    def _clear_keywords(self):
        """Clear all keywords."""
        self.keywords_list.clear()
        self.keywords_text.clear()
        self._update_ok_button()
    
    def _extract_keywords(self):
        """Extract keywords from selected documents."""
        selected_doc_ids = self._get_selected_document_ids()
        if not selected_doc_ids:
            return
        
        try:
            # Get text from selected documents
            all_text = ""
            for doc_id in selected_doc_ids:
                doc = self.document_service.get_document(doc_id)
                if doc:
                    # Try extracted_text first, then content for compatibility
                    text_content = None
                    if hasattr(doc, 'extracted_text') and doc.extracted_text:
                        text_content = doc.extracted_text
                    elif hasattr(doc, 'content') and doc.content:
                        text_content = doc.content
                    
                    if text_content:
                        all_text += text_content + "\n"
            
            if all_text:
                # Extract keywords
                keywords = self.concordance_service.extract_keywords_from_text(
                    all_text,
                    min_length=self.min_length_spin.value(),
                    max_length=self.max_length_spin.value(),
                    exclude_stop_words=self.exclude_stop_words_check.isChecked(),
                    min_frequency=self.min_frequency_spin.value()
                )
                
                # Add top keywords to the list
                self.keywords_list.clear()
                for keyword, frequency in keywords[:50]:  # Limit to top 50
                    item = QListWidgetItem(f"{keyword} ({frequency})")
                    item.setData(Qt.ItemDataRole.UserRole, keyword)
                    self.keywords_list.addItem(item)
                
                self._update_ok_button()
        
        except Exception as e:
            print(f"Error extracting keywords: {e}")
    
    def _select_all_documents(self):
        """Select all documents."""
        for i in range(self.documents_list.count()):
            item = self.documents_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def _deselect_all_documents(self):
        """Deselect all documents."""
        for i in range(self.documents_list.count()):
            item = self.documents_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def _select_text_documents(self):
        """Select only text documents."""
        for i in range(self.documents_list.count()):
            item = self.documents_list.item(i)
            # For now, select all since we're only showing documents with content
            item.setCheckState(Qt.CheckState.Checked)
    
    def _update_selected_docs_count(self):
        """Update the selected documents count label."""
        count = len(self._get_selected_document_ids())
        self.selected_docs_label.setText(f"Selected: {count} documents")
        self._update_ok_button()
    
    def _get_selected_document_ids(self) -> List[str]:
        """Get the IDs of selected documents."""
        selected_ids = []
        for i in range(self.documents_list.count()):
            item = self.documents_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                doc_id = item.data(Qt.ItemDataRole.UserRole)
                selected_ids.append(doc_id)
        return selected_ids
    
    def _get_keywords(self) -> List[str]:
        """Get the list of keywords."""
        keywords = []
        for i in range(self.keywords_list.count()):
            item = self.keywords_list.item(i)
            # Check if item has stored keyword data (from extraction)
            keyword = item.data(Qt.ItemDataRole.UserRole)
            if keyword:
                keywords.append(keyword)
            else:
                keywords.append(item.text())
        return keywords
    
    def _get_settings(self) -> ConcordanceSettings:
        """Get the concordance settings from the UI."""
        return ConcordanceSettings(
            context_window=self.context_window_spin.value(),
            case_sensitive=self.case_sensitive_check.isChecked(),
            whole_words_only=self.whole_words_only_check.isChecked(),
            include_punctuation=self.include_punctuation_check.isChecked(),
            min_keyword_length=self.min_keyword_length_spin.value(),
            max_keyword_length=self.max_keyword_length_spin.value(),
            exclude_common_words=self.exclude_common_words_check.isChecked(),
            sort_by=self.sort_by_combo.currentText(),
            group_by_document=self.group_by_document_check.isChecked()
        )
    
    def _update_ok_button(self):
        """Update the OK button enabled state."""
        name_valid = bool(self.name_edit.text().strip())
        keywords_valid = self.keywords_list.count() > 0
        docs_valid = len(self._get_selected_document_ids()) > 0
        
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            name_valid and keywords_valid and docs_valid
        )
    
    def _create_concordance(self):
        """Create the concordance and close the dialog."""
        try:
            # Get form data
            name = self.name_edit.text().strip()
            description = self.description_edit.toPlainText().strip() or None
            tags = [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()]
            created_by = self.created_by_edit.text().strip() or None
            keywords = self._get_keywords()
            document_ids = self._get_selected_document_ids()
            settings = self._get_settings()
            
            # Generate concordance
            concordance_table = self.concordance_service.generate_concordance(
                name=name,
                keywords=keywords,
                document_ids=document_ids,
                settings=settings,
                description=description,
                tags=tags,
                created_by=created_by
            )
            
            # Save concordance
            table_id = self.concordance_service.save_concordance(concordance_table)
            
            # Emit signal and close
            self.concordanceCreated.emit(table_id)
            self.accept()
            
        except Exception as e:
            print(f"Error creating concordance: {e}")
            # Could show an error dialog here 