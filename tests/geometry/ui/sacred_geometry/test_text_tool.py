"""Tests for the Text Tool."""

import unittest
from unittest.mock import MagicMock, patch
import sys
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

# Create a QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, Circle, Text, Style
from geometry.ui.sacred_geometry.tools import TextTool, ToolState


class TestTextTool(unittest.TestCase):
    """Tests for the TextTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = TextTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool._complete_operation = MagicMock()
        self.tool._init_tool()

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.tool.name, "Text")
        self.assertEqual(self.tool.icon_name, "text")
        self.assertEqual(self.tool.mode, self.tool.MODE_FREE_TEXT)
        self.assertEqual(self.tool.font_family, "Arial")
        self.assertEqual(self.tool.font_size, 12.0)
        self.assertEqual(self.tool.font_style, 0)
        self.assertEqual(self.tool.text_color, QColor(0, 0, 0))
        self.assertTrue(self.tool.auto_position)

    def test_create_text_style(self):
        """Test creating text style."""
        # Set custom style properties
        self.tool.font_family = "Times New Roman"
        self.tool.font_size = 14.0
        self.tool.font_style = 1  # Bold
        self.tool.text_color = QColor(255, 0, 0)  # Red

        # Create style
        style = self.tool._create_text_style()

        # Check style properties
        self.assertEqual(style.font_family, "Times New Roman")
        self.assertEqual(style.font_size, 14.0)
        self.assertEqual(style.font_style, 1)
        self.assertEqual(style.stroke_color, QColor(255, 0, 0))

    @patch('geometry.ui.sacred_geometry.tools.TextDialog')
    def test_free_text_mode(self, mock_text_dialog):
        """Test creating free text."""
        # Mock the TextDialog
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec.return_value = True  # Dialog accepted
        mock_dialog_instance.get_text.return_value = "Test Text"
        mock_dialog_instance.get_font_family.return_value = "Arial"
        mock_dialog_instance.get_font_size.return_value = 12.0
        mock_dialog_instance.get_font_style.return_value = 0
        mock_dialog_instance.get_color.return_value = QColor(0, 0, 0)
        mock_dialog_instance.get_auto_position.return_value = True
        mock_text_dialog.return_value = mock_dialog_instance

        # Mock the _create_object method
        self.tool._create_object = MagicMock(return_value=Text())

        # Set the mode to free text
        self.tool.mode = self.tool.MODE_FREE_TEXT

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Call mouse_press to create text
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that TextDialog was created with correct parameters
        mock_text_dialog.assert_called_once()

        # Check that dialog.exec was called
        mock_dialog_instance.exec.assert_called_once()

        # Check that _create_object was called with the correct parameters
        self.tool._create_object.assert_called_once()
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(args[0], 'text')
        self.assertEqual(kwargs['x'], 100)
        self.assertEqual(kwargs['y'], 100)
        self.assertEqual(kwargs['text'], "Test Text")

        # Check that _complete_operation was called
        self.tool._complete_operation.assert_called_once()

    @patch('geometry.ui.sacred_geometry.tools.TextDialog')
    def test_label_object_mode(self, mock_text_dialog):
        """Test labeling an object."""
        # Mock the TextDialog
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec.return_value = True  # Dialog accepted
        mock_dialog_instance.get_text.return_value = "Object Label"
        mock_dialog_instance.get_font_family.return_value = "Arial"
        mock_dialog_instance.get_font_size.return_value = 12.0
        mock_dialog_instance.get_font_style.return_value = 0
        mock_dialog_instance.get_color.return_value = QColor(0, 0, 0)
        mock_dialog_instance.get_auto_position.return_value = True
        mock_text_dialog.return_value = mock_dialog_instance

        # Create a mock object
        mock_obj = MagicMock(spec=Point)
        mock_obj.x = 50
        mock_obj.y = 50

        # Mock the canvas.get_object_at method to return our mock object
        self.tool.canvas.get_object_at.return_value = mock_obj

        # Mock the _create_object method
        mock_text = MagicMock(spec=Text)
        self.tool._create_object = MagicMock(return_value=mock_text)

        # Set the mode to label object
        self.tool.mode = self.tool.MODE_LABEL_OBJECT

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Call mouse_press to create label
        self.tool.mouse_press(event, QPointF(50, 50))

        # Check that TextDialog was created with correct parameters
        mock_text_dialog.assert_called_once()

        # Check that dialog.exec was called
        mock_dialog_instance.exec.assert_called_once()

        # Check that _create_object was called with the correct parameters
        self.tool._create_object.assert_called_once()
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(args[0], 'text')
        self.assertEqual(kwargs['text'], "Object Label")
        self.assertEqual(kwargs['target_object'], mock_obj)
        self.assertEqual(kwargs['auto_position'], True)

        # Check that update_position_from_target was called
        mock_text.update_position_from_target.assert_called_once()

        # Check that _complete_operation was called
        self.tool._complete_operation.assert_called_once()

    def test_set_mode(self):
        """Test setting the tool mode."""
        # Set the mode to label object
        self.tool.set_mode(self.tool.MODE_LABEL_OBJECT)

        # Check that the mode was set
        self.assertEqual(self.tool.mode, self.tool.MODE_LABEL_OBJECT)

        # Set the mode back to free text
        self.tool.set_mode(self.tool.MODE_FREE_TEXT)

        # Check that the mode was set
        self.assertEqual(self.tool.mode, self.tool.MODE_FREE_TEXT)

    def test_set_font_properties(self):
        """Test setting font properties."""
        # Set font family
        self.tool.set_font_family("Helvetica")
        self.assertEqual(self.tool.font_family, "Helvetica")

        # Set font size
        self.tool.set_font_size(16.0)
        self.assertEqual(self.tool.font_size, 16.0)

        # Set font style
        self.tool.set_font_style(2)  # Italic
        self.assertEqual(self.tool.font_style, 2)

        # Set text color
        self.tool.set_text_color(QColor(0, 0, 255))  # Blue
        self.assertEqual(self.tool.text_color, QColor(0, 0, 255))

        # Set auto position
        self.tool.set_auto_position(False)
        self.assertFalse(self.tool.auto_position)


if __name__ == '__main__':
    unittest.main()
