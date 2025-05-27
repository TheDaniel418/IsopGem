# Stonehenge Eclipse Predictor: Project Plan

## Project Objective:

Develop an interactive window within the IsopGem application to simulate Fred Hoyle's theory of Stonehenge as an eclipse prediction device. The simulation will visually represent the 56 Aubrey Holes and marker movements, indicate potential eclipse events, and integrate with `shared/ui/window_management.py`. It will also explore options for leveraging `skyfield` or `Swiss Ephemeris` for enhanced accuracy or initialization.

## I. Core Components & Data Structures (Logic Engine - Python):

1.  **`TheCircle`**:
    *   Manages 56 discrete, indexed positions (0-55).
2.  **`Marker` Class**:
    *   Attributes: `name` (S, M, N, N'), `current_position` (0-55).
    *   Methods for movement specific to each marker type based on Hoyle's rules.
3.  **`TimeState`**:
    *   Variables: `current_day`, `current_year`, `day_within_13_day_cycle` (0-12), `day_within_year_cycle` (0-363, assuming Hoyle's 364-day year for model simplicity).
4.  **`SimulationEngine`**:
    *   Main simulation loop (advances day-by-day).
    *   Orchestrates marker movements by calling their respective methods.
    *   Manages `TimeState` updates.
5.  **`EclipseDetector`**:
    *   Implements Hoyle's conditions for solar and lunar eclipses based on marker proximity (S, M, N/N').
    *   `proximity_threshold` (e.g., 0 or 1 hole difference).
6.  **`RecalibrationLogic` (Optional - Phase 4)**:
    *   Functions for simulated recalibration of Moon and Sun markers.
7.  **`EphemerisInterface` (Optional - Phase 5)**:
    *   Module to interact with `skyfield`.
    *   **Initial Scope**: Primarily for setting initial marker positions based on a user-provided date of a known historical eclipse.
    *   **Potential Future Scope**: Validating Hoyle's model predictions.

## II. UI Components (PyQt6):

1.  **`StonehengePredictorWindow(QMainWindow)`**:
    *   Main window for the simulation. Managed by `shared/ui/window_management.py`.
    *   Title: "Circle of 56: Stonehenge Eclipse Predictor".
2.  **`CircleViewWidget(QWidget)`**:
    *   Visual representation of the 56 Aubrey Holes and markers.
    *   Updates dynamically.
3.  **`ControlsPanelWidget(QWidget)`**:
    *   Buttons: "Start", "Stop", "Step Day", "Reset Simulation".
    *   Input for simulation speed.
    *   Display for `current_day` and `current_year`.
    *   (Phase 5) Input field for a date for ephemeris-assisted initialization.
4.  **`EclipseLogViewWidget(QTextBrowser or QTableView)`**:
    *   Displays a log of predicted eclipses.
5.  **Integration with Astrology Tab**:
    *   New `QPushButton` ("Circle of 56") on the Astrology tab.
    *   Button click uses `shared/ui/window_management.py` to open/focus the window.

## III. Initialization Logic:

1.  **Default Start**: Markers at predefined positions (e.g., M=0, S=28, N=0, N'=28). Time: Day 1, Year 1.
2.  **Ephemeris-Assisted Start (Phase 5)**:
    *   User inputs a historical date.
    *   `EphemerisInterface` uses `skyfield` to determine Sun, Moon, and Lunar Ascending Node longitudes.
    *   Translate these to the nearest positions (0-55) for S, M, N markers. N' opposite N. Mapping: ~6.43 degrees per hole.

## IV. Simulation Loop & Movement Rules:

*   Daily increment of time and cycle counters.
*   Moon Marker (M): +2 positions daily (anticlockwise).
*   Sun Marker (S): +2 positions every 13 days (anticlockwise).
*   Node Markers (N, N'): -3 positions yearly (clockwise), N' maintained opposite N.

## V. Eclipse Detection Logic:

*   Solar Eclipse: New Moon (M ~ S) AND Moon near a Node (M ~ N or M ~ N').
*   Lunar Eclipse: Full Moon (M ~ S+28) AND Moon near a Node (M ~ N or M ~ N').

## VI. Visualization & Interaction:

*   Clear visuals for markers.
*   Smooth dynamic updates.
*   Responsive controls.
*   Visual feedback for eclipse events.

## VII. Output:

*   Live log in `EclipseLogViewWidget`.
*   Option to save log to file.

## VIII. Implementation Strategy (Phased):

1.  **Phase 1: Core Logic & Basic Window Structure**:
    *   Implement `TheCircle`, `Marker`, `TimeState`, `SimulationEngine` (console testing).
    *   Implement `EclipseDetector` (console testing).
    *   Create `StonehengePredictorWindow` skeleton.
    *   Add "Circle of 56" button to Astrology Tab, integrate with `window_management.py`.
    *   Unit tests for core logic.
2.  **Phase 2: Visualization & Basic Interactivity**:
    *   Develop `CircleViewWidget` for dynamic marker display.
    *   Connect `SimulationEngine` to `CircleViewWidget`.
    *   Implement "Step Day" button, time display.
    *   Implement `EclipseLogViewWidget` and connect `EclipseDetector`.
3.  **Phase 3: Full Controls & UI Polish**:
    *   Implement "Start", "Stop", "Reset", speed controls.
    *   Refine visuals, eclipse event highlighting.
4.  **Phase 4: Recalibration Logic (Optional)**:
    *   Implement simpler recalibration rules for Moon/Sun markers.
5.  **Phase 5: Ephemeris Integration (`skyfield`)**:
    *   Develop `EphemerisInterface` for initial marker setup from a date.
    *   Add UI for date input.
    *   (Optional) Add "Reality Check" feature comparing Hoyle's predictions to `skyfield`.

## IX. Key Considerations & Decisions:

*   **Ephemeris Role**:
    *   **Initial**: Focus on accurate *initial positions* from `skyfield`.
    *   **Future**: Consider validation of predictions.
*   **Year Length in Model**: Use Hoyle's 364-day year for core mechanics.
*   **Coordinate Systems & Translation**: Clearly define mapping from 0-360° celestial longitudes to 0-55 hole positions.
*   **User Experience**: Distinguish Hoyle's model from ephemeris data.

## X. Architectural Alignment (5-Pillar Structure):

This feature will be integrated into the existing `astrology` module, adhering to the project's 5-pillar architecture. If the feature grows substantially, it could be promoted to its own top-level feature module following the same architectural pattern.

1.  **`astrology/models/`**:
    *   `stonehenge_marker.py`: Defines the `Marker` class (attributes: S, M, N, N'; `current_position`).
    *   `stonehenge_time_state.py`: Defines the `TimeState` class/dataclass (attributes: `current_day`, `current_year`, cycle counters).
    *   `stonehenge_circle_config.py`: May hold constants for `TheCircle` (e.g., `NUM_HOLES = 56`) or `TheCircle` representation itself if it primarily serves as a configuration/data holder.

2.  **`astrology/repositories/`**:
    *   `skyfield_ephemeris_repository.py` (Required for Phase 5 `EphemerisInterface`):
        *   Responsible for all interactions with the `skyfield` library.
        *   Provides methods to fetch celestial body positions for a given date, abstracting direct `skyfield` calls.
        *   The `stonehenge_simulation_service` will consume this repository for ephemeris-assisted initialization.

3.  **`astrology/services/`**:
    *   `stonehenge_simulation_service.py`:
        *   Contains the `SimulationEngine` class: Manages the simulation loop, marker movements (by interacting with `Marker` objects), and `TimeState`.
        *   Houses the `EclipseDetector` logic (either within `SimulationEngine` or as a closely related component).
        *   Manages `RecalibrationLogic` (Phase 4).

4.  **`astrology/ui/`**:
    *   A new subdirectory will be created, e.g., `astrology/ui/widgets/stonehenge_predictor/`.
    *   `stonehenge_predictor_window.py`: Defines `StonehengePredictorWindow(QMainWindow)`.
    *   `circle_view_widget.py`: Defines `CircleViewWidget(QWidget)` for visualization.
    *   `controls_panel_widget.py`: Defines `ControlsPanelWidget(QWidget)` for user interaction.
    *   `eclipse_log_view_widget.py`: Defines `EclipseLogViewWidget` for displaying predictions.
    *   The "Circle of 56" `QPushButton` will be added to the relevant existing UI file for the Astrology tab (e.g., `astrology/ui/panels/astrology_panel.py`), which will use `shared/ui/window_management.py` to launch the `StonehengePredictorWindow`.

5.  **`astrology/utils/`**:
    *   `stonehenge_helper.py`:
        *   Utility functions for translating celestial longitudes (0-360°) from `skyfield` to Hoyle's 56 hole positions (0-55) and vice-versa.
        *   May also store constants specific to the Hoyle model if not housed in `astrology/models/stonehenge_circle_config.py`.
