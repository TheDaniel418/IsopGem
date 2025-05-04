# Sacred Geometry Explorer Development Plan

This document outlines the comprehensive development plan for the Sacred Geometry Explorer in IsopGem. The Sacred Geometry Explorer will be implemented as a separate window that opens from the existing "Sacred Geometry" button in the Geometry tab. The development is organized into chapters, each containing sequential tasks to implement specific features.

## Implementation Status

**Important Note:** As of April 2025, none of the geometric tools described in these tasks have been implemented yet. The tasks outline the planned implementation, with special attention paid to preventing construction points from remaining as separate objects when creating geometric objects (lines, circles, polygons, etc). This issue will be handled through proper object lifecycle management in the tool implementations.

## Development Approach

The Sacred Geometry Explorer will be a GeoGebra-like environment focused on sacred geometry, providing tools for constructing, exploring, and analyzing sacred geometric patterns and relationships. It will open in a separate window, following the application's focus-based window management system.

## Layering System (NEW)

A core feature of the Sacred Geometry Explorer is a flexible layering system, similar to those found in professional graphics and geometry tools. Layers allow users to:
- Organize geometric objects into named groups
- Toggle visibility and lock status for each layer
- Reorder layers (top-to-bottom rendering)
- Assign objects to specific layers
- Load templates or guides into separate layers
- Edit only objects in the active, unlocked layer

This system enhances organization, editing power, and analysis, and is essential for working with complex sacred patterns.

### Example Layer Class
```python
class Layer:
    def __init__(self, name: str, visible: bool = True, locked: bool = False):
        self.name = name
        self.visible = visible
        self.locked = locked
        self.objects: List[GeometricObject] = []
```

## Development Chapters

1. [Foundation and Basic Framework](01_foundation_revised.md)
   - Setting up the basic architecture and UI framework for the Sacred Geometry Explorer
   - **Add basic layer support to the window and data model**

2. [Basic Geometric Tools](02_basic_tools.md)
   - Implementing fundamental geometric construction tools
   - **Ensure all created objects are assigned to the active layer**

3. [Sacred Geometry Specialized Tools](03_sacred_geometry_tools.md)
   - Adding specialized tools for sacred geometry constructions

4. [Dynamic Geometry System](04_dynamic_geometry.md)
   - Implementing the constraint-based dynamic geometry system

5. [Measurement and Analysis](05_measurement_analysis.md)
   - Adding tools for measuring and analyzing geometric constructions

6. [Templates and Guides](06_templates_guides.md)
   - Creating pre-built templates and step-by-step guides
   - **Templates and guides should be loaded into their own layers**

7. [Advanced Features](07_advanced_features.md)
   - Implementing advanced functionality like fractals and scripting

8. [3D Geometry](08_3d_geometry.md)
   - Adding support for 3D sacred geometry

9. [Integration with Other Pillars](09_integration.md)
   - Connecting with Gematria, Astrology, and other pillars

10. [Polishing and Optimization](10_polishing.md)
    - Final refinements, optimizations, and user experience improvements
    - **Enhance layer management UI and usability**

## Implementation Strategy

- The Sacred Geometry Explorer will be implemented as a separate module within the Geometry pillar
- It will be opened from the existing "Sacred Geometry" button in the Geometry tab
- The Explorer will follow the application's focus-based window management system
- Each chapter represents a logical phase of development
- Tasks within chapters are designed to be completed sequentially
- Complex tasks are broken down into simpler subtasks
- **Layering will be integrated from the start and refined throughout development**

## Technical Specification

**Language:** Python 3.11
**UI Framework:** PyQt6
**OS:** Linux (primary target, cross-platform support desirable)
**Project Structure:** See workspace tree above

### General Requirements
- All UI components must use PyQt6 widgets and idioms.
- All new code must be type-annotated and compatible with mypy strict mode.
- All geometric tools and objects must be implemented as Python classes.
- **All geometric objects must belong to a Layer.**
- **Layer state (order, visibility, lock status) must be serializable and restorable.**
- All persistent state (window, tool, object, layer) must be serializable (preferably JSON-compatible).
- All user-facing strings must be ready for i18n (use Qt translation where possible).

### Base Class Interfaces

#### GeometricObject (abstract base class)
```python
class GeometricObject(QObject):
    id: str
    layer: Layer  # NEW: reference to parent layer
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "GeometricObject": ...
    def set_selected(self, selected: bool) -> None: ...
    def move(self, dx: float, dy: float) -> None: ...
    def delete(self) -> None: ...
```

#### GeometryTool (abstract base class)
```python
class GeometryTool(QObject):
    name: str
    def activate(self) -> None: ...
    def deactivate(self) -> None: ...
    def handle_mouse_press(self, event: QMouseEvent) -> None: ...
    def handle_mouse_move(self, event: QMouseEvent) -> None: ...
    def handle_mouse_release(self, event: QMouseEvent) -> None: ...
    def cancel(self) -> None: ...
```

#### SacredGeometryExplorer (window)
```python
class SacredGeometryExplorer(AuxiliaryWindow):
    def __init__(self, window_manager: WindowManager, *args, **kwargs): ...
    def save_state(self) -> dict: ...
    def restore_state(self, state: dict) -> None: ...
    def add_tool(self, tool: GeometryTool) -> None: ...
    def set_active_tool(self, tool_name: str) -> None: ...
    # NEW: Layer management methods
    def add_layer(self, name: str) -> Layer: ...
    def remove_layer(self, layer_id: str) -> None: ...
    def set_active_layer(self, layer_id: str) -> None: ...
    def reorder_layers(self, new_order: List[str]) -> None: ...
    def toggle_layer_visibility(self, layer_id: str) -> None: ...
    def toggle_layer_lock(self, layer_id: str) -> None: ...
```

### Data Structures
- All geometric objects must have a unique string `id`.
- **All geometric objects must belong to a layer.**
- **Layers are ordered, named, and have visibility/lock status.**
- All tool state must be serializable via `to_dict`/`from_dict`.
- Window state must include active tool, object list, layer list, and view parameters.

### Error Handling
- All user actions must be validated; invalid actions should show a `QMessageBox` error.
- All exceptions must be logged to `logs/error.log`.
- Tool operations must be cancelable via `Esc`.

### Integration
- All windows must register with `WindowManager` on creation and unregister on close.
- Tool state and window state must be restorable after application restart.
- All geometric objects must be compatible with the dynamic constraint system (see Chapter 4).
- **Layer state must be saved and restored with the rest of the explorer state.**

### Testing
- All new classes must have unit tests in `tests/`.
- All UI actions must be testable via simulated events.
- 100% code coverage is required for all new modules.

## Getting Started

Begin with Chapter 1: [Foundation and Basic Framework](01_foundation_revised.md) to set up the basic architecture for the Sacred Geometry Explorer.
