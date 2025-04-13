# Chapter 2: Basic Geometric Tools

This chapter focuses on implementing the fundamental geometric construction tools that will form the basis of the Geometry tab's functionality.

## Tasks

### 2.1 Implement Point Tool

**Description:** Create the tool for placing points on the canvas.

**Subtasks:**
1. Implement `PointTool` class
2. Add point creation on mouse click
3. Implement point dragging functionality
4. Add snapping to grid and existing objects
5. Create point style customization options

**Acceptance Criteria:**
- Points can be created by clicking on the canvas
- Points can be selected and dragged
- Points snap to grid and existing objects when appropriate
- Point appearance can be customized

**Dependencies:** Chapter 1 foundation

---

### 2.2 Implement Line Tool

**Description:** Create the tool for drawing lines between two points.

**Subtasks:**
1. Implement `LineTool` class
2. Add line creation by selecting two points
3. Implement preview during creation
4. Add support for infinite lines, rays, and line segments
5. Implement line style customization

**Acceptance Criteria:**
- Lines can be created by selecting two points
- Preview shows during creation process
- Different line types (infinite, ray, segment) are supported
- Line appearance can be customized

**Dependencies:** 2.1

---

### 2.3 Implement Circle Tool

**Description:** Create the tool for drawing circles with center and radius.

**Subtasks:**
1. Implement `CircleTool` class
2. Add circle creation by center and point on circumference
3. Implement preview during creation
4. Add support for circles with fixed radius
5. Implement circle style customization

**Acceptance Criteria:**
- Circles can be created by selecting center and radius
- Preview shows during creation process
- Fixed radius circles can be created
- Circle appearance can be customized

**Dependencies:** 2.1

---

### 2.4 Implement Polygon Tool

**Description:** Create the tool for drawing polygons with arbitrary number of vertices.

**Subtasks:**
1. Implement `PolygonTool` class
2. Add polygon creation by selecting vertices
3. Implement preview during creation
4. Add completion mechanisms (double-click, close to start)
5. Implement polygon style customization

**Acceptance Criteria:**
- Polygons can be created by selecting vertices
- Preview shows during creation process
- Polygons can be completed through various methods
- Polygon appearance can be customized

**Dependencies:** 2.1

---

### 2.5 Implement Regular Polygon Tool

**Description:** Create the tool for drawing regular polygons with specified number of sides.

**Subtasks:**
1. Implement `RegularPolygonTool` class
2. Add regular polygon creation by center and vertex
3. Implement side count selection
4. Add orientation options (vertex at top, side at top)
5. Implement preview during creation

**Acceptance Criteria:**
- Regular polygons can be created with specified number of sides
- User can select number of sides (3-20)
- Orientation can be controlled
- Preview shows during creation process

**Dependencies:** 2.4

---

### 2.6 Implement Intersection Tool

**Description:** Create the tool for finding and marking intersections between objects.

**Subtasks:**
1. Implement `IntersectionTool` class
2. Add intersection detection between lines
3. Add intersection detection between lines and circles
4. Add intersection detection between circles
5. Implement automatic intersection point creation

**Acceptance Criteria:**
- Intersections between different object types can be found
- Intersection points are created automatically
- Tool handles multiple intersections appropriately
- Intersections update when objects move

**Dependencies:** 2.1, 2.2, 2.3

---

### 2.7 Implement Perpendicular Line Tool

**Description:** Create the tool for drawing perpendicular lines.

**Subtasks:**
1. Implement `PerpendicularLineTool` class
2. Add perpendicular line creation from point to line
3. Add perpendicular line creation through point on line
4. Implement preview during creation
5. Ensure perpendicular constraint is maintained

**Acceptance Criteria:**
- Perpendicular lines can be created from point to line
- Perpendicular lines can be created through points on lines
- Preview shows during creation process
- Perpendicularity is maintained when objects move

**Dependencies:** 2.2

---

### 2.8 Implement Parallel Line Tool

**Description:** Create the tool for drawing parallel lines.

**Subtasks:**
1. Implement `ParallelLineTool` class
2. Add parallel line creation through point
3. Implement preview during creation
4. Add distance measurement option
5. Ensure parallel constraint is maintained

**Acceptance Criteria:**
- Parallel lines can be created through points
- Preview shows during creation process
- Distance between parallel lines can be measured
- Parallelism is maintained when objects move

**Dependencies:** 2.2

---

### 2.9 Implement Angle Bisector Tool

**Description:** Create the tool for drawing angle bisectors.

**Subtasks:**
1. Implement `AngleBisectorTool` class
2. Add angle bisector creation from three points
3. Add angle bisector creation from two lines
4. Implement preview during creation
5. Ensure bisector constraint is maintained

**Acceptance Criteria:**
- Angle bisectors can be created from three points
- Angle bisectors can be created from two lines
- Preview shows during creation process
- Bisector property is maintained when objects move

**Dependencies:** 2.2

---

### 2.10 Implement Compass Tool

**Description:** Create the tool for drawing circles with radius equal to a given distance.

**Subtasks:**
1. Implement `CompassTool` class
2. Add radius selection by two points
3. Add circle creation with selected radius
4. Implement preview during creation
5. Add support for transferring measurements

**Acceptance Criteria:**
- Circles can be created with radius equal to distance between two points
- Preview shows during creation process
- Multiple circles with same radius can be created
- Tool supports classical compass-and-straightedge construction

**Dependencies:** 2.1, 2.3

---

### 2.11 Implement Selection and Transformation Tools

**Description:** Create tools for selecting, moving, and transforming objects.

**Subtasks:**
1. Implement `SelectionTool` class
2. Add single and multiple object selection
3. Implement object moving functionality
4. Add rotation and scaling transformations
5. Implement selection rectangle for area selection

**Acceptance Criteria:**
- Objects can be selected individually or in groups
- Selected objects can be moved, rotated, and scaled
- Selection rectangle allows selecting multiple objects
- Transformations maintain object constraints

**Dependencies:** 2.1 through 2.10

---

### 2.12 Implement Text and Label Tool

**Description:** Create the tool for adding text and labels to the construction.

**Subtasks:**
1. Implement `TextTool` class
2. Add text creation and editing
3. Implement object labeling functionality
4. Add text formatting options
5. Implement automatic label positioning

**Acceptance Criteria:**
- Text can be added to the construction
- Objects can be labeled
- Text can be formatted (font, size, color)
- Labels automatically position relative to objects

**Dependencies:** 2.1

---

### 2.13 Test and Refine Basic Tools

**Description:** Perform comprehensive testing and refinement of all basic tools.

**Subtasks:**
1. Test each tool individually
2. Test interactions between tools
3. Verify constraint maintenance
4. Optimize tool performance
5. Refine user interaction based on testing

**Acceptance Criteria:**
- All tools function correctly individually
- Tools work together without conflicts
- Constraints are properly maintained
- Tools perform efficiently
- User interaction is smooth and intuitive
- Must attain 100% coverage to ensure a firm basis

**Dependencies:** 2.1 through 2.12

## Next Chapter

Once the basic geometric tools are implemented, proceed to [Chapter 3: Sacred Geometry Specialized Tools](03_sacred_geometry_tools.md).
