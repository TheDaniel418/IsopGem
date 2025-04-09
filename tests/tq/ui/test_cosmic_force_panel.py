"""
Tests for the Cosmic Force Analysis Panel in the TQ pillar.

This file contains tests for verifying the functionality of the
Cosmic Force Analysis Panel, focusing on digit interpretation,
pattern analysis, and UI interactions.
"""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from tq.ui.widgets.cosmic_force_panel import CosmicForceInterpreter, CosmicForceAnalysisPanel


class TestCosmicForceInterpreter:
    """Tests for the CosmicForceInterpreter class."""
    
    def test_interpret_digit(self):
        """Test the digit interpretation functionality."""
        interpreter = CosmicForceInterpreter()
        
        # Test different digit interpretations
        assert "Neutral Force" in interpreter.interpret_digit(0, 0)
        assert "Expansive Force" in interpreter.interpret_digit(1, 0)
        assert "Contractive Force" in interpreter.interpret_digit(2, 0)
        
        # Test positions affect interpretations
        first_pos = interpreter.interpret_digit(1, 0)
        middle_pos = interpreter.interpret_digit(1, 3)
        last_pos = interpreter.interpret_digit(1, 8)
        assert first_pos != middle_pos != last_pos
    
    def test_analyze_ternary(self):
        """Test the ternary number analysis functionality."""
        interpreter = CosmicForceInterpreter()
        
        # Test analysis of simple ternary number
        analysis = interpreter.analyze_ternary([1, 0, 2])
        assert len(analysis) == 3  # One interpretation per digit
        assert "Expansive" in analysis[0]
        assert "Neutral" in analysis[1]
        assert "Contractive" in analysis[2]
        
        # Test analysis of longer ternary number
        analysis = interpreter.analyze_ternary([1, 2, 0, 1, 2])
        assert len(analysis) == 5  # One interpretation per digit
    
    def test_analyze_patterns(self):
        """Test the pattern analysis functionality."""
        interpreter = CosmicForceInterpreter()
        
        # Test pattern analysis
        patterns = interpreter.analyze_patterns([1, 1, 1, 0, 0, 2, 2])
        assert "Expansive" in patterns
        assert "Neutral" in patterns
        assert "Contractive" in patterns
        
        # Test empty pattern
        empty_patterns = interpreter.analyze_patterns([])
        assert "No patterns" in empty_patterns


@pytest.mark.skip(reason="Requires QApplication instance")
class TestCosmicForceAnalysisPanel:
    """Tests for the CosmicForceAnalysisPanel UI component."""
    
    def test_decimal_to_ternary_conversion(self, qtbot):
        """Test decimal to ternary conversion in the panel."""
        # This test would require a QApplication instance
        panel = CosmicForceAnalysisPanel()
        qtbot.addWidget(panel)
        
        # Set decimal input and trigger analysis
        panel.decimal_input.setText("28")
        qtbot.mouseClick(panel.analyze_button, Qt.MouseButton.LeftButton)
        
        # Verify ternary output is correct (28 in decimal = 1001 in ternary)
        assert panel.ternary_display.text() == "1001"
        
        # Verify analysis is generated
        assert panel.interpretation_text.toPlainText() != "" 