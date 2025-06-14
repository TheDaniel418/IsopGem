"""Gematria Search panel.

This module provides a panel implementation for searching the Gematria database
for calculations based on various criteria.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger
from PyQt6.QtCore import QRect, QRegularExpression, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QRegularExpressionValidator,
)
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.ui.widgets.calculation_detail_widget import CalculationDetailWidget
from shared.ui.window_management import WindowManager


class NumericTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem that sorts numerically."""
    
    def __init__(self, value: int):
        super().__init__(str(value))
        self.numeric_value = value
    
    def __lt__(self, other):
        """Override less than operator for proper numeric sorting."""
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        return super().__lt__(other)


class TagItemDelegate(QStyledItemDelegate):
    """Custom delegate for displaying tags with colors in the search results table."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        """Custom paint method to display tags with colored backgrounds."""
        # Get the tag data from the model
        tag_data = index.data(Qt.ItemDataRole.UserRole)
        
        if not tag_data:
            # No tags - just paint empty cell
            super().paint(painter, option, index)
            return

        # Set up the painter
        painter.save()
        
        # Fill the background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, option.palette.base())

        # Calculate layout for tags
        rect = option.rect
        margin = 2
        tag_height = rect.height() - (2 * margin)
        tag_spacing = 4
        current_x = rect.x() + margin
        
        # Set up font
        font = painter.font()
        font.setPointSize(max(8, font.pointSize() - 1))  # Slightly smaller font
        painter.setFont(font)
        
        # Draw each tag
        for i, tag in enumerate(tag_data):
            if current_x >= rect.right() - margin:
                break  # No more space
                
            tag_name = tag.get('name', 'Unknown')
            tag_color = tag.get('color', '#cccccc')
            
            # Calculate tag width
            text_width = painter.fontMetrics().horizontalAdvance(tag_name)
            tag_width = text_width + 8  # Add padding
            
            # Check if tag fits
            if current_x + tag_width > rect.right() - margin:
                if i == 0:
                    # First tag doesn't fit, truncate it
                    available_width = rect.right() - current_x - margin - 20  # Leave space for "..."
                    if available_width > 20:
                        truncated_name = painter.fontMetrics().elidedText(
                            tag_name, Qt.TextElideMode.ElideRight, available_width
                        )
                        tag_width = painter.fontMetrics().horizontalAdvance(truncated_name) + 8
                        tag_name = truncated_name
                    else:
                        break
                else:
                    # Show "..." for additional tags
                    painter.setPen(QColor('#666666'))
                    painter.drawText(
                        current_x, rect.y() + margin,
                        rect.right() - current_x - margin, tag_height,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        "..."
                    )
                    break
            
            # Draw tag background
            tag_rect = QRect(current_x, rect.y() + margin, tag_width, tag_height)
            
            # Parse color and create brush
            try:
                color = QColor(tag_color)
                # Make color slightly transparent for better readability
                color.setAlpha(200)
                painter.fillRect(tag_rect, color)
                
                # Draw border
                border_color = QColor(tag_color)
                border_color.setAlpha(255)
                painter.setPen(QPen(border_color, 1))
                painter.drawRect(tag_rect)
                
            except Exception:
                # Fallback to gray if color parsing fails
                painter.fillRect(tag_rect, QColor('#e0e0e0'))
                painter.setPen(QPen(QColor('#cccccc'), 1))
                painter.drawRect(tag_rect)
            
            # Draw tag text
            # Choose text color based on background brightness
            try:
                bg_color = QColor(tag_color)
                # Calculate luminance to determine if we need dark or light text
                luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255
                text_color = QColor('#000000') if luminance > 0.5 else QColor('#ffffff')
            except Exception:
                text_color = QColor('#000000')
                
            painter.setPen(text_color)
            painter.drawText(
                tag_rect,
                Qt.AlignmentFlag.AlignCenter,
                tag_name
            )
            
            # Move to next position
            current_x += tag_width + tag_spacing

        painter.restore()

    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        # Make rows a bit taller to accommodate tag display
        size = super().sizeHint(option, index)
        size.setHeight(max(size.height(), 28))  # Minimum height of 28px
        return size


class SearchPanel(QWidget):
    """Panel for searching the Gematria database."""

    # Signal emitted when a search result is selected
    result_selected = pyqtSignal(CalculationResult)

    def __init__(
        self,
        calculation_db_service: CalculationDatabaseService,
        custom_cipher_service: CustomCipherService,
        window_manager: Optional[WindowManager] = None,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the search panel.

        Args:
            calculation_db_service: Service for database operations
            custom_cipher_service: Service for custom cipher operations
            window_manager: Window manager for opening additional windows
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculation_db_service = calculation_db_service
        self.custom_cipher_service = custom_cipher_service
        self.selected_calculation: Optional[CalculationResult] = None

        # Store window manager
        self.window_manager = window_manager

        # If no window manager is provided, try to find it in the parent chain
        if self.window_manager is None:
            self.window_manager = self._find_window_manager()

        self._setup_ui()

    def _find_window_manager(self) -> Optional[WindowManager]:
        """Find the window manager by traversing the parent widget hierarchy.

        Returns:
            The window manager if found, None otherwise
        """
        result: Optional[WindowManager] = None

        try:
            # Start with the current parent
            parent = self.parent()

            # Check parent chain
            while parent is not None and result is None:
                # Check if parent has window_manager attribute
                if hasattr(parent, "window_manager"):
                    potential_manager = getattr(parent, "window_manager")
                    if isinstance(potential_manager, WindowManager):
                        result = potential_manager

                # Move up to parent if we haven't found a manager
                if result is None:
                    parent = parent.parent()

            # Log if we didn't find anything
            if result is None:
                logger.debug(
                    "No window manager found in parent widget chain, but this is expected when opened from other panels"
                )

        except Exception as e:
            logger.error(f"Error while finding window manager: {e}")

        return result

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Gematria Search")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Search criteria area
        criteria_layout = QHBoxLayout()

        # Left side - text and value search
        left_group = QGroupBox("Search Criteria")
        left_layout = QFormLayout()

        # Text search
        self.text_search = QLineEdit()
        self.text_search.setPlaceholderText("Enter text to search...")
        left_layout.addRow("Text:", self.text_search)

        self.exact_text_match = QCheckBox("Exact match")
        left_layout.addRow("", self.exact_text_match)

        # Exact value - Changed from QSpinBox to QLineEdit with numeric validation
        self.exact_value = QLineEdit()
        self.exact_value.setPlaceholderText("Enter exact value...")
        # Only allow numbers with a validator
        validator = QRegularExpressionValidator(QRegularExpression("^[0-9]*$"))
        self.exact_value.setValidator(validator)
        left_layout.addRow("Exact value:", self.exact_value)

        left_group.setLayout(left_layout)
        criteria_layout.addWidget(left_group)

        # Right side - method filter
        right_group = QGroupBox("Additional Filters")
        right_layout = QFormLayout()

        # Language/Method filter
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Any Language", "Hebrew", "Greek", "English"])
        self.language_combo.currentIndexChanged.connect(self._update_method_combo)
        right_layout.addRow("Language:", self.language_combo)

        self.method_combo = QComboBox()
        self.method_combo.addItem("Any Method")
        right_layout.addRow("Method:", self.method_combo)

        # Other filters
        self.favorites_only = QCheckBox("Favorites only")
        right_layout.addRow("", self.favorites_only)

        # Tags filter with dropdown
        tags_layout = QHBoxLayout()
        self.has_tags = QCheckBox("Has tags")
        self.has_tags.stateChanged.connect(self._on_has_tags_changed)
        tags_layout.addWidget(self.has_tags)
        
        self.tag_combo = QComboBox()
        self.tag_combo.setEnabled(False)  # Initially disabled
        self.tag_combo.setMinimumWidth(150)
        tags_layout.addWidget(self.tag_combo)
        
        right_layout.addRow("", tags_layout)

        self.has_notes = QCheckBox("Has notes")
        right_layout.addRow("", self.has_notes)

        right_group.setLayout(right_layout)
        criteria_layout.addWidget(right_group)

        layout.addLayout(criteria_layout)

        # Buttons row
        button_layout = QHBoxLayout()

        self.search_button = QPushButton("Search")
        self.search_button.setIcon(QIcon.fromTheme("search"))
        self.search_button.clicked.connect(self._perform_search)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.clicked.connect(self._clear_search)

        button_layout.addStretch()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Text", "Value", "Method", "Tags", "★"])
        
        # Set column widths for better display
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Text column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Value column
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Method column
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Tags column - fixed width
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Favorite column
        
        # Set specific width for Tags column to ensure tag names are visible
        self.results_table.setColumnWidth(3, 200)  # Tags column - 200px width
        
        # Enable sorting
        self.results_table.setSortingEnabled(True)
        
        # Set up the tag delegate for the Tags column (column 3)
        tag_delegate = TagItemDelegate(self.results_table)
        self.results_table.setItemDelegateForColumn(3, tag_delegate)

        # Configure table behavior
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.itemSelectionChanged.connect(self._on_result_selected)
        # Connect double-click to view details in a separate window
        self.results_table.itemDoubleClicked.connect(self._open_detail_window)

        # Make the rows a bit taller to accommodate the tags
        self.results_table.verticalHeader().setDefaultSectionSize(30)

        layout.addWidget(self.results_table)

        # Initialize method combo
        self._update_method_combo()
        
        # Initialize tag combo
        self._update_tag_combo()

    def _update_method_combo(self) -> None:
        """Update the method combo box based on the selected language."""
        self.method_combo.clear()
        self.method_combo.addItem("Any Method")

        language_idx = self.language_combo.currentIndex()

        # Get calculation types for selected language
        if language_idx == 0:  # Any Language
            methods = CalculationType.get_all_types()
        elif language_idx == 1:  # Hebrew
            methods = CalculationType.get_types_for_language(Language.HEBREW)
        elif language_idx == 2:  # Greek
            methods = CalculationType.get_types_for_language(Language.GREEK)
        elif language_idx == 3:  # English
            methods = CalculationType.get_types_for_language(Language.ENGLISH)
        else:
            methods = []

        # Add standard methods to combo - use our improved method for display
        for method in methods:
            # Format display name consistently with our new method
            display_name = method.name.replace("_", " ").title()
            self.method_combo.addItem(display_name, method)

        # Add separator and custom methods if applicable
        if language_idx > 0:
            language = [Language.HEBREW, Language.GREEK, Language.ENGLISH][
                language_idx - 1
            ]
            custom_methods = self.custom_cipher_service.get_methods_for_language(
                language
            )

            if custom_methods:
                self.method_combo.insertSeparator(self.method_combo.count())
                for custom_method in custom_methods:
                    custom_method_obj: CustomCipherConfig = custom_method
                    # Store the custom method name as a string, not as a CalculationType
                    # Important: We store just the name (without 'Custom: ' prefix) as the data
                    # but display it with the prefix in the UI
                    display_name = f"Custom: {custom_method_obj.name}"
                    self.method_combo.addItem(display_name, custom_method_obj.name)

    def _perform_search(self) -> None:
        """Perform search based on current criteria."""
        from loguru import logger

        logger.debug("Performing search in SearchPanel")
        criteria: Dict[str, Any] = {}

        # Text criteria
        if self.text_search.text():
            if self.exact_text_match.isChecked():
                # Use exact match (case-insensitive)
                criteria["input_text"] = self.text_search.text()
            else:
                # Use partial match (case-insensitive)
                # The %wildcards% are used by SQLite for LIKE queries
                criteria["input_text_like"] = f"%{self.text_search.text()}%"

        # Value criteria - Updated to handle the QLineEdit instead of QSpinBox
        exact_value_text = self.exact_value.text().strip()
        if exact_value_text:
            try:
                criteria["result_value"] = int(exact_value_text)
            except ValueError:
                # If text is not a valid integer, ignore it
                pass

        # Language/Method filter
        language_idx = self.language_combo.currentIndex()
        if language_idx > 0:
            language = [Language.HEBREW, Language.GREEK, Language.ENGLISH][
                language_idx - 1
            ]
            criteria["language"] = language

        method_idx = self.method_combo.currentIndex()
        if method_idx > 0:
            method_data = self.method_combo.currentData()
            method_text = self.method_combo.currentText()
            logger.debug(
                f"Selected method: {method_text}, data type: {type(method_data)}, value: {method_data}"
            )

            if isinstance(method_data, CalculationType):
                logger.debug(f"Adding standard calculation type filter: {method_data}")
                criteria["calculation_type"] = method_data
            elif isinstance(method_data, str):
                # For custom ciphers, the method_text will have 'Custom: ' prefix but method_data might not
                # Make sure we're consistent with how we store and search for custom method names
                if method_text.startswith("Custom: "):
                    # Use the display name without the prefix for searching
                    clean_name = method_data
                    logger.debug(
                        f"Adding custom cipher filter (from data): {clean_name}"
                    )
                    criteria["custom_method_name"] = clean_name
                else:
                    logger.debug(f"Adding custom cipher filter: {method_data}")
                    criteria["custom_method_name"] = method_data

        # Other filters
        if self.favorites_only.isChecked():
            criteria["favorite"] = True

        if self.has_tags.isChecked():
            # Check if a specific tag is selected
            tag_idx = self.tag_combo.currentIndex()
            if tag_idx > 0:  # Not "Any Tag"
                tag_id = self.tag_combo.currentData()
                if tag_id:
                    criteria["tag_id"] = tag_id
            else:
                # Just check for any tags
                criteria["has_tags"] = True

        if self.has_notes.isChecked():
            criteria["has_notes"] = True

        # Perform search
        logger.debug(f"Sending search criteria to calculation_db_service: {criteria}")
        results = self.calculation_db_service.search_calculations(criteria)
        logger.debug(f"Search returned {len(results)} results")
        self._display_results(results)

    def _clear_search(self) -> None:
        """Clear all search fields."""
        self.text_search.clear()
        self.exact_text_match.setChecked(False)
        self.exact_value.clear()
        self.language_combo.setCurrentIndex(0)
        self.method_combo.setCurrentIndex(0)
        self.favorites_only.setChecked(False)
        self.has_tags.setChecked(False)
        self.tag_combo.setCurrentIndex(0)
        self.tag_combo.setEnabled(False)
        self.has_notes.setChecked(False)

        # Clear results
        self.results_table.setRowCount(0)
        self.selected_calculation = None

    def _display_results(self, results: List[CalculationResult]) -> None:
        """Display search results in the table.

        Args:
            results: List of calculation results to display
        """
        # Temporarily disable sorting while populating the table to avoid performance issues
        self.results_table.setSortingEnabled(False)
        
        self.results_table.setRowCount(0)
        self.selected_calculation = None

        if not results:
            # Re-enable sorting even if no results
            self.results_table.setSortingEnabled(True)
            return

        self.results_table.setRowCount(len(results))

        for i, result in enumerate(results):
            # Text column
            text_item = QTableWidgetItem(result.input_text)
            text_item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_table.setItem(i, 0, text_item)

            # Value column - Set up for proper numerical sorting
            value_item = NumericTableWidgetItem(result.result_value)
            value_item.setData(Qt.ItemDataRole.UserRole, result.result_value)
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(i, 1, value_item)

            # Method column - Set up for proper text sorting
            method_name = self._get_method_name(result)
            method_item = QTableWidgetItem(method_name)
            # Store the method name for sorting (already a string, so it will sort alphabetically)
            method_item.setData(Qt.ItemDataRole.UserRole + 1, method_name)
            self.results_table.setItem(i, 2, method_item)

            # Tags column
            tags_item = QTableWidgetItem()
            tag_display_list = []  # List for the delegate to use for drawing

            if hasattr(result, "tags") and result.tags:
                try:
                    # Get full tag objects so we can display tag names
                    for tag_id in result.tags:
                        tag = self.calculation_db_service.get_tag(tag_id)
                        if tag:
                            # Store tag data for the delegate
                            tag_display_list.append(
                                {"name": tag.name, "color": tag.color, "id": tag.id}
                            )

                    # Create a plain text representation for fallback and tooltip
                    tag_names = [tag["name"] for tag in tag_display_list]
                    plain_text = ", ".join(tag_names) if tag_names else ""
                    tags_item.setText(plain_text)
                    tags_item.setToolTip(plain_text)

                except Exception as e:
                    logger.error(f"Error getting tag data: {e}")

            # Store the tag data for the delegate to use
            tags_item.setData(Qt.ItemDataRole.UserRole, tag_display_list)
            self.results_table.setItem(i, 3, tags_item)

            # Favorite column
            favorite_item = QTableWidgetItem("★" if result.favorite else "")
            favorite_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Store a sortable value for favorites (1 for favorite, 0 for not favorite)
            favorite_item.setData(Qt.ItemDataRole.UserRole + 1, 1 if result.favorite else 0)
            self.results_table.setItem(i, 4, favorite_item)
        
        # Re-enable sorting after populating the table
        self.results_table.setSortingEnabled(True)

    def _get_method_name(self, calculation: CalculationResult) -> str:
        """Get the display name for a calculation method.

        Args:
            calculation: The calculation result

        Returns:
            Display name for the calculation method
        """
        logger.debug(
            f"_get_method_name for input: '{calculation.input_text}'. "
            f"calc_type is: {calculation.calculation_type}, "
            f"type is: {type(calculation.calculation_type)}"
        )

        # Priority 1: Custom method name explicitly set on the result
        if calculation.custom_method_name:
            return f"Custom: {calculation.custom_method_name}"

        # Priority 2: calculation_type is already a CalculationType enum instance
        if isinstance(calculation.calculation_type, CalculationType):
            return calculation.calculation_type.display_name

        # Priority 3: calculation_type is a string - attempt to resolve it
        if isinstance(calculation.calculation_type, str):
            calc_type_str = calculation.calculation_type

            # 3a: Check if it's an enum member NAME (e.g., "HEBREW_STANDARD_VALUE")
            try:
                enum_member = CalculationType[calc_type_str]
                logger.debug(
                    f"Resolved string '{calc_type_str}' to enum member {enum_member.name} by name."
                )
                return enum_member.display_name
            except KeyError:
                pass  # Not a direct enum member name, try other string formats

            # 3b: Check for old stringified tuple format, e.g., "('Hebrew Standard Value', ...)"
            if calc_type_str.startswith("(") and calc_type_str.endswith(")"):
                try:
                    first_quote_start = calc_type_str.find("'")
                    if first_quote_start != -1:
                        first_quote_end = calc_type_str.find("'", first_quote_start + 1)
                        if first_quote_end != -1:
                            potential_display_name = calc_type_str[
                                first_quote_start + 1 : first_quote_end
                            ]
                            logger.debug(
                                f"Parsed display name '{potential_display_name}' from string tuple '{calc_type_str}'."
                            )
                            # Optionally, we could try to match this display name back to a current enum member's display_name
                            # for consistency, but for now, returning the parsed name is a good step.
                            return potential_display_name
                except Exception as e:
                    logger.warning(
                        f"Error parsing string tuple '{calc_type_str}': {e}. Will fallback."
                    )

            # 3c: Handle "CUSTOM_CIPHER" literal string if custom_method_name wasn't set
            if calc_type_str == "CUSTOM_CIPHER":
                logger.debug(
                    "Encountered 'CUSTOM_CIPHER' string as calc_type without a custom_method_name."
                )
                return "Custom Cipher (Name Missing)"

            # 3d: Handle purely numeric strings (e.g., "3") - This is where a specific mapping would be useful
            # For now, we'll just indicate it's a legacy ID.
            if calc_type_str.isdigit():
                logger.warning(
                    f"Encountered numeric string calc_type: '{calc_type_str}'. This is likely an unmappable legacy ID."
                )
                # TODO: Implement a mapping here if old numeric IDs correspond to known method names.
                # Example: legacy_id_map = {"3": "Hebrew Standard Value (Legacy ID)"}
                # if calc_type_str in legacy_id_map: return legacy_id_map[calc_type_str]
                return f"Unmapped Legacy ID: {calc_type_str}"

            # 3e: Fallback for other strings - display as is (could be an old custom name)
            logger.warning(
                f"Treating string calc_type '{calc_type_str}' as a literal display name (possibly legacy)."
            )
            return calc_type_str

        # Priority 4: Fallback for None or any other unexpected type
        if calculation.calculation_type is None:
            logger.warning("_get_method_name: calculation.calculation_type is None.")
            return "Unknown Method (None)"

        logger.error(
            f"_get_method_name: Unexpected type for calculation.calculation_type: "
            f"{type(calculation.calculation_type)} with value '{calculation.calculation_type}'."
        )
        return f"Unknown Method Type ({str(calculation.calculation_type)})"

    def _on_result_selected(self) -> None:
        """Handle selection change in the results table."""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            self.selected_calculation = None
            return

        # Get the calculation result from the first column
        row = selected_items[0].row()
        self.selected_calculation = cast(
            CalculationResult,
            self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole),
        )

        # Emit signal that result was selected
        self.result_selected.emit(self.selected_calculation)

    def _open_detail_window(self, item: QTableWidgetItem) -> None:
        """Open calculation details in a separate window.

        Args:
            item: The table item that was double-clicked
        """
        if not self.selected_calculation or not self.window_manager:
            return

        # Create detail widget
        detail_widget = CalculationDetailWidget(
            self.calculation_db_service, self.custom_cipher_service
        )
        detail_widget.set_calculation(self.selected_calculation)

        # Generate a unique window ID based on the calculation
        window_id = f"calculation_detail_{self.selected_calculation.id}"
        window_title = f"Calculation Details - {self.selected_calculation.input_text}"

        # Open the detail widget in a new window
        self.window_manager.open_window(window_id, detail_widget)

        # Set the window title
        detail_widget.setWindowTitle(window_title)

    def _on_has_tags_changed(self) -> None:
        """Handle changes in the 'Has tags' checkbox."""
        if self.has_tags.isChecked():
            self.tag_combo.setEnabled(True)
        else:
            self.tag_combo.setEnabled(False)

    def _update_tag_combo(self) -> None:
        """Update the tag combo box with available tags."""
        self.tag_combo.clear()
        self.tag_combo.addItem("Any Tag")
        
        try:
            # Get all available tags from the database
            all_tags = self.calculation_db_service.get_all_tags()
            
            # Add each tag to the combo box
            for tag in all_tags:
                self.tag_combo.addItem(tag.name, tag.id)
                
        except Exception as e:
            logger.error(f"Error loading tags for combo box: {e}")
            # Add a fallback option if tags can't be loaded
            self.tag_combo.addItem("Error loading tags")
