"""
@file celestial_data_table_widget.py
@description QTableWidget to display celestial body projection data,
             including Zodiac position, pillar, and cube level.
@author IsopGemini
@created 2024-08-13
@lastModified 2024-08-14
@dependencies PyQt6
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt

class CelestialDataTableWidget(QTableWidget):
    """
    A table widget to display celestial body data including name,
    Ecliptic Longitude/Latitude, Zodiac Position, Projected Pillar/Cube Level,
    and projected X, Y, Z coordinates on the veil.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()

    def _setup_table(self):
        self.setColumnCount(9) # Updated to 9 columns
        self.setHorizontalHeaderLabels([
            "Celestial Body",       # 0
            "Ecliptic Lon (°)",     # 1
            "Ecliptic Lat (°)",     # 2
            "Zodiac Position",      # 3 (New)
            "Projected Pillar",     # 4 (New)
            "Projected Cube Level", # 5 (New)
            "Projected X (Z'B)",    # 6
            "Projected Y (Z'B)",    # 7
            "Projected Z (Z'B)"     # 8
        ])
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Read-only
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Celestial Body
        for i in range(1, 9): # Adjusted loop for new column count
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def update_data(self, projection_data: dict):
        """
        Populates the table with celestial projection data.

        Args:
            projection_data (dict): Data from AdytonOpenGLWidget.get_celestial_projection_data()
                                   Format: {body_name: {'ecl_lon': ..., 'ecl_lat': ..., 
                                                        'zodiac_sign': ..., 'degrees_in_sign': ...,
                                                        'pillar_idx': ..., 'cube_lvl': ...,
                                                        'x': ..., 'y': ..., 'z': ..., 'name': ...}}
        """
        self.setRowCount(0) # Clear existing rows
        if not projection_data:
            return

        sorted_items = sorted(projection_data.items(), key=lambda item: item[0])

        for body_name, body_data_dict in sorted_items:
            if body_data_dict:
                row_position = self.rowCount()
                self.insertRow(row_position)
                
                # Column 0: Celestial Body
                self.setItem(row_position, 0, QTableWidgetItem(str(body_name)))
                
                ecl_lon = body_data_dict.get('ecl_lon')
                ecl_lat = body_data_dict.get('ecl_lat') # True ecliptic latitude
                zodiac_sign = body_data_dict.get('zodiac_sign')
                degrees_in_sign = body_data_dict.get('degrees_in_sign')
                pillar_idx = body_data_dict.get('pillar_idx')
                cube_lvl = body_data_dict.get('cube_lvl')
                proj_x = body_data_dict.get('x')
                proj_y = body_data_dict.get('y')
                proj_z = body_data_dict.get('z')

                # Column 1: Ecliptic Lon
                self.setItem(row_position, 1, QTableWidgetItem(f"{ecl_lon:.2f}°" if ecl_lon is not None else "N/A"))
                # Column 2: Ecliptic Lat
                self.setItem(row_position, 2, QTableWidgetItem(f"{ecl_lat:.2f}°" if ecl_lat is not None else "N/A"))
                # Column 3: Zodiac Position
                self.setItem(row_position, 3, QTableWidgetItem(f"{zodiac_sign} {degrees_in_sign:.2f}°" if zodiac_sign and zodiac_sign != "N/A" and degrees_in_sign is not None else "N/A"))
                # Column 4: Projected Pillar
                self.setItem(row_position, 4, QTableWidgetItem(str(pillar_idx) if pillar_idx is not None else "N/A"))
                # Column 5: Projected Cube Level
                self.setItem(row_position, 5, QTableWidgetItem(str(cube_lvl) if cube_lvl is not None else "N/A"))
                # Column 6: Projected X
                self.setItem(row_position, 6, QTableWidgetItem(f"{proj_x:.2f}" if proj_x is not None else "N/A"))
                # Column 7: Projected Y
                self.setItem(row_position, 7, QTableWidgetItem(f"{proj_y:.2f}" if proj_y is not None else "N/A"))
                # Column 8: Projected Z
                self.setItem(row_position, 8, QTableWidgetItem(f"{proj_z:.2f}" if proj_z is not None else "N/A"))
            else:
                row_position = self.rowCount()
                self.insertRow(row_position)
                self.setItem(row_position, 0, QTableWidgetItem(str(body_name)))
                item_status = QTableWidgetItem("Data Error")
                item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_position, 1, item_status)
                self.setSpan(row_position, 1, 1, 8) # Span status across other 8 columns

        self.resizeRowsToContents() 