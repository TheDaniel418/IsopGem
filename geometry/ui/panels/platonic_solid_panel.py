"""
Platonic Solid Calculator Panel.

This module provides a UI panel for calculating properties of Platonic solids.
"""

import math
from typing import List, Tuple

import numpy as np
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtDataVisualization import (
    Q3DCamera,
    Q3DScatter,
    Q3DTheme,
    QAbstract3DGraph,
    QScatter3DSeries,
    QScatterDataItem,
    QScatterDataProxy,
)
from PyQt6.QtGui import QColor, QVector3D
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.platonic_solid_calculator import (
    PlatonicSolidCalculator,
    PlatonicSolidType,
)
from geometry.ui.widgets.platonic_solid_opengl_widget import PlatonicSolidOpenGLWidget


class PlatonicSolidVisualization(QWidget):
    """Widget for visualizing a Platonic solid in 3D."""

    def __init__(self, parent=None):
        """Initialize the visualization widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = PlatonicSolidCalculator()
        self.show_insphere = True
        self.show_midsphere = True
        self.show_circumsphere = True
        self.show_vertices = True
        self.show_edges = True
        self.show_faces = False
        self.rotation_x = 30.0
        self.rotation_y = 40.0
        self.zoom = 1.0

        # Set minimum size for better visualization
        self.setMinimumSize(400, 400)

        # Create layout
        layout = QVBoxLayout(self)

        # Create 3D scatter graph
        self.graph = Q3DScatter()
        self.container = QWidget.createWindowContainer(self.graph)
        self.container.setMinimumSize(QSize(400, 400))
        self.container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.container)

        # Create control layout
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        # Create rotation sliders
        rotation_group = QGroupBox("Camera Controls")
        rotation_layout = QVBoxLayout(rotation_group)

        # X rotation
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Rotation:"))
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(0, 360)
        self.x_slider.setValue(int(self.rotation_x))
        self.x_slider.valueChanged.connect(self._update_rotation)
        x_layout.addWidget(self.x_slider)
        rotation_layout.addLayout(x_layout)

        # Y rotation
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Rotation:"))
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(0, 360)
        self.y_slider.setValue(int(self.rotation_y))
        self.y_slider.valueChanged.connect(self._update_rotation)
        y_layout.addWidget(self.y_slider)
        rotation_layout.addLayout(y_layout)

        # Zoom
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(int(self.zoom * 100))
        self.zoom_slider.valueChanged.connect(self._update_zoom)
        zoom_layout.addWidget(self.zoom_slider)
        rotation_layout.addLayout(zoom_layout)

        # Camera presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            [
                "Isometric",
                "Front",
                "Right",
                "Top",
                "Front Right",
                "Front Top",
                "Right Top",
            ]
        )
        self.preset_combo.currentIndexChanged.connect(self._update_camera_preset)
        preset_layout.addWidget(self.preset_combo)
        rotation_layout.addLayout(preset_layout)

        # Reset button
        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset View")
        self.reset_button.clicked.connect(self._reset_camera)
        reset_layout.addWidget(self.reset_button)
        rotation_layout.addLayout(reset_layout)

        control_layout.addWidget(rotation_group)

        # Create appearance controls
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)

        # Vertex size
        vertex_size_layout = QHBoxLayout()
        vertex_size_layout.addWidget(QLabel("Vertex Size:"))
        self.vertex_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.vertex_size_slider.setRange(5, 30)
        self.vertex_size_slider.setValue(12)
        self.vertex_size_slider.valueChanged.connect(self._update_vertex_size)
        vertex_size_layout.addWidget(self.vertex_size_slider)
        appearance_layout.addLayout(vertex_size_layout)

        # Edge size
        edge_size_layout = QHBoxLayout()
        edge_size_layout.addWidget(QLabel("Edge Size:"))
        self.edge_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.edge_size_slider.setRange(1, 15)
        self.edge_size_slider.setValue(5)
        self.edge_size_slider.valueChanged.connect(self._update_edge_size)
        edge_size_layout.addWidget(self.edge_size_slider)
        appearance_layout.addLayout(edge_size_layout)

        # Sphere size
        sphere_size_layout = QHBoxLayout()
        sphere_size_layout.addWidget(QLabel("Sphere Size:"))
        self.sphere_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.sphere_size_slider.setRange(1, 10)
        self.sphere_size_slider.setValue(3)
        self.sphere_size_slider.valueChanged.connect(self._update_sphere_size)
        sphere_size_layout.addWidget(self.sphere_size_slider)
        appearance_layout.addLayout(sphere_size_layout)

        # Shadow quality
        shadow_layout = QHBoxLayout()
        shadow_layout.addWidget(QLabel("Shadows:"))
        self.shadow_combo = QComboBox()
        self.shadow_combo.addItems(
            ["None", "Low", "Medium", "High", "Soft Low", "Soft Medium", "Soft High"]
        )
        self.shadow_combo.setCurrentIndex(6)  # Soft High
        self.shadow_combo.currentIndexChanged.connect(self._update_shadow_quality)
        shadow_layout.addWidget(self.shadow_combo)
        appearance_layout.addLayout(shadow_layout)

        # Display options
        display_layout = QVBoxLayout()

        # Show vertices
        self.show_vertices_check = QCheckBox("Show Vertices")
        self.show_vertices_check.setChecked(True)
        self.show_vertices_check.toggled.connect(self._toggle_vertices)
        display_layout.addWidget(self.show_vertices_check)

        # Show edges
        self.show_edges_check = QCheckBox("Show Edges")
        self.show_edges_check.setChecked(True)
        self.show_edges_check.toggled.connect(self._toggle_edges)
        display_layout.addWidget(self.show_edges_check)

        # Show transparent faces
        self.show_faces_check = QCheckBox("Show Transparent Faces")
        self.show_faces_check.setChecked(False)
        self.show_faces_check.toggled.connect(self._toggle_faces)
        display_layout.addWidget(self.show_faces_check)

        appearance_layout.addLayout(display_layout)

        control_layout.addWidget(appearance_group)

        # Setup the graph
        self._setup_graph()

    def _setup_graph(self):
        """Set up the 3D graph."""
        # Set up the graph
        self.graph.setAspectRatio(1.0)
        self.graph.setHorizontalAspectRatio(1.0)
        self.graph.setShadowQuality(
            QAbstract3DGraph.ShadowQuality.ShadowQualitySoftHigh
        )

        # Set up a custom theme
        theme = self.graph.activeTheme()
        theme.setType(Q3DTheme.Theme.ThemeUserDefined)
        theme.setBackgroundEnabled(True)
        theme.setBackgroundColor(QColor(240, 240, 245))
        theme.setWindowColor(QColor(255, 255, 255))
        theme.setLabelBackgroundEnabled(False)
        theme.setLabelBorderEnabled(False)
        theme.setFont(self.font())
        theme.setLightColor(QColor(255, 255, 255))
        theme.setBaseColors(
            [QColor(190, 190, 255), QColor(255, 190, 190), QColor(190, 255, 190)]
        )
        theme.setColorStyle(Q3DTheme.ColorStyle.ColorStyleObjectGradient)
        theme.setLightStrength(5.0)  # Valid range is 0.0 to 10.0
        theme.setAmbientLightStrength(0.5)
        theme.setGridEnabled(False)  # Disable grid lines

        # Set up the camera
        camera = self.graph.scene().activeCamera()
        camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetIsometricRightHigh)
        camera.setZoomLevel(120)

        # Hide the axes for a cleaner look
        self.graph.axisX().setTitleVisible(False)
        self.graph.axisY().setTitleVisible(False)
        self.graph.axisZ().setTitleVisible(False)

        # Hide labels by setting empty format
        self.graph.axisX().setLabelFormat("")
        self.graph.axisY().setLabelFormat("")
        self.graph.axisZ().setLabelFormat("")

        # Create series for the solid vertices
        self.vertex_proxy = QScatterDataProxy()
        self.vertex_series = QScatter3DSeries(self.vertex_proxy)
        self.vertex_series.setItemSize(0.12)
        self.vertex_series.setMeshSmooth(True)
        self.vertex_series.setBaseColor(QColor(50, 50, 200))
        self.vertex_series.setVisible(self.show_vertices)
        self.graph.addSeries(self.vertex_series)

        # Create series for the solid edges
        self.edge_proxy = QScatterDataProxy()
        self.edge_series = QScatter3DSeries(self.edge_proxy)
        self.edge_series.setItemSize(0.05)
        self.edge_series.setMeshSmooth(True)
        self.edge_series.setBaseColor(QColor(20, 20, 20))
        self.edge_series.setVisible(self.show_edges)
        self.graph.addSeries(self.edge_series)

        # Create series for the solid faces
        self.face_proxy = QScatterDataProxy()
        self.face_series = QScatter3DSeries(self.face_proxy)
        self.face_series.setItemSize(0.08)
        self.face_series.setMeshSmooth(True)
        self.face_series.setBaseColor(
            QColor(100, 150, 255, 80)
        )  # Semi-transparent blue
        self.face_series.setVisible(self.show_faces)
        self.graph.addSeries(self.face_series)

        # Create series for the insphere
        self.insphere_proxy = QScatterDataProxy()
        self.insphere_series = QScatter3DSeries(self.insphere_proxy)
        self.insphere_series.setItemSize(0.03)
        self.insphere_series.setMeshSmooth(True)
        self.insphere_series.setBaseColor(QColor(255, 100, 100, 100))
        self.graph.addSeries(self.insphere_series)

        # Create series for the midsphere
        self.midsphere_proxy = QScatterDataProxy()
        self.midsphere_series = QScatter3DSeries(self.midsphere_proxy)
        self.midsphere_series.setItemSize(0.03)
        self.midsphere_series.setMeshSmooth(True)
        self.midsphere_series.setBaseColor(QColor(100, 255, 100, 100))
        self.graph.addSeries(self.midsphere_series)

        # Create series for the circumsphere
        self.circumsphere_proxy = QScatterDataProxy()
        self.circumsphere_series = QScatter3DSeries(self.circumsphere_proxy)
        self.circumsphere_series.setItemSize(0.03)
        self.circumsphere_series.setMeshSmooth(True)
        self.circumsphere_series.setBaseColor(QColor(100, 100, 255, 100))
        self.graph.addSeries(self.circumsphere_series)

        # Update the visualization
        self._update_visualization()

    def _update_rotation(self):
        """Update the rotation of the graph."""
        self.rotation_x = self.x_slider.value()
        self.rotation_y = self.y_slider.value()
        self.graph.scene().activeCamera().setXRotation(self.rotation_x)
        self.graph.scene().activeCamera().setYRotation(self.rotation_y)

    def _update_zoom(self):
        """Update the zoom of the graph."""
        self.zoom = self.zoom_slider.value() / 100.0
        self.graph.scene().activeCamera().setZoomLevel(self.zoom * 100)

    def _update_camera_preset(self, index):
        """Update the camera preset.

        Args:
            index: The index of the selected preset.
        """
        camera = self.graph.scene().activeCamera()
        if index == 0:  # Isometric
            camera.setCameraPreset(
                Q3DCamera.CameraPreset.CameraPresetIsometricRightHigh
            )
        elif index == 1:  # Front
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetFrontHigh)
        elif index == 2:  # Right
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetRightHigh)
        elif index == 3:  # Top
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetDirectlyAbove)
        elif index == 4:  # Front Right
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetIsometricRight)
        elif index == 5:  # Front Top
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetFrontHigh)
        elif index == 6:  # Right Top
            camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetRightHigh)

        # Update sliders to match the new camera position
        self.x_slider.setValue(int(camera.xRotation()))
        self.y_slider.setValue(int(camera.yRotation()))
        self.zoom_slider.setValue(int(camera.zoomLevel()))

    def _reset_camera(self):
        """Reset the camera to the default position."""
        camera = self.graph.scene().activeCamera()
        camera.setCameraPreset(Q3DCamera.CameraPreset.CameraPresetIsometricRightHigh)
        camera.setZoomLevel(120)

        # Update sliders
        self.x_slider.setValue(int(camera.xRotation()))
        self.y_slider.setValue(int(camera.yRotation()))
        self.zoom_slider.setValue(int(camera.zoomLevel()))

    def _update_vertex_size(self, size):
        """Update the vertex size.

        Args:
            size: The new vertex size.
        """
        self.vertex_series.setItemSize(size / 100.0)

    def _update_edge_size(self, size):
        """Update the edge size.

        Args:
            size: The new edge size.
        """
        self.edge_series.setItemSize(size / 100.0)

    def _update_sphere_size(self, size):
        """Update the sphere size.

        Args:
            size: The new sphere size.
        """
        sphere_size = size / 100.0
        self.insphere_series.setItemSize(sphere_size)
        self.midsphere_series.setItemSize(sphere_size)
        self.circumsphere_series.setItemSize(sphere_size)

    def _update_shadow_quality(self, index):
        """Update the shadow quality.

        Args:
            index: The index of the selected shadow quality.
        """
        if index == 0:  # None
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualityNone
            )
        elif index == 1:  # Low
            self.graph.setShadowQuality(QAbstract3DGraph.ShadowQuality.ShadowQualityLow)
        elif index == 2:  # Medium
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualityMedium
            )
        elif index == 3:  # High
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualityHigh
            )
        elif index == 4:  # Soft Low
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualitySoftLow
            )
        elif index == 5:  # Soft Medium
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualitySoftMedium
            )
        elif index == 6:  # Soft High
            self.graph.setShadowQuality(
                QAbstract3DGraph.ShadowQuality.ShadowQualitySoftHigh
            )

    def _toggle_vertices(self, show):
        """Toggle the visibility of vertices.

        Args:
            show: Whether to show the vertices.
        """
        self.show_vertices = show
        self.vertex_series.setVisible(show)

    def _toggle_edges(self, show):
        """Toggle the visibility of edges.

        Args:
            show: Whether to show the edges.
        """
        self.show_edges = show
        self.edge_series.setVisible(show)

    def _toggle_faces(self, show):
        """Toggle the visibility of faces.

        Args:
            show: Whether to show the faces.
        """
        self.show_faces = show
        self.face_series.setVisible(show)
        self._update_solid()  # Need to regenerate face points

    def set_calculator(self, calculator: PlatonicSolidCalculator) -> None:
        """Set the calculator.

        Args:
            calculator: The calculator to use.
        """
        self.calculator = calculator
        self._update_visualization()

    def set_show_insphere(self, show: bool) -> None:
        """Set whether to show the insphere.

        Args:
            show: Whether to show the insphere.
        """
        self.show_insphere = show
        self.insphere_series.setVisible(show)

    def set_show_midsphere(self, show: bool) -> None:
        """Set whether to show the midsphere.

        Args:
            show: Whether to show the midsphere.
        """
        self.show_midsphere = show
        self.midsphere_series.setVisible(show)

    def set_show_circumsphere(self, show: bool) -> None:
        """Set whether to show the circumsphere.

        Args:
            show: Whether to show the circumsphere.
        """
        self.show_circumsphere = show
        self.circumsphere_series.setVisible(show)

    def update(self) -> None:
        """Update the visualization."""
        self._update_visualization()
        super().update()

    def _update_visualization(self) -> None:
        """Update the visualization with the current calculator values."""
        # Update the solid
        self._update_solid()

        # Update the spheres
        self._update_spheres()

        # Update the axes ranges
        self._update_axes()

    def _update_solid(self) -> None:
        """Update the solid visualization."""
        solid_type = self.calculator.solid_type
        edge_length = self.calculator.edge_length

        # Generate vertices and edges based on the solid type
        if solid_type == PlatonicSolidType.TETRAHEDRON:
            vertices, edges, faces = self._generate_tetrahedron(edge_length)
        elif solid_type == PlatonicSolidType.CUBE:
            vertices, edges, faces = self._generate_cube(edge_length)
        elif solid_type == PlatonicSolidType.OCTAHEDRON:
            vertices, edges, faces = self._generate_octahedron(edge_length)
        elif solid_type == PlatonicSolidType.DODECAHEDRON:
            vertices, edges, faces = self._generate_dodecahedron(edge_length)
        elif solid_type == PlatonicSolidType.ICOSAHEDRON:
            vertices, edges, faces = self._generate_icosahedron(edge_length)

        # Create data items for vertices
        vertex_items = []
        for vertex in vertices:
            item = QScatterDataItem(QVector3D(vertex[0], vertex[1], vertex[2]))
            vertex_items.append(item)

        # Create data items for edges (add points along each edge)
        edge_items = []
        for edge in edges:
            v1 = vertices[edge[0]]
            v2 = vertices[edge[1]]
            # Add several points along the edge
            for t in np.linspace(0, 1, 15):
                x = v1[0] + t * (v2[0] - v1[0])
                y = v1[1] + t * (v2[1] - v1[1])
                z = v1[2] + t * (v2[2] - v1[2])
                item = QScatterDataItem(QVector3D(x, y, z))
                edge_items.append(item)

        # Create data items for faces (if enabled)
        face_items = []
        if self.show_faces:
            for face in faces:
                # Get the vertices of the face
                face_vertices = [vertices[i] for i in face]

                # Calculate the center of the face
                center = [0, 0, 0]
                for vertex in face_vertices:
                    center[0] += vertex[0]
                    center[1] += vertex[1]
                    center[2] += vertex[2]
                center[0] /= len(face_vertices)
                center[1] /= len(face_vertices)
                center[2] /= len(face_vertices)

                # Create a grid of points to fill the face
                for i in range(len(face)):
                    v1 = face_vertices[i]
                    v2 = face_vertices[(i + 1) % len(face)]

                    # Create points along the edge and from edge to center
                    for t1 in np.linspace(0, 1, 5):  # Points along edge
                        edge_point = [
                            v1[0] + t1 * (v2[0] - v1[0]),
                            v1[1] + t1 * (v2[1] - v1[1]),
                            v1[2] + t1 * (v2[2] - v1[2]),
                        ]

                        for t2 in np.linspace(0, 1, 3):  # Points from edge to center
                            x = edge_point[0] + t2 * (center[0] - edge_point[0])
                            y = edge_point[1] + t2 * (center[1] - edge_point[1])
                            z = edge_point[2] + t2 * (center[2] - edge_point[2])

                            item = QScatterDataItem(QVector3D(x, y, z))
                            face_items.append(item)

        # Update the vertex, edge, and face series separately for better visualization
        self.vertex_proxy.resetArray(vertex_items)
        self.edge_proxy.resetArray(edge_items)
        self.face_proxy.resetArray(face_items)

    def _update_spheres(self) -> None:
        """Update the sphere visualizations."""
        # Update insphere
        if self.show_insphere:
            insphere_radius = self.calculator.get_insphere_radius()
            insphere_items = self._generate_sphere(insphere_radius, 15)
            self.insphere_proxy.resetArray(insphere_items)
        else:
            self.insphere_proxy.resetArray([])

        # Update midsphere
        if self.show_midsphere:
            midsphere_radius = self.calculator.get_midsphere_radius()
            midsphere_items = self._generate_sphere(midsphere_radius, 15)
            self.midsphere_proxy.resetArray(midsphere_items)
        else:
            self.midsphere_proxy.resetArray([])

        # Update circumsphere
        if self.show_circumsphere:
            circumsphere_radius = self.calculator.get_circumsphere_radius()
            circumsphere_items = self._generate_sphere(circumsphere_radius, 15)
            self.circumsphere_proxy.resetArray(circumsphere_items)
        else:
            self.circumsphere_proxy.resetArray([])

    def _update_axes(self) -> None:
        """Update the axes ranges based on the current solid."""
        # Get the maximum radius
        max_radius = self.calculator.get_circumsphere_radius()

        # Set the axes ranges
        self.graph.axisX().setRange(-max_radius * 1.2, max_radius * 1.2)
        self.graph.axisY().setRange(-max_radius * 1.2, max_radius * 1.2)
        self.graph.axisZ().setRange(-max_radius * 1.2, max_radius * 1.2)

    def _generate_sphere(
        self, radius: float, resolution: int = 10
    ) -> List[QScatterDataItem]:
        """Generate points for a sphere.

        Args:
            radius: The radius of the sphere.
            resolution: The resolution of the sphere.

        Returns:
            A list of QScatterDataItem objects representing the sphere.
        """
        items = []

        # Generate points on the sphere using spherical coordinates
        for theta in np.linspace(0, np.pi, resolution):
            for phi in np.linspace(0, 2 * np.pi, resolution):
                x = radius * np.sin(theta) * np.cos(phi)
                y = radius * np.sin(theta) * np.sin(phi)
                z = radius * np.cos(theta)
                item = QScatterDataItem(QVector3D(x, y, z))
                items.append(item)

        return items

    def _generate_tetrahedron(
        self, edge_length: float
    ) -> Tuple[List[List[float]], List[List[int]], List[List[int]]]:
        """Generate vertices, edges, and faces for a tetrahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # Calculate the coordinates based on edge length
        a = edge_length / math.sqrt(2)

        # Define the vertices
        vertices = [
            [a, 0, -a / math.sqrt(2)],
            [-a, 0, -a / math.sqrt(2)],
            [0, a, a / math.sqrt(2)],
            [0, -a, a / math.sqrt(2)],
        ]

        # Define the edges
        edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]

        # Define the faces (triangles)
        faces = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]

        return vertices, edges, faces

    def _generate_cube(
        self, edge_length: float
    ) -> Tuple[List[List[float]], List[List[int]], List[List[int]]]:
        """Generate vertices, edges, and faces for a cube.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # Calculate the half-edge length
        a = edge_length / 2

        # Define the vertices
        vertices = [
            [-a, -a, -a],  # 0: left-bottom-back
            [a, -a, -a],  # 1: right-bottom-back
            [a, a, -a],  # 2: right-top-back
            [-a, a, -a],  # 3: left-top-back
            [-a, -a, a],  # 4: left-bottom-front
            [a, -a, a],  # 5: right-bottom-front
            [a, a, a],  # 6: right-top-front
            [-a, a, a],  # 7: left-top-front
        ]

        # Define the edges
        edges = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],  # back face
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],  # front face
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],  # connecting edges
        ]

        # Define the faces (squares)
        faces = [
            [0, 1, 2, 3],  # back face
            [4, 5, 6, 7],  # front face
            [0, 1, 5, 4],  # bottom face
            [2, 3, 7, 6],  # top face
            [0, 3, 7, 4],  # left face
            [1, 2, 6, 5],  # right face
        ]

        return vertices, edges, faces

    def _generate_octahedron(
        self, edge_length: float
    ) -> Tuple[List[List[float]], List[List[int]], List[List[int]]]:
        """Generate vertices, edges, and faces for an octahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # Calculate the distance from center to vertex
        a = edge_length / math.sqrt(2)

        # Define the vertices
        vertices = [
            [a, 0, 0],  # 0: right
            [-a, 0, 0],  # 1: left
            [0, a, 0],  # 2: top
            [0, -a, 0],  # 3: bottom
            [0, 0, a],  # 4: front
            [0, 0, -a],  # 5: back
        ]

        # Define the edges
        edges = [
            [0, 2],
            [0, 3],
            [0, 4],
            [0, 5],  # from right vertex
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],  # from left vertex
            [2, 4],
            [2, 5],
            [3, 4],
            [3, 5],  # remaining edges
        ]

        # Define the faces (triangles)
        faces = [
            [0, 2, 4],  # right-top-front
            [0, 4, 3],  # right-front-bottom
            [0, 3, 5],  # right-bottom-back
            [0, 5, 2],  # right-back-top
            [1, 4, 2],  # left-front-top
            [1, 3, 4],  # left-bottom-front
            [1, 5, 3],  # left-back-bottom
            [1, 2, 5],  # left-top-back
        ]

        return vertices, edges, faces

    def _generate_dodecahedron(
        self, edge_length: float
    ) -> Tuple[List[List[float]], List[List[int]], List[List[int]]]:
        """Generate vertices, edges, and faces for a dodecahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # Calculate the scaling factor
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        a = edge_length / (2 * math.sin(math.pi / 5))

        # Define the vertices
        vertices = [
            [a, a, a],  # 0
            [a, a, -a],  # 1
            [a, -a, a],  # 2
            [a, -a, -a],  # 3
            [-a, a, a],  # 4
            [-a, a, -a],  # 5
            [-a, -a, a],  # 6
            [-a, -a, -a],  # 7
            [0, phi * a, (1 / phi) * a],  # 8
            [0, phi * a, -(1 / phi) * a],  # 9
            [0, -phi * a, (1 / phi) * a],  # 10
            [0, -phi * a, -(1 / phi) * a],  # 11
            [(1 / phi) * a, 0, phi * a],  # 12
            [(1 / phi) * a, 0, -phi * a],  # 13
            [-(1 / phi) * a, 0, phi * a],  # 14
            [-(1 / phi) * a, 0, -phi * a],  # 15
            [phi * a, (1 / phi) * a, 0],  # 16
            [phi * a, -(1 / phi) * a, 0],  # 17
            [-phi * a, (1 / phi) * a, 0],  # 18
            [-phi * a, -(1 / phi) * a, 0],  # 19
        ]

        # Define the edges (this is a simplified version)
        edges = [
            [0, 8],
            [0, 12],
            [0, 16],
            [1, 9],
            [1, 13],
            [1, 16],
            [2, 10],
            [2, 12],
            [2, 17],
            [3, 11],
            [3, 13],
            [3, 17],
            [4, 8],
            [4, 14],
            [4, 18],
            [5, 9],
            [5, 15],
            [5, 18],
            [6, 10],
            [6, 14],
            [6, 19],
            [7, 11],
            [7, 15],
            [7, 19],
            [8, 9],
            [10, 11],
            [12, 14],
            [13, 15],
            [16, 17],
            [18, 19],
            [8, 14],
            [9, 15],
            [10, 14],
            [11, 15],
            [12, 16],
            [13, 16],
            [8, 16],
            [9, 16],
            [10, 17],
            [11, 17],
            [12, 17],
            [13, 17],
            [14, 18],
            [15, 18],
            [14, 19],
            [15, 19],
            [18, 19],
        ]

        # Define the faces (pentagons)
        faces = [
            [0, 8, 9, 1, 16],  # Top front
            [0, 16, 17, 2, 12],  # Right top
            [0, 12, 14, 4, 8],  # Front top
            [1, 9, 5, 15, 13],  # Top back
            [1, 13, 3, 17, 16],  # Right back
            [2, 17, 3, 11, 10],  # Bottom right
            [2, 10, 6, 14, 12],  # Front bottom
            [3, 13, 15, 7, 11],  # Bottom back
            [4, 14, 6, 19, 18],  # Left front
            [4, 18, 5, 9, 8],  # Top left
            [5, 18, 19, 7, 15],  # Left back
            [6, 10, 11, 7, 19],  # Bottom left
        ]

        return vertices, edges, faces

    def _generate_icosahedron(
        self, edge_length: float
    ) -> Tuple[List[List[float]], List[List[int]], List[List[int]]]:
        """Generate vertices, edges, and faces for an icosahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # Calculate the scaling factor
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        a = edge_length / (2 * math.sin(math.pi / 5))

        # Define the vertices
        vertices = [
            [0, a, phi * a],  # 0
            [0, a, -phi * a],  # 1
            [0, -a, phi * a],  # 2
            [0, -a, -phi * a],  # 3
            [a, phi * a, 0],  # 4
            [a, -phi * a, 0],  # 5
            [-a, phi * a, 0],  # 6
            [-a, -phi * a, 0],  # 7
            [phi * a, 0, a],  # 8
            [phi * a, 0, -a],  # 9
            [-phi * a, 0, a],  # 10
            [-phi * a, 0, -a],  # 11
        ]

        # Define the edges
        edges = [
            [0, 2],
            [0, 4],
            [0, 6],
            [0, 8],
            [0, 10],
            [1, 3],
            [1, 4],
            [1, 6],
            [1, 9],
            [1, 11],
            [2, 5],
            [2, 7],
            [2, 8],
            [2, 10],
            [3, 5],
            [3, 7],
            [3, 9],
            [3, 11],
            [4, 6],
            [4, 8],
            [4, 9],
            [5, 7],
            [5, 8],
            [5, 9],
            [6, 10],
            [6, 11],
            [7, 10],
            [7, 11],
            [8, 9],
            [10, 11],
        ]

        # Define the faces (triangles)
        faces = [
            [0, 2, 8],  # Top front right
            [0, 8, 4],  # Top right front
            [0, 4, 6],  # Top left right
            [0, 6, 10],  # Top left front
            [0, 10, 2],  # Top front left
            [1, 4, 9],  # Bottom right front
            [1, 6, 4],  # Bottom left right
            [1, 11, 6],  # Bottom left back
            [1, 9, 11],  # Bottom right back
            [1, 3, 9],  # Bottom back right
            [2, 10, 7],  # Front left bottom
            [2, 7, 5],  # Front bottom left
            [2, 5, 8],  # Front bottom right
            [3, 5, 9],  # Back bottom right
            [3, 7, 5],  # Back bottom left
            [3, 11, 7],  # Back left bottom
            [4, 8, 9],  # Right front bottom
            [5, 7, 8],  # Bottom left right
            [6, 11, 10],  # Left back front
            [7, 11, 10],  # Bottom back front
        ]

        return vertices, edges, faces


class PlatonicSolidPanel(QWidget):
    """Panel for calculating properties of Platonic solids."""

    def __init__(self, parent=None, opengl_widget=None):
        """Initialize the panel.

        Args:
            parent: Parent widget
            opengl_widget: Optional shared OpenGL widget
        """
        super().__init__(parent)
        # Initialize calculator
        self.calculator = PlatonicSolidCalculator()
        # Use provided OpenGL widget or create a new one
        self.opengl_widget = (
            opengl_widget if opengl_widget is not None else PlatonicSolidOpenGLWidget()
        )
        # Initialize UI
        self._init_ui()
        # Update the display
        self._update_solid()

    def _init_ui(self):
        """Initialize the UI components."""
        # --- Initialize all widget and visualization attributes before use ---
        self.solid_type_combo = QComboBox()
        self.edge_length_spin = QDoubleSpinBox()
        self.face_area_spin = QDoubleSpinBox()
        self.surface_area_spin = QDoubleSpinBox()
        self.volume_spin = QDoubleSpinBox()
        self.face_diagonal_spin = QDoubleSpinBox()
        self.space_diagonal_spin = QDoubleSpinBox()
        self.height_spin = QDoubleSpinBox()
        self.insphere_radius_spin = QDoubleSpinBox()
        self.insphere_circumference_spin = QDoubleSpinBox()
        self.insphere_area_spin = QDoubleSpinBox()
        self.insphere_volume_spin = QDoubleSpinBox()
        self.midsphere_radius_spin = QDoubleSpinBox()
        self.midsphere_circumference_spin = QDoubleSpinBox()
        self.midsphere_area_spin = QDoubleSpinBox()
        self.midsphere_volume_spin = QDoubleSpinBox()
        self.circumsphere_radius_spin = QDoubleSpinBox()
        self.circumsphere_circumference_spin = QDoubleSpinBox()
        self.circumsphere_area_spin = QDoubleSpinBox()
        self.circumsphere_volume_spin = QDoubleSpinBox()
        self.face_count_label = QLabel()
        self.vertex_count_label = QLabel()
        self.edge_count_label = QLabel()
        self.face_type_label = QLabel()
        self.vertex_config_label = QLabel()
        self.schlaefli_label = QLabel()
        self.dual_label = QLabel()
        self.symmetry_label = QLabel()
        self.dihedral_angle_label = QLabel()
        # self.opengl_widget = PlatonicSolidOpenGLWidget()  # <-- now set in __init__

        # --- Main 3-pane layout ---
        main_layout = QHBoxLayout(self)

        # --- Left Pane: Calculator Controls ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_pane.setMinimumWidth(320)
        left_pane.setMaximumWidth(400)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Solid type selection
        solid_group = QGroupBox("Platonic Solid Type")
        solid_layout = QFormLayout(solid_group)
        self.solid_type_combo.addItem("Tetrahedron", PlatonicSolidType.TETRAHEDRON)
        self.solid_type_combo.addItem("Cube", PlatonicSolidType.CUBE)
        self.solid_type_combo.addItem("Octahedron", PlatonicSolidType.OCTAHEDRON)
        self.solid_type_combo.addItem("Dodecahedron", PlatonicSolidType.DODECAHEDRON)
        self.solid_type_combo.addItem("Icosahedron", PlatonicSolidType.ICOSAHEDRON)
        self.solid_type_combo.addItem("Cuboctahedron", PlatonicSolidType.CUBOCTAHEDRON)
        self.solid_type_combo.currentIndexChanged.connect(self._solid_type_changed)
        solid_layout.addRow("Solid Type:", self.solid_type_combo)
        scroll_layout.addWidget(solid_group)

        # Dimensional properties
        dim_group = QGroupBox("Dimensional Properties")
        dim_layout = QFormLayout(dim_group)
        self.edge_length_spin.setRange(0.1, 1e12)
        self.edge_length_spin.setDecimals(8)
        self.edge_length_spin.setSingleStep(1.0)
        self.edge_length_spin.editingFinished.connect(self._edge_length_changed)
        dim_layout.addRow("Edge Length:", self.edge_length_spin)
        self.face_area_spin.setRange(0.1, 1e12)
        self.face_area_spin.setDecimals(8)
        self.face_area_spin.setSingleStep(1.0)
        self.face_area_spin.editingFinished.connect(self._face_area_changed)
        dim_layout.addRow("Face Area:", self.face_area_spin)
        self.surface_area_spin.setRange(0.1, 1e12)
        self.surface_area_spin.setDecimals(8)
        self.surface_area_spin.setSingleStep(1.0)
        self.surface_area_spin.editingFinished.connect(self._surface_area_changed)
        dim_layout.addRow("Total Surface Area:", self.surface_area_spin)
        self.volume_spin.setRange(0.1, 1e12)
        self.volume_spin.setDecimals(8)
        self.volume_spin.setSingleStep(1.0)
        self.volume_spin.editingFinished.connect(self._volume_changed)
        dim_layout.addRow("Volume:", self.volume_spin)
        self.face_diagonal_spin.setRange(0.1, 1e12)
        self.face_diagonal_spin.setDecimals(8)
        self.face_diagonal_spin.setSingleStep(1.0)
        self.face_diagonal_spin.editingFinished.connect(self._face_diagonal_changed)
        dim_layout.addRow("Face Diagonal:", self.face_diagonal_spin)
        self.space_diagonal_spin.setRange(0.1, 1e12)
        self.space_diagonal_spin.setDecimals(8)
        self.space_diagonal_spin.setSingleStep(1.0)
        self.space_diagonal_spin.editingFinished.connect(self._space_diagonal_changed)
        dim_layout.addRow("Space Diagonal:", self.space_diagonal_spin)
        self.height_spin.setRange(0.1, 1e12)
        self.height_spin.setDecimals(8)
        self.height_spin.setSingleStep(1.0)
        self.height_spin.editingFinished.connect(self._height_changed)
        dim_layout.addRow("Height:", self.height_spin)
        scroll_layout.addWidget(dim_group)

        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        basic_layout.addRow("Number of Faces:", self.face_count_label)
        basic_layout.addRow("Number of Vertices:", self.vertex_count_label)
        basic_layout.addRow("Number of Edges:", self.edge_count_label)
        basic_layout.addRow("Face Type:", self.face_type_label)
        basic_layout.addRow("Vertex Configuration:", self.vertex_config_label)
        basic_layout.addRow("Schläfli Symbol:", self.schlaefli_label)
        basic_layout.addRow("Dual Polyhedron:", self.dual_label)
        basic_layout.addRow("Symmetry Group:", self.symmetry_label)
        basic_layout.addRow("Dihedral Angle:", self.dihedral_angle_label)
        scroll_layout.addWidget(basic_group)

        # Insphere properties
        insphere_group = QGroupBox("Insphere Properties")
        insphere_layout = QFormLayout(insphere_group)
        self.insphere_radius_spin.setRange(0.1, 1e12)
        self.insphere_radius_spin.setDecimals(8)
        self.insphere_radius_spin.setSingleStep(1.0)
        self.insphere_radius_spin.editingFinished.connect(self._insphere_radius_changed)
        insphere_layout.addRow("Radius:", self.insphere_radius_spin)
        self.insphere_circumference_spin.setRange(0.1, 1e12)
        self.insphere_circumference_spin.setDecimals(8)
        self.insphere_circumference_spin.setSingleStep(1.0)
        self.insphere_circumference_spin.editingFinished.connect(
            self._insphere_circumference_changed
        )
        insphere_layout.addRow("Circumference:", self.insphere_circumference_spin)
        self.insphere_area_spin.setRange(0.1, 1e12)
        self.insphere_area_spin.setDecimals(8)
        self.insphere_area_spin.setSingleStep(1.0)
        self.insphere_area_spin.editingFinished.connect(self._insphere_area_changed)
        insphere_layout.addRow("Surface Area:", self.insphere_area_spin)
        self.insphere_volume_spin.setRange(0.1, 1e12)
        self.insphere_volume_spin.setDecimals(8)
        self.insphere_volume_spin.setSingleStep(1.0)
        self.insphere_volume_spin.editingFinished.connect(self._insphere_volume_changed)
        insphere_layout.addRow("Volume:", self.insphere_volume_spin)
        scroll_layout.addWidget(insphere_group)

        # Midsphere properties
        midsphere_group = QGroupBox("Midsphere Properties")
        midsphere_layout = QFormLayout(midsphere_group)
        self.midsphere_radius_spin.setRange(0.1, 1e12)
        self.midsphere_radius_spin.setDecimals(8)
        self.midsphere_radius_spin.setSingleStep(1.0)
        self.midsphere_radius_spin.editingFinished.connect(
            self._midsphere_radius_changed
        )
        midsphere_layout.addRow("Radius:", self.midsphere_radius_spin)
        self.midsphere_circumference_spin.setRange(0.1, 1e12)
        self.midsphere_circumference_spin.setDecimals(8)
        self.midsphere_circumference_spin.setSingleStep(1.0)
        self.midsphere_circumference_spin.editingFinished.connect(
            self._midsphere_circumference_changed
        )
        midsphere_layout.addRow("Circumference:", self.midsphere_circumference_spin)
        self.midsphere_area_spin.setRange(0.1, 1e12)
        self.midsphere_area_spin.setDecimals(8)
        self.midsphere_area_spin.setSingleStep(1.0)
        self.midsphere_area_spin.editingFinished.connect(self._midsphere_area_changed)
        midsphere_layout.addRow("Surface Area:", self.midsphere_area_spin)
        self.midsphere_volume_spin.setRange(0.1, 1e12)
        self.midsphere_volume_spin.setDecimals(8)
        self.midsphere_volume_spin.setSingleStep(1.0)
        self.midsphere_volume_spin.editingFinished.connect(
            self._midsphere_volume_changed
        )
        midsphere_layout.addRow("Volume:", self.midsphere_volume_spin)
        scroll_layout.addWidget(midsphere_group)

        # Circumsphere properties
        circumsphere_group = QGroupBox("Circumsphere Properties")
        circumsphere_layout = QFormLayout(circumsphere_group)
        self.circumsphere_radius_spin.setRange(0.1, 1e12)
        self.circumsphere_radius_spin.setDecimals(8)
        self.circumsphere_radius_spin.setSingleStep(1.0)
        self.circumsphere_radius_spin.editingFinished.connect(
            self._circumsphere_radius_changed
        )
        circumsphere_layout.addRow("Radius:", self.circumsphere_radius_spin)
        self.circumsphere_circumference_spin.setRange(0.1, 1e12)
        self.circumsphere_circumference_spin.setDecimals(8)
        self.circumsphere_circumference_spin.setSingleStep(1.0)
        self.circumsphere_circumference_spin.editingFinished.connect(
            self._circumsphere_circumference_changed
        )
        circumsphere_layout.addRow(
            "Circumference:", self.circumsphere_circumference_spin
        )
        self.circumsphere_area_spin.setRange(0.1, 1e12)
        self.circumsphere_area_spin.setDecimals(8)
        self.circumsphere_area_spin.setSingleStep(1.0)
        self.circumsphere_area_spin.editingFinished.connect(
            self._circumsphere_area_changed
        )
        circumsphere_layout.addRow("Surface Area:", self.circumsphere_area_spin)
        self.circumsphere_volume_spin.setRange(0.1, 1e12)
        self.circumsphere_volume_spin.setDecimals(8)
        self.circumsphere_volume_spin.setSingleStep(1.0)
        self.circumsphere_volume_spin.editingFinished.connect(
            self._circumsphere_volume_changed
        )
        circumsphere_layout.addRow("Volume:", self.circumsphere_volume_spin)
        scroll_layout.addWidget(circumsphere_group)

        scroll_layout.addStretch(1)
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_pane)

        # --- Center Pane: OpenGL Viewport ---
        center_pane = QWidget()
        center_layout = QVBoxLayout(center_pane)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(self.opengl_widget)
        main_layout.addWidget(center_pane, stretch=2)

        # --- Right Pane: Toggle Controls ---
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_pane.setMinimumWidth(180)
        right_pane.setMaximumWidth(240)
        right_layout.addWidget(QLabel("Viewport Controls"))
        right_layout.addSpacing(10)
        self.toggle_faces = QCheckBox("Show Faces")
        self.toggle_faces.setChecked(True)
        self.toggle_faces.toggled.connect(
            lambda checked: self._toggle_viewport_feature("faces", checked)
        )
        right_layout.addWidget(self.toggle_faces)
        self.toggle_wireframe = QCheckBox("Show Wireframe")
        self.toggle_wireframe.setChecked(False)
        self.toggle_wireframe.toggled.connect(
            lambda checked: self._toggle_viewport_feature("wireframe", checked)
        )
        right_layout.addWidget(self.toggle_wireframe)
        self.toggle_vertices = QCheckBox("Show Vertices")
        self.toggle_vertices.setChecked(False)
        self.toggle_vertices.toggled.connect(
            lambda checked: self._toggle_viewport_feature("vertices", checked)
        )
        right_layout.addWidget(self.toggle_vertices)
        self.toggle_insphere = QCheckBox("Show Insphere")
        self.toggle_insphere.setChecked(False)
        self.toggle_insphere.toggled.connect(
            lambda checked: self._toggle_viewport_feature("insphere", checked)
        )
        right_layout.addWidget(self.toggle_insphere)
        self.toggle_midsphere = QCheckBox("Show Midsphere")
        self.toggle_midsphere.setChecked(False)
        self.toggle_midsphere.toggled.connect(
            lambda checked: self._toggle_viewport_feature("midsphere", checked)
        )
        right_layout.addWidget(self.toggle_midsphere)
        self.toggle_circumsphere = QCheckBox("Show Circumsphere")
        self.toggle_circumsphere.setChecked(False)
        self.toggle_circumsphere.toggled.connect(
            lambda checked: self._toggle_viewport_feature("circumsphere", checked)
        )
        right_layout.addWidget(self.toggle_circumsphere)
        right_layout.addStretch(1)
        main_layout.addWidget(right_pane)

    def _solid_type_changed(self, index):
        solid_type = PlatonicSolidType(index + 1)
        self.calculator.set_solid_type(solid_type)
        self.opengl_widget.set_solid_type(solid_type)
        # Enable space diagonal only for cubes
        if solid_type == PlatonicSolidType.CUBE:
            self.space_diagonal_spin.setEnabled(True)
            self.space_diagonal_spin.setToolTip("")
        else:
            self.space_diagonal_spin.setEnabled(False)
            self.space_diagonal_spin.setToolTip(
                "Space diagonal is only defined for cubes."
            )
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _edge_length_changed(self):
        value = self.edge_length_spin.value()
        self.calculator.set_edge_length(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _face_area_changed(self):
        value = self.face_area_spin.value()
        self.calculator.calculate_from_face_area(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _surface_area_changed(self):
        value = self.surface_area_spin.value()
        self.calculator.calculate_from_surface_area(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _volume_changed(self):
        value = self.volume_spin.value()
        self.calculator.calculate_from_volume(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _face_diagonal_changed(self):
        value = self.face_diagonal_spin.value()
        self.calculator.calculate_from_face_diagonal(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _space_diagonal_changed(self):
        value = self.space_diagonal_spin.value()
        self.calculator.calculate_from_space_diagonal(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _height_changed(self):
        value = self.height_spin.value()
        self.calculator.calculate_from_height(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _insphere_radius_changed(self):
        value = self.insphere_radius_spin.value()
        self.calculator.calculate_from_insphere_radius(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _insphere_circumference_changed(self):
        value = self.insphere_circumference_spin.value()
        radius = value / (2 * math.pi)
        self.calculator.calculate_from_insphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _insphere_area_changed(self):
        value = self.insphere_area_spin.value()
        radius = math.sqrt(value / (4 * math.pi))
        self.calculator.calculate_from_insphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _insphere_volume_changed(self):
        value = self.insphere_volume_spin.value()
        radius = ((3 * value) / (4 * math.pi)) ** (1 / 3)
        self.calculator.calculate_from_insphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _midsphere_radius_changed(self):
        value = self.midsphere_radius_spin.value()
        self.calculator.calculate_from_midsphere_radius(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _midsphere_circumference_changed(self):
        value = self.midsphere_circumference_spin.value()
        radius = value / (2 * math.pi)
        self.calculator.calculate_from_midsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _midsphere_area_changed(self):
        value = self.midsphere_area_spin.value()
        radius = math.sqrt(value / (4 * math.pi))
        self.calculator.calculate_from_midsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _midsphere_volume_changed(self):
        value = self.midsphere_volume_spin.value()
        radius = ((3 * value) / (4 * math.pi)) ** (1 / 3)
        self.calculator.calculate_from_midsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _circumsphere_radius_changed(self):
        value = self.circumsphere_radius_spin.value()
        self.calculator.calculate_from_circumsphere_radius(value)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _circumsphere_circumference_changed(self):
        value = self.circumsphere_circumference_spin.value()
        radius = value / (2 * math.pi)
        self.calculator.calculate_from_circumsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _circumsphere_area_changed(self):
        value = self.circumsphere_area_spin.value()
        radius = math.sqrt(value / (4 * math.pi))
        self.calculator.calculate_from_circumsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _circumsphere_volume_changed(self):
        value = self.circumsphere_volume_spin.value()
        radius = ((3 * value) / (4 * math.pi)) ** (1 / 3)
        self.calculator.calculate_from_circumsphere_radius(radius)
        self._update_spinners()
        self._update_display()
        self.opengl_widget.update()

    def _update_solid(self):
        """Update the solid type and recalculate all properties."""
        # Get the selected solid type
        solid_type = self.solid_type_combo.currentData()

        # Update the calculator
        self.calculator.set_solid_type(solid_type)

        # Update the visualization
        self.opengl_widget.set_solid_type(solid_type)

        # Update the display
        self._update_display()

    def _update_display(self):
        """Update all display values except input spinners."""
        # Update basic properties
        self.face_count_label.setText(str(self.calculator.get_face_count()))
        self.vertex_count_label.setText(str(self.calculator.get_vertex_count()))
        self.edge_count_label.setText(str(self.calculator.get_edge_count()))
        self.face_type_label.setText(self.calculator.get_face_type())
        self.vertex_config_label.setText(self.calculator.get_vertex_configuration())
        self.schlaefli_label.setText(self.calculator.get_schlaefli_symbol())
        self.dual_label.setText(self.calculator.get_dual_polyhedron())
        self.symmetry_label.setText(self.calculator.get_symmetry_group())
        self.dihedral_angle_label.setText(
            f"{self.calculator.get_dihedral_angle():.4f}°"
        )

        # Update insphere properties
        insphere_radius = self.calculator.get_insphere_radius()
        self.insphere_radius_spin.setValue(insphere_radius)
        self.insphere_circumference_spin.setValue(2 * math.pi * insphere_radius)
        self.insphere_area_spin.setValue(self.calculator.get_insphere_surface_area())
        self.insphere_volume_spin.setValue(self.calculator.get_insphere_volume())

        # Update midsphere properties
        midsphere_radius = self.calculator.get_midsphere_radius()
        self.midsphere_radius_spin.setValue(midsphere_radius)
        self.midsphere_circumference_spin.setValue(2 * math.pi * midsphere_radius)
        self.midsphere_area_spin.setValue(self.calculator.get_midsphere_surface_area())
        self.midsphere_volume_spin.setValue(self.calculator.get_midsphere_volume())

        # Update circumsphere properties
        circumsphere_radius = self.calculator.get_circumsphere_radius()
        self.circumsphere_radius_spin.setValue(circumsphere_radius)
        self.circumsphere_circumference_spin.setValue(2 * math.pi * circumsphere_radius)
        self.circumsphere_area_spin.setValue(
            self.calculator.get_circumsphere_surface_area()
        )
        self.circumsphere_volume_spin.setValue(
            self.calculator.get_circumsphere_volume()
        )

        # Update visualization
        self.opengl_widget.update()

    def _update_spinners(self):
        """Update the spinner values without triggering events."""
        # Block all signals
        self._block_signals(True)

        # Update dimensional properties
        self.edge_length_spin.setValue(self.calculator.edge_length)
        self.face_area_spin.setValue(self.calculator.get_face_area())
        self.surface_area_spin.setValue(self.calculator.get_total_surface_area())
        self.volume_spin.setValue(self.calculator.get_volume())

        # Face diagonal and space diagonal (cube only)
        face_diagonal = self.calculator.get_face_diagonal()
        space_diagonal = self.calculator.get_space_diagonal()
        height = self.calculator.get_height()

        if face_diagonal is not None:
            self.face_diagonal_spin.setValue(face_diagonal)
            self.face_diagonal_spin.setEnabled(True)
        else:
            self.face_diagonal_spin.setValue(0)
            self.face_diagonal_spin.setEnabled(False)

        if space_diagonal is not None:
            self.space_diagonal_spin.setValue(space_diagonal)
            self.space_diagonal_spin.setEnabled(True)
        else:
            self.space_diagonal_spin.setValue(0)
            self.space_diagonal_spin.setEnabled(False)

        self.height_spin.setValue(height)

        # Unblock signals
        self._block_signals(False)

    def _block_signals(self, block: bool):
        """Block or unblock signals from all input widgets.

        Args:
            block: Whether to block signals
        """
        # Dimensional properties
        self.edge_length_spin.blockSignals(block)
        self.face_area_spin.blockSignals(block)
        self.surface_area_spin.blockSignals(block)
        self.volume_spin.blockSignals(block)
        self.face_diagonal_spin.blockSignals(block)
        self.space_diagonal_spin.blockSignals(block)
        self.height_spin.blockSignals(block)

        # Insphere properties
        self.insphere_radius_spin.blockSignals(block)
        self.insphere_circumference_spin.blockSignals(block)
        self.insphere_area_spin.blockSignals(block)
        self.insphere_volume_spin.blockSignals(block)

        # Midsphere properties
        self.midsphere_radius_spin.blockSignals(block)
        self.midsphere_circumference_spin.blockSignals(block)
        self.midsphere_area_spin.blockSignals(block)
        self.midsphere_volume_spin.blockSignals(block)

        # Circumsphere properties
        self.circumsphere_radius_spin.blockSignals(block)
        self.circumsphere_circumference_spin.blockSignals(block)
        self.circumsphere_area_spin.blockSignals(block)
        self.circumsphere_volume_spin.blockSignals(block)

    def _toggle_viewport_feature(self, feature, checked):
        if feature == "faces":
            self.opengl_widget.set_show_faces(checked)
            # If faces are off, ensure wireframe is on for visibility
            if not checked and not self.toggle_wireframe.isChecked():
                self.toggle_wireframe.setChecked(True)
        elif feature == "wireframe":
            self.opengl_widget.set_show_wireframe(checked)
            # If faces are off and wireframe is toggled off, force wireframe back on
            if not self.toggle_faces.isChecked() and not checked:
                self.toggle_wireframe.setChecked(True)
        elif feature == "vertices":
            self.opengl_widget.set_show_vertices(checked)
        elif feature == "insphere":
            self.opengl_widget.set_show_insphere(checked)
        elif feature == "midsphere":
            self.opengl_widget.set_show_midsphere(checked)
        elif feature == "circumsphere":
            self.opengl_widget.set_show_circumsphere(checked)
