"""
/**
 * @file astrology/ui/widgets/stonehenge_predictor/eclipse_catalog_widget.py
 * @description Widget for displaying and interacting with a catalog of solar eclipses.
 * @author Gemini AI Assistant
 * @created YYYY-MM-DD
 * @lastModified YYYY-MM-DD
 * @dependencies PyQt6, astrology.models.eclipse_data, astrology.services.eclipse_catalog_service
 */
"""

from typing import List, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from astrology.models.eclipse_data import EclipseData

# We'll need the service to fetch data. This assumes it's in the services directory.
# from astrology.services.eclipse_catalog_service import EclipseCatalogService
# For __main__ example, we might use a mock or a simplified version if direct import is complex here


class EclipseCatalogWidget(QWidget):
    """
    A widget to display a filterable list of solar eclipses from a catalog.

    Signals:
        eclipse_selected (EclipseData): Emitted when an eclipse is selected
                                        (e.g., by double-clicking).
        view_nasa_map_requested (EclipseData): Emitted when the user wants to view the NASA map
                                     for an eclipse, carrying the whole object.
        create_chart_requested (EclipseData): Emitted when the user wants to create an astrological
                                     chart for an eclipse, carrying the whole object.
    """

    eclipse_selected = pyqtSignal(EclipseData)
    view_nasa_map_requested = pyqtSignal(EclipseData)
    create_chart_requested = pyqtSignal(EclipseData)

    # Store eclipse data associated with table rows
    _eclipse_data_map: dict[int, EclipseData]  # row_index -> EclipseData

    def __init__(self, eclipse_catalog_service, parent: Optional[QWidget] = None):
        """
        Initializes the EclipseCatalogWidget.

        Args:
            eclipse_catalog_service: An instance of the EclipseCatalogService
                                     to fetch eclipse data.
            parent (Optional[QWidget]): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.eclipse_catalog_service = eclipse_catalog_service
        self._eclipse_data_map = {}
        self._init_ui()

    def _init_ui(self) -> None:
        """Initializes the user interface components of the widget."""
        main_layout = QVBoxLayout(self)

        # 1. Filter Controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Year:"))
        self.start_year_spinbox = QSpinBox(self)
        self.start_year_spinbox.setRange(1, 9999)  # Assuming a wide range
        self.start_year_spinbox.setValue(1600)  # Default example
        filter_layout.addWidget(self.start_year_spinbox)

        filter_layout.addWidget(QLabel("End Year:"))
        self.end_year_spinbox = QSpinBox(self)
        self.end_year_spinbox.setRange(1, 9999)
        self.end_year_spinbox.setValue(1700)  # Default example
        filter_layout.addWidget(self.end_year_spinbox)

        self.load_button = QPushButton("Load Eclipses", self)
        self.load_button.clicked.connect(self._load_eclipses)
        filter_layout.addWidget(self.load_button)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # 2. Eclipse Table
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(
            7
        )  # Date, Type, Cat.No., Time, Dur, Event Chart, Map
        self.table_widget.setHorizontalHeaderLabels(
            ["Date", "Type", "Cat. No.", "Time", "Duration", "Event Chart", "View Map"]
        )
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_widget.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Cat.No.
        self.table_widget.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )  # Event Chart
        self.table_widget.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.ResizeMode.ResizeToContents
        )  # View Map
        main_layout.addWidget(self.table_widget)

        # Connect signals
        self.table_widget.itemDoubleClicked.connect(self._on_table_item_double_clicked)

        self.setLayout(main_layout)

    def _load_eclipses(self) -> None:
        """Fetches eclipses using the service based on year filters and populates the table."""
        start_year = self.start_year_spinbox.value()
        end_year = self.end_year_spinbox.value()

        if start_year > end_year:
            # Ideally, show a QMessageBox error here
            print("Start year cannot be after end year.")
            self._clear_table()
            return

        print(f"Loading eclipses from {start_year} to {end_year}...")
        try:
            eclipses = self.eclipse_catalog_service.get_solar_eclipses(
                start_year, end_year
            )
            self._populate_table(eclipses)
            if not eclipses:
                print("No eclipses found for the specified period.")
        except Exception as e:
            print(f"Error loading eclipses: {e}")
            self._clear_table()

    def _clear_table(self) -> None:
        """Clears all rows and data from the table."""
        self.table_widget.setRowCount(0)
        self._eclipse_data_map.clear()

    def _populate_table(self, eclipses: List[EclipseData]) -> None:
        """
        Populates the table widget with the given list of eclipse data.

        Args:
            eclipses (List[EclipseData]): A list of EclipseData objects.
        """
        self._clear_table()
        self.table_widget.setRowCount(len(eclipses))

        for row_idx, eclipse in enumerate(eclipses):
            self._eclipse_data_map[row_idx] = eclipse  # Store data for later retrieval

            date_str = f"{eclipse.year}-{eclipse.month:02d}-{eclipse.day:02d}"
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(date_str))
            self.table_widget.setItem(
                row_idx, 1, QTableWidgetItem(eclipse.eclipse_type)
            )
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(eclipse.cat_no))
            self.table_widget.setItem(
                row_idx, 3, QTableWidgetItem(eclipse.td_ge if eclipse.td_ge else "N/A")
            )
            self.table_widget.setItem(
                row_idx,
                4,
                QTableWidgetItem(
                    eclipse.central_duration if eclipse.central_duration else "N/A"
                ),
            )

            # Add "Event Chart" button instead of path width
            event_chart_button = QPushButton("Event Chart", self)
            event_chart_button.clicked.connect(
                lambda checked, r=row_idx: self._on_create_chart_button_clicked(r)
            )
            self.table_widget.setCellWidget(row_idx, 5, event_chart_button)

            # Add "View Map" button
            view_map_button = QPushButton("View Map", self)
            view_map_button.clicked.connect(
                lambda checked, r=row_idx: self._on_view_map_button_clicked(r)
            )
            self.table_widget.setCellWidget(row_idx, 6, view_map_button)

        # Adjust row heights if necessary, or let it be default
        # self.table_widget.resizeRowsToContents()

    def _on_table_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handles double-click on a table item to select an eclipse."""
        row = item.row()
        if row in self._eclipse_data_map:
            eclipse_data = self._eclipse_data_map[row]
            print(f"Eclipse double-clicked: {eclipse_data.cat_no}")
            self.eclipse_selected.emit(eclipse_data)
        else:
            print(f"Warning: Double-clicked row {row} not found in data map.")

    def _on_view_map_button_clicked(self, row_idx: int) -> None:
        """
        Handles the click of a "View Map" button in a table row.
        Emits the view_nasa_map_requested signal with the catalog number.
        """
        if row_idx in self._eclipse_data_map:
            eclipse_data = self._eclipse_data_map[row_idx]
            print(f"View Map button clicked for: {eclipse_data.cat_no}")
            self.view_nasa_map_requested.emit(eclipse_data)
        else:
            print(f"Warning: View Map button clicked for unknown row {row_idx}.")

    def _on_create_chart_button_clicked(self, row_idx: int) -> None:
        """
        Handles the click of an "Event Chart" button in a table row.
        Emits the create_chart_requested signal with the eclipse data.
        """
        if row_idx in self._eclipse_data_map:
            eclipse_data = self._eclipse_data_map[row_idx]
            print(f"Event Chart button clicked for: {eclipse_data.cat_no}")
            self.create_chart_requested.emit(eclipse_data)
        else:
            print(f"Warning: Event Chart button clicked for unknown row {row_idx}.")

    def get_currently_selected_eclipse_data(self) -> Optional[EclipseData]:
        """
        Retrieves the EclipseData for the currently selected row in the table.

        Returns:
            Optional[EclipseData]: The EclipseData object for the selected row,
                                   or None if no single row is selected or data is not found.
        """
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if len(selected_rows) == 1:
            current_row_index = selected_rows[0].row()
            if current_row_index in self._eclipse_data_map:
                return self._eclipse_data_map[current_row_index]
        return None


# --- Example Usage ---
if __name__ == "__main__":
    import sys

    # This example needs a mock or real EclipseCatalogService
    # For simplicity, let's assume the service file is adjacent or in PYTHONPATH
    try:
        from astrology.services.eclipse_catalog_service import EclipseCatalogService

        pandas_available = True
        try:
            import pandas
        except ImportError:
            pandas_available = False
            print("Pandas not found, EclipseCatalogService might fail.")

    except ImportError:
        print("Could not import EclipseCatalogService for example. Mocking it.")

        class MockEclipseCatalogService:
            def get_solar_eclipses(
                self, start_year: Optional[int] = None, end_year: Optional[int] = None
            ) -> List[EclipseData]:
                print(f"Mock service: Getting eclipses for {start_year}-{end_year}")
                # Return a few dummy EclipseData objects for testing the UI
                sample_eclipses = [
                    EclipseData(
                        year=1605,
                        month=10,
                        day=12,
                        eclipse_type="A",
                        cat_no="05805",
                        magnitude=0.9376,
                        central_duration="07m41s",
                        path_width="250km",
                    ),
                    EclipseData(
                        year=1608,
                        month=3,
                        day=30,
                        eclipse_type="T",
                        cat_no="05815",
                        magnitude=1.045,
                        central_duration="03m50s",
                        path_width="150km",
                    ),
                    EclipseData(
                        year=start_year or 1600,
                        month=1,
                        day=1,
                        eclipse_type="P",
                        cat_no="00001",
                        magnitude=0.5,
                    ),
                ]
                if start_year is not None and end_year is not None:
                    return [
                        e for e in sample_eclipses if start_year <= e.year <= end_year
                    ]
                return sample_eclipses[:1]  # Default return one

        eclipse_service_instance = (
            MockEclipseCatalogService()
        )  # Assign to a consistent variable name
        pandas_available = True  # Mock assumes pandas conceptually worked

    if pandas_available:
        app = QApplication(sys.argv)
        # If using the real service, ensure the CSV path is correct relative to execution
        # For the mock, it doesn't matter.
        if "MockEclipseCatalogService" not in locals():  # If real service was imported
            try:
                # Ensure the instance is assigned to eclipse_service_instance
                eclipse_service_instance = (
                    EclipseCatalogService()
                )  # Uses default CSV path
            except Exception as e:
                print(
                    f"Failed to initialize real EclipseCatalogService: {e}. Using mock."
                )
                # Fallback to mock if real one fails to initialize
                if (
                    "eclipse_service_instance" not in locals()
                ):  # Check if already defined by outer except

                    class MockEclipseCatalogService:  # Redefine mock if not in scope from outer except
                        def get_solar_eclipses(
                            self,
                            start_year: Optional[int] = None,
                            end_year: Optional[int] = None,
                        ) -> List[EclipseData]:
                            print(
                                f"Mock service: Getting eclipses for {start_year}-{end_year}"
                            )
                            sample_eclipses = [
                                EclipseData(
                                    year=1605,
                                    month=10,
                                    day=12,
                                    eclipse_type="A",
                                    cat_no="05805",
                                    magnitude=0.9376,
                                    central_duration="07m41s",
                                    path_width="250km",
                                ),
                                EclipseData(
                                    year=1608,
                                    month=3,
                                    day=30,
                                    eclipse_type="T",
                                    cat_no="05815",
                                    magnitude=1.045,
                                    central_duration="03m50s",
                                    path_width="150km",
                                ),
                                EclipseData(
                                    year=start_year or 1600,
                                    month=1,
                                    day=1,
                                    eclipse_type="P",
                                    cat_no="00001",
                                    magnitude=0.5,
                                ),
                            ]
                            if start_year is not None and end_year is not None:
                                return [
                                    e
                                    for e in sample_eclipses
                                    if start_year <= e.year <= end_year
                                ]
                            return sample_eclipses[:1]

                    eclipse_service_instance = MockEclipseCatalogService()

        # Use the consistently named instance variable
        main_window = EclipseCatalogWidget(eclipse_service_instance)
        main_window.setWindowTitle("Solar Eclipse Catalog Viewer")
        main_window.setGeometry(100, 100, 800, 500)
        main_window.show()
        sys.exit(app.exec())
    else:
        print(
            "Cannot run example without pandas for EclipseCatalogService or if its import failed."
        )
