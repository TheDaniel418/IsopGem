"""
@file platonic_solid_opengl_widget.py
@description PyOpenGL-based widget for wireframe visualization of Platonic solids.
@author Daniel (AI-assisted)
@created 2024-06-09
@lastModified 2024-06-15
@dependencies PyQt6, PyOpenGL, geometry.calculator.platonic_solid_calculator, numpy
"""

import math

import numpy as np  # Added for vector math
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt6.QtCore import Qt
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QPushButton

from geometry.calculator.platonic_solid_calculator import (
    PlatonicSolidCalculator,
    PlatonicSolidType,
)


class OpenGLAxesIndicator:
    """
    Modular OpenGL 3D axes indicator for overlay use in any QOpenGLWidget.
    Usage: instantiate and call draw_axes() in paintGL after main scene.
    """

    def __init__(self, size=60, margin=12):
        self.size = size
        self.margin = margin

    def draw_axes(self, widget_width, widget_height):
        # Note: widget_width and widget_height parameters are not used in this implementation
        # but are kept for potential future enhancements (e.g., responsive sizing)

        # Save current viewport and projection
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glViewport(self.margin, self.margin, self.size, self.size)
        gluPerspective(40, 1, 0.1, 10)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(0, 0, -3)
        # Draw axes: X (red), Y (green), Z (blue)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        # X axis
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        # Y axis
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        # Z axis
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glEnd()
        # Restore matrices and viewport
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()


class PlatonicSolidOpenGLWidget(QOpenGLWidget):
    """
    @class PlatonicSolidOpenGLWidget
    @description QOpenGLWidget for rendering Platonic solids as wireframes using PyOpenGL.
    @param parent QWidget parent
    @example
        widget = PlatonicSolidOpenGLWidget()
        widget.set_solid_type(PlatonicSolidType.CUBE)
        widget.set_edge_length(2.0)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calculator = PlatonicSolidCalculator()
        self.rotation_x = 30.0
        self.rotation_y = 40.0
        self.zoom = 1.5
        self.last_pos = None
        self.setMinimumSize(400, 400)
        self.axes_indicator = OpenGLAxesIndicator()
        # Viewport feature toggles
        self._show_faces = True
        self._show_wireframe = False
        self._show_vertices = False
        self._show_insphere = False
        self._show_midsphere = False
        self._show_circumsphere = False
        # Reset view button overlay
        self.reset_btn = QPushButton("Reset View", self)
        self.reset_btn.setStyleSheet(
            "background: rgba(255,255,255,0.8); border-radius: 8px; padding: 4px 12px;"
        )
        self.reset_btn.move(self.width() - 110, 10)
        self.reset_btn.clicked.connect(self.reset_view)
        self.reset_btn.raise_()
        self.reset_btn.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reset_btn.move(self.width() - 110, 10)

    def reset_view(self):
        self.rotation_x = 30.0
        self.rotation_y = 40.0
        self.zoom = 1.5
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Left:
            self.rotation_y -= 10
        elif key == Qt.Key.Key_Right:
            self.rotation_y += 10
        elif key == Qt.Key.Key_Up:
            self.rotation_x -= 10
        elif key == Qt.Key.Key_Down:
            self.rotation_x += 10
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.zoom = max(0.2, self.zoom * 0.9)
        elif key in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore):
            self.zoom = min(5.0, self.zoom * 1.1)
        elif key == Qt.Key.Key_R:
            self.reset_view()
        self.update()

    def set_solid_type(self, solid_type: PlatonicSolidType):
        self.calculator.set_solid_type(solid_type)
        self.update()

    def set_edge_length(self, edge_length: float):
        self.calculator.set_edge_length(edge_length)
        self.update()

    def set_show_faces(self, show: bool):
        self._show_faces = show
        self.update()

    def set_show_wireframe(self, show: bool):
        self._show_wireframe = show
        self.update()

    def set_show_vertices(self, show: bool):
        self._show_vertices = show
        self.update()

    def set_show_insphere(self, show: bool):
        self._show_insphere = show
        self.update()

    def set_show_midsphere(self, show: bool):
        self._show_midsphere = show
        self.update()

    def set_show_circumsphere(self, show: bool):
        self._show_circumsphere = show
        self.update()

    def initializeGL(self):
        # Set background color to dark gray
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(1.0)  # Default line width

        # --- Lighting Setup ---
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)  # Automatically normalize normals
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        # Light properties
        light_pos = [1.0, 2.0, 3.0, 1.0]  # Positional light
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [0.6, 0.6, 0.6, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # Material properties (using glColorMaterial, but specular needs glMaterialfv)
        mat_specular = [0.5, 0.5, 0.5, 1.0]
        mat_shininess = [50.0]  # Shininess factor
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

        # Enable smooth shading
        glShadeModel(GL_SMOOTH)

        # Enable backface culling (Temporarily disabled for debugging)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h != 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0 * self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        self._draw_solid()

        # Draw axes indicator overlay
        self.axes_indicator.draw_axes(self.width(), self.height())

    def _draw_solid(self):
        solid_type = self.calculator.solid_type
        # Use a fixed visualization edge length for consistent display
        vis_edge_length = 1.0
        vertices, edges, faces = [], [], []
        if solid_type.name == "TETRAHEDRON":
            vertices, edges, faces = self._generate_tetrahedron(vis_edge_length)
        elif solid_type.name == "CUBE":
            vertices, edges, faces = self._generate_cube(vis_edge_length)
        elif solid_type.name == "OCTAHEDRON":
            vertices, edges, faces = self._generate_octahedron(vis_edge_length)
        elif solid_type.name == "DODECAHEDRON":
            vertices, edges, faces = self._generate_dodecahedron(vis_edge_length)
        elif solid_type.name == "ICOSAHEDRON":
            vertices, edges, faces = self._generate_icosahedron(vis_edge_length)
        elif solid_type.name == "CUBOCTAHEDRON":
            vertices, edges, faces = self._generate_cuboctahedron(vis_edge_length)
        else:
            return
        if not vertices or not faces:
            return

        # --- Draw Solid Faces ---
        if self._show_faces:
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(1.0, 1.0)
            glColor3f(0.6, 0.7, 0.8)
            for face in faces:
                if len(face) < 3:
                    continue
                normal = self._calculate_normal(
                    vertices[face[0]], vertices[face[1]], vertices[face[2]]
                )
                glNormal3fv(normal)
                glBegin(GL_POLYGON)
                for vertex_index in face:
                    glVertex3fv(vertices[vertex_index])
                glEnd()
            glDisable(GL_POLYGON_OFFSET_FILL)

        # --- Draw Edges (Wireframe Overlay) ---
        if self._show_wireframe or not self._show_faces:
            glLineWidth(1.5)
            glColor3f(0.8, 0.8, 0.8)
            glDisable(GL_LIGHTING)
            glBegin(GL_LINES)
            for edge in edges:
                v1, v2 = vertices[edge[0]], vertices[edge[1]]
                glVertex3fv(v1)
                glVertex3fv(v2)
            glEnd()
            glEnable(GL_LIGHTING)

        # --- Draw Vertices ---
        if self._show_vertices:
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 0.2, 0.2)
            for v in vertices:
                glPushMatrix()
                glTranslatef(*v)
                quad = gluNewQuadric()
                gluSphere(quad, 0.045, 12, 8)
                gluDeleteQuadric(quad)
                glPopMatrix()
            glEnable(GL_LIGHTING)

        # --- Draw Spheres (Insphere, Midsphere, Circumsphere) ---
        # For the spheres, we need to use the correct proportions relative to the solid
        # Since we're using a fixed visualization edge length (vis_edge_length),
        # we need to calculate the sphere radii directly using the same proportions

        # Calculate the sphere radii based on the visualization edge length
        if solid_type.name == "TETRAHEDRON":
            insphere_r = vis_edge_length / (2 * math.sqrt(6))
            midsphere_r = vis_edge_length / math.sqrt(2)
            circumsphere_r = vis_edge_length * math.sqrt(6) / 4
        elif solid_type.name == "CUBE":
            insphere_r = vis_edge_length / 2
            midsphere_r = vis_edge_length * math.sqrt(2) / 2
            circumsphere_r = vis_edge_length * math.sqrt(3) / 2
        elif solid_type.name == "OCTAHEDRON":
            insphere_r = vis_edge_length * math.sqrt(6) / 6
            midsphere_r = vis_edge_length / math.sqrt(2)
            circumsphere_r = vis_edge_length * math.sqrt(2) / 2
        elif solid_type.name == "DODECAHEDRON":
            insphere_r = vis_edge_length * math.sqrt(250 + 110 * math.sqrt(5)) / 20
            midsphere_r = vis_edge_length * math.sqrt(10 + 2 * math.sqrt(5)) / 4
            circumsphere_r = vis_edge_length * math.sqrt(3) * (1 + math.sqrt(5)) / 4
        elif solid_type.name == "ICOSAHEDRON":
            insphere_r = vis_edge_length * math.sqrt(10 + 2 * math.sqrt(5)) / 10
            midsphere_r = vis_edge_length * (1 + math.sqrt(5)) / 4
            circumsphere_r = vis_edge_length * math.sqrt(10 + 2 * math.sqrt(5)) / 4
        elif solid_type.name == "CUBOCTAHEDRON":
            insphere_r = vis_edge_length * (1 + math.sqrt(2)) / 2
            midsphere_r = vis_edge_length * math.sqrt(2) / 2
            circumsphere_r = vis_edge_length
        else:
            insphere_r = midsphere_r = circumsphere_r = 0.0

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)

        if self._show_insphere:
            glColor4f(1.0, 0.3, 0.3, 0.25)  # Soft red, transparent
            quad = gluNewQuadric()
            gluSphere(quad, insphere_r, 32, 16)
            gluDeleteQuadric(quad)
        if self._show_midsphere:
            glColor4f(0.3, 1.0, 0.3, 0.22)  # Soft green, transparent
            quad = gluNewQuadric()
            gluSphere(quad, midsphere_r, 32, 16)
            gluDeleteQuadric(quad)
        if self._show_circumsphere:
            glColor4f(0.3, 0.3, 1.0, 0.18)  # Soft blue, transparent
            quad = gluNewQuadric()
            gluSphere(quad, circumsphere_r, 32, 16)
            gluDeleteQuadric(quad)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)

    # --- Mouse interaction for rotation and zoom ---
    def mousePressEvent(self, event):
        self.last_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.last_pos is not None:
            dx = event.position().x() - self.last_pos.x()
            dy = event.position().y() - self.last_pos.y()
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.last_pos = event.position().toPoint()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom *= 0.9 if delta > 0 else 1.1
        self.zoom = max(0.2, min(self.zoom, 5.0))
        self.update()

    # --- Geometry generation (complete versions) ---
    def _generate_tetrahedron(self, edge_length: float):
        """Generate vertices, edges, and faces for a tetrahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        a = edge_length / math.sqrt(2)
        vertices = [
            [a, 0, -a / math.sqrt(2)],
            [-a, 0, -a / math.sqrt(2)],
            [0, a, a / math.sqrt(2)],
            [0, -a, a / math.sqrt(2)],
        ]
        edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
        faces = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
        return vertices, edges, faces

    def _generate_cube(self, edge_length: float):
        """Generate vertices, edges, and faces for a cube.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        a = edge_length / 2
        vertices = [
            [-a, -a, -a],
            [a, -a, -a],
            [a, a, -a],
            [-a, a, -a],
            [-a, -a, a],
            [a, -a, a],
            [a, a, a],
            [-a, a, a],
        ]
        edges = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
        ]
        faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [0, 3, 7, 4],
            [1, 2, 6, 5],
        ]
        return vertices, edges, faces

    def _generate_octahedron(self, edge_length: float):
        """Generate vertices, edges, and faces for an octahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        a = edge_length / math.sqrt(2)
        vertices = [[a, 0, 0], [-a, 0, 0], [0, a, 0], [0, -a, 0], [0, 0, a], [0, 0, -a]]
        edges = [
            [0, 2],
            [0, 3],
            [0, 4],
            [0, 5],
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],
            [2, 4],
            [2, 5],
            [3, 4],
            [3, 5],
        ]
        faces = [
            [0, 2, 4],
            [0, 4, 3],
            [0, 3, 5],
            [0, 5, 2],
            [1, 4, 2],
            [1, 3, 4],
            [1, 5, 3],
            [1, 2, 5],
        ]
        return vertices, edges, faces

    def _generate_dodecahedron(self, edge_length: float):
        """Generate vertices, edges, and faces for a dodecahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        phi = (1 + math.sqrt(5)) / 2
        inv_phi = 1 / phi
        # Scale factor ensures edge length is correct
        scale_factor = edge_length / (2 * inv_phi)

        v = scale_factor
        pv = phi * scale_factor
        ipv = inv_phi * scale_factor

        vertices = [
            [v, v, v],
            [-v, v, v],
            [v, -v, v],
            [-v, -v, v],  # 0-3
            [v, v, -v],
            [-v, v, -v],
            [v, -v, -v],
            [-v, -v, -v],  # 4-7
            [0, ipv, pv],
            [0, -ipv, pv],
            [0, ipv, -pv],
            [0, -ipv, -pv],  # 8-11
            [pv, 0, ipv],
            [pv, 0, -ipv],
            [-pv, 0, ipv],
            [-pv, 0, -ipv],  # 12-15
            [ipv, pv, 0],
            [ipv, -pv, 0],
            [-ipv, pv, 0],
            [-ipv, -pv, 0],  # 16-19
        ]

        faces = [
            [0, 8, 9, 2, 12],
            [0, 12, 13, 4, 16],
            [0, 16, 18, 1, 8],
            [1, 18, 5, 15, 14],
            [1, 14, 3, 9, 8],
            [2, 9, 3, 19, 17],
            [2, 17, 6, 13, 12],
            [3, 14, 15, 7, 19],
            [4, 13, 6, 11, 10],
            [4, 10, 5, 18, 16],
            [5, 10, 11, 7, 15],
            [6, 17, 19, 7, 11],
        ]

        # Define edges from faces
        edge_set = set()
        for face in faces:
            for i in range(len(face)):
                v1_idx = face[i]
                v2_idx = face[(i + 1) % len(face)]
                edge_set.add(tuple(sorted((v1_idx, v2_idx))))
        edges = [list(edge) for edge in edge_set]

        return vertices, edges, faces

    def _generate_icosahedron(self, edge_length: float):
        """Generate vertices, edges, and faces for an icosahedron."""
        phi = (1 + math.sqrt(5)) / 2
        a = edge_length / 2

        vertices = [
            [-a, phi * a, 0],
            [a, phi * a, 0],
            [-a, -phi * a, 0],
            [a, -phi * a, 0],
            [0, -a, phi * a],
            [0, a, phi * a],
            [0, -a, -phi * a],
            [0, a, -phi * a],
            [phi * a, 0, -a],
            [phi * a, 0, a],
            [-phi * a, 0, -a],
            [-phi * a, 0, a],
        ]

        faces = [
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
        ]

        # Edges from faces
        edge_set = set()
        for face in faces:
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge_set.add(tuple(sorted((v1, v2))))
        edges = [list(edge) for edge in edge_set]

        return vertices, edges, faces

    def _generate_cuboctahedron(self, edge_length: float):
        """
        Generate vertices, edges, and faces for a cuboctahedron.

        Args:
            edge_length: The length of each edge.

        Returns:
            A tuple containing:
                - A list of vertices, where each vertex is a list of [x, y, z] coordinates.
                - A list of edges, where each edge is a list of [v1, v2] indices into the vertices list.
                - A list of faces, where each face is a list of vertex indices.
        """
        # The cuboctahedron has 12 vertices, 24 edges, 8 triangles, 6 squares
        # Vertices: all permutations of (±a/2, ±a/2, 0)
        a = edge_length / math.sqrt(2)
        verts = []
        for i in [-1, 1]:
            for j in [-1, 1]:
                verts.append([0, i * a, j * a])
                verts.append([i * a, 0, j * a])
                verts.append([i * a, j * a, 0])
        # Remove duplicates (should be 12 unique)
        vertices = []
        for v in verts:
            if v not in vertices:
                vertices.append(v)
        # Edges: connect vertices with distance = edge_length
        edges = []
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if i < j:
                    dist = math.sqrt(sum((v1[k] - v2[k]) ** 2 for k in range(3)))
                    if abs(dist - edge_length) < 1e-6:
                        edges.append([i, j])
        # Faces: 8 triangles, 6 squares
        # List of faces by vertex indices
        faces = [
            # Triangles
            [0, 2, 4],
            [1, 3, 5],
            [6, 8, 10],
            [7, 9, 11],
            [0, 6, 8],
            [1, 7, 9],
            [2, 10, 4],
            [3, 11, 5],
            # Squares
            [0, 2, 10, 6],
            [1, 3, 11, 7],
            [4, 5, 9, 8],
            [2, 3, 5, 4],
            [6, 7, 9, 8],
            [0, 1, 7, 6],
        ]
        return vertices, edges, faces

    def _calculate_normal(self, v1, v2, v3):
        """Calculate the normal vector of a triangle face.

        Args:
            v1, v2, v3: Lists or tuples representing the [x, y, z] coordinates of the vertices.

        Returns:
            A numpy array representing the normalized normal vector.
        """
        vec1 = np.array(v2) - np.array(v1)
        vec2 = np.array(v3) - np.array(v1)
        normal = np.cross(vec1, vec2)
        norm = np.linalg.norm(normal)
        if norm == 0:
            return np.array([0.0, 0.0, 0.0])
        return normal / norm
