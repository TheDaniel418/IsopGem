"""
@file adyton_opengl_widget.py
@description PyOpenGL-based widget for 3D visualization of the Adyton of the Seven.
@author IsopGemini
@created 2024-08-12
@lastModified 2024-08-12
@dependencies PyQt6, PyOpenGL, numpy, OpenGL.GLUT
"""

import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QPainter, QFont, QImage
from PyQt6.QtCore import QSize

from astrology.services.skyfield_service import SkyfieldService
from astrology.services.ephemeris_service import EphemerisService
from datetime import datetime

# --- Constants for Adyton's Geographical Grounding ---
# Location: Presumably Temple of Karnak, Luxor, Egypt
ADYTON_LATITUDE_DEG = 25.0 + (43.0 / 60.0) + (7.46 / 3600.0)  # 25°43'7.46" N
ADYTON_LONGITUDE_DEG = 32.0 + (39.0 / 60.0) + (26.64 / 3600.0) # 32°39'26.64" E
ADYTON_ELEVATION_M = 80.0  # 80 meters above sea level
# The 3D scene origin (0,0,0) corresponds to this precise point of observation.
# The floor of the Adyton (drawn at y=0 in local coordinates) represents the ground
# at this elevation.
# ----------------------------------------------------

# --- Unit of Measure: The Z'Bit (Cubit of AMUN) ---
ZBIT_IMPERIAL_INCHES = 19.0
IMPERIAL_INCHES_TO_METERS = 0.0254
METERS_PER_ZBIT = ZBIT_IMPERIAL_INCHES * IMPERIAL_INCHES_TO_METERS # Approx 0.4826 meters
# For OpenGL rendering, 1.0 unit will represent 1 Z'Bit.
# --------------------------------------------------

# --- Constants for Adyton's Dimensions (in Z'Bits where applicable) ---
ADYTON_NUM_SIDES = 7
ADYTON_PILLARS_PER_SIDE = 8
ADYTON_CUBES_PER_PILLAR = 13
ADYTON_CUBE_SIDE_LENGTH_ZBITS = 2.0 # Each cube is 2 Z'Bit wide, high, and deep
ADYTON_SIDE_FILL_FACTOR = 0.95
MAX_DISPLAY_ECLIPTIC_LATITUDE = 15.0 # Max +/- ecliptic latitude to display on the veil height

# Calculate the effective outer radius in Z'Bits based on fitting the Z'Bit cubes
l_side_for_pillars_zbits = ADYTON_PILLARS_PER_SIDE * ADYTON_CUBE_SIDE_LENGTH_ZBITS
l_side_total_zbits = l_side_for_pillars_zbits / ADYTON_SIDE_FILL_FACTOR
ADYTON_CALCULATED_OUTER_RADIUS_ZBITS = l_side_total_zbits / (2 * math.sin(math.pi / ADYTON_NUM_SIDES))
# Cube dimensions are derived from the above to fit the structure.
# -------------------------------------------------

# --- Planetary Color Mappings (RGB values divided by 255) ---
PLANETARY_COLORS = {
    "Sun": (254/255, 0/255, 0/255),          # Bright Red
    "Mercury": (254/255, 0/255, 60/255),     # Magenta/Purple-Red
    "Venus": (60/255, 60/255, 254/255),      # Indigo/Blue-Purple
    "Moon": (0/255, 254/255, 254/255),       # Cyan
    "Mars": (0/255, 0/255, 254/255),         # Deep Blue
    "Jupiter": (254/255, 194/255, 0/255),    # Gold/Amber
    "Saturn": (194/255, 254/255, 0/255)      # Chartreuse/Lime
}

# --- Zodiacal Sign Color Mappings (RGB values divided by 255) ---
ZODIAC_COLORS = {
    "Sagittarius": (97/255, 254/255, 0/255),    # Decimal 4, Letter p
    "Virgo": (0/255, 97/255, 254/255),          # Decimal 5, Letter w
    "Gemini": (254/255, 97/255, 0/255),         # Decimal 7, Letter j
    "Pisces": (97/255, 0/255, 254/255),         # Decimal 8, Letter w
    "Aries": (254/255, 60/255, 0/255),          # Decimal 10, Letter o
    "Libra": (254/255, 0/255, 97/255),          # Decimal 11, Letter g
    "Capricorn": (0/255, 254/255, 97/255),      # Decimal 19, Letter z
    "Cancer": (0/255, 194/255, 254/255),        # Decimal 20, Letter b
    "Leo": (254/255, 0/255, 194/255),           # Decimal 12, Letter f
    "Taurus": (194/255, 0/255, 254/255),        # Decimal 15, Letter s
    "Aquarius": (60/255, 254/255, 0/255),       # Decimal 21, Letter m
    "Scorpio": (0/255, 254/255, 60/255)         # Decimal 24, Letter n
}

# Mapping of planets to their Trigrammaton letters - changed to lowercase
PLANET_TRIGRAMMATON_LETTERS = {
    "Sun": "e",
    "Jupiter": "v",
    "Saturn": "r",
    "Moon": "0",  # Changed from ")" to "0" for correct Moon trigram
    "Venus": "k",
    "Mars": "u",
    "Mercury": "q"
}

# Mapping of zodiac signs to their Trigrammaton letters
ZODIAC_TRIGRAMMATON_LETTERS = {
    "Sagittarius": "p",    # Decimal 4
    "Virgo": "w",          # Decimal 5
    "Gemini": "j",         # Decimal 7
    "Pisces": "w",         # Decimal 8 (Note: Same as Virgo, might be an error?)
    "Aries": "o",          # Decimal 10
    "Libra": "g",          # Decimal 11
    "Capricorn": "z",      # Decimal 19
    "Cancer": "b",         # Decimal 20
    "Leo": "f",            # Decimal 12
    "Taurus": "s",         # Decimal 15
    "Aquarius": "m",       # Decimal 21
    "Scorpio": "n"         # Decimal 24
}

# Non-lit/toon version of colors for maximum visibility
PLANET_TOON_COLORS = {
    "Sun": (1.0, 0.0, 0.0),                  # Pure Red
    "Mercury": (1.0, 0.0, 0.6),              # Pure Magenta
    "Venus": (0.0, 0.0, 1.0),                # Pure Blue
    "Moon": (0.0, 1.0, 1.0),                 # Pure Cyan
    "Mars": (0.0, 0.0, 1.0),                 # Pure Blue
    "Jupiter": (1.0, 0.5, 0.0),              # Pure Orange for Jupiter
    "Saturn": (0.5, 1.0, 0.0)                # Pure Lime for Saturn
}

# --- Adyton Wall to Planet Mapping ---
WALL_PLANET_MAPPING = [
    "Saturn",   # Wall 0
    "Sun",      # Wall 1
    "Mercury",  # Wall 2
    "Moon",     # Wall 3
    "Venus",    # Wall 4
    "Jupiter",  # Wall 5
    "Mars"      # Wall 6
]

# --- Column to Planet Mapping for each Wall ---
COLUMN_PLANET_MAPPING = {
    "Saturn": ["Venus", "Jupiter", "Mars", "Saturn", "Saturn", "Sun", "Mercury", "Moon"],
    "Sun": ["Jupiter", "Mars", "Saturn", "Sun", "Sun", "Mercury", "Moon", "Venus"],
    "Mercury": ["Mars", "Saturn", "Sun", "Mercury", "Mercury", "Moon", "Venus", "Jupiter"],
    "Moon": ["Saturn", "Sun", "Mercury", "Moon", "Moon", "Venus", "Jupiter", "Mars"],
    "Venus": ["Sun", "Mercury", "Moon", "Venus", "Venus", "Jupiter", "Mars", "Saturn"],
    "Jupiter": ["Mercury", "Moon", "Venus", "Jupiter", "Jupiter", "Mars", "Saturn", "Sun"],
    "Mars": ["Moon", "Venus", "Jupiter", "Mars", "Mars", "Saturn", "Sun", "Mercury"]
}

class OpenGLAxesIndicator:
    """
    Modular OpenGL 3D axes indicator for overlay use in any QOpenGLWidget.
    Usage: instantiate and call draw_axes() in paintGL after main scene.
    """

    def __init__(self, size=60, margin=12):
        self.size = size
        self.margin = margin

    def draw_axes(self, widget_width, widget_height):
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


class AdytonOpenGLWidget(QOpenGLWidget):
    """
    OpenGL Widget for 3D visualization of the Adyton of the Seven.
    Renders the heptagonal structure with 56 pillars that are 13 cubes high.
    """
    
    # Define signals for interaction
    pillar_selected = pyqtSignal(int, int, int)  # pillar_index, cube_index, cube_height
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Adyton Location Data (for reference within the instance if needed later) ---
        self.latitude = ADYTON_LATITUDE_DEG
        self.longitude = ADYTON_LONGITUDE_DEG
        self.elevation = ADYTON_ELEVATION_M
        # --------------------------------------------------------------------------
        
        # --- Adyton Structure Parameters (dimensions in Z'Bits) ---
        self.num_sides = ADYTON_NUM_SIDES
        self.pillars_per_side = ADYTON_PILLARS_PER_SIDE
        self.cubes_per_pillar = ADYTON_CUBES_PER_PILLAR
        self.cube_side_length_zbits = ADYTON_CUBE_SIDE_LENGTH_ZBITS
        self.outer_radius_zbits = ADYTON_CALCULATED_OUTER_RADIUS_ZBITS # Using calculated radius
        self.side_fill_factor = ADYTON_SIDE_FILL_FACTOR # Still needed for interpretation
        self.total_pillars = self.num_sides * self.pillars_per_side
        # ----------------------------------
        
        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(500, 500)
        
        # Camera and view parameters
        self.rotation_x = 30.0
        self.rotation_y = 40.0 # Initial rotation, pillars are calculated relative to this
        self.zoom = 1.0
        self.last_pos = None
        
        # Visualization options
        self._show_wireframe = True
        self._show_solid = True
        self._show_markers = True
        self._show_labels = True
        self._show_floor = True
        
        # Marker positions (from 2D circle view)
        self._marker_positions = {}
        
        # Pillar positions
        self._pillar_positions = []
        
        # Axes indicator
        self.axes_indicator = OpenGLAxesIndicator()
        
        # Display list ID
        self.cube_with_pyramid_dl_id = None
        
        # Reset view button
        self.reset_btn = QPushButton("Reset View", self)
        self.reset_btn.setStyleSheet(
            "background: rgba(255,255,255,0.8); border-radius: 8px; padding: 4px 12px;"
        )
        self.reset_btn.clicked.connect(self.reset_view)
        self.reset_btn.raise_()
        self.reset_btn.show()
        
        # Selected pillar/cube
        self.selected_pillar = None
        self.selected_cube = None

        # --- Skyfield Service ---
        self.skyfield_service = SkyfieldService()
        self.skyfield_service.set_observer_location(
            latitude_deg=ADYTON_LATITUDE_DEG,
            longitude_deg=ADYTON_LONGITUDE_DEG,
            elevation_m=ADYTON_ELEVATION_M
        )

        # --- Adyton Belt Calculation & Sky Dome (MUST be defined before pillar calculation) ---
        self.wall_height_zbits = self.cubes_per_pillar * self.cube_side_length_zbits
        self.inner_wall_radius_zbits = self.outer_radius_zbits - self.cube_side_length_zbits
        if self.inner_wall_radius_zbits > 0:
            alpha_rad = math.atan2(self.wall_height_zbits, self.inner_wall_radius_zbits)
            self.adyton_belt_upper_alt_deg = math.degrees(alpha_rad)
        else:
            self.adyton_belt_upper_alt_deg = 90.0
            print("WARNING: inner_wall_radius_zbits is not positive, Adyton belt calculation might be off.")
        self.sky_dome_radius = self.outer_radius_zbits * 4.0
        # --------------------------------
        
        # Pillar positions - Initialize list then calculate
        self._pillar_positions = [] 
        self._calculate_pillar_positions()
        
        # Display list ID - This should be initialized in initializeGL, not here.
        # self.cube_with_pyramid_dl_id = None 
        
        # Reset view button
        self.reset_btn.show()

        # For celestial projections
        self.ephemeris_service = EphemerisService() # Initialize or receive an instance
        # Default to Winter Solstice 2020, noon UTC, for the Great Conjunction
        self.current_datetime = datetime(2020, 12, 21, 12, 0, 0) 
        self.current_latitude = ADYTON_LATITUDE_DEG  # Use defined Adyton latitude
        self.current_longitude = ADYTON_LONGITUDE_DEG # Use defined Adyton longitude
        
        self.traditional_planets = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"
        ]
        # Skyfield might use 'jupiter barycenter', 'saturn barycenter'
        # We'll map these in EphemerisService or handle common names

        self.famous_stars = [
            "Sirius", "Canopus", "Alpha Centauri", "Arcturus", "Vega", 
            "Capella", "Rigel", "Procyon", "Achernar", "Betelgeuse", 
            "Hadar", "Altair", "Acrux", "Aldebaran", "Spica", 
            "Antares", "Pollux", "Fomalhaut", "Deneb", "Mimosa"
        ]
        
        self.celestial_body_positions = {} # Stores {name: (alt, az, projected_3d_pos)}

        # Dimensions for the "inner veil"
        self.inner_veil_radius = self.outer_radius_zbits * 0.85 # Slightly smaller than pillar inner radius
        self.inner_veil_height = self.wall_height_zbits # Full height of pillars

        # --- Calculate Celestial Reference Angles for Ecliptic Projection ---
        # This needs _pillar_positions to be calculated first.
        # And ephemeris_service to be initialized.
        if self._pillar_positions and self.ephemeris_service:
            # 1. Visual angle of the Adyton's reference point (midpoint between pillar 27 and 28)
            # Pillar indices are 0-55. Pillar 28 is index 27, Pillar 29 is index 28.
            # The user specified "between pillars 28 and 29 (index 27 and 28)"
            # which means between the pillar at index 27 and the pillar at index 28.
            if len(self._pillar_positions) > 28: # Ensure pillars exist
                x_p27 = self._pillar_positions[27]['position'][0]
                z_p27 = self._pillar_positions[27]['position'][2]
                x_p28 = self._pillar_positions[28]['position'][0]
                z_p28 = self._pillar_positions[28]['position'][2]
                
                mid_x = (x_p27 + x_p28) / 2.0
                mid_z = (z_p27 + z_p28) / 2.0
                adyton_midpoint_visual_angle_deg = math.degrees(math.atan2(mid_z, mid_x))

                # 2. Ecliptic longitude of the Sun at the reference datetime (Winter Solstice 2020)
                # self.current_datetime is already set to Dec 21, 2020, 12:00 UTC
                ws_sun_ecl_coords = self.ephemeris_service.get_celestial_body_ecliptic_coords(
                    "Sun",
                    self.current_datetime.year,
                    self.current_datetime.month,
                    self.current_datetime.day,
                    self.current_datetime.hour,
                    self.current_datetime.minute,
                    self.current_datetime.second,
                )
                if ws_sun_ecl_coords:
                    self.winter_solstice_sun_ecliptic_lon_deg = ws_sun_ecl_coords[0]
                     # 3. Calculate the Adyton's visual angle for 0° Ecliptic Longitude (Aries)
                    self.adyton_aries_angle_deg = adyton_midpoint_visual_angle_deg - self.winter_solstice_sun_ecliptic_lon_deg
                    print(f"DEBUG: Adyton Midpoint Visual Angle: {adyton_midpoint_visual_angle_deg:.2f}°")
                    print(f"DEBUG: Winter Solstice Sun Ecliptic Lon: {self.winter_solstice_sun_ecliptic_lon_deg:.2f}°")
                    print(f"DEBUG: Adyton Aries Angle (Offset): {self.adyton_aries_angle_deg:.2f}°")
                else:
                    print("ERROR: Could not get Winter Solstice Sun ecliptic coordinates for reference.")
                    self.winter_solstice_sun_ecliptic_lon_deg = 270.0 # Fallback
                    self.adyton_aries_angle_deg = adyton_midpoint_visual_angle_deg - self.winter_solstice_sun_ecliptic_lon_deg # Fallback

            else:
                print("ERROR: Pillar positions not sufficient to calculate Adyton reference angle.")
                self.winter_solstice_sun_ecliptic_lon_deg = 270.0 # Fallback
                self.adyton_aries_angle_deg = 0.0 # Fallback
        else:
            print("ERROR: Pillar positions or ephemeris service not ready for celestial reference calculation.")
            self.winter_solstice_sun_ecliptic_lon_deg = 270.0 # Fallback
            self.adyton_aries_angle_deg = 0.0 # Fallback
        # ---------------------------------------------------------------------

        self._recalculate_celestial_positions() # Initial calculation with new references if available

        # Timer for animation (optional, if we want smooth transitions or real-time updates)
        # self.animation_timer = QTimer(self)
        # self.animation_timer.timeout.connect(self.update) # Or a specific update method
        # self.animation_timer.start(50) # Update every 50ms

        # Initialize font if glutBitmapCharacter is available
        if bool(glutBitmapCharacter):
            try:
                # Configure font for Trigrammaton if possible
                # GLUT only supports built-in fonts, so we'll need to use QPainter for custom fonts
                self.use_custom_font = True
            except Exception as e:
                print(f"Warning: Could not initialize Trigrammaton font: {e}")
                self.use_custom_font = False
        else:
            self.use_custom_font = False
            print("Warning: glutBitmapCharacter not available, cannot render text in OpenGL")

        # Textures for Trigrammaton letters
        self.trigrammaton_textures = {}

    def _calculate_pillar_positions(self):
        """Calculate positions for all pillars in the heptagon.
           All calculations here will use Z'Bits as the unit of length.
        """
        # self._pillar_positions is already initialized in __init__ before this is called
        
        center = [0.0, 0.0, 0.0] # Origin in Z'Bits
        # Use the defined constants for dimensions
        radius = self.outer_radius_zbits # This is now in Z'Bits
        num_holes_per_side = self.pillars_per_side
        num_sides = self.num_sides
        total_pillars = self.total_pillars
        side_fill_factor = self.side_fill_factor # For reference, though radius is now derived
        cube_actual_side_length_zbits = self.cube_side_length_zbits # Should be 2.0 Z'Bit

        # l_side (heptagon edge length) in Z'Bits, derived from the calculated radius
        l_side_zbits = 2 * radius * math.sin(math.pi / num_sides)
        
        # This should closely match cube_actual_side_length_zbits * num_holes_per_side / side_fill_factor
        # Let's verify the allocatable length based on the derived radius and the target cube size.
        # The important part is that the cube drawing will use cube_actual_side_length_zbits.
        allocatable_length_for_pillars_zbits = num_holes_per_side * cube_actual_side_length_zbits
        
        # actual_cube_full_width is essentially our defined cube_actual_side_length_zbits
        # The term is kept for consistency with prior logic, but it's now based on a fixed definition.
        actual_cube_full_width = cube_actual_side_length_zbits
        actual_cube_half_width = 0.5 * actual_cube_full_width
        
        heptagon_vertices = []
        for i in range(num_sides):
            angle_rad = 2.0 * math.pi * i / num_sides - math.pi / 2.0
            x_vert = center[0] + radius * math.cos(angle_rad)
            z_vert = center[2] + radius * math.sin(angle_rad)
            heptagon_vertices.append((x_vert, 0.0, z_vert))
        
        first_hole_of_bottom_edge = 24
        temp_positions = [None] * total_pillars

        for side_index in range(num_sides):
            start_vertex = heptagon_vertices[side_index]
            end_vertex = heptagon_vertices[(side_index + 1) % num_sides]
            
            side_dx = end_vertex[0] - start_vertex[0]
            side_dz = end_vertex[2] - start_vertex[2]
            
            # Perpendicular vector to the current side (for positioning AND rotation)
            edge_perp_dx = -side_dz
            edge_perp_dz = side_dx
            
            edge_perp_length = math.sqrt(edge_perp_dx**2 + edge_perp_dz**2)
            norm_edge_perp_dx, norm_edge_perp_dz = (0, 0)
            if edge_perp_length > 0:
                norm_edge_perp_dx = edge_perp_dx / edge_perp_length
                norm_edge_perp_dz = edge_perp_dz / edge_perp_length
            
            # Rotation angle is calculated ONCE per side, shared by all pillars on this side.
            rotation_angle = math.degrees(math.atan2(norm_edge_perp_dz, norm_edge_perp_dx))
            if rotation_angle < 0:
                rotation_angle += 360.0
            
            for i in range(num_holes_per_side):
                # Distribute pillars along the side
                # t is the normalized distance along the current heptagon side
                t = (i + 0.5) / num_holes_per_side
                
                # Center of the pillar base ON the heptagon edge
                cx_on_edge = start_vertex[0] + t * side_dx
                cz_on_edge = start_vertex[2] + t * side_dz
                
                # Shift the pillar center INWARD from the edge by half the cube's depth
                # so that the CUBE'S OUTER FACE is flush with the heptagon edge.
                # The outward normal is (norm_edge_perp_dx, norm_edge_perp_dz).
                # The cube's local +X face will align with this outward normal.
                # This local +X face is actual_cube_half_width from the cube's center.
                # So, the cube's center must be -actual_cube_half_width along the outward normal from the edge.
                cx_shifted = cx_on_edge - norm_edge_perp_dx * actual_cube_half_width
                cz_shifted = cz_on_edge - norm_edge_perp_dz * actual_cube_half_width
                
                pillar_base_center_y = -radius + actual_cube_half_width # Floor level
                
                pillar_index_abs = (first_hole_of_bottom_edge + (side_index * num_holes_per_side) + i) % total_pillars
                
                temp_positions[pillar_index_abs] = {
                    'index': pillar_index_abs,
                    'position': (cx_shifted, 0.0, cz_shifted),
                    'side': side_index,
                    'side_position': i,
                    'rotation': rotation_angle, # Use the shared rotation angle for the side
                    'cube_draw_half_width': actual_cube_half_width
                }
        
        self._pillar_positions = temp_positions
        # DO NOT CALL DRAWING METHODS FROM HERE

    def initializeGL(self):
        """Initialize OpenGL settings."""
        # Set background color to dark blue (matches the 2D view)
        glClearColor(0.1, 0.1, 0.4, 1.0)
        
        # Enable depth testing for proper 3D rendering
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # Enable back-face culling (Optimization)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable smooth lines
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable lighting for better 3D appearance
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)  # Add a second light
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Light 0 properties - main light
        light0_pos = [5.0, 10.0, 5.0, 1.0]  # Positional light
        light0_ambient = [0.5, 0.5, 0.5, 1.0]  # Increased ambient component
        light0_diffuse = [0.9, 0.9, 0.9, 1.0]  # Increased diffuse component
        light0_specular = [0.7, 0.7, 0.7, 1.0]  # Increased specular component
        
        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)
        
        # Light 1 properties - fill light from opposite side
        light1_pos = [-5.0, 8.0, -5.0, 1.0]  # Opposite position
        light1_ambient = [0.3, 0.3, 0.3, 1.0]
        light1_diffuse = [0.6, 0.6, 0.6, 1.0]
        light1_specular = [0.4, 0.4, 0.4, 1.0]
        
        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
        glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
        glLightfv(GL_LIGHT1, GL_SPECULAR, light1_specular)

        # Enhanced material properties for better color clarity
        mat_specular = [0.8, 0.8, 0.8, 1.0]  # Increased specular component
        mat_shininess = [40.0]  # Slightly reduced shininess for less reflectivity
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

        # Enable smooth shading
        glShadeModel(GL_SMOOTH)

        # Create display list for cube with pyramid
        self.cube_with_pyramid_dl_id = glGenLists(1)
        glNewList(self.cube_with_pyramid_dl_id, GL_COMPILE)
        self._define_unit_cube_with_pyramid_geometry() # New method to draw the unit geometry
        glEndList()
        
        # Initialize glut for text rendering
        # The reset button is already initialized in __init__, no need to recreate it here
        
        # Initialize axes indicator
        self.axes_indicator = OpenGLAxesIndicator()
        
        glMatrixMode(GL_MODELVIEW)
        self.show_axes = True
        self.show_floor = True
        self.show_pillars = True
        self.show_galactic_center_marker = True
        self.show_celestial_projections = True # New toggle for projections

        # Initialize font if glutBitmapCharacter is available
        if bool(glutBitmapCharacter):
            try:
                # Configure font for Trigrammaton if possible
                # GLUT only supports built-in fonts, so we'll need to use QPainter for custom fonts
                self.use_custom_font = True
            except Exception as e:
                print(f"Warning: Could not initialize Trigrammaton font: {e}")
                self.use_custom_font = False
        else:
            self.use_custom_font = False
            print("Warning: glutBitmapCharacter not available, cannot render text in OpenGL")
        
        # Initialize textures
        self.trigrammaton_textures = {}
        self.zodiac_textures = {}  # Initialize dictionary for zodiac letter textures
        
        # Create textures for Trigrammaton letters
        self._create_trigrammaton_textures()
        
        # Pre-create textures for all zodiac signs
        for zodiac_sign, letter in ZODIAC_TRIGRAMMATON_LETTERS.items():
            self._create_zodiac_letter_texture(zodiac_sign, letter)
        
        # Load ternary data from CSV files
        self._load_ternary_data()
        
        # Debug printout of ternary data structure
        self._debug_print_ternary_data_structure()

    def _define_unit_cube_with_pyramid_geometry(self, unit_half_width=0.5):
        """
        Defines the geometry for a single unit cube (centered at origin)
        with a truncated pyramid on its +Z face. 
        This is called once to compile a display list.
        It does NOT set colors or transformations other than local cube/pyramid geometry.
        
        The following pyramid faces are NOT drawn in the display list, and are instead
        drawn individually in _draw_cube method for custom coloring:
        - Face 0: Top face (truncated square) - UPPER FACE with upper trigram
        - Face 1: Bottom diagonal face - LOWER FACE with lower trigram
        - Face 2: Right diagonal face - PLANETARY COLOR FACE
        - Face 3: Top diagonal face - TOP FACE with trigram
        - Face 4: Left diagonal face - ZODIACAL COLOR FACE
        
        No faces of the pyramid are drawn in the display list, only the cube base.
        
        Args:
            unit_half_width (float): Half the side length of the unit cube.
        """
        # --- Draw Unit Cube --- (Derived from _draw_cube)
        # No glPush/Pop/Translate/Rotate/Scale here, just raw geometry at origin.
        # Vertices for a cube of side length (2 * unit_half_width)
        s = unit_half_width
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s], # Back
            [-s, -s,  s], [s, -s,  s], [s, s,  s], [-s, s,  s]  # Front
        ]
        faces = [
            [0, 1, 2, 3], [7, 6, 5, 4], [3, 2, 6, 7], # Back, Front, Top
            [0, 4, 5, 1], [0, 3, 7, 4], [1, 5, 6, 2]  # Bottom, Left, Right
        ]
        normals = [
            [0,0,-1], [0,0,1], [0,1,0], 
            [0,-1,0], [-1,0,0], [1,0,0]
        ]

        glBegin(GL_QUADS)
        for i, face_indices in enumerate(faces):
            glNormal3fv(normals[i])
            for vertex_index in face_indices:
                glVertex3fv(vertices[vertex_index])
        glEnd()

        # --- Draw Truncated Pyramid on +Z face --- (Derived from _draw_truncated_pyramid)
        # Parameters for the pyramid relative to the unit cube's face
        pyramid_top_scale = 0.5  # Top face is 50% of cube face
        pyramid_depth_scale = 0.3  # Depth is 30% of unit_half_width

        base_s_pyr = s # Pyramid base matches cube face half_width
        top_s_pyr = base_s_pyr * pyramid_top_scale
        depth_pyr = base_s_pyr * pyramid_depth_scale

        v_base_pyr = [
            [-base_s_pyr, -base_s_pyr, base_s_pyr], 
            [ base_s_pyr, -base_s_pyr, base_s_pyr],
            [ base_s_pyr,  base_s_pyr, base_s_pyr],
            [-base_s_pyr,  base_s_pyr, base_s_pyr],
        ]
        v_top_pyr = [
            [-top_s_pyr, -top_s_pyr, base_s_pyr + depth_pyr],
            [ top_s_pyr, -top_s_pyr, base_s_pyr + depth_pyr],
            [ top_s_pyr,  top_s_pyr, base_s_pyr + depth_pyr],
            [-top_s_pyr,  top_s_pyr, base_s_pyr + depth_pyr],
        ]
        all_vertices_pyr = v_base_pyr + v_top_pyr
        
        # Define each face separately to allow different coloring
        # 0=Top(truncated), 1=Bottom, 2=Right, 3=Top, 4=Left
        pyramid_faces_def = [
            [7,6,5,4],  # Face 0: Top face (truncated square) - UPPER FACE (skip, will be drawn separately)
            [0,1,5,4],  # Face 1: Bottom diagonal face - LOWER FACE (skip, will be drawn separately)
            [1,2,6,5],  # Face 2: Right diagonal face - PLANETARY COLOR FACE (skip, drawn separately)
            [2,3,7,6],  # Face 3: Top diagonal face - TOP DIAGONAL (skip, will be drawn separately)
            [3,0,4,7]   # Face 4: Left diagonal face - ZODIACAL COLOR FACE (skip, drawn separately)
        ]
        
        # Calculate normals for each face - these will be available to anyone using display list
        # Store them as class constants so _draw_cube can access them
        if not hasattr(self, 'pyramid_normals'):
            self.pyramid_normals = []
            
            # Face 0: Top face normal (Z+)
            self.pyramid_normals.append([0, 0, 1])
            
            # Face 1: Bottom diagonal face normal
            vec1_b = np.array(all_vertices_pyr[1]) - np.array(all_vertices_pyr[0])
            vec2_b = np.array(all_vertices_pyr[4]) - np.array(all_vertices_pyr[0])
            norm_b = np.cross(vec1_b, vec2_b)
            if np.linalg.norm(norm_b) > 0:
                norm_b = norm_b / np.linalg.norm(norm_b)
            if norm_b[1] < 0:  # Ensure outward-facing normal
                self.pyramid_normals.append(list(norm_b))
            else:
                self.pyramid_normals.append(list(-norm_b))
            
            # Face 2: Right diagonal face normal
            vec1_r = np.array(all_vertices_pyr[2]) - np.array(all_vertices_pyr[1])
            vec2_r = np.array(all_vertices_pyr[5]) - np.array(all_vertices_pyr[1])
            norm_r = np.cross(vec1_r, vec2_r)
            if np.linalg.norm(norm_r) > 0:
                norm_r = norm_r / np.linalg.norm(norm_r)
            if norm_r[0] > 0:  # Ensure outward-facing normal
                self.pyramid_normals.append(list(norm_r))
            else:
                self.pyramid_normals.append(list(-norm_r))
            
            # Face 3: Top diagonal face normal
            vec1_t = np.array(all_vertices_pyr[3]) - np.array(all_vertices_pyr[2])
            vec2_t = np.array(all_vertices_pyr[6]) - np.array(all_vertices_pyr[2])
            norm_t = np.cross(vec1_t, vec2_t)
            if np.linalg.norm(norm_t) > 0:
                norm_t = norm_t / np.linalg.norm(norm_t)
            if norm_t[1] > 0:  # Ensure outward-facing normal
                self.pyramid_normals.append(list(norm_t))
            else:
                self.pyramid_normals.append(list(-norm_t))
            
            # Face 4: Left diagonal face normal
            vec1_l = np.array(all_vertices_pyr[0]) - np.array(all_vertices_pyr[3])
            vec2_l = np.array(all_vertices_pyr[7]) - np.array(all_vertices_pyr[3])
            norm_l = np.cross(vec1_l, vec2_l)
            if np.linalg.norm(norm_l) > 0:
                norm_l = norm_l / np.linalg.norm(norm_l)
            if norm_l[0] < 0:  # Ensure outward-facing normal
                self.pyramid_normals.append(list(norm_l))
            else:
                self.pyramid_normals.append(list(-norm_l))
        
        # Store vertices for later reference - helpful for custom face drawing
        if not hasattr(self, 'pyramid_vertices'):
            self.pyramid_vertices = all_vertices_pyr
            
        # Skip ALL pyramid faces in the display list
        # Faces 0-4 are drawn separately in _draw_cube with custom colors and textures
        
        # We don't draw any pyramid faces here
        # Just storing the normals and vertices for use in _draw_cube

        # Wireframe for pyramid (part of the display list)
        # No lighting for wireframes
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)
        
        # Edges for pyramid wireframe
        pyramid_edges_def = [
            [0,1],[1,2],[2,3],[3,0],  # Base edges
            [4,5],[5,6],[6,7],[7,4],  # Top edges
            [0,4],[1,5],[2,6],[3,7]   # Connecting edges
        ]
        
        glBegin(GL_LINES)
        for edge in pyramid_edges_def:
            glVertex3fv(all_vertices_pyr[edge[0]])
            glVertex3fv(all_vertices_pyr[edge[1]])
        glEnd()
        
        glEnable(GL_LIGHTING) # Re-enable lighting
        
        # Print debug info about the geometry once
        if not hasattr(self, '_pyramid_debug_printed'):
            print("DEBUG: Pyramid vertices and normals initialized:")
            print(f"DEBUG: Face 0 (Upper) normal: {self.pyramid_normals[0]}")
            print(f"DEBUG: Face 1 (Lower) normal: {self.pyramid_normals[1]}")
            print(f"DEBUG: Face 2 (Right) normal: {self.pyramid_normals[2]}")
            print(f"DEBUG: Face 3 (Top) normal: {self.pyramid_normals[3]}")
            print(f"DEBUG: Face 4 (Left) normal: {self.pyramid_normals[4]}")
            self._pyramid_debug_printed = True

    def resizeGL(self, width, height):
        """Handle widget resize events."""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / max(height, 1)
        gluPerspective(45.0, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Update reset button position
        self.reset_btn.move(width - 110, 10)

    def paintGL(self):
        """Render the OpenGL scene."""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up camera view
        glLoadIdentity()
        glTranslatef(0.0, -2.0, -20.0 * self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Draw the scene
        if self.show_floor:
            self._draw_floor()
        
        # Draw pillars and cubes
        if self.show_pillars:
            self._draw_pillars()
        
        # Draw markers
        if self.show_galactic_center_marker and hasattr(self, 'gc_alt_az_position'):
            self._draw_galactic_center(self.gc_alt_az_position)
        
        if self.show_celestial_projections:
            self._draw_projected_celestial_bodies()
        
        # Draw pillar number labels if enabled
        if self._show_labels:
            self._draw_pillar_number_labels()
        
        # Draw galactic center reference line
        self._draw_galactic_center()
        
        # Draw axes indicator overlay
        self.axes_indicator.draw_axes(self.width(), self.height())

        # Draw the central truncated tetrahedron
        self._draw_center_truncated_tetrahedron()

        # Draw celestial references (like Adyton Belt guides)
        self._draw_celestial_references()

    def _draw_floor(self):
        """Draw the floor with heptagon outline."""
        center = [0.0, 0.0, 0.0]
        wall_outer_radius_zbits = self.outer_radius_zbits
        cube_side_length_zbits = self.cube_side_length_zbits
        inner_wall_radius_zbits = wall_outer_radius_zbits - cube_side_length_zbits
        # floor_radius_zbits defines the inner edge of the silver ring
        floor_radius_zbits = inner_wall_radius_zbits - 1.0 

        # Vertices for the inner edge of the silver ring
        ring_inner_vertices = []
        for i in range(self.num_sides):
            angle = 2.0 * math.pi * i / self.num_sides - math.pi / 2.0
            x = center[0] + floor_radius_zbits * math.cos(angle)
            z = center[2] + floor_radius_zbits * math.sin(angle)
            ring_inner_vertices.append((x, 0.0, z))

        # Vertices for the outer edge of the silver ring (coincides with inner wall base)
        ring_outer_vertices = []
        for i in range(self.num_sides):
            angle = 2.0 * math.pi * i / self.num_sides - math.pi / 2.0
            x = center[0] + inner_wall_radius_zbits * math.cos(angle)
            z = center[2] + inner_wall_radius_zbits * math.sin(angle)
            ring_outer_vertices.append((x, 0.0, z))

        glDisable(GL_LIGHTING)

        # 1. Draw the Ma'at Blue central floor
        maat_blue_r, maat_blue_g, maat_blue_b = 97/255, 97/255, 248/255
        glColor3f(maat_blue_r, maat_blue_g, maat_blue_b)
        glBegin(GL_POLYGON)
        for vertex in reversed(ring_inner_vertices): # ring_inner_vertices are for the Ma'at Blue floor
            glVertex3fv(vertex)
        glEnd()

        # 2. Draw the silver polygon ring as a series of quads
        silver_r, silver_g, silver_b = 192/255, 192/255, 192/255
        glColor3f(silver_r, silver_g, silver_b)
        glBegin(GL_QUADS)
        for i in range(self.num_sides):
            glVertex3fv(ring_inner_vertices[i])
            glVertex3fv(ring_inner_vertices[(i + 1) % self.num_sides])
            glVertex3fv(ring_outer_vertices[(i + 1) % self.num_sides])
            glVertex3fv(ring_outer_vertices[i])
        glEnd()
        
        # 3. Draw black outline for the Ma'at Blue central floor
        glColor3f(0.0, 0.0, 0.0) # Black
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for vertex in ring_inner_vertices: # Outline for Ma'at Blue floor
            glVertex3fv(vertex)
        glEnd()
        
        # 4. Draw black outline for the outer edge of the silver ring
        glBegin(GL_LINE_LOOP)
        for vertex in ring_outer_vertices:
            glVertex3fv(vertex)
        glEnd()

        # 4. Draw radial lines from the inner ring edge vertices to WALL OUTER base vertices
        glColor3f(0.0, 0.0, 0.0) # Black
        glLineWidth(1.0)
        
        wall_actual_outer_base_vertices = []
        for i in range(self.num_sides):
            angle = 2.0 * math.pi * i / self.num_sides - math.pi / 2.0
            x_outer = center[0] + wall_outer_radius_zbits * math.cos(angle)
            z_outer = center[2] + wall_outer_radius_zbits * math.sin(angle)
            wall_actual_outer_base_vertices.append((x_outer, 0.0, z_outer))

        glBegin(GL_LINES)
        for i in range(self.num_sides):
            inner_ring_v = ring_inner_vertices[i]
            outer_wall_v = wall_actual_outer_base_vertices[i]
            glVertex3fv(inner_ring_v)
            glVertex3fv(outer_wall_v)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glLineWidth(1.0) # Reset default line width

    def _draw_pillars(self):
        """Draw all pillars with their cubes."""
        # Iterate through the calculated and stored pillar positions
        for pillar_data in self._pillar_positions:
            if pillar_data is None:
                continue
                
            x, y, z = pillar_data['position']
            pillar_index = pillar_data['index']
            rotation = pillar_data['rotation']
            cube_actual_half_dim = pillar_data['cube_draw_half_width'] # Use stored dynamic size
            
            # Calculate wall and column indices
            wall_index = pillar_index // ADYTON_PILLARS_PER_SIDE
            column_index = pillar_index % ADYTON_PILLARS_PER_SIDE
            
            has_marker = False
            marker_type = None
            for name, pos in self._marker_positions.items():
                if pos == pillar_index:
                    has_marker = True
                    marker_type = name
                    break
            
            for cube_height in range(self.cubes_per_pillar):
                # Calculate cube_y using the actual_cube_half_dim for consistent cubic shape
                cube_y_center = y + (cube_height * cube_actual_half_dim * 2) + cube_actual_half_dim
                
                is_selected = (self.selected_pillar == pillar_index and 
                              self.selected_cube == cube_height)
                
                if is_selected:
                    glColor3f(1.0, 1.0, 0.0)
                elif has_marker:
                    if marker_type == 'S' and pillar_index == 28:
                        # Pillar 28 with Sun marker should now be default color
                        base_color = 0.4 + (cube_height / self.cubes_per_pillar) * 0.3
                        glColor3f(base_color, base_color, base_color)
                    elif marker_type == 'S':
                        brightness = 0.5 + (cube_height / self.cubes_per_pillar) * 0.5
                        glColor3f(brightness, brightness, 0.0)
                    elif marker_type == 'M':
                        brightness = 0.5 + (cube_height / self.cubes_per_pillar) * 0.3
                        glColor3f(brightness, brightness, brightness)
                    elif marker_type == 'N':
                        glColor3f(0.0, 0.6 + (cube_height / self.cubes_per_pillar) * 0.4, 
                                 0.6 + (cube_height / self.cubes_per_pillar) * 0.4)
                    elif marker_type == "N'":
                        glColor3f(0.6 + (cube_height / self.cubes_per_pillar) * 0.4, 
                                 0.0, 
                                 0.6 + (cube_height / self.cubes_per_pillar) * 0.4)
                    else:
                        glColor3f(0.7, 0.7, 0.7)
                else:
                    base_color = 0.4 + (cube_height / self.cubes_per_pillar) * 0.3
                    glColor3f(base_color, base_color, base_color)
                
                self._draw_cube(x, cube_y_center, z, size=cube_actual_half_dim, rotation=rotation, 
                              wireframe=self._show_wireframe, solid=self._show_solid,
                              pillar_index=pillar_index, column_index=column_index, wall_index=wall_index)
                
                if is_selected:
                    glColor3f(1.0, 0.0, 0.0)
                    glLineWidth(2.0)
                    self._draw_cube(x, cube_y_center, z, size=cube_actual_half_dim * 1.05, rotation=rotation,
                                  wireframe=True, solid=False)
                    glLineWidth(1.0)

    def _draw_cube(self, x, y, z, size, rotation=0.0, wireframe=True, solid=True, pillar_index=None, column_index=None, wall_index=None):
        """
        Draw a cube at the specified position with the given size and rotation,
        using a display list for the geometry (cube + pyramid).
        
        Args:
            x, y, z: Position coordinates (center of the base of the cube)
            size: Actual half-width of the cube to be drawn.
            rotation: Rotation angle in degrees of the HEPTAGON EDGE'S OUTWARD NORMAL.
            wireframe: Whether to draw a wireframe for the main cube (pyramid wireframe is in DL).
            solid: Whether to draw solid faces (display list contains solid faces).
            pillar_index: Index of the pillar (0-55)
            column_index: Column index within the wall (0-7)
            wall_index: Wall index (0-6)
        """
        glPushMatrix()
        
        glTranslatef(x, y, z)
        effective_rotation_angle = 90.0 - rotation
        glRotatef(effective_rotation_angle, 0, 1, 0)
        
        # The display list defines a unit cube (total width 1.0, so half-width 0.5).
        # We need to scale it to the actual full width (2 * size).
        actual_full_width = size * 2.0
        glScalef(actual_full_width, actual_full_width, actual_full_width)
        
        if solid:
            # First draw main geometry from display list except right and left faces
            if self.cube_with_pyramid_dl_id is not None:
                glCallList(self.cube_with_pyramid_dl_id)
            
            # Common parameters for both faces
            s = 0.5  # unit_half_width
            base_s_pyr = s
            top_s_pyr = base_s_pyr * 0.5  # pyramid_top_scale
            depth_pyr = base_s_pyr * 0.3  # pyramid_depth_scale
            
            v_base_pyr = [
                [-base_s_pyr, -base_s_pyr, base_s_pyr], 
                [base_s_pyr, -base_s_pyr, base_s_pyr],
                [base_s_pyr, base_s_pyr, base_s_pyr],
                [-base_s_pyr, base_s_pyr, base_s_pyr],
            ]
            v_top_pyr = [
                [-top_s_pyr, -top_s_pyr, base_s_pyr + depth_pyr],
                [top_s_pyr, -top_s_pyr, base_s_pyr + depth_pyr],
                [top_s_pyr,  top_s_pyr, base_s_pyr + depth_pyr],
                [-top_s_pyr,  top_s_pyr, base_s_pyr + depth_pyr],
            ]
            all_vertices_pyr = v_base_pyr + v_top_pyr
            
            # Get wall planet and pillar planet
            wall_planet = None
            pillar_planet = None
            if wall_index is not None and column_index is not None:
                wall_planet = WALL_PLANET_MAPPING[wall_index]
                pillar_planet = COLUMN_PLANET_MAPPING[wall_planet][column_index]
            
            # Save the current GL state
            previous_depth_test = glIsEnabled(GL_DEPTH_TEST)
            previous_lighting = glIsEnabled(GL_LIGHTING)
            previous_texture_2d = glIsEnabled(GL_TEXTURE_2D)
            previous_blend = glIsEnabled(GL_BLEND)
            
            # --- RIGHT DIAGONAL FACE (PLANETARY) ---
            # Disable lighting for accurate color rendering
            glDisable(GL_LIGHTING)
            
            # Set the planetary color for the right diagonal face
            if pillar_planet:
                planet_color = PLANETARY_COLORS.get(pillar_planet, (0.7, 0.7, 0.7))
                glColor3f(planet_color[0], planet_color[1], planet_color[2])
            else:
                glColor3f(0.7, 0.7, 0.7)  # Default gray if planet not found
            
            # Right diagonal face (face 2)
            right_face = [1, 2, 6, 5]  # Indices for right diagonal face
            
            # Draw the face with flat coloring (no lighting)
            glBegin(GL_QUADS)
            for vertex_index in right_face:
                glVertex3fv(all_vertices_pyr[vertex_index])
            glEnd()
            
            # Now render a smaller quad with the Trigrammaton letter texture for the right face
            if pillar_planet in self.trigrammaton_textures:
                text_color = (1.0 - planet_color[0], 1.0 - planet_color[1], 1.0 - planet_color[2])
                
                glDisable(GL_DEPTH_TEST)
                glEnable(GL_TEXTURE_2D)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
                glColor3f(text_color[0], text_color[1], text_color[2])
                glBindTexture(GL_TEXTURE_2D, self.trigrammaton_textures[pillar_planet])
                
                # Calculate center and vectors as before...
                face_center_x = 0
                face_center_y = 0
                face_center_z = 0
                for idx in right_face:
                    face_center_x += all_vertices_pyr[idx][0]
                    face_center_y += all_vertices_pyr[idx][1]
                    face_center_z += all_vertices_pyr[idx][2]
                face_center_x /= 4
                face_center_y /= 4
                face_center_z /= 4
                
                face_normal_x = 1
                face_normal_y = 0
                face_normal_z = 0
                text_offset = 0.02
                
                # Calculate the slope and vectors as before...
                bottom_midpoint_x = (all_vertices_pyr[1][0] + all_vertices_pyr[5][0]) / 2
                bottom_midpoint_y = (all_vertices_pyr[1][1] + all_vertices_pyr[5][1]) / 2
                bottom_midpoint_z = (all_vertices_pyr[1][2] + all_vertices_pyr[5][2]) / 2
                
                top_midpoint_x = (all_vertices_pyr[2][0] + all_vertices_pyr[6][0]) / 2
                top_midpoint_y = (all_vertices_pyr[2][1] + all_vertices_pyr[6][1]) / 2
                top_midpoint_z = (all_vertices_pyr[2][2] + all_vertices_pyr[6][2]) / 2
                
                slope_x = top_midpoint_x - bottom_midpoint_x
                slope_y = top_midpoint_y - bottom_midpoint_y
                slope_z = top_midpoint_z - bottom_midpoint_z
                
                horiz_x = all_vertices_pyr[1][0] - all_vertices_pyr[5][0]
                horiz_y = all_vertices_pyr[1][1] - all_vertices_pyr[5][1] 
                horiz_z = all_vertices_pyr[1][2] - all_vertices_pyr[5][2]
                
                quad_size = 0.6
                h_scale = 0.5 * quad_size
                v_scale = 0.5 * quad_size
                
                # Define the quad corners for the right face
                # Bottom left
                bl_x = face_center_x - horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                bl_y = face_center_y - horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                bl_z = face_center_z - horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                
                # Bottom right
                br_x = face_center_x + horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                br_y = face_center_y + horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                br_z = face_center_z + horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                
                # Top right
                tr_x = face_center_x + horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                tr_y = face_center_y + horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                tr_z = face_center_z + horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                
                # Top left
                tl_x = face_center_x - horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                tl_y = face_center_y - horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                tl_z = face_center_z - horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                
                # Draw the textured quad for the right face
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex3f(bl_x, bl_y, bl_z)
                glTexCoord2f(0, 0); glVertex3f(br_x, br_y, br_z)
                glTexCoord2f(1, 0); glVertex3f(tr_x, tr_y, tr_z)
                glTexCoord2f(1, 1); glVertex3f(tl_x, tl_y, tl_z)
                glEnd()
                
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)
            
            # --- LEFT DIAGONAL FACE (ZODIACAL) ---
            # Determine zodiac sign based on cube height (row)
            cube_height = self._get_cube_height_from_y_position(y)
            # Middle row (cube 7 out of 13) belongs to the wall's planet, others to zodiac signs
            
            # Left diagonal face (face 4)
            left_face = [3, 0, 4, 7]  # Indices for left diagonal face
            
            # Set the zodiac color for the left diagonal face
            # For the middle row (cube 7), use wall_planet's color
            if cube_height == 6 and wall_planet:  # Zero-indexed, so cube 7 is index 6
                planet_color = PLANETARY_COLORS.get(wall_planet, (0.7, 0.7, 0.7))
                glColor3f(planet_color[0], planet_color[1], planet_color[2])
                zodiac_sign = wall_planet
                use_wall_planet = True
            else:
                # Map the 12 zodiac signs to the 12 other cubes (excluding the middle one)
                # Adjusted cube_height to account for the middle row being the wall planet
                # We have cubes 0-5 and 7-12 for zodiac signs (12 total)
                zodiac_idx = cube_height if cube_height < 6 else cube_height - 1
                # Get list of zodiac signs in order
                zodiac_signs = list(ZODIAC_COLORS.keys())
                zodiac_sign = zodiac_signs[zodiac_idx % 12]
                zodiac_color = ZODIAC_COLORS.get(zodiac_sign, (0.7, 0.7, 0.7))
                glColor3f(zodiac_color[0], zodiac_color[1], zodiac_color[2])
                use_wall_planet = False
            
            # Draw the left face with flat coloring
            glBegin(GL_QUADS)
            for vertex_index in left_face:
                glVertex3fv(all_vertices_pyr[vertex_index])
            glEnd()
            
            # Now render the Trigrammaton letter for the left face
            # Create a dictionary to look up the texture ID
            texture_id = None
            if use_wall_planet and wall_planet in self.trigrammaton_textures:
                texture_id = self.trigrammaton_textures[wall_planet]
                text_color = (1.0 - planet_color[0], 1.0 - planet_color[1], 1.0 - planet_color[2])
            elif zodiac_sign in ZODIAC_TRIGRAMMATON_LETTERS:
                # We need to create textures for zodiac letters if they don't exist
                letter = ZODIAC_TRIGRAMMATON_LETTERS[zodiac_sign]
                # Since we're using trigrammaton_textures which is based on planet names,
                # we'll use a special key format for zodiac letters
                zodiac_texture_key = f"zodiac_{zodiac_sign}"
                
                # Check if we already created this texture
                if not hasattr(self, 'zodiac_textures'):
                    self.zodiac_textures = {}
                
                if zodiac_texture_key not in self.zodiac_textures:
                    # Create the texture for this zodiac sign's letter
                    self._create_zodiac_letter_texture(zodiac_sign, letter)
                
                if zodiac_texture_key in self.zodiac_textures:
                    texture_id = self.zodiac_textures[zodiac_texture_key]
                    zodiac_color = ZODIAC_COLORS.get(zodiac_sign, (0.7, 0.7, 0.7))
                    text_color = (1.0 - zodiac_color[0], 1.0 - zodiac_color[1], 1.0 - zodiac_color[2])
            
            if texture_id:
                glDisable(GL_DEPTH_TEST)
                glEnable(GL_TEXTURE_2D)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
                glColor3f(text_color[0], text_color[1], text_color[2])
                glBindTexture(GL_TEXTURE_2D, texture_id)
                
                # Calculate center and vectors for the left face
                face_center_x = 0
                face_center_y = 0
                face_center_z = 0
                for idx in left_face:
                    face_center_x += all_vertices_pyr[idx][0]
                    face_center_y += all_vertices_pyr[idx][1]
                    face_center_z += all_vertices_pyr[idx][2]
                face_center_x /= 4
                face_center_y /= 4
                face_center_z /= 4
                
                # For left face, normal is in -X direction
                face_normal_x = -1
                face_normal_y = 0
                face_normal_z = 0
                text_offset = 0.02
                
                # Calculate slopes and vectors for the left face
                bottom_midpoint_x = (all_vertices_pyr[3][0] + all_vertices_pyr[7][0]) / 2
                bottom_midpoint_y = (all_vertices_pyr[3][1] + all_vertices_pyr[7][1]) / 2
                bottom_midpoint_z = (all_vertices_pyr[3][2] + all_vertices_pyr[7][2]) / 2
                
                top_midpoint_x = (all_vertices_pyr[0][0] + all_vertices_pyr[4][0]) / 2
                top_midpoint_y = (all_vertices_pyr[0][1] + all_vertices_pyr[4][1]) / 2
                top_midpoint_z = (all_vertices_pyr[0][2] + all_vertices_pyr[4][2]) / 2
                
                slope_x = top_midpoint_x - bottom_midpoint_x
                slope_y = top_midpoint_y - bottom_midpoint_y
                slope_z = top_midpoint_z - bottom_midpoint_z
                
                horiz_x = all_vertices_pyr[3][0] - all_vertices_pyr[7][0]
                horiz_y = all_vertices_pyr[3][1] - all_vertices_pyr[7][1]
                horiz_z = all_vertices_pyr[3][2] - all_vertices_pyr[7][2]
                
                quad_size = 0.6
                h_scale = 0.5 * quad_size
                v_scale = 0.5 * quad_size
                
                # Define the quad corners for the left face
                # Bottom left
                bl_x = face_center_x - horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                bl_y = face_center_y - horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                bl_z = face_center_z - horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                
                # Bottom right
                br_x = face_center_x + horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                br_y = face_center_y + horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                br_z = face_center_z + horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                
                # Top right
                tr_x = face_center_x + horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                tr_y = face_center_y + horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                tr_z = face_center_z + horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                
                # Top left
                tl_x = face_center_x - horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                tl_y = face_center_y - horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                tl_z = face_center_z - horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                
                # Draw the textured quad for the left face - flip texture coordinates to fix upside-down appearance
                glBegin(GL_QUADS)
                glTexCoord2f(1, 0); glVertex3f(bl_x, bl_y, bl_z)
                glTexCoord2f(1, 1); glVertex3f(br_x, br_y, br_z)
                glTexCoord2f(0, 1); glVertex3f(tr_x, tr_y, tr_z)
                glTexCoord2f(0, 0); glVertex3f(tl_x, tl_y, tl_z)
                glEnd()
                
                glDisable(GL_TEXTURE_2D)
                glDisable(GL_BLEND)
                
            # --- UPPER FACE (truncated square) and LOWER FACE (bottom diagonal face) ---
            # Check if we have ternary data for this wall and column
            if hasattr(self, 'wall_ternary_data') and wall_index is not None and column_index is not None:
                wall_planet = WALL_PLANET_MAPPING[wall_index]
                
                # Adjust cube_height to match the CSV file's indexing
                # Convert the OpenGL cube height (0 = bottom) to CSV row index (0 = bottom)
                csv_row_index = cube_height  # They use the same convention, bottom is 0
                
                # Debug print for first cube only to avoid log spam
                if pillar_index == 0 and cube_height == 0:  
                    print(f"DEBUG: Processing ternary data for Wall: {wall_planet}, Column: {column_index}, Height: {cube_height}")
                    print(f"DEBUG: Using CSV row index: {csv_row_index}")
                    
                    if wall_planet in self.wall_ternary_data:
                        print(f"DEBUG: Found wall_planet {wall_planet} in wall_ternary_data")
                        if 'ternary' in self.wall_ternary_data[wall_planet]:
                            print(f"DEBUG: 'ternary' key exists in wall_ternary_data[{wall_planet}]")
                            if csv_row_index in self.wall_ternary_data[wall_planet]['ternary']:
                                print(f"DEBUG: csv_row_index {csv_row_index} exists in 'ternary' data")
                                if column_index in self.wall_ternary_data[wall_planet]['ternary'][csv_row_index]:
                                    ternary_value = self.wall_ternary_data[wall_planet]['ternary'][csv_row_index][column_index]
                                    print(f"DEBUG: Found ternary value: {ternary_value}")
                                else:
                                    print(f"DEBUG: column_index {column_index} NOT found in ternary data")
                            else:
                                print(f"DEBUG: csv_row_index {csv_row_index} NOT found in 'ternary' data")
                        else:
                            print(f"DEBUG: 'ternary' key NOT found in wall_ternary_data[{wall_planet}]")
                    else:
                        print(f"DEBUG: wall_planet {wall_planet} NOT found in wall_ternary_data")
                
                # Improved error checking for data access
                if wall_planet in self.wall_ternary_data and 'ternary' in self.wall_ternary_data[wall_planet]:
                    # Check for row indices in different formats
                    ternary_heights = self.wall_ternary_data[wall_planet]['ternary']
                    
                    # Try different variations of the index 
                    row_index_variations = [
                        csv_row_index,  # Try as-is (int)
                        str(csv_row_index),  # Try as string
                        f"{csv_row_index}",  # Try formatted as string
                    ]
                    
                    # Find the right row key to use
                    row_key = None
                    for idx in row_index_variations:
                        if idx in ternary_heights:
                            row_key = idx
                            break
                    
                    if row_key is not None and column_index in ternary_heights[row_key]:
                        # Get the 6-digit ternary value for this position
                        ternary_value = ternary_heights[row_key][column_index]
                        
                        # Add validation for ternary value format
                        if ternary_value and len(ternary_value) == 6 and all(c in '012' for c in ternary_value):
                            # Extract upper and lower trigrams
                            upper_trigram = self._get_trigram_from_ternary(ternary_value, 'upper')
                            lower_trigram = self._get_trigram_from_ternary(ternary_value, 'lower')
                            
                            # --- UPPER FACE (Face 0: Top face/truncated square) ---
                            upper_face = [7, 6, 5, 4]  # Indices for upper face
                            
                            # Set color for upper face based on trigram
                            if upper_trigram in self.ternary_attributes:
                                upper_color = self.ternary_attributes[upper_trigram]['rgb']
                                
                                # Save current GL state for upper face
                                previous_cull_face = glIsEnabled(GL_CULL_FACE)
                                if previous_cull_face:
                                    glDisable(GL_CULL_FACE)  # Temporarily disable face culling
                                
                                # Draw the upper face with flat coloring
                                glDisable(GL_LIGHTING)
                                glColor3f(upper_color[0], upper_color[1], upper_color[2])
                                
                                # Increase emission for better visibility of the face
                                glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [upper_color[0]*0.9, upper_color[1]*0.9, upper_color[2]*0.9, 1.0])
                                
                                # Temporarily disable depth test to ensure top face is always visible
                                glDisable(GL_DEPTH_TEST)
                                
                                glBegin(GL_QUADS)
                                # Use the stored normal for upper face (face 0) but ensure it points outward
                                glNormal3f(0, 0, 1)  # Always use this normal for the upper face for consistency
                                for vertex_index in upper_face:
                                    # Get the vertex and lift it slightly to prevent z-fighting
                                    vertex = all_vertices_pyr[vertex_index]
                                    glVertex3f(vertex[0], vertex[1], vertex[2] + 0.001)
                                glEnd()
                                
                                # Re-enable depth test for subsequent rendering
                                glEnable(GL_DEPTH_TEST)
                                glDepthFunc(GL_LESS)  # Reset depth function
                                
                                # Reset emission and restore face culling
                                glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
                                glDepthFunc(GL_LESS)  # Restore standard depth function
                                if previous_cull_face:
                                    glEnable(GL_CULL_FACE)
                                    
                                # Now render the Trigrammaton letter for the upper trigram
                                tex_id = self._create_trigram_letter_texture(upper_trigram)
                                if tex_id:
                                    # Set contrasting text color
                                    text_color = (1.0 - upper_color[0], 1.0 - upper_color[1], 1.0 - upper_color[2])
                                    
                                    glDisable(GL_DEPTH_TEST)
                                    glEnable(GL_TEXTURE_2D)
                                    glEnable(GL_BLEND)
                                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                                    
                                    glColor3f(text_color[0], text_color[1], text_color[2])
                                    glBindTexture(GL_TEXTURE_2D, tex_id)
                                    
                                    # Calculate the center of the upper face
                                    face_center_x = 0
                                    face_center_y = 0
                                    face_center_z = 0
                                    for idx in upper_face:
                                        face_center_x += all_vertices_pyr[idx][0]
                                        face_center_y += all_vertices_pyr[idx][1]
                                        face_center_z += all_vertices_pyr[idx][2]
                                    face_center_x /= 4
                                    face_center_y /= 4
                                    face_center_z /= 4
                                    
                                    # For the upper face, we need different vectors
                                    # The face is a truncated square on the Z+ direction
                                    face_normal_x = 0
                                    face_normal_y = 0
                                    face_normal_z = 1
                                    text_offset = 0.08  # Significantly increased offset for better visibility
                                    
                                    # Calculate X and Y axes for the upper face
                                    x_axis_x = all_vertices_pyr[5][0] - all_vertices_pyr[4][0]
                                    x_axis_y = all_vertices_pyr[5][1] - all_vertices_pyr[4][1]
                                    
                                    y_axis_x = all_vertices_pyr[7][0] - all_vertices_pyr[4][0]
                                    y_axis_y = all_vertices_pyr[7][1] - all_vertices_pyr[4][1]
                                    
                                    # No need for slope calculation for the flat upper face
                                    quad_size = 0.6
                                    x_scale = 0.4 * quad_size
                                    y_scale = 0.4 * quad_size
                                    
                                    # Define the quad corners for the upper face
                                    # Bottom left
                                    bl_x = face_center_x - x_axis_x * x_scale - y_axis_x * y_scale 
                                    bl_y = face_center_y - x_axis_y * x_scale - y_axis_y * y_scale 
                                    bl_z = face_center_z + face_normal_z * text_offset  # Offset in Z direction
                                    
                                    # Bottom right
                                br_x = face_center_x + x_axis_x * x_scale - y_axis_x * y_scale
                                br_y = face_center_y + x_axis_y * x_scale - y_axis_y * y_scale
                                br_z = face_center_z + face_normal_z * text_offset  # Offset in Z direction
                                
                                # Top right
                                tr_x = face_center_x + x_axis_x * x_scale + y_axis_x * y_scale
                                tr_y = face_center_y + x_axis_y * x_scale + y_axis_y * y_scale
                                tr_z = face_center_z + face_normal_z * text_offset  # Offset in Z direction
                                
                                # Top left
                                tl_x = face_center_x - x_axis_x * x_scale + y_axis_x * y_scale
                                tl_y = face_center_y - x_axis_y * x_scale + y_axis_y * y_scale
                                tl_z = face_center_z + face_normal_z * text_offset  # Offset in Z direction
                                
                                # Draw the textured quad for the upper face with clear texture coordinates
                                glBegin(GL_QUADS)
                                glNormal3f(0, 0, 1)  # Ensure normal points outward
                                glTexCoord2f(0, 1); glVertex3f(bl_x, bl_y, bl_z)
                                glTexCoord2f(1, 1); glVertex3f(br_x, br_y, br_z)
                                glTexCoord2f(1, 0); glVertex3f(tr_x, tr_y, tr_z)
                                glTexCoord2f(0, 0); glVertex3f(tl_x, tl_y, tl_z)
                                glEnd()
                                
                                # Clean up GL state
                                glDisable(GL_TEXTURE_2D)
                                glDisable(GL_BLEND)
                                glEnable(GL_DEPTH_TEST)
                            
                            # --- LOWER FACE (Face 1: Bottom diagonal face) ---
                            lower_face = [0, 1, 5, 4]  # Indices for lower face
                            
                            # Set color for lower face based on trigram
                            if lower_trigram in self.ternary_attributes:
                                lower_color = self.ternary_attributes[lower_trigram]['rgb']
                                
                                # Draw the lower face with flat coloring
                                glDisable(GL_LIGHTING)
                                glColor3f(lower_color[0], lower_color[1], lower_color[2])
                                
                                # Force emissive material for better color visibility
                                glMaterialfv(GL_FRONT, GL_EMISSION, [lower_color[0]*0.7, lower_color[1]*0.7, lower_color[2]*0.7, 1.0])
                                
                                # Let's use the same normal calculation as in _define_unit_cube_with_pyramid_geometry
                                # This ensures consistency with the wireframe
                                glBegin(GL_QUADS)
                                # Use the stored normal for lower face (face 1)
                                if hasattr(self, 'pyramid_normals') and len(self.pyramid_normals) > 1:
                                    glNormal3fv(self.pyramid_normals[1])
                                else:
                                    glNormal3f(0, -0.95, 0.30)  # Fallback if not stored
                                for vertex_index in lower_face:
                                    glVertex3fv(all_vertices_pyr[vertex_index])
                                glEnd()
                                
                                # Reset emission
                                glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
                                
                                # Continue with the texture for the lower face as in the original code
                                # Now render the Trigrammaton letter for the lower trigram
                                tex_id = self._create_trigram_letter_texture(lower_trigram)
                                if tex_id:
                                    # Set contrasting text color
                                    text_color = (1.0 - lower_color[0], 1.0 - lower_color[1], 1.0 - lower_color[2])
                                    
                                    glDisable(GL_DEPTH_TEST)
                                    glEnable(GL_TEXTURE_2D)
                                    glEnable(GL_BLEND)
                                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                                    
                                    glColor3f(text_color[0], text_color[1], text_color[2])
                                    glBindTexture(GL_TEXTURE_2D, tex_id)
                                    
                                    # The rest of the existing lower face texture code...
                                    # Calculate the center of the lower face
                                    face_center_x = 0
                                    face_center_y = 0
                                    face_center_z = 0
                                    for idx in lower_face:
                                        face_center_x += all_vertices_pyr[idx][0]
                                        face_center_y += all_vertices_pyr[idx][1]
                                        face_center_z += all_vertices_pyr[idx][2]
                                    face_center_x /= 4
                                    face_center_y /= 4
                                    face_center_z /= 4
                                    
                                    # For the lower face, the normal points down and slightly out
                                    face_normal_x = 0
                                    face_normal_y = -0.95
                                    face_normal_z = 0.30
                                    text_offset = 0.02
                                    
                                    # Calculate the slope and vectors for the lower face
                                    bottom_midpoint_x = (all_vertices_pyr[0][0] + all_vertices_pyr[1][0]) / 2
                                    bottom_midpoint_y = (all_vertices_pyr[0][1] + all_vertices_pyr[1][1]) / 2
                                    bottom_midpoint_z = (all_vertices_pyr[0][2] + all_vertices_pyr[1][2]) / 2
                                    
                                    top_midpoint_x = (all_vertices_pyr[4][0] + all_vertices_pyr[5][0]) / 2
                                    top_midpoint_y = (all_vertices_pyr[4][1] + all_vertices_pyr[5][1]) / 2
                                    top_midpoint_z = (all_vertices_pyr[4][2] + all_vertices_pyr[5][2]) / 2
                                    
                                    slope_x = top_midpoint_x - bottom_midpoint_x
                                    slope_y = top_midpoint_y - bottom_midpoint_y
                                    slope_z = top_midpoint_z - bottom_midpoint_z
                                    
                                    horiz_x = all_vertices_pyr[1][0] - all_vertices_pyr[0][0]
                                    horiz_y = all_vertices_pyr[1][1] - all_vertices_pyr[0][1]
                                    horiz_z = all_vertices_pyr[1][2] - all_vertices_pyr[0][2]
                                    
                                    quad_size = 0.6
                                    h_scale = 0.5 * quad_size
                                    v_scale = 0.5 * quad_size
                                    
                                    # Define the quad corners for the lower face
                                    # Bottom left
                                    bl_x = face_center_x - horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                                    bl_y = face_center_y - horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                                    bl_z = face_center_z - horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                                    
                                    # Bottom right
                                    br_x = face_center_x + horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                                    br_y = face_center_y + horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                                    br_z = face_center_z + horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                                    
                                    # Top right
                                    tr_x = face_center_x + horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                                    tr_y = face_center_y + horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                                    tr_z = face_center_z + horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                                    
                                    # Top left
                                    tl_x = face_center_x - horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                                    tl_y = face_center_y - horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                                    tl_z = face_center_z - horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                                    
                                    # Draw the textured quad for the lower face with correct orientation
                                    glBegin(GL_QUADS)
                                    glTexCoord2f(0, 1); glVertex3f(bl_x, bl_y, bl_z)
                                    glTexCoord2f(1, 1); glVertex3f(br_x, br_y, br_z)
                                    glTexCoord2f(1, 0); glVertex3f(tr_x, tr_y, tr_z)
                                    glTexCoord2f(0, 0); glVertex3f(tl_x, tl_y, tl_z)
                                    glEnd()
                                    
                                    glDisable(GL_TEXTURE_2D)
                                    glDisable(GL_BLEND)
                                    
                                    # --- TOP DIAGONAL FACE (Face 3) with top trigram ---
                                    # Extract another trigram for this face - we'll use the same ternary data
                                    # but combine the last digit of upper trigram with first two of lower trigram
                                    if ternary_value and len(ternary_value) == 6:
                                        # Create a new trigram from last digit of upper + first two of lower
                                        top_trigram = ternary_value[2] + ternary_value[3] + ternary_value[4]
                                        
                                        if top_trigram in self.ternary_attributes:
                                            top_color = self.ternary_attributes[top_trigram]['rgb']
                                            
                                            # Define the top diagonal face (face 3)
                                            top_diag_face = [2, 3, 7, 6]  # Indices for top diagonal face
                                            
                                            # Draw the top diagonal face with flat coloring
                                            glDisable(GL_LIGHTING)
                                            glColor3f(top_color[0], top_color[1], top_color[2])
                                            
                                            # Force emissive material for better color visibility
                                            glMaterialfv(GL_FRONT, GL_EMISSION, [top_color[0]*0.7, top_color[1]*0.7, top_color[2]*0.7, 1.0])
                                            
                                            glBegin(GL_QUADS)
                                            # Use the stored normal for top diagonal face (face 3)
                                            if hasattr(self, 'pyramid_normals') and len(self.pyramid_normals) > 3:
                                                glNormal3fv(self.pyramid_normals[3])
                                            else:
                                                glNormal3f(0, 0.707, 0.707)  # Fallback if not stored
                                            for vertex_index in top_diag_face:
                                                glVertex3fv(all_vertices_pyr[vertex_index])
                                            glEnd()
                                            
                                            # Reset emission
                                            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
                                            
                                            # Render the Trigrammaton letter for the top trigram
                                            tex_id = self._create_trigram_letter_texture(top_trigram)
                                            if tex_id:
                                                # Set contrasting text color
                                                text_color = (1.0 - top_color[0], 1.0 - top_color[1], 1.0 - top_color[2])
                                                
                                                glDisable(GL_DEPTH_TEST)
                                                glEnable(GL_TEXTURE_2D)
                                                glEnable(GL_BLEND)
                                                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                                                
                                                glColor3f(text_color[0], text_color[1], text_color[2])
                                                glBindTexture(GL_TEXTURE_2D, tex_id)
                                                
                                                # Calculate the center of the top diagonal face
                                                face_center_x = 0
                                                face_center_y = 0
                                                face_center_z = 0
                                                for idx in top_diag_face:
                                                    face_center_x += all_vertices_pyr[idx][0]
                                                    face_center_y += all_vertices_pyr[idx][1]
                                                    face_center_z += all_vertices_pyr[idx][2]
                                                face_center_x /= 4
                                                face_center_y /= 4
                                                face_center_z /= 4
                                                
                                                # For the top diagonal face
                                                face_normal_x = 0
                                                face_normal_y = 0.707
                                                face_normal_z = 0.707
                                                text_offset = 0.02
                                                
                                                # Calculate vectors for the top diagonal face
                                                bottom_midpoint_x = (all_vertices_pyr[2][0] + all_vertices_pyr[3][0]) / 2
                                                bottom_midpoint_y = (all_vertices_pyr[2][1] + all_vertices_pyr[3][1]) / 2
                                                bottom_midpoint_z = (all_vertices_pyr[2][2] + all_vertices_pyr[3][2]) / 2
                                                
                                                top_midpoint_x = (all_vertices_pyr[6][0] + all_vertices_pyr[7][0]) / 2
                                                top_midpoint_y = (all_vertices_pyr[6][1] + all_vertices_pyr[7][1]) / 2
                                                top_midpoint_z = (all_vertices_pyr[6][2] + all_vertices_pyr[7][2]) / 2
                                                
                                                slope_x = top_midpoint_x - bottom_midpoint_x
                                                slope_y = top_midpoint_y - bottom_midpoint_y
                                                slope_z = top_midpoint_z - bottom_midpoint_z
                                                
                                                horiz_x = all_vertices_pyr[3][0] - all_vertices_pyr[2][0]
                                                horiz_y = all_vertices_pyr[3][1] - all_vertices_pyr[2][1]
                                                horiz_z = all_vertices_pyr[3][2] - all_vertices_pyr[2][2]
                                                
                                                quad_size = 0.6
                                                h_scale = 0.5 * quad_size
                                                v_scale = 0.5 * quad_size
                                                
                                                # Define the quad corners for the top diagonal face
                                                # Bottom left
                                                bl_x = face_center_x - horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                                                bl_y = face_center_y - horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                                                bl_z = face_center_z - horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                                                
                                                # Bottom right
                                                br_x = face_center_x + horiz_x * h_scale - slope_x * v_scale + face_normal_x * text_offset
                                                br_y = face_center_y + horiz_y * h_scale - slope_y * v_scale + face_normal_y * text_offset
                                                br_z = face_center_z + horiz_z * h_scale - slope_z * v_scale + face_normal_z * text_offset
                                                
                                                # Top right
                                                tr_x = face_center_x + horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                                                tr_y = face_center_y + horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                                                tr_z = face_center_z + horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                                                
                                                # Top left
                                                tl_x = face_center_x - horiz_x * h_scale + slope_x * v_scale + face_normal_x * text_offset
                                                tl_y = face_center_y - horiz_y * h_scale + slope_y * v_scale + face_normal_y * text_offset
                                                tl_z = face_center_z - horiz_z * h_scale + slope_z * v_scale + face_normal_z * text_offset
                                                
                                                # Draw the textured quad for the top face with correct orientation
                                                glBegin(GL_QUADS)
                                                glTexCoord2f(0, 1); glVertex3f(bl_x, bl_y, bl_z)
                                                glTexCoord2f(1, 1); glVertex3f(br_x, br_y, br_z)
                                                glTexCoord2f(1, 0); glVertex3f(tr_x, tr_y, tr_z)
                                                glTexCoord2f(0, 0); glVertex3f(tl_x, tl_y, tl_z)
                                                glEnd()
                                                
                                                glDisable(GL_TEXTURE_2D)
                                                glDisable(GL_BLEND)
            
            # Restore GL state
            if previous_lighting:
                glEnable(GL_LIGHTING)
            if previous_depth_test:
                glEnable(GL_DEPTH_TEST)
            else:
                glDisable(GL_DEPTH_TEST)
            if previous_texture_2d:
                glEnable(GL_TEXTURE_2D)
            else:
                glDisable(GL_TEXTURE_2D)
            if previous_blend:
                glEnable(GL_BLEND)
            else:
                glDisable(GL_BLEND)
        
        # Draw wireframe if enabled
        if wireframe and not solid:
            if self.cube_with_pyramid_dl_id is not None:
                glDisable(GL_LIGHTING)
                glColor3f(0.0, 0.0, 0.0)
                glCallList(self.cube_with_pyramid_dl_id)
                glEnable(GL_LIGHTING)
        elif wireframe and solid:
            s_unit = 0.5 
            unit_vertices = [
                [-s_unit, -s_unit, -s_unit], [s_unit, -s_unit, -s_unit],
                [s_unit, s_unit, -s_unit], [-s_unit, s_unit, -s_unit],
                [-s_unit, -s_unit, s_unit], [s_unit, -s_unit, s_unit],
                [s_unit, s_unit, s_unit], [-s_unit, s_unit, s_unit]
            ]
            unit_edges = [
                [0,1],[1,2],[2,3],[3,0], [4,5],[5,6],[6,7],[7,4], [0,4],[1,5],[2,6],[3,7]
            ]
            glDisable(GL_LIGHTING)
            glColor3f(0.0,0.0,0.0)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            for edge in unit_edges:
                glVertex3fv(unit_vertices[edge[0]])
                glVertex3fv(unit_vertices[edge[1]])
            glEnd()
            glEnable(GL_LIGHTING)

        glPopMatrix()

    def _draw_pillar_number_labels(self):
        """Draws numerical labels on top of each pillar."""
        if not self._show_labels: # Controlled by the existing toggle
            return

        glDisable(GL_LIGHTING) # Text is usually drawn unlit
        glColor3f(1.0, 1.0, 1.0)  # White color for labels

        for pillar_data in self._pillar_positions:
            if pillar_data is None:
                continue

            pillar_idx_str = str(pillar_data['index'] + 1) # Display as 1-56
            base_x, y_base_center, base_z = pillar_data['position']
            cube_half_dim = pillar_data['cube_draw_half_width']
            
            # Calculate Y position for the label (top of the pillar + small offset)
            # The y_base_center is the center of the very bottom cube of the pillar if cubes_per_pillar is odd,
            # or the plane between the two middle cubes if even. More accurately, it's the Y of the pillar base.
            # The actual drawing of cubes starts from y_base_center + cube_half_dim for the first cube's center.
            pillar_top_y = y_base_center + (self.cubes_per_pillar * cube_half_dim * 2.0) + (cube_half_dim * 0.5) # Offset above pillar

            # Need to adjust text position slightly for multi-digit numbers to center them better
            # This is a rough adjustment; true text metrics are hard with bitmap fonts.
            text_width_approx = len(pillar_idx_str) * cube_half_dim * 0.3 # Very rough estimate
            label_x = base_x - text_width_approx / 2.0
            label_z = base_z

            glRasterPos3f(label_x, pillar_top_y, label_z)
            for char_code in pillar_idx_str:
                if bool(glutBitmapCharacter): # Check if function is available
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char_code))
                else:
                    # Fallback or warning if GLUT text is not available
                    if not hasattr(self, '_glut_text_warning_shown'):
                        print("WARNING: glutBitmapCharacter not available, labels will not be drawn.")
                        self._glut_text_warning_shown = True # Show warning only once
                    break # Stop trying to draw this label
        
        glEnable(GL_LIGHTING)

    def _draw_markers(self):
        """Draw special markers for Sun, Moon, and Nodes."""
        # The primary visual indication of markers is now handled by pillar coloring in _draw_pillars.
        # The _show_labels toggle will now control the new _draw_pillar_number_labels method.
        # So, the old point-based label drawing here can be removed or commented out.
        
        # Old label logic (drawing a point) - to be removed/disabled:
        # for name, pillar_index in self._marker_positions.items():
        #     if 0 <= pillar_index < len(self._pillar_positions):
        #         pillar = self._pillar_positions[pillar_index]
        #         x, y, z = pillar['position']
                
        #         if self._show_labels: # This toggle is now for number labels
        #             glDisable(GL_LIGHTING)
        #             label_y = y + (self.cubes_per_pillar * pillar['cube_draw_half_width'] * 2) + 1.0
        #             if name == 'S': glColor3f(1.0, 1.0, 0.0)
        #             elif name == 'M': glColor3f(1.0, 1.0, 1.0)
        #             elif name == 'N': glColor3f(0.0, 1.0, 1.0)
        #             elif name == "N'": glColor3f(1.0, 0.0, 1.0)
        #             glPointSize(10.0)
        #             glBegin(GL_POINTS)
        #             glVertex3f(x, label_y, z)
        #             glEnd()
        #             glEnable(GL_LIGHTING)
        pass # _draw_markers might do other things in future, but not labels now.

    def _draw_galactic_center(self):
        """Draw a reference line for the Galactic Center."""
        # Draw a vertical golden line from the center upward
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.84, 0.0)  # Gold color
        glLineWidth(2.0)
        
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, 0.0)  # From center
        glVertex3f(0.0, 15.0, 0.0)  # Straight up
        glEnd()
        
        glEnable(GL_LIGHTING)
        glLineWidth(1.0)

    def _draw_center_truncated_tetrahedron(self):
        """Draws a truncated tetrahedron at the center of the Adyton."""
        L_base = 2.618  # Z'Bits
        L_top = 1.618   # Z'Bits
        H_trunc = 1.0   # Z'Bits (height of the truncated solid)

        # --- Calculate GC Alignment Angle for the Yellow Face ---
        # The yellow face should be centered along the radius pointing to the
        # line between pillars with index 27 and 28.
        if not self._pillar_positions or \
           len(self._pillar_positions) <= 28 or \
           self._pillar_positions[27] is None or \
           self._pillar_positions[28] is None:
            print("WARNING: Pillar positions (27/28) not available for GC alignment of tetrahedron. Skipping draw.")
            return

        P27_pos = self._pillar_positions[27]['position'] # (x,y,z)
        P28_pos = self._pillar_positions[28]['position'] # (x,y,z)

        # Midpoint vector (direction) from origin to the point between P27 and P28
        mid_x = (P27_pos[0] + P28_pos[0]) / 2.0
        mid_z = (P27_pos[2] + P28_pos[2]) / 2.0
        # Angle of this midpoint vector in the XZ plane
        target_alignment_angle_rad = math.atan2(mid_z, mid_x)
        target_alignment_angle_deg = math.degrees(target_alignment_angle_rad)

        # --- Calculate Vertices for an unrotated tetrahedron centered at origin ---
        # Base triangle (equilateral) in Y=0 plane, side L_base
        # Height of an equilateral triangle: (sqrt(3)/2) * side
        h_base_tri = (math.sqrt(3.0) / 2.0) * L_base
        # Vertices: (one point on y-axis, others symmetric)
        # To align one edge with X-axis for easier rotation later:
        # vB0 = ( L_base / 2.0, 0, -h_base_tri / 3.0)
        # vB1 = (-L_base / 2.0, 0, -h_base_tri / 3.0)
        # vB2 = (0,             0,  2 * h_base_tri / 3.0)
        # Let's place it so that the midpoint of vB0-vB1 is at origin, then orient it.
        # Base vertices (centered, one edge along X axis for now before rotation)
        vB0_x =  L_base / 2.0
        vB0_z = -h_base_tri * (1/3) # Centroid to edge midpoint
        vB1_x = -L_base / 2.0
        vB1_z = -h_base_tri * (1/3)
        vB2_x =  0.0
        vB2_z =  h_base_tri * (2/3)

        base_vertices = [
            (vB0_x, 0, vB0_z), 
            (vB1_x, 0, vB1_z), 
            (vB2_x, 0, vB2_z)
        ]

        # Top triangle (equilateral) in Y=H_trunc plane, side L_top
        # Scaled version of base vertices, translated up
        scale_factor = L_top / L_base
        top_vertices = [
            (v[0] * scale_factor, H_trunc, v[2] * scale_factor) for v in base_vertices
        ]

        # --- Drawing --- 
        glPushMatrix()
        glDisable(GL_LIGHTING) # Simple colors, no complex lighting for now

        # Rotate to align the base of the YELLOW face (vB0-vB1 edge) with GC direction
        # The edge vB0-vB1 is currently along the X-axis.
        # We want its normal (which would be -Z in its local unrotated frame) to align with target_alignment_angle_deg.
        glRotatef(target_alignment_angle_deg + 90.0, 0, 1, 0) # Rotate around Y axis

        # Top Face (Black)
        glColor3f(0.0, 0.0, 0.0) # Black
        glBegin(GL_POLYGON)
        for v in top_vertices:
            glVertex3fv(v)
        glEnd()

        # Side Faces (Trapezoids - Quads)
        # Face 1 (Yellow - GC aligned - uses base_vertices[0] and base_vertices[1])
        glColor3f(1.0, 1.0, 0.0) # Yellow
        glBegin(GL_QUADS)
        glVertex3fv(base_vertices[0])
        glVertex3fv(base_vertices[1])
        glVertex3fv(top_vertices[1])
        glVertex3fv(top_vertices[0])
        glEnd()

        # Face 2 (Cyan - "right" - uses base_vertices[1] and base_vertices[2])
        glColor3f(0.0, 1.0, 1.0) # Cyan
        glBegin(GL_QUADS)
        glVertex3fv(base_vertices[1])
        glVertex3fv(base_vertices[2])
        glVertex3fv(top_vertices[2])
        glVertex3fv(top_vertices[1])
        glEnd()

        # Face 3 (Magenta - "left" - uses base_vertices[2] and base_vertices[0])
        glColor3f(1.0, 0.0, 1.0) # Magenta
        glBegin(GL_QUADS)
        glVertex3fv(base_vertices[2])
        glVertex3fv(base_vertices[0])
        glVertex3fv(top_vertices[0])
        glVertex3fv(top_vertices[2])
        glEnd()
        
        # Base triangle (optional - draw if needed, e.g. different color from floor)
        # For now, assume it sits on the floor and doesn't need separate drawing if floor is bg.

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def _draw_celestial_references(self):
        """Draws celestial reference lines like horizon, Adyton belt limits, etc."""
        if not hasattr(self, "_printed_belt_angle"): # Print only once
            print(f"INFO: Adyton Belt - Upper Obscuration Altitude: {self.adyton_belt_upper_alt_deg:.2f} degrees")
            self._printed_belt_angle = True

        glDisable(GL_LIGHTING)
        glColor3f(0.7, 0.7, 0.7) # Light grey for reference lines
        glLineWidth(1.0)

        num_segments = 72 # Number of segments to approximate the circle

        # 1. Draw Horizon Line (Altitude = 0 degrees)
        # This is a circle in the XZ plane at y=0, with radius sky_dome_radius
        glBegin(GL_LINE_LOOP)
        for i in range(num_segments):
            theta = 2.0 * math.pi * float(i) / float(num_segments)
            x = self.sky_dome_radius * math.cos(theta)
            z = self.sky_dome_radius * math.sin(theta)
            glVertex3f(x, 0.0, z) # y=0 for horizon
        glEnd()

        # 2. Draw Adyton Belt Upper Limit Line (Altitude = self.adyton_belt_upper_alt_deg)
        alt_rad = math.radians(self.adyton_belt_upper_alt_deg)
        y_belt_line = self.sky_dome_radius * math.sin(alt_rad)
        radius_belt_line_xz = self.sky_dome_radius * math.cos(alt_rad)

        glBegin(GL_LINE_LOOP)
        for i in range(num_segments):
            theta = 2.0 * math.pi * float(i) / float(num_segments)
            x = radius_belt_line_xz * math.cos(theta)
            z = radius_belt_line_xz * math.sin(theta)
            glVertex3f(x, y_belt_line, z)
        glEnd()

        glEnable(GL_LIGHTING)
        # Future: Draw Ecliptic, Celestial Equator, Stars etc.
        pass

    def set_marker_positions(self, positions):
        """
        Set marker positions from the 2D circle view.
        
        Args:
            positions (dict): Dictionary mapping marker names to pillar indices.
        """
        self._marker_positions = positions
        self.update()

    def get_marker_positions(self):
        """
        Get the current marker positions.
        
        Returns:
            dict: Dictionary mapping marker names to pillar indices.
        """
        return self._marker_positions

    def toggle_wireframe(self, show):
        """Toggle wireframe display."""
        self._show_wireframe = show
        self.update()

    def toggle_solid(self, show):
        """Toggle solid cube display."""
        self._show_solid = show
        self.update()

    def toggle_markers(self, show):
        """Toggle marker display."""
        self._show_markers = show
        self.update()

    def toggle_labels(self, show):
        """Toggle label display."""
        self._show_labels = show
        self.update()

    def toggle_floor(self, show):
        """Toggle floor display."""
        self._show_floor = show
        self.update()

    def reset_view(self):
        """Reset the camera view to default position."""
        self.rotation_x = 30.0
        self.rotation_y = 40.0
        self.zoom = 1.0
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse press events for rotation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = QPoint(int(event.position().x()), int(event.position().y()))

    def mouseMoveEvent(self, event):
        """Handle mouse move events for rotation."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            pos = QPoint(int(event.position().x()), int(event.position().y()))
            dx = pos.x() - self.last_pos.x()
            dy = pos.y() - self.last_pos.y()
            
            self.rotation_y += dx / 2.0
            self.rotation_x += dy / 2.0
            
            self.last_pos = pos
            self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom = max(0.1, self.zoom * 0.9)  # Zoom in
        else:
            self.zoom = min(15.0, self.zoom * 1.1)  # Zoom out - Increased limit from 5.0 to 15.0
        self.update()

    def select_pillar_at(self, x, y):
        """
        Select a pillar based on screen coordinates.
        This is a placeholder for ray picking implementation.
        
        Args:
            x (int): Screen x-coordinate
            y (int): Screen y-coordinate
        """
        # This would require ray picking which is complex in raw OpenGL
        # For now, we'll implement a simpler version in the future
        pass 

    def _draw_projected_celestial_bodies(self):
        """Draws the selected planets and stars projected on the inner veil."""
        if not self.celestial_body_positions:
            print("[ADYTON DEBUG DRAW] No celestial body positions to draw.")
            return

        # Iterate through the dictionary: name is the key, body_data_dict is the value (another dictionary)
        for name, body_data_dict in self.celestial_body_positions.items():
            if not body_data_dict: # Check if the dictionary for this body exists
                print(f"[ADYTON DEBUG DRAW] Skipping {name}, no data dictionary found.")
                continue

            # Get projected coordinates directly from the dictionary
            projected_x = body_data_dict.get('x')
            projected_y = body_data_dict.get('y')
            projected_z = body_data_dict.get('z')
            
            # Also retrieve ecliptic coordinates for debugging if needed, though not used for drawing here
            ecl_lon = body_data_dict.get('ecl_lon')
            ecl_lat = body_data_dict.get('ecl_lat')

            if projected_x is None or projected_y is None or projected_z is None:
                # This might happen if coordinates couldn't be calculated or body is not visible
                # print(f"[ADYTON DEBUG DRAW] Skipping {name}, missing one or more projected coordinates (X,Y,Z). EclLon: {ecl_lon}, EclLat: {ecl_lat}")
                continue
            
            # Optional: Add a more detailed debug print if issues persist
            # print(f"[ADYTON DEBUG DRAW] Attempting to draw {name} at X:{projected_x:.2f}, Y:{projected_y:.2f}, Z:{projected_z:.2f} (EclLon:{ecl_lon:.2f}, EclLat:{ecl_lat:.2f})")

            glPushMatrix()
            glTranslatef(projected_x, projected_y, projected_z) # Use the retrieved coordinates

            # Determine size and color based on the celestial body name
            point_size = 5.0 # Default point size, though we use spheres
            color = [0.8, 0.8, 0.8, 0.9] # Default: bright white for generic stars/planets

            if name == "Venus":
                point_size = 8.0
                color = [1.0, 0.9, 0.7, 1.0] # Creamy yellow for Venus
            elif name == "Sirius":
                point_size = 8.0
                color = [0.7, 0.8, 1.0, 1.0] # Bright blue-white for Sirius
            elif name == "Sun":
                point_size = 10.0
                color = [1.0, 1.0, 0.0, 1.0] # Yellow for Sun
            elif name == "Moon":
                point_size = 9.0
                color = [0.9, 0.9, 0.9, 0.9] # Silvery for Moon
            elif name == "Mars":
                color = [1.0, 0.4, 0.2, 1.0] # Reddish for Mars
            # Add more custom colors/sizes for other bodies if desired
            
            glColor4f(*color)
            
            # Draw as a small sphere
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH) # Add normals for lighting
            gluSphere(quad, 0.5, 16, 16) # Draw a sphere of radius 0.5 Z'Bits
            gluDeleteQuadric(quad)
            
            glPopMatrix()
        # glPointSize(1.0) # Reset point size if it was set - not needed as we use spheres

    def update_celestial_view(self, dt: datetime, latitude: float, longitude: float):
        # Update current time and location
        self.current_datetime = dt
        self.current_latitude = latitude
        self.current_longitude = longitude
        
        # Recalculate positions based on the new time/location
        self._recalculate_celestial_positions()
        
        # Trigger a repaint of the OpenGL scene
        self.update() # QOpenGLWidget method to schedule a repaint

    def _recalculate_celestial_positions(self):
        """
        Recalculates the projected 3D positions of celestial bodies on the inner veil
        using Ecliptic Coordinates. Also calculates their zodiac position,
        projected pillar index, and cube level.
        """
        if not self.ephemeris_service or not hasattr(self, 'adyton_aries_angle_deg'):
            print("ERROR: Ephemeris service not available or Adyton Aries angle not set for celestial calculation.")
            return

        all_bodies = self.traditional_planets + self.famous_stars
        new_celestial_positions = {}

        for body_name in all_bodies:
            ecl_coords = self.ephemeris_service.get_celestial_body_ecliptic_coords(
                body_name,
                self.current_datetime.year,
                self.current_datetime.month,
                self.current_datetime.day,
                self.current_datetime.hour,
                self.current_datetime.minute,
                self.current_datetime.second,
            )

            if ecl_coords:
                ecl_lon, ecl_lat_true = ecl_coords # Store true ecl_lat

                # Get Zodiac sign and degree
                zodiac_sign, degrees_in_sign = "N/A", 0.0
                if ecl_lon is not None: # Ensure ecl_lon is valid before getting zodiac
                    zodiac_sign, degrees_in_sign = self.ephemeris_service.longitude_to_zodiac(ecl_lon)

                # Determine ecliptic latitude for projection (stars on equator)
                ecl_lat_for_projection = 0.0 if body_name in self.famous_stars else ecl_lat_true
                
                # --- Longitude to X, Z on Veil ---
                visual_angle_deg = self.adyton_aries_angle_deg + ecl_lon
                theta_rad = math.radians(visual_angle_deg)
                
                projected_x = self.inner_veil_radius * math.cos(theta_rad)
                projected_z = self.inner_veil_radius * math.sin(theta_rad)

                # --- Latitude to Y on Veil (using ecl_lat_for_projection) ---
                veil_center_y = self.inner_veil_height / 2.0
                clamped_lat_proj = max(-MAX_DISPLAY_ECLIPTIC_LATITUDE, min(ecl_lat_for_projection, MAX_DISPLAY_ECLIPTIC_LATITUDE))
                
                scaled_latitude_proj = 0.0
                if MAX_DISPLAY_ECLIPTIC_LATITUDE != 0:
                    scaled_latitude_proj = clamped_lat_proj / MAX_DISPLAY_ECLIPTIC_LATITUDE
                
                projected_y = veil_center_y + scaled_latitude_proj * (self.inner_veil_height / 2.0)
                projected_y = max(0, min(projected_y, self.inner_veil_height))

                # --- Calculate Pillar Index (Column) ---
                # Normalize visual_angle_deg to 0-360
                normalized_angle_deg = visual_angle_deg % 360
                if normalized_angle_deg < 0: # Ensure positive angle
                    normalized_angle_deg += 360
                
                # Assuming pillars are numbered 0-55, distributed evenly around 360 degrees.
                # Pillar 0 might correspond to the direction of the Adyton's Aries angle.
                # The user previously wanted pillar 24 (index 23) at North, and WS between 27/28.
                # The adyton_aries_angle_deg establishes where 0 Aries is.
                # A direct mapping from normalized_angle_deg:
                pillar_idx = int(normalized_angle_deg / (360.0 / self.total_pillars)) % self.total_pillars


                # --- Calculate Cube Level (Row) ---
                # Map projected_y (0 to self.inner_veil_height) to cube_lvl (1 to self.cubes_per_pillar)
                # Ensure no division by zero if inner_veil_height is 0, though unlikely
                relative_y_pos = 0.0
                if self.inner_veil_height > 0:
                    relative_y_pos = projected_y / self.inner_veil_height # Range 0.0 to 1.0
                
                # Map to 0 to (cubes_per_pillar - 1), then add 1
                cube_lvl_float = relative_y_pos * (self.cubes_per_pillar -1)
                cube_lvl = 1 + int(round(cube_lvl_float)) # Round to nearest integer level
                cube_lvl = max(1, min(cube_lvl, self.cubes_per_pillar)) # Clamp to 1-13


                new_celestial_positions[body_name] = {
                    'ecl_lon': ecl_lon,
                    'ecl_lat': ecl_lat_true, # Store TRUE ecliptic latitude
                    'zodiac_sign': zodiac_sign,
                    'degrees_in_sign': degrees_in_sign,
                    'x': projected_x,
                    'y': projected_y,
                    'z': projected_z,
                    'pillar_idx': pillar_idx,
                    'cube_lvl': cube_lvl,
                    'name': body_name
                }
            else:
                if body_name in self.celestial_body_positions:
                    new_celestial_positions[body_name] = self.celestial_body_positions[body_name]

        self.celestial_body_positions = new_celestial_positions
        # self.update() # Schedule a repaint - update_celestial_view calls this.

    def get_celestial_projection_data(self):
        """Returns the current celestial body projection data."""
        return self.celestial_body_positions

    def set_gc_orientation_data(self, azimuth, altitude, zodiac_label):
        # ... existing code ...
        pass 

    def _create_trigrammaton_textures(self):
        """Create textures for each Trigrammaton letter using the system Trigrammaton font."""
        # Clear any existing textures
        if hasattr(self, 'trigrammaton_textures') and self.trigrammaton_textures:
            for tex_id in self.trigrammaton_textures.values():
                glDeleteTextures(1, [tex_id])
        self.trigrammaton_textures = {}
        
        # Create a texture for each letter
        for planet, letter in PLANET_TRIGRAMMATON_LETTERS.items():
            # Create texture ID
            tex_id = glGenTextures(1)
            
            # Create QImage for rendering text
            image_size = 128  # Size of the texture (power of 2)
            image = QImage(QSize(image_size, image_size), QImage.Format.Format_RGBA8888)
            image.fill(Qt.GlobalColor.transparent)
            
            # Set up painter
            painter = QPainter(image)
            
            # Use Trigrammaton font - make sure it's installed in your system
            font = QFont("Trigrammaton", 90)  # Increased size for better visibility
            font.setBold(False) 
            painter.setFont(font)
            
            # Calculate text size for centering
            painter.setPen(Qt.GlobalColor.white)  # White text on transparent background
            
            # Center text
            text_rect = painter.fontMetrics().boundingRect(letter)
            x_pos = (image_size - text_rect.width()) // 2
            y_pos = (image_size - text_rect.height()) // 2 + painter.fontMetrics().ascent()
            
            # Draw text
            painter.drawText(x_pos, y_pos, letter)
            painter.end()
            
            # Convert QImage to numpy array for OpenGL compatibility
            ptr = image.bits()
            ptr.setsize(image.sizeInBytes())  # Use sizeInBytes() instead of byteCount()
            arr = np.array(ptr).reshape(image_size, image_size, 4)  # RGBA data
            
            # Bind and setup texture
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Use the numpy array for texture data
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGBA, 
                image_size, image_size, 0,
                GL_RGBA, GL_UNSIGNED_BYTE, arr
            )
            
            # Store texture ID
            self.trigrammaton_textures[planet] = tex_id
            
            print(f"Created texture for {planet} ({letter}) with ID {tex_id}")

    def _create_zodiac_letter_texture(self, zodiac_sign, letter):
        """Create a texture for a zodiac sign's Trigrammaton letter.
        
        Args:
            zodiac_sign (str): The zodiac sign name
            letter (str): The Trigrammaton letter to render
        """
        # Create a special key for this zodiac sign's texture
        zodiac_texture_key = f"zodiac_{zodiac_sign}"
        
        # Create the texture ID
        tex_id = glGenTextures(1)
        
        # Create QImage for rendering text
        image_size = 128  # Size of the texture (power of 2)
        image = QImage(QSize(image_size, image_size), QImage.Format.Format_RGBA8888)
        image.fill(Qt.GlobalColor.transparent)
        
        # Set up painter
        painter = QPainter(image)
        
        # Use Trigrammaton font - make sure it's installed in your system
        font = QFont("Trigrammaton", 90)  # Increased size for better visibility
        font.setBold(False) 
        painter.setFont(font)
        
        # Calculate text size for centering
        painter.setPen(Qt.GlobalColor.white)  # White text on transparent background
        
        # Center text
        text_rect = painter.fontMetrics().boundingRect(letter)
        x_pos = (image_size - text_rect.width()) // 2
        y_pos = (image_size - text_rect.height()) // 2 + painter.fontMetrics().ascent()
        
        # Draw text
        painter.drawText(x_pos, y_pos, letter)
        painter.end()
        
        # Convert QImage to numpy array for OpenGL compatibility
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())  # Use sizeInBytes() instead of byteCount()
        arr = np.array(ptr).reshape(image_size, image_size, 4)  # RGBA data
        
        # Bind and setup texture
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Use the numpy array for texture data
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, 
            image_size, image_size, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, arr
        )
        
        # Store texture ID in zodiac_textures dictionary
        if not hasattr(self, 'zodiac_textures'):
            self.zodiac_textures = {}
        self.zodiac_textures[zodiac_texture_key] = tex_id
        
        print(f"Created texture for zodiac sign {zodiac_sign} ({letter}) with ID {tex_id}")

    def _get_cube_height_from_y_position(self, y_position):
        """
        Calculate the cube height (row) from its y-position.
        
        Args:
            y_position (float): Y-coordinate of the cube's center
            
        Returns:
            int: The cube height (row) from 0 to 12
        """
        # Calculate the base height for cube row 0
        base_height = self.cube_side_length_zbits * 0.5  # Half the cube's height
        
        # Calculate how far up this cube is from the base
        height_diff = y_position - base_height
        
        # Calculate the row number based on the height difference
        cube_height = int(round(height_diff / self.cube_side_length_zbits))
        
        # Clamp to valid range (0-12)
        return max(0, min(cube_height, self.cubes_per_pillar - 1))
        
    def _load_ternary_data(self):
        """
        Load ternary data from CSV files for all walls and ternary attributes.
        This data is used to color and label the upper and lower faces.
        """
        import csv
        import os
        
        # Initialize dictionaries
        self.wall_ternary_data = {}
        self.ternary_attributes = {}
        
        # Base directory for CSV files
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
                               "assets", "cvs", "wall_csv")
        
        print(f"Looking for CSV files in: {base_dir}")
        
        # Load ternary attributes
        attributes_file = os.path.join(base_dir, "ternary_attributes_trigrams.csv")
        if os.path.exists(attributes_file):
            try:
                with open(attributes_file, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Store by ternary value for easy lookup
                        ternary = row.get('Ternary', '')
                        if ternary:
                            self.ternary_attributes[ternary] = {
                                'decimal': int(row.get('decimal', 0)),
                                'letter': row.get('Letter', ''),
                                'celestial': row.get('Celestial', ''),
                                'rgb': (
                                    int(row.get('Red', 0)) / 255.0,
                                    int(row.get('Green', 0)) / 255.0,
                                    int(row.get('Blue', 0)) / 255.0
                                )
                            }
                print(f"Loaded {len(self.ternary_attributes)} ternary attributes")
            except Exception as e:
                print(f"Error loading ternary attributes: {e}")
        
        # Load wall data
        for planet in WALL_PLANET_MAPPING:
            file_path = os.path.join(base_dir, f"{planet.lower()}_wall.csv")
            if os.path.exists(file_path):
                try:
                    # Initialize data for this wall
                    self.wall_ternary_data[planet] = {
                        'decimal': {},  # row -> column -> value
                        'ternary': {}   # row -> column -> value
                    }
                    
                    with open(file_path, 'r') as file:
                        csv_content = file.read()
                        
                        # Debug output of the first 200 characters
                        print(f"\nReading {planet} wall CSV. First 200 chars:\n{csv_content[:200]}...\n")
                        
                        # Debug the format of the file to see if it has two sections
                        section_separator = '\n\n'
                        if section_separator in csv_content:
                            sections = csv_content.split(section_separator)
                            print(f"Found {len(sections)} sections in {planet} wall CSV")
                        else:
                            print(f"WARNING: Could not find section separator in {planet} wall CSV")
                            # Try to handle as single section
                            sections = [csv_content]
                        
                        # Process the binary ternary section directly
                        ternary_portion = ''
                        if len(sections) >= 2:
                            ternary_portion = sections[1]
                        else:
                            # If there's only one section, try to detect the ternary portion by looking for 6-digit values
                            lines = csv_content.split('\n')
                            for i, line in enumerate(lines):
                                if i > 2:  # Skip header lines
                                    parts = line.split(',')
                                    if len(parts) > 1:
                                        # Check if this line contains 6-digit ternary values (containing only 0, 1, 2)
                                        for part in parts[1:]:
                                            if part.strip() and len(part.strip()) == 6 and all(c in '012' for c in part.strip()):
                                                # Found a line with ternary values
                                                ternary_portion = '\n'.join(lines[i-1:])  # Include header
                                                break
                                    if ternary_portion:
                                        break
                        
                        if ternary_portion:
                            # Split into lines and process
                            ternary_lines = ternary_portion.strip().split('\n')
                            
                            # Find header line with "row index"
                            header_idx = -1
                            for i, line in enumerate(ternary_lines):
                                if 'row index' in line.lower():
                                    header_idx = i
                                    break
                            
                            if header_idx >= 0:
                                print(f"Found header at line {header_idx} in {planet} wall ternary section")
                                
                                # Process each line after header
                                for i in range(header_idx + 1, len(ternary_lines)):
                                    line = ternary_lines[i].strip()
                                    if not line or ',' not in line:
                                        continue
                                    
                                    parts = line.split(',')
                                    if len(parts) < 2:
                                        continue
                                    
                                    # Try to get row index
                                    try:
                                        row_idx = int(parts[0])
                                        
                                        # Store both as integer and string keys
                                        if row_idx not in self.wall_ternary_data[planet]['ternary']:
                                            self.wall_ternary_data[planet]['ternary'][row_idx] = {}
                                        if str(row_idx) not in self.wall_ternary_data[planet]['ternary']:
                                            self.wall_ternary_data[planet]['ternary'][str(row_idx)] = {}
                                        
                                        # Process each column
                                        for col_idx in range(min(8, len(parts) - 1)):
                                            col_value = parts[col_idx + 1].strip()
                                            if col_value:
                                                # Check if the value is a 6-digit ternary number
                                                if len(col_value) == 6 and all(c in '012' for c in col_value):
                                                    # Value is already a 6-digit ternary number
                                                    ternary_value = col_value
                                                else:
                                                    # Try to convert from decimal to 6-digit ternary
                                                    try:
                                                        decimal_value = int(col_value)
                                                        # Convert to 6-digit ternary (base 3)
                                                        ternary_value = ""
                                                        temp_decimal = decimal_value
                                                        
                                                        # Ensure we get 6 digits
                                                        for _ in range(6):
                                                            ternary_value = str(temp_decimal % 3) + ternary_value
                                                            temp_decimal //= 3
                                                        
                                                        # Debug output
                                                        if pillar_index == 0 and cube_height == 0:
                                                            print(f"Converted decimal {decimal_value} to ternary {ternary_value}")
                                                    except (ValueError, TypeError):
                                                        # If conversion fails, use a default value
                                                        ternary_value = "000000"
                                                        print(f"Warning: Could not convert '{col_value}' to ternary for {planet} wall")
                                                
                                                self.wall_ternary_data[planet]['ternary'][row_idx][col_idx] = ternary_value
                                                self.wall_ternary_data[planet]['ternary'][str(row_idx)][col_idx] = ternary_value
                                        
                                        print(f"Processed row {row_idx} for {planet} wall with {min(8, len(parts) - 1)} columns")
                                    except ValueError:
                                        print(f"Error parsing row index from '{parts[0]}' in {planet} wall")
                            else:
                                print(f"WARNING: Could not find 'row index' header in {planet} wall ternary section")
                        else:
                            print(f"WARNING: No ternary data found in {planet} wall CSV")
                            
                    # Print the structure of the loaded data
                    row_count = len(self.wall_ternary_data[planet]['ternary'])
                    print(f"Loaded {row_count} rows for {planet} wall ternary data")
                    
                    # Debug: print the row keys
                    row_keys = sorted(list(self.wall_ternary_data[planet]['ternary'].keys()))
                    if row_keys:
                        print(f"Row keys for {planet}: {row_keys}")
                
                except Exception as e:
                    print(f"Error loading {planet} wall data: {str(e)}")
        
        # Print a summary at the end
        loaded_walls = [planet for planet in WALL_PLANET_MAPPING if planet in self.wall_ternary_data and self.wall_ternary_data[planet]['ternary']]
        print(f"Successfully loaded ternary data for walls: {loaded_walls}")
        print(f"Total ternary attributes: {len(self.ternary_attributes)}")
        
        # Check if we have any valid data loaded, and if not, generate test data
        has_valid_data = False
        for planet in WALL_PLANET_MAPPING:
            if (planet in self.wall_ternary_data and 
                'ternary' in self.wall_ternary_data[planet] and 
                self.wall_ternary_data[planet]['ternary']):
                has_valid_data = True
                break
                
        if not has_valid_data:
            print("No valid ternary data loaded from CSV files. Generating test data...")
            self._generate_test_ternary_data()

    def _get_trigram_from_ternary(self, ternary_value, position):
        """
        Extract a trigram from a 6-digit ternary value based on position.
        
        Args:
            ternary_value (str): 6-digit ternary value
            position (str): 'upper' or 'lower' to select which trigram to extract
            
        Returns:
            str: 3-digit trigram value
        """
        if not ternary_value or len(ternary_value) != 6:
            return "000"  # Default value
            
        if position == 'upper':
            # Extract left 3 digits for upper face
            return ternary_value[:3]
        elif position == 'lower':
            # Extract right 3 digits for lower face
            return ternary_value[3:]
        else:
            return "000"  # Default value
            
    def _create_trigram_letter_texture(self, trigram):
        """Create a texture for a trigram's Trigrammaton letter.
        
        Args:
            trigram (str): The trigram value (3-digit ternary)
            
        Returns:
            int: Texture ID or None if texture couldn't be created
        """
        # If the texture already exists, return it
        texture_key = f"trigram_{trigram}"
        if hasattr(self, 'trigram_textures') and texture_key in self.trigram_textures:
            return self.trigram_textures[texture_key]
            
        # Make sure ternary attributes are loaded
        if not hasattr(self, 'ternary_attributes') or not self.ternary_attributes:
            self._load_ternary_data()
            
        # Look up the letter for this trigram
        if trigram not in self.ternary_attributes:
            return None
            
        letter = self.ternary_attributes[trigram]['letter']
        if not letter:
            return None
            
        # Create texture ID
        tex_id = glGenTextures(1)
        
        # Create QImage for rendering text
        image_size = 128  # Size of the texture (power of 2)
        image = QImage(QSize(image_size, image_size), QImage.Format.Format_RGBA8888)
        image.fill(Qt.GlobalColor.transparent)
        
        # Set up painter
        painter = QPainter(image)
        
        # Use Trigrammaton font - make sure it's installed in your system
        font = QFont("Trigrammaton", 90)  # Increased size for better visibility
        font.setBold(False) 
        painter.setFont(font)
        
        # Calculate text size for centering
        painter.setPen(Qt.GlobalColor.white)  # White text on transparent background
        
        # Center text
        text_rect = painter.fontMetrics().boundingRect(letter)
        x_pos = (image_size - text_rect.width()) // 2
        y_pos = (image_size - text_rect.height()) // 2 + painter.fontMetrics().ascent()
        
        # Draw text
        painter.drawText(x_pos, y_pos, letter)
        painter.end()
        
        # Convert QImage to numpy array for OpenGL compatibility
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())  # Use sizeInBytes() instead of byteCount()
        arr = np.array(ptr).reshape(image_size, image_size, 4)  # RGBA data
        
        # Bind and setup texture
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Use the numpy array for texture data
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, 
            image_size, image_size, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, arr
        )
        
        # Store texture ID
        if not hasattr(self, 'trigram_textures'):
            self.trigram_textures = {}
        self.trigram_textures[texture_key] = tex_id
        
        print(f"Created texture for trigram {trigram} ({letter}) with ID {tex_id}")
        return tex_id

    def _debug_print_ternary_data_structure(self):
        """Print the structure of loaded ternary data for debugging purposes."""
        if not hasattr(self, 'wall_ternary_data'):
            print("DEBUG: wall_ternary_data not found!")
            return
            
        print("\n=== TERNARY DATA STRUCTURE SUMMARY ===")
        for planet, data in self.wall_ternary_data.items():
            if 'ternary' in data:
                # Count total rows
                rows = data['ternary'].keys()
                
                # Convert all keys to strings before sorting to avoid str/int comparison
                str_rows = [str(r) for r in rows]
                print(f"Planet {planet} has {len(rows)} rows with keys: {sorted(str_rows)}")
                
                # Print example of first row if it exists
                if rows:
                    # Find the lowest index (convert to int for numeric sorting)
                    numeric_rows = []
                    for r in rows:
                        try:
                            numeric_rows.append(int(r))
                        except (ValueError, TypeError):
                            # If it can't be converted to int, skip it
                            pass
                    
                    if numeric_rows:
                        first_row = min(numeric_rows)
                        row_type = "integer"
                    else:
                        # If no convertible rows, just use the first string key
                        first_row = next(iter(rows))
                        row_type = f"string '{first_row}'"
                        
                    # Use the key as it exists in the dictionary
                    if first_row in data['ternary']:
                        row_key = first_row
                    else:
                        # Try the string version
                        row_key = str(first_row)
                        
                    if row_key in data['ternary']:
                        print(f"  First row ({row_type}) has {len(data['ternary'][row_key])} columns")
                        
                        # Print sample value
                        if data['ternary'][row_key]:
                            # Convert column keys to strings too
                            col_keys = [str(c) for c in data['ternary'][row_key].keys()]
                            if col_keys:
                                # Find lowest numeric column
                                numeric_cols = []
                                for c in data['ternary'][row_key].keys():
                                    try:
                                        numeric_cols.append(int(c))
                                    except (ValueError, TypeError):
                                        pass
                                
                                if numeric_cols:
                                    first_col = min(numeric_cols)
                                    if first_col in data['ternary'][row_key]:
                                        col_key = first_col
                                    else:
                                        col_key = str(first_col)
                                else:
                                    col_key = next(iter(data['ternary'][row_key].keys()))
                                
                                val = data['ternary'][row_key][col_key]
                                print(f"  Sample value at row {row_key}, col {col_key}: '{val}'")
        
        # Print trigram attribute count
        if hasattr(self, 'ternary_attributes'):
            print(f"\nLoaded {len(self.ternary_attributes)} ternary trigram attributes")
            if self.ternary_attributes:
                sample_key = next(iter(self.ternary_attributes.keys()))
                print(f"Sample trigram '{sample_key}' attributes: {self.ternary_attributes[sample_key]}")
        
        print("=== END TERNARY DATA STRUCTURE SUMMARY ===\n")
        
    def _generate_test_ternary_data(self):
        """
        Generate test ternary data if no data was loaded from CSV files.
        This ensures we can see the upper and lower faces with colors and letters.
        """
        print("Generating test ternary data for visualization...")
        
        # Make sure we have the wall_ternary_data structure
        if not hasattr(self, 'wall_ternary_data'):
            self.wall_ternary_data = {}
            
        # Generate or ensure ternary attributes exist
        if not hasattr(self, 'ternary_attributes') or not self.ternary_attributes:
            self.ternary_attributes = {
                # Some sample trigrams with their attributes
                '000': {'decimal': 0, 'letter': 'A', 'celestial': 'test', 
                       'rgb': (1.0, 0.0, 0.0)},  # Red
                '111': {'decimal': 13, 'letter': 'E', 'celestial': 'sun', 
                       'rgb': (0.0, 1.0, 0.0)},  # Green
                '222': {'decimal': 26, 'letter': 'Z', 'celestial': 'earth', 
                       'rgb': (0.0, 0.0, 1.0)},  # Blue
                '012': {'decimal': 5, 'letter': 'M', 'celestial': 'mercury', 
                       'rgb': (1.0, 1.0, 0.0)},  # Yellow
                '021': {'decimal': 7, 'letter': 'J', 'celestial': 'venus', 
                       'rgb': (0.0, 1.0, 1.0)},  # Cyan
                '102': {'decimal': 11, 'letter': 'T', 'celestial': 'mars', 
                       'rgb': (1.0, 0.0, 1.0)},  # Magenta
                '120': {'decimal': 15, 'letter': 'Q', 'celestial': 'jupiter', 
                       'rgb': (0.5, 0.5, 1.0)},  # Light blue
                '201': {'decimal': 19, 'letter': 'W', 'celestial': 'saturn', 
                       'rgb': (1.0, 0.5, 0.5)},  # Light red
                '210': {'decimal': 21, 'letter': 'V', 'celestial': 'uranus', 
                       'rgb': (0.5, 1.0, 0.5)},  # Light green
            }
            
        # Generate data for each planet if it doesn't exist or is empty
        for wall_idx, planet in enumerate(WALL_PLANET_MAPPING):
            if planet not in self.wall_ternary_data or 'ternary' not in self.wall_ternary_data[planet] or not self.wall_ternary_data[planet]['ternary']:
                # Initialize the structure
                if planet not in self.wall_ternary_data:
                    self.wall_ternary_data[planet] = {}
                    
                self.wall_ternary_data[planet]['ternary'] = {}
                
                # Generate data for each height (0-12) and column (0-7)
                for height in range(13):  # 13 heights (0-12)
                    self.wall_ternary_data[planet]['ternary'][height] = {}
                    
                    for col in range(8):  # 8 columns (0-7)
                        # Generate a pseudo-random 6-digit ternary value based on the position
                        upper_trigram = f"{(height % 3)}{(col % 3)}{((height + col) % 3)}"
                        lower_trigram = f"{(col % 3)}{(height % 3)}{((col + wall_idx) % 3)}"
                        ternary_value = upper_trigram + lower_trigram
                        
                        # Store the value
                        self.wall_ternary_data[planet]['ternary'][height][col] = ternary_value
                        
                        # Also store with string key for flexibility
                        if str(height) not in self.wall_ternary_data[planet]['ternary']:
                            self.wall_ternary_data[planet]['ternary'][str(height)] = {}
                        self.wall_ternary_data[planet]['ternary'][str(height)][col] = ternary_value
                
                print(f"Generated test data for {planet} wall: 13 heights × 8 columns")
                        
        print(f"Test ternary data generation complete for {len(WALL_PLANET_MAPPING)} walls.")