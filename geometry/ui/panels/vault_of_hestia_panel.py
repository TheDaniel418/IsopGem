"""
@file vault_of_hestia_panel.py
@description Panel for exploring the Vault of Hestia geometric design: a square, an isosceles triangle, and an inscribed circle.
@author Daniel (AI-generated)
@created 2024-06-09
@lastModified 2024-06-09
@dependencies PyQt6, shared.ui.widgets.panel.Panel
@example
    panel = VaultOfHestiaPanel()
"""

from PyQt6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QDoubleSpinBox, QFormLayout, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QGroupBox, QPushButton, QScrollArea
from shared.ui.widgets.panel import Panel
import math
import weakref

class VaultOfHestiaDiagram(QWidget):
    """
    @class VaultOfHestiaDiagram
    @description Widget for drawing the Vault of Hestia diagram: square, isosceles triangle, and inscribed circle.
    @param parent QWidget parent
    @param triangle_side float, side length of the square
    @param triangle_height float, height of the isosceles triangle
    @example
        diagram = VaultOfHestiaDiagram(triangle_side=200, triangle_height=200)
    """
    def __init__(self, triangle_side=200, triangle_height=200, parent=None):
        super().__init__(parent)
        self.triangle_side = triangle_side
        self.triangle_height = triangle_height
        self.setFixedSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_geometry(self, triangle_side, triangle_height):
        self.triangle_side = triangle_side
        self.triangle_height = triangle_height
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Draw a static Vault of Hestia diagram at fixed pixel size (e.g., 280x280 square)
        margin = 20
        S = 280  # Fixed pixel size for the square
        H = 280  # Fixed pixel height for the triangle
        left = margin
        top = margin
        # Draw square
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(QRectF(left, top + H - S, S, S))
        # Draw isosceles triangle
        base_y = top + H
        apex = QPointF(left + S/2, top)
        left_base = QPointF(left, base_y)
        right_base = QPointF(left + S, base_y)
        painter.drawLine(apex, left_base)
        painter.drawLine(apex, right_base)
        painter.drawLine(left_base, right_base)
        # Draw incircle for this fixed triangle
        a = math.hypot(S/2, H)
        b = S
        s = (a + a + b) / 2
        area = (b * H) / 2
        r = area / s
        center_x = left + S/2
        center_y = base_y - r
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(QPointF(center_x, center_y), r, r)

class VaultOfHestiaPanel(Panel):
    """
    @class VaultOfHestiaPanel
    @description Panel for exploring the Vault of Hestia geometric design.
    @example
        panel = VaultOfHestiaPanel()
    """
    def __init__(self, parent=None):
        super().__init__("The Vault of Hestia", parent)
        self.side_length = 200.0
        self.diagram = VaultOfHestiaDiagram(self.side_length, self.side_length)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(24)
        # --- Left Pane: Calculations and Info ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(18)
        desc = QLabel(
            "<b>The Vault of Hestia</b> is a geometric design consisting of a square, "
            "an isosceles triangle whose base is parallel to the square's base, and an inscribed circle "
            "tangent to the triangle's sides. This construction explores symmetry, ratios, and the beauty of classical geometry."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #333; background: #eaf6fb; border-radius: 8px; padding: 8px 12px;")
        left_layout.addWidget(desc)
        # Section header for editable fields
        editable_header = QLabel("<span style='font-size:16px; font-weight:bold; color:#1976d2;'>✏️ Editable Fields</span>")
        editable_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(editable_header)
        # Editable fields group
        editable_group = QGroupBox()
        editable_group.setStyleSheet("QGroupBox { background: #f0f8ff; border: 1px solid #b3d1e6; border-radius: 8px; margin-top: 8px; }")
        editable_layout = QFormLayout(editable_group)
        editable_layout.setSpacing(8)
        spin_style = (
            "QDoubleSpinBox { background: #e3f2fd; border-radius: 6px; padding: 4px 8px; font-size: 14px; }"
            "QDoubleSpinBox:focus { border: 2px solid #1976d2; background: #bbdefb; }"
        )
        self.side_spin = QDoubleSpinBox(); self.side_spin.setRange(1, 10000); self.side_spin.setDecimals(6); self.side_spin.setStyleSheet(spin_style)
        self.height_spin = QDoubleSpinBox(); self.height_spin.setRange(1, 10000); self.height_spin.setDecimals(6); self.height_spin.setStyleSheet(spin_style)
        self.radius_spin = QDoubleSpinBox(); self.radius_spin.setRange(1, 10000); self.radius_spin.setDecimals(6); self.radius_spin.setStyleSheet(spin_style)
        self.area_circle_spin = QDoubleSpinBox(); self.area_circle_spin.setRange(1, 1e8); self.area_circle_spin.setDecimals(6); self.area_circle_spin.setStyleSheet(spin_style)
        self.area_triangle_spin = QDoubleSpinBox(); self.area_triangle_spin.setRange(1, 1e8); self.area_triangle_spin.setDecimals(6); self.area_triangle_spin.setStyleSheet(spin_style)
        self.area_square_spin = QDoubleSpinBox(); self.area_square_spin.setRange(1, 1e8); self.area_square_spin.setDecimals(6); self.area_square_spin.setStyleSheet(spin_style)
        self.circumference_spin = QDoubleSpinBox(); self.circumference_spin.setRange(1, 1e8); self.circumference_spin.setDecimals(6); self.circumference_spin.setStyleSheet(spin_style)
        self.hypotenuse_spin = QDoubleSpinBox(); self.hypotenuse_spin.setRange(1, 1e8); self.hypotenuse_spin.setDecimals(6); self.hypotenuse_spin.setStyleSheet(spin_style)
        self.side_spin.setToolTip("Length of the square's side (editable)")
        self.height_spin.setToolTip("Height of the isosceles triangle (editable)")
        self.radius_spin.setToolTip("Radius of the inscribed circle (editable)")
        self.area_circle_spin.setToolTip("Area of the inscribed circle (editable)")
        self.area_triangle_spin.setToolTip("Area of the isosceles triangle (editable)")
        self.area_square_spin.setToolTip("Area of the square (editable)")
        self.circumference_spin.setToolTip("Circumference of the inscribed circle (editable)")
        self.hypotenuse_spin.setToolTip("Hypotenuse (side) of the isosceles triangle (editable)")
        editable_layout.addRow("Square Side Length:", self.side_spin)
        editable_layout.addRow("Triangle Height:", self.height_spin)
        editable_layout.addRow("Circle Radius:", self.radius_spin)
        editable_layout.addRow("Area of the Circle:", self.area_circle_spin)
        editable_layout.addRow("Area of the Triangle:", self.area_triangle_spin)
        editable_layout.addRow("Area of the Square:", self.area_square_spin)
        editable_layout.addRow("Circumference of the Circle:", self.circumference_spin)
        editable_layout.addRow("Hypotenuse (Triangle Side):", self.hypotenuse_spin)
        left_layout.addWidget(editable_group)
        # Section header for static fields
        static_header = QLabel("<span style='font-size:16px; font-weight:bold; color:#607d8b;'>🔒 Area Differences (Read-Only)</span>")
        static_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(static_header)
        # Static fields group
        static_group = QGroupBox()
        static_group.setStyleSheet("QGroupBox { background: #f8f8f8; border: 1px solid #bdbdbd; border-radius: 8px; margin-top: 8px; }")
        static_layout = QFormLayout(static_group)
        static_layout.setSpacing(8)
        self.square_minus_circle_label = QLabel(); self.square_minus_circle_label.setToolTip("Area of square minus area of circle (read-only)")
        self.square_minus_triangle_label = QLabel(); self.square_minus_triangle_label.setToolTip("Area of square minus area of triangle (read-only)")
        self.triangle_minus_circle_label = QLabel(); self.triangle_minus_circle_label.setToolTip("Area of triangle minus area of circle (read-only)")
        static_layout.addRow("Area of Square - Area of Circle:", self.square_minus_circle_label)
        static_layout.addRow("Area of Square - Area of Triangle:", self.square_minus_triangle_label)
        static_layout.addRow("Area of Triangle - Area of Circle:", self.triangle_minus_circle_label)
        left_layout.addWidget(static_group)
        # --- Golden Ratio Relationships ---
        golden_group = QGroupBox("Golden Ratio Relationships")
        golden_group.setStyleSheet("QGroupBox { background: #fff8e1; border: 1.5px solid #ffd54f; border-radius: 8px; margin-top: 8px; }")
        golden_layout = QFormLayout(golden_group)
        golden_layout.setSpacing(8)
        self.em_label = QLabel(); self.eh_label = QLabel(); self.hm_label = QLabel(); self.em_eh_ratio_label = QLabel()
        self.de2_label = QLabel(); self.ae_label = QLabel(); self.de2_hm_sum_label = QLabel(); self.de2_hm_ae_compare_label = QLabel()
        self.area_sum_label = QLabel(); self.area_sum_compare_label = QLabel()
        self.perimeter_aeb_label = QLabel(); self.perimeter_adem_label = QLabel(); self.perimeter_compare_label = QLabel()
        self.golden_rect_label = QLabel()
        golden_layout.addRow("EM (altitude):", self.em_label)
        golden_layout.addRow("EH (apex to circle):", self.eh_label)
        golden_layout.addRow("HM (circle to base):", self.hm_label)
        golden_layout.addRow("EM/EH:", self.em_eh_ratio_label)
        golden_layout.addRow("DE/2:", self.de2_label)
        golden_layout.addRow("HM:", self.hm_label)
        golden_layout.addRow("AE (hypotenuse):", self.ae_label)
        golden_layout.addRow("DE/2 + HM:", self.de2_hm_sum_label)
        golden_layout.addRow("Compare to AE:", self.de2_hm_ae_compare_label)
        golden_layout.addRow("Area ADE + BCE:", self.area_sum_label)
        golden_layout.addRow("Compare to 2·diam·φ³:", self.area_sum_compare_label)
        golden_layout.addRow("Perimeter AEB:", self.perimeter_aeb_label)
        golden_layout.addRow("Perimeter ADEM:", self.perimeter_adem_label)
        golden_layout.addRow("Compare perimeters:", self.perimeter_compare_label)
        golden_layout.addRow("Golden Rectangle:", self.golden_rect_label)
        left_layout.addWidget(golden_group)
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("QPushButton { background: #1976d2; color: white; border-radius: 6px; padding: 8px 18px; font-size: 14px; font-weight: bold; } QPushButton:hover { background: #1565c0; }")
        reset_btn.setToolTip("Restore all fields to default values")
        reset_btn.clicked.connect(self._reset_fields)
        left_layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignRight)
        left_layout.addStretch(1)
        left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Wrap left_widget in a scroll area for overflow
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_widget)
        left_scroll.setMinimumWidth(380)
        # --- Right Pane: Diagram ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Custom diagram container
        diagram_container = QWidget()
        diagram_container.setStyleSheet("background: #f5faff; border: 1.5px solid #b3d1e6; border-radius: 12px;")
        diagram_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        diagram_layout = QVBoxLayout(diagram_container)
        diagram_layout.setContentsMargins(20, 20, 20, 12)
        self.diagram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        diagram_layout.addWidget(self.diagram, alignment=Qt.AlignmentFlag.AlignCenter)
        diagram_caption = QLabel("<i>Vault of Hestia Construction</i>")
        diagram_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diagram_caption.setStyleSheet("color: #607d8b; font-size: 13px; margin-top: 6px;")
        diagram_layout.addWidget(diagram_caption)
        # --- Reference Image ---
        ref_img_label = ScalableImageLabel("assets/geometry/hestia_geometry.png")
        ref_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_img_label.setStyleSheet("background: #fff; border: 1px solid #bdbdbd; border-radius: 8px; margin-top: 8px;")
        ref_img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ref_img_label.setMinimumHeight(180)
        ref_caption = QLabel("<i>Reference Diagram</i>")
        ref_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_caption.setStyleSheet("color: #607d8b; font-size: 13px; margin-top: 4px;")
        # Add widgets to right_layout with stretch factors
        right_layout.addWidget(diagram_container, stretch=2)
        right_layout.addWidget(ref_img_label, stretch=2)
        right_layout.addWidget(ref_caption, alignment=Qt.AlignmentFlag.AlignTop)
        right_layout.addStretch(1)
        # --- Make right pane scrollable ---
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_widget)
        # --- Add Panes to Main Layout ---
        main_layout.addWidget(left_scroll, stretch=0)
        main_layout.addWidget(right_scroll, stretch=1)
        self.setMinimumHeight(600)
        self.content_layout.addLayout(main_layout)
        self._connect_editable_fields()
        self._update_properties()

    def _connect_editable_fields(self):
        # Add highlight animation and validation on value change
        for spin in [self.side_spin, self.height_spin, self.radius_spin, self.area_circle_spin, self.area_triangle_spin, self.area_square_spin, self.circumference_spin, self.hypotenuse_spin]:
            spin.editingFinished.connect(lambda s=spin: self._on_field_edited(s))
        self.side_spin.editingFinished.connect(lambda: self._recalculate_from('side'))
        self.height_spin.editingFinished.connect(lambda: self._recalculate_from('height'))
        self.radius_spin.editingFinished.connect(lambda: self._recalculate_from('radius'))
        self.area_circle_spin.editingFinished.connect(lambda: self._recalculate_from('area_circle'))
        self.area_triangle_spin.editingFinished.connect(lambda: self._recalculate_from('area_triangle'))
        self.area_square_spin.editingFinished.connect(lambda: self._recalculate_from('area_square'))
        self.circumference_spin.editingFinished.connect(lambda: self._recalculate_from('circumference'))
        self.hypotenuse_spin.editingFinished.connect(lambda: self._recalculate_from('hypotenuse'))

    def _on_field_edited(self, spin):
        # Animate highlight
        orig_style = spin.styleSheet()
        highlight = orig_style + "QDoubleSpinBox { background: #fffde7; border: 2px solid #ffd54f; }"
        spin.setStyleSheet(highlight)
        spin_ref = weakref.ref(spin)
        QTimer.singleShot(400, lambda: spin_ref() and spin_ref().setStyleSheet(orig_style))
        # Validate
        if spin.value() < spin.minimum() or spin.value() > spin.maximum():
            spin.setStyleSheet(orig_style + "QDoubleSpinBox { border: 2px solid #d32f2f; background: #ffebee; }")
            spin.setToolTip("Value out of allowed range!")
        else:
            spin.setToolTip(spin.toolTip().replace("Value out of allowed range!", ""))

    def _reset_fields(self):
        self._block_signals(True)
        self.side_spin.setValue(200.0)
        self.height_spin.setValue(200.0)
        self.radius_spin.setValue(self._calc_radius(200.0, 200.0))
        self.area_circle_spin.setValue(math.pi * self.radius_spin.value() ** 2)
        self.area_triangle_spin.setValue(0.5 * 200.0 * 200.0)
        self.area_square_spin.setValue(200.0 * 200.0)
        self.circumference_spin.setValue(2 * math.pi * self.radius_spin.value())
        self.hypotenuse_spin.setValue(math.hypot(200.0/2, 200.0))
        self._block_signals(False)
        self._update_properties()

    def _recalculate_from(self, field):
        # Get current values
        S = self.side_spin.value()
        H = self.height_spin.value()
        r = self.radius_spin.value()
        area_c = self.area_circle_spin.value()
        area_t = self.area_triangle_spin.value()
        area_s = self.area_square_spin.value()
        circ = self.circumference_spin.value()
        hypo = self.hypotenuse_spin.value()
        pi = math.pi
        # Determine which field was edited and recalculate base values
        if field == 'side':
            S = self.side_spin.value(); H = S; r = self._calc_radius(S, H)
        elif field == 'height':
            H = self.height_spin.value(); S = H; r = self._calc_radius(S, H)
        elif field == 'radius':
            r = self.radius_spin.value(); S = self._side_from_radius(r); H = S
        elif field == 'area_circle':
            r = math.sqrt(area_c / pi); S = self._side_from_radius(r); H = S
        elif field == 'area_triangle':
            area_t = self.area_triangle_spin.value(); S = math.sqrt(2 * area_t); H = S; r = self._calc_radius(S, H)
        elif field == 'area_square':
            S = math.sqrt(area_s); H = S; r = self._calc_radius(S, H)
        elif field == 'circumference':
            r = circ / (2 * pi); S = self._side_from_radius(r); H = S
        elif field == 'hypotenuse':
            S = self._side_from_hypotenuse(hypo); H = S; r = self._calc_radius(S, H)
        # Update all fields
        self._block_signals(True)
        self.side_spin.setValue(S)
        self.height_spin.setValue(H)
        self.radius_spin.setValue(r)
        self.area_circle_spin.setValue(pi * r * r)
        self.area_triangle_spin.setValue(0.5 * S * H)
        self.area_square_spin.setValue(S * S)
        self.circumference_spin.setValue(2 * pi * r)
        self.hypotenuse_spin.setValue(math.hypot(S/2, S))
        self._block_signals(False)
        self._update_properties()

    def _block_signals(self, block):
        for spin in [self.side_spin, self.height_spin, self.radius_spin, self.area_circle_spin, self.area_triangle_spin, self.area_square_spin, self.circumference_spin, self.hypotenuse_spin]:
            spin.blockSignals(block)

    def _calc_radius(self, S, H):
        a = math.hypot(S/2, H); b = S; s = (a + a + b) / 2; area = (b * H) / 2; return area / s
    def _side_from_radius(self, r):
        def f(x):
            a = math.hypot(x/2, x); b = x; s = (a + a + b) / 2; area = (b * x) / 2; return area / s - r
        x = max(r * 2, 1.0)
        for _ in range(20):
            fx = f(x); d = 1e-5; dfx = (f(x + d) - fx) / d
            if abs(dfx) < 1e-8: break
            x_new = x - fx / dfx
            if abs(x_new - x) < 1e-6: break
            x = x_new
        return max(x, 1.0)
    def _side_from_hypotenuse(self, hypo):
        # hypo^2 = (S/2)^2 + S^2 => S = 2 * hypo / sqrt(5)
        return 2 * hypo / math.sqrt(5)

    def _update_properties(self):
        S = self.side_spin.value(); H = self.height_spin.value(); r = self.radius_spin.value(); pi = math.pi
        area_c = pi * r * r
        area_t = 0.5 * S * H
        area_s = S * S
        circ = 2 * pi * r
        hypo = math.hypot(S/2, S)
        self.square_minus_circle_label.setText(f"{area_s - area_c:.6f}")
        self.square_minus_triangle_label.setText(f"{area_s - area_t:.6f}")
        self.triangle_minus_circle_label.setText(f"{area_t - area_c:.6f}")
        # Update diagram
        self.diagram.set_geometry(S, H)
        # --- Golden Ratio Relationships ---
        phi = (1 + math.sqrt(5)) / 2
        # EM = H (altitude), EH = H - r, HM = r
        EM = H
        EH = H - r
        HM = r
        em_eh_ratio = EM / EH if EH != 0 else float('inf')
        # DE/2 = S/2, AE = hypo, DE/2 + HM
        DE2 = S / 2
        AE = hypo
        DE2_HM_sum = DE2 + HM
        # Compare DE2 + HM to AE
        de2_hm_ae_diff = abs(DE2_HM_sum - AE)
        # Area sum: ADE + BCE (each is 0.5 * S * H / 2)
        area_ade = 0.5 * S * H / 2
        area_bce = 0.5 * S * H / 2
        area_sum = area_ade + area_bce
        area_sum_compare = 2 * (2 * r) * phi**3
        area_sum_diff = abs(area_sum - area_sum_compare)
        # Perimeter of triangle AEB: 2*AE + S
        perimeter_aeb = 2 * AE + S
        # Perimeter of golden rectangle ADEM: 2*(S + S/phi)
        golden_rect_long = S
        golden_rect_short = S / phi
        perimeter_adem = 2 * (golden_rect_long + golden_rect_short)
        perimeter_diff = abs(perimeter_aeb - perimeter_adem)
        # Golden rectangle label
        golden_rect_str = f"{golden_rect_long:.6f} × {golden_rect_short:.6f} (long × short)"
        # Highlight if close to phi
        def goldify(label, value, target=phi, tol=0.01):
            if abs(value - target) / target < tol:
                label.setStyleSheet("color: #bfa100; font-weight: bold;")
            else:
                label.setStyleSheet("")
        self.em_label.setText(f"{EM:.6f}")
        self.eh_label.setText(f"{EH:.6f}")
        self.hm_label.setText(f"{HM:.6f}")
        self.em_eh_ratio_label.setText(f"{em_eh_ratio:.6f} (φ={phi:.6f})")
        goldify(self.em_eh_ratio_label, em_eh_ratio)
        self.de2_label.setText(f"{DE2:.6f}")
        self.ae_label.setText(f"{AE:.6f}")
        self.de2_hm_sum_label.setText(f"{DE2_HM_sum:.6f}")
        self.de2_hm_ae_compare_label.setText(f"Δ={de2_hm_ae_diff:.6f}")
        self.area_sum_label.setText(f"{area_sum:.6f}")
        self.area_sum_compare_label.setText(f"{area_sum_compare:.6f} (Δ={area_sum_diff:.6f})")
        self.perimeter_aeb_label.setText(f"{perimeter_aeb:.6f}")
        self.perimeter_adem_label.setText(f"{perimeter_adem:.6f}")
        self.perimeter_compare_label.setText(f"Δ={perimeter_diff:.6f}")
        self.golden_rect_label.setText(golden_rect_str)

# --- ScalableImageLabel helper class ---
class ScalableImageLabel(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(image_path)
        self.setScaledContents(False)
        self.setMinimumHeight(60)
        self.setMaximumHeight(10000)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._update_pixmap()
    def resizeEvent(self, event):
        self._update_pixmap()
        super().resizeEvent(event)
    def _update_pixmap(self):
        if not self._pixmap.isNull():
            # Scale to fit height, maintain aspect ratio
            scaled = self._pixmap.scaledToHeight(self.height(), Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(scaled) 