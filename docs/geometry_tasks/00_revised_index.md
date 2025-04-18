# Sacred Geometry Explorer Development Plan

This document outlines the comprehensive development plan for the Sacred Geometry Explorer in IsopGem. The Sacred Geometry Explorer will be implemented as a separate window that opens from the existing "Sacred Geometry" button in the Geometry tab. The development is organized into chapters, each containing sequential tasks to implement specific features.

## Implementation Status

**Important Note:** As of April 2025, none of the geometric tools described in these tasks have been implemented yet. The tasks outline the planned implementation, with special attention paid to preventing construction points from remaining as separate objects when creating geometric objects (lines, circles, polygons, etc). This issue will be handled through proper object lifecycle management in the tool implementations.

## Development Approach

The Sacred Geometry Explorer will be a GeoGebra-like environment focused on sacred geometry, providing tools for constructing, exploring, and analyzing sacred geometric patterns and relationships. It will open in a separate window, following the application's focus-based window management system.

## Development Chapters

1. [Foundation and Basic Framework](01_foundation_revised.md)
   - Setting up the basic architecture and UI framework for the Sacred Geometry Explorer

2. [Basic Geometric Tools](02_basic_tools.md)
   - Implementing fundamental geometric construction tools

3. [Sacred Geometry Specialized Tools](03_sacred_geometry_tools.md)
   - Adding specialized tools for sacred geometry constructions

4. [Dynamic Geometry System](04_dynamic_geometry.md)
   - Implementing the constraint-based dynamic geometry system

5. [Measurement and Analysis](05_measurement_analysis.md)
   - Adding tools for measuring and analyzing geometric constructions

6. [Templates and Guides](06_templates_guides.md)
   - Creating pre-built templates and step-by-step guides

7. [Advanced Features](07_advanced_features.md)
   - Implementing advanced functionality like fractals and scripting

8. [3D Geometry](08_3d_geometry.md)
   - Adding support for 3D sacred geometry

9. [Integration with Other Pillars](09_integration.md)
   - Connecting with Gematria, Astrology, and other pillars

10. [Polishing and Optimization](10_polishing.md)
    - Final refinements, optimizations, and user experience improvements

## Implementation Strategy

- The Sacred Geometry Explorer will be implemented as a separate module within the Geometry pillar
- It will be opened from the existing "Sacred Geometry" button in the Geometry tab
- The Explorer will follow the application's focus-based window management system
- Each chapter represents a logical phase of development
- Tasks within chapters are designed to be completed sequentially
- Complex tasks are broken down into simpler subtasks

## Technical Specification

**Language:** Python 3.11
**UI Framework:** PyQt6
**OS:** Linux (primary target, cross-platform support desirable)
**Project Structure:** See workspace tree above

### General Requirements
- All UI components must use PyQt6 widgets and idioms.
- All new code must be type-annotated and compatible with mypy strict mode.
- All geometric tools and objects must be implemented as Python classes.
- All persistent state (window, tool, object) must be serializable (preferably JSON-compatible).
- All user-facing strings must be ready for i18n (use Qt translation where possible).

### Base Class Interfaces

#### GeometricObject (abstract base class)
```python
class GeometricObject(QObject):
    id: str
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
```

### Data Structures
- All geometric objects must have a unique string `id`.
- All tool state must be serializable via `to_dict`/`from_dict`.
- Window state must include active tool, object list, and view parameters.

### Error Handling
- All user actions must be validated; invalid actions should show a `QMessageBox` error.
- All exceptions must be logged to `logs/error.log`.
- Tool operations must be cancelable via `Esc`.

### Integration
- All windows must register with `WindowManager` on creation and unregister on close.
- Tool state and window state must be restorable after application restart.
- All geometric objects must be compatible with the dynamic constraint system (see Chapter 4).

### Testing
- All new classes must have unit tests in `tests/`.
- All UI actions must be testable via simulated events.
- 100% code coverage is required for all new modules.

## Getting Started

Begin with Chapter 1: [Foundation and Basic Framework](01_foundation_revised.md) to set up the basic architecture for the Sacred Geometry Explorer.
