import sys
from PyQt6.QtWidgets import QApplication, QTextEdit, QMenu, QInputDialog, QMainWindow
from PyQt6.QtGui import (
    QTextTableFormat,
    QTextCursor,
    QTextTable,
    QTextCharFormat,
    QBrush,
    QTextTableCellFormat,
)
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from .table_properties_dialog import TablePropertiesDialog  # Import the dialog


class TableManager(QObject):
    """Manages table operations for the RTF editor."""

    # Signals
    table_inserted = pyqtSignal(QTextTable)
    table_modified = pyqtSignal()

    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setup_table_menu()

    def setup_table_menu(self):
        """Create the table menu."""
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
        """Return the table menu for the menubar."""
        return self.table_menu

    def get_current_table(self):
        """Get the table at the current cursor position."""
        cursor = self.editor.textCursor()
        return cursor.currentTable()

    def insert_table(self):
        """Insert a new table at the current cursor position."""
        rows, ok = QInputDialog.getInt(
            self.editor, "Insert Table", "Number of rows:", 3, 1, 50, 1
        )
        if not ok:
            return

        cols, ok = QInputDialog.getInt(
            self.editor, "Insert Table", "Number of columns:", 3, 1, 20, 1
        )
        if not ok:
            return

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
        """Add a row after the current row."""
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
        """Remove the current row."""
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
        """Add a column after the current column."""
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
        """Remove the current column."""
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
        """Merge selected cells."""
        table = self.get_current_table()
        if table:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                table.mergeCells(cursor)
                self.table_modified.emit()

    def split_cells(self):
        """Split merged cells."""
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
        """Apply formatting to the current table."""
        table = self.get_current_table()
        if table:
            table.setFormat(table_format)
            self.table_modified.emit()

    def show_table_properties(self):
        """Open a dialog to edit properties of the current table."""
        table = self.get_current_table()
        if not table:
            # Optional: Show a QMessageBox error here instead of printing
            print("Cursor is not inside a table.")
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
        """Helper to apply consistent cell borders after table format change."""
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
