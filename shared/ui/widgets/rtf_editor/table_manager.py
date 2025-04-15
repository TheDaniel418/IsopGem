import sys
from pathlib import Path

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import (
    QTextTable,
    QTextTableCellFormat,
    QTextTableFormat,
)
from PyQt6.QtWidgets import QApplication, QInputDialog, QMainWindow, QMenu, QMessageBox, QTextEdit

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger
from shared.ui.widgets.rtf_editor.utils.error_utils import handle_error, handle_warning
from .table_properties_dialog import TablePropertiesDialog  # Import the dialog

# Initialize logger
logger = get_logger(__name__)


class TableManager(QObject):
    """Manages table operations for the RTF editor.
    
    This class handles all table-related functionality for the RTF editor, including:
    - Creating and inserting tables
    - Modifying table properties (borders, spacing, etc.)
    - Adding and removing rows and columns
    - Merging and splitting cells
    
    It provides a complete table menu with actions for all table operations
    and handles the technical details of working with Qt's table implementation.
    
    Attributes:
        table_inserted (pyqtSignal): Signal emitted when a new table is inserted
        table_modified (pyqtSignal): Signal emitted when a table is modified
        
    Signals:
        table_inserted(QTextTable): Emitted with the new table when inserted
        table_modified(): Emitted when any table property is modified
    """

    # Signals
    table_inserted = pyqtSignal(QTextTable)
    table_modified = pyqtSignal()

    def __init__(self, editor):
        """Initialize the TableManager.
        
        Sets up the table manager with a reference to the editor and
        initializes the table menu.
        
        Args:
            editor (QTextEdit): The text editor where tables will be managed
            
        Returns:
            None
        """
        super().__init__()
        self.editor = editor
        self.setup_table_menu()

    def setup_table_menu(self):
        """Create the table menu.
        
        Sets up the Table menu with all table-related actions, including:
        - Insert table
        - Table properties
        - Add/remove rows and columns
        - Merge/split cells
        
        Returns:
            None
        """
        self.table_menu = QMenu("Table")

        # Insert table
        insert_action = self.table_menu.addAction("Insert Table...")
        insert_action.triggered.connect(self.insert_table)

        self.table_menu.addSeparator()

        # Row operations
        add_row_action = self.table_menu.addAction("Add Row")
        add_row_action.triggered.connect(self.add_row)
        remove_row_action = self.table_menu.addAction("Remove Row")
        remove_row_action.triggered.connect(self.remove_row)

        self.table_menu.addSeparator()

        # Column operations
        add_column_action = self.table_menu.addAction("Add Column")
        add_column_action.triggered.connect(self.add_column)
        remove_column_action = self.table_menu.addAction("Remove Column")
        remove_column_action.triggered.connect(self.remove_column)

        self.table_menu.addSeparator()

        # Cell operations
        merge_cells_action = self.table_menu.addAction("Merge Cells")
        merge_cells_action.triggered.connect(self.merge_cells)
        split_cells_action = self.table_menu.addAction("Split Cells")
        split_cells_action.triggered.connect(self.split_cells)

        self.table_menu.addSeparator()

        # Table Properties
        properties_action = self.table_menu.addAction("Table Properties...")
        properties_action.triggered.connect(self.show_table_properties)

    def get_table_menu(self):
        """Return the table menu for the menubar.
        
        Provides access to the table menu for adding to the main menubar
        or context menu.
        
        Returns:
            QMenu: The table menu with all table-related actions
        """
        return self.table_menu

    def get_current_table(self):
        """Get the table at the current cursor position.
        
        Retrieves the QTextTable at the current cursor position, if any.
        
        Returns:
            QTextTable: The table at the current cursor position, or None if not in a table
        """
        cursor = self.editor.textCursor()
        return cursor.currentTable()

    def insert_table(self):
        """Insert a new table at the current cursor position.
        
        Prompts the user for the number of rows and columns, then creates
        a new table with the specified dimensions at the current cursor position.
        
        The table is created with default properties, which can be modified later
        using the table properties dialog.
        
        Returns:
            None
            
        Signals:
            table_inserted: Emitted with the new table after insertion
        """
        # Get number of rows with validation
        rows, ok = QInputDialog.getInt(
            self.editor, 
            "Insert Table", 
            "Number of rows (1-50):", 
            3,  # Default value
            1,  # Minimum value
            50, # Maximum value - prevent excessive rows
            1   # Step
        )
        if not ok:
            return
            
        # Validate rows (extra safety check)
        if rows < 1 or rows > 50:
            logger.warning(f"Invalid row count: {rows}, constraining to 1-50")
            rows = max(1, min(rows, 50))

        # Get number of columns with validation
        cols, ok = QInputDialog.getInt(
            self.editor, 
            "Insert Table", 
            "Number of columns (1-20):", 
            3,  # Default value
            1,  # Minimum value
            20, # Maximum value - prevent excessive columns
            1   # Step
        )
        if not ok:
            return
            
        # Validate columns (extra safety check)
        if cols < 1 or cols > 20:
            logger.warning(f"Invalid column count: {cols}, constraining to 1-20")
            cols = max(1, min(cols, 20))

        cursor = self.editor.textCursor()

        # Create table format (keep settings simple for now)
        table_format = QTextTableFormat()
        table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)  # Try 0 spacing
        table_format.setBorder(1)  # Back to 1 border width
        table_format.setBorderBrush(Qt.GlobalColor.black)  # Black border
        table_format.setHeaderRowCount(1)
        table_format.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Insert table
        table = cursor.insertTable(rows, cols, table_format)

        # --- Try setting cell borders explicitly ---
        cell_format = QTextTableCellFormat()
        cell_format.setBorder(1)  # Set border on cell format
        cell_format.setBorderBrush(Qt.GlobalColor.black)  # Black border for cells
        cell_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)

        for row in range(rows):
            for col in range(cols):
                cell = table.cellAt(row, col)
                cell.setFormat(cell_format)  # Apply format to the cell
                # Optional: Add text to cells for visual confirmation
                # cell_cursor = cell.firstCursorPosition()
                # cell_cursor.insertText(f"R{row+1}C{col+1}")
        # ------------------------------------------

        self.table_inserted.emit(table)

    def add_row(self):
        """Add a row after the current row.
        
        Inserts a new row after the row containing the current cursor position.
        If the cursor is not in a table, nothing happens.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if a row is added
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            cell = table.cellAt(cursor)
            if cell.isValid():  # Check if cursor is actually in a cell
                row_index = cell.row()
                table.insertRows(row_index + 1, 1)
                self.apply_cell_borders(
                    table, table.format()
                )  # Reapply borders to new cells
                self.table_modified.emit()

    def remove_row(self):
        """Remove the current row.
        
        Removes the row containing the current cursor position.
        If the cursor is not in a table or if it's the last row, nothing happens.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if a row is removed
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            cell = table.cellAt(cursor)
            if cell.isValid():
                row_index = cell.row()
                if table.rows() > 1:  # Don't remove the last row
                    table.removeRows(row_index, 1)
                    self.table_modified.emit()

    def add_column(self):
        """Add a column after the current column.
        
        Inserts a new column after the column containing the current cursor position.
        If the cursor is not in a table, nothing happens.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if a column is added
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            cell = table.cellAt(cursor)
            if cell.isValid():
                col_index = cell.column()
                table.insertColumns(col_index + 1, 1)
                self.apply_cell_borders(
                    table, table.format()
                )  # Reapply borders to new cells
                self.table_modified.emit()

    def remove_column(self):
        """Remove the current column.
        
        Removes the column containing the current cursor position.
        If the cursor is not in a table or if it's the last column, nothing happens.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if a column is removed
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            cell = table.cellAt(cursor)
            if cell.isValid():
                col_index = cell.column()
                if table.columns() > 1:  # Don't remove the last column
                    table.removeColumns(col_index, 1)
                    self.table_modified.emit()

    def merge_cells(self):
        """Merge selected cells.
        
        Merges multiple selected cells into a single cell.
        The selection must be within a table and must include multiple cells.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if cells are merged
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                table.mergeCells(cursor)
                self.table_modified.emit()

    def split_cells(self):
        """Split merged cells.
        
        Splits a merged cell back into individual cells.
        The cursor must be inside a merged cell (one that spans multiple rows or columns).
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if a cell is split
        """
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            cell = table.cellAt(cursor)
            if cell.isValid():
                row_index = cell.row()
                col_index = cell.column()
                # Check if the cell actually spans more than one row or column
                if cell.rowSpan() > 1 or cell.columnSpan() > 1:
                    table.splitCell(row_index, col_index, 1, 1)
                    self.apply_cell_borders(table, table.format())  # Reapply borders
                    self.table_modified.emit()

    def format_table(self, table_format):
        """Apply formatting to the current table.
        
        Applies the specified format to the table at the current cursor position.
        
        Args:
            table_format (QTextTableFormat): The format to apply to the table
            
        Returns:
            None
            
        Signals:
            table_modified: Emitted if the table format is changed
        """
        table = self.get_current_table()
        if table:
            table.setFormat(table_format)
            self.table_modified.emit()

    def show_table_properties(self):
        """Open a dialog to edit properties of the current table.
        
        Displays a dialog allowing the user to modify table properties such as:
        - Border width, style, and color
        - Cell spacing and padding
        - Background color
        - Alignment
        
        If the cursor is not currently inside a table, shows a warning message.
        
        Returns:
            None
            
        Signals:
            table_modified: Emitted if the table properties are changed
            
        Raises:
            Warning: Handled internally if cursor is not in a table
        """
        table = self.get_current_table()
        if not table:
            error_msg = "Cursor is not inside a table."
            handle_warning(self.editor, error_msg)
            return

        current_format = table.format()
        dialog = TablePropertiesDialog(
            current_format, self.editor
        )  # Pass editor as parent

        if dialog.exec():
            new_format = dialog.get_new_format()
            table.setFormat(new_format)
            # Re-apply cell formats to ensure borders render with new table format
            self.apply_cell_borders(table, new_format)
            self.table_modified.emit()

    def apply_cell_borders(self, table, table_format):
        """Helper to apply consistent cell borders after table format change.
        
        Ensures that all cells in the table have consistent border formatting
        that matches the table's overall format. This is necessary because
        Qt's table implementation doesn't automatically propagate border changes
        to all cells.
        
        Args:
            table (QTextTable): The table to update
            table_format (QTextTableFormat): The format to apply to cell borders
            
        Returns:
            None
        """
        cell_format = QTextTableCellFormat()
        cell_format.setBorder(table_format.border())  # Use table's border width
        cell_format.setBorderBrush(
            table_format.borderBrush()
        )  # Use table's border color
        cell_format.setBorderStyle(
            table_format.borderStyle()
        )  # Use table's border style

        rows = table.rows()
        cols = table.columns()
        for row in range(rows):
            for col in range(cols):
                cell = table.cellAt(row, col)
                cell.setFormat(cell_format)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.table_manager = TableManager(self.editor)
        self.menuBar().addMenu(self.table_manager.get_table_menu())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
