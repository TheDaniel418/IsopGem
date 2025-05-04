# Chapter 1: Foundation and Basic Framework

This chapter focuses on establishing the foundational architecture and basic UI framework for the Sacred Geometry Explorer window that will open from the existing "Sacred Geometry" button in the Geometry tab.

## Tasks

### 1.1 Create Sacred Geometry Explorer Module Structure

**Description:** Set up the basic module structure for the Sacred Geometry Explorer with proper window management integration.

**Subtasks:**
1. Create the `geometry/ui/sacred_geometry` directory structure
2. Set up the necessary `__init__.py` files
3. Create the main `explorer.py` file inheriting from `AuxiliaryWindow`
4. Set up imports including window management dependencies
5. Create placeholder files for major components:
   - tool_system/
   - canvas/
   - objects/
   - properties/
   - commands/
   - utils/

**Acceptance Criteria:**
- Module structure is properly set up with window management integration
- All necessary `__init__.py` files are in place
- Main `explorer.py` file created with proper window management inheritance
- All required window management imports are set up
- Component directories and placeholders are created

**Dependencies:** None

---

### 1.2 Implement Sacred Geometry Explorer Window

**Description:** Create the main Sacred Geometry Explorer window class inheriting from AuxiliaryWindow to ensure proper focus-based window management, with support for multiple instances.

**Subtasks:**
1. Implement `SacredGeometryExplorer` class inheriting from `AuxiliaryWindow` with:
   - Instance-specific identifiers
   - Tool state persistence per instance
   - Window geometry tracking
2. Set up window layout with:
   - Toolbar area (top)
   - Canvas area (center)
   - Properties panel (right, collapsible)
   - Status bar (bottom)
   - Window instance indicator
3. Implement window initialization with:
   - Window title and icon
   - Default size (800x600)
   - Window flags for proper focus handling
   - Window state persistence
   - Instance-specific settings storage
4. Connect to existing window management system:
   - Register with WindowManager using unique instance ID
   - Implement proper window ID handling
   - Set up window state save/restore per instance
   - Add window visibility handlers
   - Implement focus event handling
5. Add window management functionality:
   - Focus management with visual feedback
   - Window state persistence per instance
   - Z-order handling with instance awareness
   - Window destruction cleanup
   - Tool state transfer between instances

**Acceptance Criteria:**
- SacredGeometryExplorer properly inherits from AuxiliaryWindow
- Layout structure follows application standards
- Window initializes with correct instance-specific settings
- Window properly registers with WindowManager using unique ID
- Window state persists between sessions per instance
- Focus management follows application standards with visual feedback
- Window cleanup handles instance-specific resources
- Tool states transfer smoothly between instances
- Visual feedback indicates active/inactive window state
- Properties panel updates based on window focus

**Dependencies:** 1.1

---

### 1.3 Implement Canvas Framework

**Description:** Create the canvas framework that will serve as the main construction area.

**Subtasks:**
1. Implement a `GeometryCanvas` class using `QGraphicsView` and `QGraphicsScene`
2. Set up coordinate system with proper scaling and origin
3. Implement basic navigation controls (zoom, pan)
4. Add grid display with customizable spacing
5. Implement basic mouse interaction handling

**Acceptance Criteria:**
- Canvas displays with proper coordinate system
- User can zoom in/out and pan the view
- Grid displays correctly and scales with zoom level
- Basic mouse interactions (click, drag) are captured
- Canvas is properly integrated into the Explorer window

**Dependencies:** 1.2

---

### 1.4 Create Geometry Object Model

**Description:** Design and implement the core object model for geometric entities.

**Subtasks:**
1. Create base `GeometricObject` class with common properties and methods
2. Implement derived classes for basic objects (Point, Line, Circle)
3. Design the object hierarchy with proper inheritance
4. Implement serialization/deserialization for geometric objects
5. Create factory methods for object creation
6. Integrate layer reference into `GeometricObject` and ensure all objects are assigned to a layer upon creation.

**Acceptance Criteria:**
- Object model supports all basic geometric entities
- Objects can be created, modified, and deleted
- Object properties can be accessed and modified
- Objects can be serialized and deserialized
- Factory methods create objects correctly
- All objects are assigned to a layer and reference their parent layer

**Dependencies:** None

---

### 1.5 Implement Object Rendering System

**Description:** Create the rendering system for displaying geometric objects on the canvas.

**Subtasks:**
1. Implement `GraphicsItem` classes for each geometric object type
2. Create mapping between model objects and their visual representations
3. Implement styling system for objects (color, line style, etc.)
4. Add selection highlighting and handles
5. Ensure proper z-ordering of objects
6. Render objects according to their layer order and respect layer visibility and lock status.

**Acceptance Criteria:**
- All geometric objects render correctly on the canvas
- Object styling (color, line style) works properly
- Selected objects show appropriate highlighting
- Objects maintain proper visual layering
- Rendering system integrates with the canvas framework
- Layer order and visibility/lock are respected in rendering

**Dependencies:** 1.3, 1.4

---

### 1.6 Implement Layering System

**Description:** Add foundational support for layers in the Sacred Geometry Explorer.

**Subtasks:**
1. Implement `Layer` class with name, visibility, lock status, and object list
2. Add layer management to the Explorer (create, delete, rename, reorder, set active)
3. Integrate layer assignment into object creation and deletion
4. Implement serialization/deserialization for layers and their objects
5. Add basic UI for layer management (list, add, remove, reorder, set active, toggle visibility/lock)

**Acceptance Criteria:**
- Users can create, delete, rename, and reorder layers
- Objects are always assigned to a layer
- Layer visibility and lock status affect rendering and editing
- Layer state is saved and restored with the Explorer

**Dependencies:** 1.4, 1.5

---

### 1.7 Create Tool System Framework

**Description:** Implement the framework for geometric construction tools.

**Subtasks:**
1. Design the tool system architecture
2. Create base `GeometryTool` class with common functionality
3. Implement tool selection mechanism
4. Create tool state management system
5. Implement basic mouse event handling for tools

**Acceptance Criteria:**
- Tool system architecture is in place
- Tools can be selected and activated
- Active tool receives mouse events
- Tool state is properly managed
- Tool system integrates with the canvas framework

**Dependencies:** 1.3

---

### 1.8 Implement Properties Panel

**Description:** Create the properties panel for viewing and editing object properties.

**Subtasks:**
1. Design the properties panel UI
2. Implement property editors for common properties (coordinates, radius, etc.)
3. Create the connection between selected objects and the properties panel
4. Implement property change handling and object updating
5. Add support for multi-object selection properties

**Acceptance Criteria:**
- Properties panel displays properties of selected objects
- Properties can be edited through the panel
- Changes in properties are immediately reflected in the objects
- Panel updates when selection changes
- Multi-object selection properties are handled correctly

**Dependencies:** 1.4, 1.5

---

### 1.9 Create Command System for Undo/Redo

**Description:** Implement a command-based system for undo/redo functionality.

**Subtasks:**
1. Design the command pattern implementation
2. Create base `GeometryCommand` class
3. Implement command history management
4. Create commands for basic operations (create, modify, delete)
5. Add undo/redo UI controls

**Acceptance Criteria:**
- All operations are recorded as commands
- Undo/redo functionality works correctly
- Command history is properly managed
- UI provides access to undo/redo operations
- Command system integrates with the object model

**Dependencies:** 1.4

---

### 1.10 Create Basic Toolbar

**Description:** Implement the basic toolbar with tool selection buttons.

**Subtasks:**
1. Design the toolbar UI
2. Create tool button widgets with icons
3. Implement tool selection logic
4. Organize tools into categories
5. Add tooltips and keyboard shortcuts

**Acceptance Criteria:**
- Toolbar displays with proper organization
- Tool buttons have appropriate icons
- Selecting a tool activates it
- Tools are organized into logical categories
- Tooltips and shortcuts work correctly

**Dependencies:** 1.6

---

### 1.11 Connect to Existing Geometry Tab

**Description:** Connect the Sacred Geometry Explorer to the existing Geometry tab with robust window management integration.

**Subtasks:**
1. Update GeometryTab integration:
   - Add Sacred Geometry button with proper styling
   - Implement `_open_sacred_geometry` method
   - Add window instance tracking
   - Implement window reuse logic
2. Implement window instance management:
   - Create unique window ID generation
   - Track active instances
   - Handle instance reuse vs new creation
   - Manage instance-specific resources
3. Add window management hooks:
   - Connect to WindowManager events
   - Handle window focus changes
   - Manage window z-ordering
   - Implement window state persistence
4. Implement error handling:
   - Add window creation error handling
   - Implement resource cleanup on errors
   - Add user feedback for errors
   - Handle window initialization failures
5. Add user experience features:
   - Visual feedback when opening windows
   - Progress indication for large constructions
   - Smooth window transitions
   - Instance indicators in window titles

**Acceptance Criteria:**
- Sacred Geometry button works reliably
- Window instances are properly managed
- Focus changes work smoothly
- Errors are handled gracefully
- User gets appropriate feedback
- Window states persist correctly
- Resources are cleaned up properly
- Multiple instances work correctly
- Visual transitions are smooth
- Instance management is reliable

**Dependencies:** 1.2

---

### 1.12 Integrate Components and Test Foundation

**Description:** Integrate all foundation components and perform comprehensive testing.

**Subtasks:**
1. Connect all components (canvas, tools, properties panel)
2. Implement event propagation between components
3. Test all basic functionality
4. Fix any integration issues
5. Optimize performance if needed

**Acceptance Criteria:**
- All components work together seamlessly
- Events propagate correctly between components
- Basic functionality works as expected
- Integration issues are resolved
- Performance is acceptable

**Dependencies:** 1.1 through 1.11

---

### 1.13 Implement Multi-Window Management

**Description:** Implement support for multiple Sacred Geometry Explorer windows with proper focus management.

**Subtasks:**
1. Add multi-window tracking in WindowManager
2. Implement window state persistence per instance
3. Create unique window IDs for each explorer instance
4. Add window instance registry
5. Implement proper focus handling between instances

**Acceptance Criteria:**
- Multiple Sacred Geometry Explorer windows can be open simultaneously
- Each window maintains its own state
- Windows have unique identifiers
- Window registry tracks all instances
- Focus handling works correctly between windows

**Dependencies:** 1.2, 1.11

---

## Next Chapter

Once the foundation is complete, proceed to [Chapter 2: Basic Geometric Tools](02_basic_tools.md).
