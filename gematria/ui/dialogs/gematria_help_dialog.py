"""Gematria Help Dialog.

This module provides a dialog with detailed explanations of gematria calculation methods.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class GematriaHelpDialog(QDialog):
    """Dialog showing explanations of gematria calculation methods."""

    def __init__(self, parent=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Methods Reference")
        self.resize(800, 600)

        # Make the dialog non-modal
        self.setModal(False)

        self._init_ui()

    def _init_ui(self):
        """Set up the dialog UI."""
        # Main layout
        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()

        # Create tabs
        hebrew_tab = self._create_hebrew_tab()
        greek_tab = self._create_greek_tab()
        english_tab = self._create_english_tab()
        about_tab = self._create_about_tab()

        # Add tabs to widget
        tab_widget.addTab(hebrew_tab, "Hebrew Gematria")
        tab_widget.addTab(greek_tab, "Greek Isopsophy")
        tab_widget.addTab(english_tab, "English TQ")
        tab_widget.addTab(about_tab, "About Gematria")

        layout.addWidget(tab_widget)

        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(
            self.hide
        )  # Hide instead of accept for non-modal behavior
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _create_hebrew_tab(self):
        """Create the Hebrew gematria methods tab.

        Returns:
            QWidget: The tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Title
        title = QLabel("Hebrew Gematria Methods")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # Hebrew methods
        hebrew_methods = [
            {
                "name": "Mispar Hechrachi (מספר הכרחי)",
                "description": "The standard gematria method. Each letter is assigned its standard value.",
                "examples": "א=1, ב=2, ג=3, י=10, כ=20, ק=100",
                "notes": "This is the most common method used in traditional gematria."
            },
            {
                "name": "Mispar Siduri (מספר סידורי)",
                "description": "Ordinal value. Each letter is assigned a value based on its position in the alphabet.",
                "examples": "א=1, ב=2, ג=3, י=10, כ=11, ל=12",
                "notes": "This method emphasizes the sequential nature of the alphabet."
            },
            # Deprecated methods removed
            {
                "name": "Albam (אלבם)",
                "description": "A substitution cipher where the first letter is exchanged with the 12th, the 2nd with the 13th, etc.",
                "examples": "א→ל, ב→מ, ג→נ, ד→ס",
                "notes": "After substitution, the standard gematria value is calculated."
            },
            {
                "name": "Atbash (אתבש)",
                "description": "A substitution cipher where the alphabet is reversed, so the first letter is exchanged with the last, the second with the second-to-last, etc.",
                "examples": "א→ת, ב→ש, ג→ר, ד→ק",
                "notes": "After substitution, the standard gematria value is calculated."
            },
            {
                "name": "Mispar Gadol (מספר גדול)",
                "description": "Large value gematria. Like standard gematria but final forms of letters have increased values.",
                "examples": "ך=500, ם=600, ן=700, ף=800, ץ=900",
                "notes": "This extends the range of possible values."
            },
            {
                "name": "Mispar Boneh (מספר בונה)",
                "description": "Building value. Each letter adds to a cumulative value as the word is spelled.",
                "examples": "אב = א(1) + (א+ב)(1+2) = 1 + 3 = 4",
                "notes": "This method emphasizes the progressive building of words."
            },
            {
                "name": "Mispar Kidmi (מספר קדמי)",
                "description": "Triangular value. Each letter's value is the sum of all letters up to it in the alphabet.",
                "examples": "א=1, ב=1+2=3, ג=1+2+3=6, ד=1+2+3+4=10",
                "notes": "This creates triangular numbers for each letter."
            },
            {
                "name": "Mispar Perati (מספר פרטי)",
                "description": "Individual Square value. Each letter's value is squared before summing.",
                "examples": "א=1², ב=2², ג=3², י=10²",
                "notes": "This amplifies the contribution of larger value letters."
            },
            {
                "name": "Mispar Shemi (מספר שמי)",
                "description": "Full Name value. The value of the fully spelled-out name of each letter.",
                "examples": "א=אלף(111), ב=בית(412), ג=גימל(83)",
                "notes": "This incorporates the hidden meanings in letter names."
            },
            {
                "name": "Mispar Musafi (מספר מוסיפי)",
                "description": "Additive value. The standard value plus the number of letters.",
                "examples": "'אב' = 3 (standard) + 2 (letters) = 5",
                "notes": "This incorporates the length of the word into its value."
            }
        ]

        for method in hebrew_methods:
            self._add_detailed_method(content_layout, method)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        return tab

    def _create_greek_tab(self):
        """Create the Greek isopsophy methods tab.

        Returns:
            QWidget: The tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Title
        title = QLabel("Greek Isopsophy Methods")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # Greek methods
        greek_methods = [
            {
                "name": "Greek Isopsophy (Αριθμός Ισόψηφος)",
                "description": "The standard Greek numerological system. Each letter has a specific numerical value.",
                "examples": "α=1, β=2, γ=3, δ=4, ι=10, κ=20, ρ=100",
                "notes": "Most common method in Greek gematria."
            },
            {
                "name": "Greek Ordinal (Αριθμός Τακτικός)",
                "description": "Each letter is assigned a value based on its position in the alphabet.",
                "examples": "α=1, β=2, γ=3, ..., ω=24",
                "notes": "Similar to the Hebrew Mispar Siduri."
            },
            {
                "name": "Greek Squared (Αριθμός Τετράγωνος)",
                "description": "The square of each letter's standard value.",
                "examples": "α=1², β=2², γ=3²...",
                "notes": "Multiplies each letter value by itself before summing."
            },
            {
                "name": "Greek Reversal (Αριθμός Αντίστροφος)",
                "description": "Letter values are reversed compared to standard (α=800, ω=1).",
                "examples": "α=800, β=700, γ=600...",
                "notes": "Equivalent to the Hebrew Mispar Meshupach."
            },
            {
                "name": "Greek Alpha-Mu (Αριθμός Άλφα-Μυ)",
                "description": "Letter substitution cipher (α↔μ, β↔ν, etc.).",
                "examples": "α→μ=40, β→ν=50...",
                "notes": "Greek equivalent of Hebrew Albam."
            },
            {
                "name": "Greek Alpha-Omega (Αριθμός Άλφα-Ωμέγα)",
                "description": "Letter substitution cipher (α↔ω, β↔ψ, etc.).",
                "examples": "α→ω=800, β→ψ=700...",
                "notes": "Greek equivalent of Hebrew Atbash."
            },
            {
                "name": "Greek Building (Αριθμός Οικοδομικός)",
                "description": "Cumulative sum of letter values as the word is spelled out.",
                "examples": "θ 'theta' = θ + η + τ + α = 9 + 8 + 300 + 1 = 318",
                "notes": "Equivalent to Hebrew Mispar Boneh."
            },
            {
                "name": "Greek Triangular (Αριθμός Τριγωνικός)",
                "description": "The sum of all letters up to that letter in the alphabet.",
                "examples": "α=1, β=1+2=3, γ=1+2+3=6...",
                "notes": "Similar to Hebrew Mispar Kidmi."
            },
            {
                "name": "Greek Hidden (Αριθμός Κρυπτός)",
                "description": "The value of the letter name minus the letter itself.",
                "examples": "α = 'alpha' - 'α' = 532 - 1 = 531",
                "notes": "Reveals hidden values within letter names."
            },
            {
                "name": "Greek Full Name (Αριθμός Ονόματος)",
                "description": "The value of the full letter name.",
                "examples": "α = 'alpha' = 532",
                "notes": "Equivalent to Hebrew Mispar Shemi."
            },
            {
                "name": "Greek Additive (Αριθμός Προσθετικός)",
                "description": "Adds the number of letters to the value.",
                "examples": "θεος = 9+5+70+200+4(letters) = 284+4 = 288",
                "notes": "Equivalent to Hebrew Mispar Musafi."
            },
        ]

        for method in greek_methods:
            self._add_detailed_method(content_layout, method)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        return tab

    def _create_english_tab(self):
        """Create the English TQ methods tab.

        Returns:
            QWidget: The tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Title
        title = QLabel("Trigrammaton Qabalah (TQ)")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # Add English method
        english_method = {
            "name": "TQ English",
            "transliteration": "Trigrammaton Qabalah",
            "meaning": "Qabalah of the Book of Trigrams",
            "description": (
                "A modern English alphanumeric system developed by R.L. Gillis based on Aleister Crowley's "
                "Liber Trigrammaton (Liber 27). The system assigns values to the English alphabet (A=1 through Z=26) "
                "by corresponding them to the 27 trigrams of Liber Trigrammaton. Unlike traditional Hebrew or Greek "
                "systems, TQ was specifically designed for English language analysis within the context of Thelemic "
                "mysticism and provides a framework for English gematria analysis of Crowley's works."
            ),
            "example": "LOVE = L(12) + O(15) + V(22) + E(5) = 54",
            "chart": "A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12, M=13, N=14, O=15, P=16, Q=17, R=18, S=19, T=20, U=21, V=22, W=23, X=24, Y=25, Z=26",
        }

        self._add_detailed_method(content_layout, english_method)

        # Additional context about TQ
        context_text = QTextBrowser()
        context_text.setOpenExternalLinks(True)
        context_text.setHtml(
            """
        <h3>Trigrammaton Qabalah Background</h3>
        <p>The Trigrammaton Qabalah (TQ) is a modern qabalistic system developed by R. Leo Gillis (Rama L. Gillis).
        It is based on Aleister Crowley's 1907 work "Liber Trigrammaton" (Liber 27), which presents a cosmology
        based on 27 three-line figures called trigrams. Crowley called it "the ultimate foundation of the highest
        theoretical qabalah".</p>

        <h3>Trigrams and Base-3 System</h3>
        <p>The system uses 27 trigrams that can be assigned numerical values in base-3 notation, allowing the trigrams
        to represent all numbers from 0 to 26. Gillis mapped the 26 letters of the English alphabet to these trigrams,
        creating a system specifically designed for English language analysis.</p>

        <p>The trigrams are organized as follows:</p>
        <ul>
            <li>Each trigram consists of three lines</li>
            <li>Each line can be in one of three states: yang (firm line), yin (broken line), or neutral (absent)</li>
            <li>The 27 trigrams represent a complete cycle of creation according to Crowley's cosmology</li>
            <li>The trigrams can be arranged on a "Cube of Space" representing cosmic geometry</li>
        </ul>

        <h3>Philosophy and Design Principles</h3>
        <p>The T.Q. system attributes Hermetic categories, letters of the English alphabet, and Tarot trumps to the trigrams.
        This creates a comprehensive system for English gematria that has deep connections to Thelemic philosophy.</p>

        <p>Key aspects of the system include:</p>
        <ul>
            <li><b>English-Centric:</b> Specifically designed for working with English text</li>
            <li><b>Base-3 Mathematics:</b> Uses ternary (base-3) system instead of traditional decimal counting</li>
            <li><b>Geometric Foundation:</b> Built around sacred geometry and the "Cube of Space"</li>
            <li><b>Thelemic Framework:</b> Provides insights into Crowley's Book of the Law (Liber AL vel Legis)</li>
            <li><b>Cipher Decoding:</b> Claimed to unlock various ciphers in Crowley's works</li>
        </ul>

        <h3>Applications of TQ</h3>
        <p>According to Gillis, the Trigrammaton Qabalah serves multiple purposes:</p>
        <ul>
            <li>Analyzing Thelemic texts, particularly Crowley's Book of the Law</li>
            <li>Decoding the "cipher of verse II:76" in Liber AL</li>
            <li>Exploring connections between English words through gematria</li>
            <li>Integrating with I Ching and other divination systems</li>
            <li>Understanding sacred geometry and the Cube of Space</li>
            <li>Working with magic squares and other mathematical structures</li>
        </ul>

        <h3>Publications and Development</h3>
        <p>Gillis published his research in "The Book of Mutations" (originally in 1996, revised in 2002),
        which represents over a dozen years of research into the system. The work includes extensive charts,
        hexagram graphics, and detailed explanations of the English Qabalah system and its applications.</p>

        <h3>TQ in Modern Practice</h3>
        <p>Today, TQ continues to be used by practitioners of Thelema and others interested in
        English-language mystical systems. It provides a bridge between traditional qabalistic
        methods and modern English-language magical practices, particularly for those working
        within the Thelemic tradition.</p>
        """
        )

        content_layout.addWidget(context_text)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        return tab

    def _create_about_tab(self):
        """Create the About gematria tab.

        Returns:
            QWidget: The tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Title
        title = QLabel("About Gematria and Isopsophy")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # About text
        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml(
            """
        <h3>What is Gematria?</h3>
        <p>Gematria is a system of assigning numerical values to letters and words. It has roots in ancient Hebrew traditions and has been used for biblical interpretation, mysticism, and analysis of sacred texts.</p>

        <h3>What is Isopsophy?</h3>
        <p>Isopsophy is the Greek equivalent of gematria. It assigns numerical values to Greek letters and was used in ancient Greek texts, poetry, and religious writings.</p>

        <h3>Why Use These Methods?</h3>
        <p>These calculation methods provide tools for textual analysis, finding connections between words and concepts, and exploring patterns in sacred texts. They have been used by scholars, mystics, and religious traditions for centuries.</p>

        <h3>Historical Context</h3>
        <p>The practice of assigning numerical values to letters dates back thousands of years. In Hebrew tradition, gematria became an important tool in Kabbalistic study, while in Greek culture, isopsophy was used in various contexts including poetry, philosophy, and religious inscriptions.</p>

        <h3>Modern Applications</h3>
        <p>Today, these methods continue to be used for textual analysis, comparative studies, and as tools for deeper understanding of ancient texts. They provide a unique perspective on the relationship between language and number.</p>
        """
        )

        content_layout.addWidget(about_text)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        return tab

    def _add_method_description(self, layout, name, description):
        """Add a simple method description to the layout.

        Args:
            layout: The layout to add to
            name: Method name
            description: Method description
        """
        # Method name
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(name_label)

        # Method description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-left: 20px; margin-bottom: 15px;")
        layout.addWidget(desc_label)

    def _add_detailed_method(self, layout, method_data):
        """Add a detailed method description with all components.

        Args:
            layout: The layout to add to
            method_data: Dictionary with method details
        """
        # Container for the method
        container = QWidget()
        method_layout = QVBoxLayout(container)
        method_layout.setContentsMargins(0, 10, 0, 20)

        # Method name with transliteration
        name_label = QLabel(f"{method_data['name']} ({method_data['transliteration']})")
        name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        method_layout.addWidget(name_label)

        # Meaning
        meaning_label = QLabel(f"<b>Meaning:</b> {method_data['meaning']}")
        meaning_label.setStyleSheet("margin-left: 20px;")
        method_layout.addWidget(meaning_label)

        # Description
        desc_label = QLabel(method_data["description"])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-left: 20px; margin-top: 5px;")
        method_layout.addWidget(desc_label)

        # Example
        example_label = QLabel(f"<b>Example:</b> {method_data['example']}")
        example_label.setWordWrap(True)
        example_label.setStyleSheet("margin-left: 20px; margin-top: 10px;")
        method_layout.addWidget(example_label)

        # Chart of values
        chart_label = QLabel(f"<b>Letter Values:</b> {method_data['chart']}")
        chart_label.setWordWrap(True)
        chart_label.setStyleSheet("margin-left: 20px; margin-top: 5px;")
        method_layout.addWidget(chart_label)

        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #bdc3c7; margin-top: 10px;")
        method_layout.addWidget(line)

        layout.addWidget(container)

    def closeEvent(self, event):
        """Override close event to hide instead of close for non-modal behavior.

        Args:
            event: Close event
        """
        # Hide the dialog instead of closing it
        self.hide()
        event.ignore()  # Prevent the dialog from being closed
