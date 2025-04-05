"""
Purpose: Provides a dialog for managing document categories.

This file is part of the document_manager pillar and serves as a UI component.
It allows users to create, edit, delete, and organize document categories.

Key components:
- CategoryManagerDialog: Dialog for managing document categories 

Dependencies:
- PyQt6: For UI components
- document_manager.models.document_category: For DocumentCategory model
- document_manager.services.category_service: For category operations
"""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QIcon
from PyQt6.QtWidgets import (QColorDialog, QDialog, QHBoxLayout, QInputDialog,
                            QLabel, QLineEdit, QMenu, QPushButton, QTextEdit,
                            QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from loguru import logger

from document_manager.models.document_category import DocumentCategory
from document_manager.services.category_service import CategoryService
from shared.ui.components.message_box import MessageBox


class CategoryManagerDialog(QDialog):
    """Dialog for managing document categories."""
    
    def __init__(self, parent=None):
        """Initialize the category manager dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Service
        self.category_service = CategoryService()
        
        # Dialog setup
        self.setWindowTitle("Document Category Manager")
        self.resize(800, 600)
        
        # UI setup
        self._init_ui()
        
        # Load data
        self._load_categories()
    
    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Document Categories")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Manage document categories and their hierarchy")
        main_layout.addWidget(desc_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Add root category
        self.add_root_btn = QPushButton("Add Root Category")
        self.add_root_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_root_btn.clicked.connect(self._add_root_category)
        button_layout.addWidget(self.add_root_btn)
        
        # Add child category
        self.add_child_btn = QPushButton("Add Subcategory")
        self.add_child_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_child_btn.clicked.connect(self._add_child_category)
        button_layout.addWidget(self.add_child_btn)
        
        # Edit category
        self.edit_btn = QPushButton("Edit Category")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_btn.clicked.connect(self._edit_category)
        button_layout.addWidget(self.edit_btn)
        
        # Delete category
        self.delete_btn = QPushButton("Delete Category")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.clicked.connect(self._delete_category)
        button_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(button_layout)
        
        # Category tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["Name", "Description", "Color"])
        self.category_tree.setColumnWidth(0, 250)
        self.category_tree.setColumnWidth(1, 350)
        self.category_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_tree.customContextMenuRequested.connect(self._show_context_menu)
        main_layout.addWidget(self.category_tree)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        dialog_buttons.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        dialog_buttons.addWidget(close_btn)
        
        main_layout.addLayout(dialog_buttons)
        
        self.setLayout(main_layout)
    
    def _load_categories(self):
        """Load categories into the tree."""
        self.category_tree.clear()
        
        # Get category tree
        category_tree = self.category_service.get_category_tree()
        
        # Build tree items
        self._build_tree_items(category_tree, None)
        
        # Expand all items
        self.category_tree.expandAll()
    
    def _build_tree_items(self, categories: List[Dict], parent_item: Optional[QTreeWidgetItem] = None):
        """Recursively build tree items from category data.
        
        Args:
            categories: List of category dictionaries
            parent_item: Parent tree item, or None for root items
        """
        for category in categories:
            # Create item
            if parent_item is None:
                item = QTreeWidgetItem(self.category_tree)
            else:
                item = QTreeWidgetItem(parent_item)
            
            # Set data
            item.setText(0, category["name"])
            item.setText(1, category["description"] or "")
            
            # Set color indicator
            item.setText(2, category["color"])
            item.setBackground(2, QColor(category["color"]))
            item.setForeground(2, self._contrasting_text_color(QColor(category["color"])))
            
            # Store category ID
            item.setData(0, Qt.ItemDataRole.UserRole, category["id"])
            
            # Add children
            if "children" in category and category["children"]:
                self._build_tree_items(category["children"], item)
    
    def _contrasting_text_color(self, bg_color: QColor) -> QColor:
        """Get a contrasting text color (black or white) based on background color.
        
        Args:
            bg_color: Background color
            
        Returns:
            Contrasting text color
        """
        # Calculate brightness using luminance formula
        brightness = (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000
        
        # Return white for dark backgrounds, black for light backgrounds
        if brightness < 128:
            return QColor(255, 255, 255)  # White
        else:
            return QColor(0, 0, 0)  # Black
    
    def _show_context_menu(self, position):
        """Show context menu for category operations.
        
        Args:
            position: Position where menu should appear
        """
        item = self.category_tree.itemAt(position)
        if not item:
            return
        
        # Get category ID
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not category_id:
            return
        
        # Create context menu
        menu = QMenu()
        
        # Add actions
        add_child_action = QAction("Add Subcategory", self)
        add_child_action.triggered.connect(lambda: self._add_child_category(category_id))
        menu.addAction(add_child_action)
        
        edit_action = QAction("Edit Category", self)
        edit_action.triggered.connect(lambda: self._edit_category(category_id))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Category", self)
        delete_action.triggered.connect(lambda: self._delete_category(category_id))
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec(self.category_tree.viewport().mapToGlobal(position))
    
    def _add_root_category(self):
        """Add a new root category."""
        self._create_category(None)
    
    def _add_child_category(self, parent_id: Optional[str] = None):
        """Add a child category to the selected parent.
        
        Args:
            parent_id: Parent category ID, or None to use selection
        """
        # If no parent ID provided, get from selection
        if parent_id is None:
            selected_items = self.category_tree.selectedItems()
            if not selected_items:
                MessageBox.warning(
                    self,
                    "No Selection",
                    "Please select a parent category first."
                )
                return
            
            parent_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Verify parent exists
        parent = self.category_service.get_category(parent_id)
        if not parent:
            MessageBox.error(
                self,
                "Invalid Parent",
                "The selected parent category is not valid."
            )
            return
        
        # Create child category
        self._create_category(parent_id)
    
    def _create_category(self, parent_id: Optional[str]):
        """Create a new category.
        
        Args:
            parent_id: Parent category ID, or None for root category
        """
        # Get category name
        name, ok = QInputDialog.getText(
            self,
            "New Category",
            "Enter category name:"
        )
        
        if not ok or not name.strip():
            return
        
        # Get color
        color = QColorDialog.getColor(QColor("#1976D2"), self, "Select Category Color")
        if not color.isValid():
            color = QColor("#1976D2")  # Default blue
        
        color_hex = color.name()
        
        # Get description
        description, ok = QInputDialog.getMultiLineText(
            self,
            "Category Description",
            "Enter category description (optional):"
        )
        
        if not ok:
            description = ""
        
        # Create category
        category = self.category_service.create_category(
            name=name.strip(),
            color=color_hex,
            description=description.strip(),
            parent_id=parent_id
        )
        
        if category:
            # Refresh category tree
            self._load_categories()
        else:
            MessageBox.error(
                self,
                "Category Creation Failed",
                "Failed to create the category. Please try again."
            )
    
    def _edit_category(self, category_id: Optional[str] = None):
        """Edit the selected category.
        
        Args:
            category_id: Category ID to edit, or None to use selection
        """
        # If no category ID provided, get from selection
        if category_id is None:
            selected_items = self.category_tree.selectedItems()
            if not selected_items:
                MessageBox.warning(
                    self,
                    "No Selection",
                    "Please select a category to edit."
                )
                return
            
            category_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Get category
        category = self.category_service.get_category(category_id)
        if not category:
            MessageBox.error(
                self,
                "Category Not Found",
                "The selected category could not be found."
            )
            return
        
        # Get updated name
        name, ok = QInputDialog.getText(
            self,
            "Edit Category",
            "Category name:",
            text=category.name
        )
        
        if not ok:
            return
        
        # Get updated color
        color = QColorDialog.getColor(QColor(category.color), self, "Select Category Color")
        if not color.isValid():
            color_hex = category.color
        else:
            color_hex = color.name()
        
        # Get updated description
        desc_text, desc_ok = QInputDialog.getMultiLineText(
            self,
            "Category Description",
            "Category description:",
            text=category.description or ""
        )
        
        description: Optional[str] = desc_text if desc_ok else None
        category_data = {
            "name": name.strip(),
            "color": color_hex,
            "description": description or ""
        }
        
        # Update category
        updated_category = self.category_service.update_category(
            category_id=category_id,
            **category_data
        )
        
        if updated_category:
            # Refresh category tree
            self._load_categories()
        else:
            MessageBox.error(
                self,
                "Update Failed",
                "Failed to update the category. Please try again."
            )
    
    def _delete_category(self, category_id: Optional[str] = None):
        """Delete the selected category.
        
        Args:
            category_id: Category ID to delete, or None to use selection
        """
        # If no category ID provided, get from selection
        if category_id is None:
            selected_items = self.category_tree.selectedItems()
            if not selected_items:
                MessageBox.warning(
                    self,
                    "No Selection",
                    "Please select a category to delete."
                )
                return
            
            category_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Get category
        category = self.category_service.get_category(category_id)
        if not category:
            MessageBox.error(
                self,
                "Category Not Found",
                "The selected category could not be found."
            )
            return
        
        # Confirm deletion
        result = MessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the category '{category.name}'?\n\n"
            "This will also delete all subcategories. Documents in these categories will not be deleted, "
            "but they will no longer have a category assigned."
        )
        
        if not result:
            return
        
        # Delete category
        if self.category_service.delete_category(category_id):
            # Refresh category tree
            self._load_categories()
        else:
            MessageBox.error(
                self,
                "Delete Failed",
                "Failed to delete the category. It may contain documents or subcategories."
            ) 