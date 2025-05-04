from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from .rich_text_editor_widget import RichTextEditorWidget

class NonModalRTFEditorWindow(QMainWindow):
    """
    @class NonModalRTFEditorWindow
    @description A non-modal version of the RTF Editor Window using RichTextEditorWidget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("RTF Editor")
        self.resize(800, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Use the new rich text editor widget as the central widget
        self.editor_widget = RichTextEditorWidget(self)
        self.setCentralWidget(self.editor_widget) 