"""Gematria Help Dialog.

This module provides a dialog with detailed explanations of gematria calculation methods.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QScrollArea,
    QLabel,
    QPushButton,
    QTextBrowser,
    QFrame,
)
from PyQt6.QtGui import QFont


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

        # Add method descriptions
        hebrew_methods = [
            {
                "name": "Mispar Hechrachi (מספר הכרחי)",
                "transliteration": "Standard Value",
                "meaning": "Essential or Standard Number",
                "description": (
                    "The most common method of gematria. Each letter is assigned its basic "
                    "numerical value. Alef=1, Bet=2, and so on, with special values for tens "
                    "and hundreds. Final forms (sofits) of letters have the same value as their regular forms."
                ),
                "example": "אמת (truth) = א(1) + מ(40) + ת(400) = 441",
                "chart": "א=1, ב=2, ג=3, ד=4, ה=5, ו=6, ז=7, ח=8, ט=9, י=10, כ=20, ל=30, מ=40, נ=50, ס=60, ע=70, פ=80, צ=90, ק=100, ר=200, ש=300, ת=400",
            },
            {
                "name": "Mispar Gadol (מספר גדול)",
                "transliteration": "Large Value",
                "meaning": "Large Number",
                "description": (
                    "This method assigns larger values to the final forms (sofits) of letters. "
                    "While regular letters maintain their standard values, the five final forms "
                    "(Kaf, Mem, Nun, Peh, Tzadi) are assigned values in the hundreds."
                ),
                "example": "שלום (peace) with final Mem = ש(300) + ל(30) + ו(6) + ם(600) = 936",
                "chart": "Standard letters same as Mispar Hechrachi, plus: ך=500, ם=600, ן=700, ף=800, ץ=900",
            },
            {
                "name": "Mispar Katan (מספר קטן)",
                "transliteration": "Small Value",
                "meaning": "Small Number",
                "description": (
                    "Reduces all letter values to single digits. Letters with values 1-9 remain the same, "
                    "but letters with values 10-400 are reduced to their last digit. This method reveals "
                    "connections between words that might be hidden in the standard value."
                ),
                "example": "אמת (truth) = א(1) + מ(4) + ת(4) = 9",
                "chart": "א=1, ב=2, ג=3, ד=4, ה=5, ו=6, ז=7, ח=8, ט=9, י=1, כ=2, ל=3, מ=4, נ=5, ס=6, ע=7, פ=8, צ=9, ק=1, ר=2, ש=3, ת=4",
            },
            {
                "name": "Mispar Siduri (מספר סידורי)",
                "transliteration": "Ordinal Value",
                "meaning": "Ordinal Number",
                "description": (
                    "Values letters based on their position in the Hebrew alphabet. "
                    "Each letter is assigned a value based on its sequential position, from 1 to 22. "
                    "Final forms of letters have the same value as their regular forms."
                ),
                "example": "אמת (truth) = א(1) + מ(13) + ת(22) = 36",
                "chart": "א=1, ב=2, ג=3, ד=4, ה=5, ו=6, ז=7, ח=8, ט=9, י=10, כ=11, ל=12, מ=13, נ=14, ס=15, ע=16, פ=17, צ=18, ק=19, ר=20, ש=21, ת=22",
            },
            {
                "name": "Mispar Katan Mispari (מספר קטן מספרי)",
                "transliteration": "Integral Reduced Value",
                "meaning": "Small Integral Number",
                "description": (
                    "This method first calculates the standard value of a word, "
                    "then reduces the sum to a single digit by adding the digits together. "
                    "This process continues until a single digit is reached."
                ),
                "example": "אמת (truth) = א(1) + מ(40) + ת(400) = 441 → 4+4+1 = 9",
                "chart": "Uses standard values, then reduces the final sum",
            },
            {
                "name": "Mispar Boneh (מספר בונה)",
                "transliteration": "Building Value",
                "meaning": "Builder Number",
                "description": (
                    "Each letter's value is the square of its standard value. "
                    "The method reveals the 'building' or constructive potential of the letters, "
                    "highlighting the internal dynamics and energy within words."
                ),
                "example": "אב (father) = א(1²=1) + ב(2²=4) = 5",
                "chart": "Each letter's standard value is squared",
            },
            {
                "name": "Mispar Kidmi (מספר קדמי)",
                "transliteration": "Triangular Value",
                "meaning": "Triangular Number",
                "description": (
                    "Each letter's value is the sum of all numbers from 1 to its standard value. "
                    "This method reveals the cumulative energy of each letter, showing how "
                    "letters build upon previous values in a triangular pattern."
                ),
                "example": "א (alef) = 1+0 = 1, ב (bet) = 1+2 = 3, ג (gimel) = 1+2+3 = 6",
                "chart": "א=1, ב=3, ג=6, ד=10, ה=15...",
            },
            {
                "name": "Mispar Perati (מספר פרטי)",
                "transliteration": "Individual Square Value",
                "meaning": "Individual Number",
                "description": (
                    "Each letter is calculated as the square of its standard value, "
                    "and then these squares are summed. This method amplifies the "
                    "individual contribution of each letter within a word."
                ),
                "example": "אב (father) = א(1²) + ב(2²) = 1 + 4 = 5",
                "chart": "Each letter's standard value is squared then summed",
            },
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

        # Add method descriptions
        greek_methods = [
            {
                "name": "Greek Isopsophy (Ισοψηφία)",
                "transliteration": "Standard Value",
                "meaning": "Equal in numerical value",
                "description": (
                    "The standard method of Greek isopsophy. Each letter is assigned its traditional "
                    "numerical value. Alpha=1, Beta=2, and so on, with special values for tens "
                    "and hundreds. This is the Greek equivalent of Hebrew Mispar Hechrachi."
                ),
                "example": "λόγος (logos/word) = λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373",
                "chart": "α=1, β=2, γ=3, δ=4, ε=5, ζ=7, η=8, θ=9, ι=10, κ=20, λ=30, μ=40, ν=50, ξ=60, ο=70, π=80, ρ=100, σ=200, τ=300, υ=400, φ=500, χ=600, ψ=700, ω=800",
            },
            {
                "name": "Greek Ordinal (Τακτική Αξία)",
                "transliteration": "Ordinal Value",
                "meaning": "Sequential Value",
                "description": (
                    "Values letters based on their position in the Greek alphabet. "
                    "Each letter is assigned a value based on its sequential position. "
                    "This is the Greek equivalent of Hebrew Mispar Siduri."
                ),
                "example": "λόγος (logos/word) = λ(11) + ό(15) + γ(3) + ο(15) + ς(18) = 62",
                "chart": "α=1, β=2, γ=3, δ=4, ε=5, ζ=6, η=7, θ=8, ι=9, κ=10, λ=11, μ=12, ν=13, ξ=14, ο=15, π=16, ρ=17, σ=18, τ=19, υ=20, φ=21, χ=22, ψ=23, ω=24",
            },
            {
                "name": "Greek Reduced (Μειωμένη Αξία)",
                "transliteration": "Reduced Value",
                "meaning": "Reduced Number",
                "description": (
                    "Reduces all letter values to single digits. Letters with values 1-9 remain the same, "
                    "but letters with values 10-800 are reduced to their last digit. This is equivalent "
                    "to Hebrew Mispar Katan."
                ),
                "example": "λόγος (logos/word) = λ(3) + ό(7) + γ(3) + ο(7) + ς(2) = 22",
                "chart": "α=1, β=2, γ=3, δ=4, ε=5, ζ=7, η=8, θ=9, ι=1, κ=2, λ=3, μ=4, ν=5, ξ=6, ο=7, π=8, ρ=1, σ=2, τ=3, υ=4, φ=5, χ=6, ψ=7, ω=8",
            },
            {
                "name": "Greek Integral Reduced (Ολοκληρωτικά Μειωμένη)",
                "transliteration": "Integral Reduced Value",
                "meaning": "Fully Reduced Number",
                "description": (
                    "This method first calculates the standard value of a word, "
                    "then reduces the sum to a single digit by adding the digits together. "
                    "This process continues until a single digit is reached. Equivalent to Hebrew "
                    "Mispar Katan Mispari."
                ),
                "example": "λόγος (logos/word) = λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373 → 3+7+3 = 13 → 1+3 = 4",
                "chart": "Uses standard values, then reduces the final sum",
            },
            {
                "name": "Greek Large (Αριθμός Μεγάλος)",
                "transliteration": "Large Value",
                "meaning": "Great Number",
                "description": (
                    "This is a theoretical method that would parallel Hebrew Mispar Gadol, "
                    "but since Greek doesn't have final forms, it uses the same values as "
                    "Standard Greek Isopsophy. Included for consistency with Hebrew methods."
                ),
                "example": "λόγος (logos/word) = λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373",
                "chart": "Same as Greek Isopsophy standard values",
            },
            {
                "name": "Greek Building (Αριθμός Οικοδομικός)",
                "transliteration": "Building Value",
                "meaning": "Building Number",
                "description": (
                    "Each letter's value is the square of its standard value. "
                    "This method, equivalent to Hebrew Mispar Boneh, reveals the 'building' "
                    "or constructive potential of the letters."
                ),
                "example": "αβ (alpha-beta) = α(1²=1) + β(2²=4) = 5",
                "chart": "Each letter's standard value is squared",
            },
            {
                "name": "Greek Triangular (Αριθμός Τριγωνικός)",
                "transliteration": "Triangular Value",
                "meaning": "Triangular Number",
                "description": (
                    "Each letter's value is the sum of all numbers from 1 to its standard value. "
                    "This Greek equivalent of Hebrew Mispar Kidmi reveals the cumulative energy "
                    "of each letter in a triangular pattern."
                ),
                "example": "α (alpha) = 1, β (beta) = 1+2 = 3, γ (gamma) = 1+2+3 = 6",
                "chart": "α=1, β=3, γ=6, δ=10, ε=15...",
            },
            {
                "name": "Greek Individual Square (Αριθμός Ατομικός)",
                "transliteration": "Individual Square Value",
                "meaning": "Individual Number",
                "description": (
                    "Each letter is calculated as the square of its standard value, "
                    "then these squares are summed. This method amplifies the "
                    "individual contribution of each letter within a word. Equivalent to "
                    "Hebrew Mispar Perati."
                ),
                "example": "αβ (alpha-beta) = α(1²) + β(2²) = 1 + 4 = 5",
                "chart": "Each letter's standard value is squared then summed",
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
