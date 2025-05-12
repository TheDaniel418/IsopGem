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

# Import CalculationType to resolve NameError
from gematria.models.calculation_type import CalculationType


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
        coptic_tab = self._create_coptic_tab()
        about_tab = self._create_about_tab()
        arabic_tab = self._create_arabic_tab()

        # Add tabs to widget
        tab_widget.addTab(hebrew_tab, "Hebrew Gematria")
        tab_widget.addTab(greek_tab, "Greek Isopsophy")
        tab_widget.addTab(english_tab, "English TQ")
        tab_widget.addTab(coptic_tab, "Coptic Gematria")
        tab_widget.addTab(arabic_tab, "Arabic Abjad")
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
                "name": "Hebrew Standard Value (Mispar Hechrachi)",
                "description": "The standard gematria method. Each letter is assigned its standard value.",
                "example": "יהוה = י(10) + ה(5) + ו(6) + ה(5) = 26",
                "notes": "This is the most common method used in traditional gematria.",
                "rationale": 'Why: This is the most common and straightforward method. It represents the inherent numerical essence of each letter as established in the Hebrew numeral system. It\'s considered the "necessary" or "absolute" value.\nWhen: Used universally in almost all forms of gematria analysis, from basic word comparisons to complex textual interpretations in Kabbalistic texts like the Zohar, Talmud, and Midrash. It\'s a foundational method for finding equivalencies between words and phrases.',
            },
            {
                "name": "Hebrew Ordinal Value (Mispar Siduri)",
                "description": "Ordinal value. Each letter is assigned a value based on its position in the alphabet.",
                "example": "יהוה = י(10th letter = 10) + ה(5th letter = 5) + ו(6th letter = 6) + ה(5th letter = 5) = 26",
                "notes": "This method emphasizes the sequential nature of the alphabet.",
                "rationale": 'Why: This method considers the sequential position of each letter in the alphabet, highlighting the developmental or progressive aspect of concepts. It can reveal relationships based on the "order" of creation or emanation.\nWhen: Often used to find simpler numerical relationships or to explore themes of sequence, hierarchy, or stages. It\'s sometimes used in conjunction with Standard Value to provide another layer of meaning.',
            },
            {
                "name": "Hebrew Final Letter Values (Mispar Sofit)",  # Corrected from Mispar Sofit/Gadol to match common Gematria_Methods.md keys
                "description": "Large value gematria. Like standard gematria but final forms of letters have increased values.",
                "example": "מלך = מ(40) + ל(30) + ך(final kaf = 500) = 570\nCompared to standard: מלך = מ(40) + ל(30) + כ(20) = 90",
                "notes": "This extends the range of possible values.",
                "rationale": 'Why: The five Hebrew letters that have final forms (Kaf, Mem, Nun, Pe, Tsadi) are given higher values when they appear at the end of a word. This is thought to represent a state of fulfillment, expansion, or a connection to a higher or more revealed plane of existence. The final forms often symbolize the unfolding of potential into actuality.\nWhen: Used specifically when a word contains one of these final letters and the interpreter wishes to explore the "fulfilled" or "expanded" meaning of the word. This method is not always applied; its use depends on the specific interpretative context and the desired depth of analysis. It\'s particularly relevant in Kabbalistic interpretations where the form of the letters carries significant meaning.',
            },
            {
                "name": "Hebrew Small Reduced Value (Mispar Katan)",
                "description": "Reduces each letter's standard value to a single digit by summing its digits (e.g., י (10) -> 1).",
                "example": "אדם = א(1) + ד(4) + ם(40→4) = 9",
                "notes": "Values above 9 are reduced to a single digit (e.g., 40→4, 400→4 by summing digits, e.g. 4+0=4).",
                "rationale": "Why: This method reduces letter values to a single digit (1-9), reflecting the idea of returning to fundamental essences or \"seeds.\" It's based on the principle that all numbers ultimately derive from the first nine digits, representing the Sefirot in their most basic form. This can reveal underlying connections obscured by larger numbers.\nWhen: Used to simplify complex values and find core numerical similarities between words. It's common in meditative practices and when seeking the most essential root of a concept. Often employed when comparing words that have vastly different standard values.",
            },
            {
                "name": "Hebrew Integral Reduced Value (Mispar Mispari)",
                "description": "Sums the digits of each letter's standard value (e.g., ת (400) -> 4+0+0=4), but not iteratively to one digit.",
                "example": "שלום = ש(300→3+0+0=3) + ל(30→3+0=3) + ו(6) + ם(final mem, 600→6+0+0=6 or standard mem 40→4+0=4). Original example used standard mem: ם(40→4+0=4) = 16.",
                "notes": "Sums the digits of each letter's standard value. If a letter's value is a single digit, it's used as is. Final forms' standard values are used (e.g., ם=40).",  # Note adjusted based on example provided by user.
                "rationale": "Why: This method involves summing the digits of each letter's standard value before summing them for the word. It's a deeper form of reduction, aiming to distill the essence of each letter's contribution to the total. It can reveal a more nuanced \"small\" value.\nWhen: Used when a more profound level of reduction than Mispar Katan is desired, focusing on the internal numerical structure of each letter's value. It's less common than Mispar Katan but offers another layer for analysis.",
            },
            {
                "name": "Hebrew Integral Reduced Ordinal Value (Mispar Katan Siduri)",
                "description": "Reduces the ordinal value of letters to their single-digit essence.",
                "example": "אבג = א(1st letter = 1) + ב(2nd letter = 2) + ג(3rd letter = 3) = 6",
                "notes": "Applied to ordinal values.",
                "rationale": "Why: Similar to Mispar Katan, but applied to the ordinal values of the letters. This reduces the sequential position to its single-digit essence, focusing on the fundamental stage or aspect represented by that position.\nWhen: Used when exploring the core meaning of a word based on the simplified positions of its letters in the alphabet. It's a way to combine the principles of ordinal position and numerical reduction.",
            },
            {
                "name": "Hebrew Square Value (Mispar Meruba)",  # Using Mispar Meruba as primary, Mispar Boneh as alternative name from user doc.
                "description": "Each letter's standard value is squared before summing.",
                "example": "אב = א(1²=1) + ב(2²=4) = 5",
                "notes": "Also known as Mispar Bone'eh. This amplifies the contribution of larger value letters.",
                "rationale": 'Why: Squaring each letter\'s value amplifies its power and significance. This method is often associated with concepts of structure, foundation, and manifestation ("building"). The square represents a stable, complete form.\nWhen: Used to explore the inherent potential or magnified force of a word. It can highlight the underlying structure or the "building blocks" of a concept. Sometimes used in architectural or cosmological symbolism.',
            },
            {
                "name": "Hebrew Cubed Value (Mispar Me'ukav)",  # Using Mispar Me'ukav from user doc.
                "description": "Each letter's standard value is cubed before summing.",
                "example": "אב = א(1³=1) + ב(2³=8) = 9",
                "notes": "Further amplifies letter contributions. Meshulash often means Triangular.",
                "rationale": "Why: Cubing values suggests a three-dimensional or fully realized manifestation, representing volume, depth, and complete development. It signifies an even greater amplification of the letter's essence than squaring.\nWhen: Used less commonly than squaring, but applied when seeking to understand the fullest possible expression or impact of a word or name, often in contexts of divine power or cosmic significance.",
            },
            {
                "name": "Hebrew Triangular Value (Mispar Kidmi)",  # Mispar Kidmi is common. User doc also offers Meshulash.
                "description": "Each letter's value is the sum of integers from 1 up to the value of the letter (n(n+1)/2).",
                "example": "אב = א(triangular of 1 = 1) + ב(triangular of 2 = 3) = 4",
                "notes": "Triangular number of n = n(n+1)/2. This creates triangular numbers for each letter.",
                "rationale": "Why: This method sums all integers from 1 up to the value of the letter (n(n+1)/2). Triangular numbers are associated with sequences, unfolding processes, and the sum of emanations. It can represent the cumulative force or development of a letter's energy.\nWhen: Used to explore the progressive unfolding or the total generative power inherent in a letter's value. It's found in more esoteric Kabbalistic calculations.",
            },
            {
                "name": "Hebrew Full Square Value (Mispar HaMerubah HaKlali)",
                "description": "Sums the squares of each letter's standard value.",
                "example": "אבג = א(1²) + ב(2²) + ג(3²) = 1 + 4 + 9 = 14",
                "notes": "Same as Square Value (Mispar Meruba).",
                "rationale": "Why: This is the same as Square Value (Mispar Bone'eh/Meruba) if it refers to summing the squares of each letter's value. It emphasizes the combined foundational strength of all letters in the word.\nWhen: Same as Square Value. Used to assess the magnified structural power or foundational energy of a word.",
            },
            {
                "name": "Hebrew Ordinal Building Value (Mispar Boneah Siduri)",
                "description": "Squares the ordinal (positional) values of the letters.",
                "example": "אבג = א(1st letter, 1²=1) + ב(2nd letter, 2²=4) + ג(3rd letter, 3²=9) = 14",
                "notes": "Amplifies significance of letter placement.",
                "rationale": 'Why: Squares the ordinal (positional) values of the letters. This method amplifies the significance of each letter\'s place in the sequence, suggesting a "built-up" importance based on order.\nWhen: Used when the order of letters is particularly significant, and one wishes to explore the magnified impact of this sequence. It combines the concepts of ordinal position with the amplifying effect of squaring.',
            },
            {
                "name": "Hebrew Full Value (Mispar Shemi / Milui)",
                "description": "The value of the fully spelled-out name of each letter, using standard letter values for the name.",
                "example": "א = אלף = א(1) + ל(30) + פ(80) = 111. Word: אב = אלף(111) + בית(412) = 523",
                "notes": "Incorporates the hidden meanings in letter names.",
                "rationale": 'Why: Spelling out the name of each letter and summing their standard values reveals a "hidden" dimension of the word. Each letter is a gateway to a concept, and its name further elaborates that concept. This method taps into the creative power inherent in the names of the letters.\nWhen: Used in advanced Kabbalistic analysis to uncover deeper meanings of divine names, scriptural verses, or significant words. It\'s believed to reveal the inner essence or potential of the word.',
            },
            {
                "name": "Hebrew Full Value with Finals (Mispar Shemi Sofit)",
                "description": "The value of spelled-out letter names, using final letter values (500-900) within the name spelling where applicable.",
                "example": "א = אלף (if Pe were final, though it isn't here) = א(1) + ל(30) + ף(final pe = 800) = 831. Word: אב = אלף(111 or 831 if final letters were used in its spelling) + בית(412) = 523 or 1243.",
                "notes": "A variation of Mispar Shemi using final values in names.",
                "rationale": 'Why: Similar to Full Value, but uses the higher values for final letters when they appear within the spelled-out names of the letters. This adds another layer of expansion or fulfillment to the hidden meaning.\nWhen: Applied when an even more expanded or "fulfilled" understanding of the letter names is sought, particularly if the final letters are seen as significant in the structure of those names.',
            },
            {
                "name": "Hebrew Name Value (Mispar Shemi - Multiplication)",
                "description": "Multiplies the standard values of the spelled-out names of each letter. (Uncommon method)",
                "example": "אב = אלף(111) × בית(412) = 45,732",
                "notes": "This is not a standard recognized Hebrew gematria method. Traditional Milui uses summation.",
                "rationale": "Why: Multiplying the values would create exponentially larger numbers, perhaps signifying a vast interconnectedness or a multiplicative creative force. However, this is not a standard recognized Hebrew gematria method.\nWhen: Its use would be highly speculative and likely modern or idiosyncratic, as traditional methods focus on summation.",
            },
            {
                "name": "Hebrew Name Value with Finals (Mispar Shemi Sofit - Multiplication)",
                "description": "Multiplies the final values of the spelled-out names of each letter. (Uncommon method)",
                "example": "אב = אלף(831) × בית(412) = 342,372",
                "notes": "Highly speculative, uses final letter values in names before multiplication.",
                "rationale": "Why: Similar to the above, but using final letter values in the spelled-out names before multiplication.\nWhen: Same as above; highly speculative.",
            },
            {
                "name": "Hebrew Hidden Value (Mispar Ne'elam)",
                "description": "Standard value of the letter name minus the standard value of the letter itself.",
                "example": "א = אלף - א = (111) - 1 = 110. Word: אב = (אלף-א) + (בית-ב) = 110 + (412-2=410) = 520",
                "notes": "Reveals a hidden aspect of the letter.",
                "rationale": 'Why: This subtracts the simple value of the letter from its full spelled-out value (Milui). It represents the "hidden" part of the letter\'s essence, the energy that remains once the manifest part is removed, pointing to its inner core or unrevealed potential.\nWhen: Used in Kabbalistic exegesis to explore the concealed aspects of divine names or important terms. It seeks to understand what is not immediately apparent.',
            },
            {
                "name": "Hebrew Hidden Value with Finals (Mispar Ne'elam Sofit)",
                "description": "Final value of the letter name (Milui with finals) minus the standard value of the letter itself.",
                "example": "א = אלף (using final Pe in its spelling if applicable) - א = (831) - 1 = 830. אך = (אלף-א using final Pe = 830) + (כף-כ using final Pe in its spelling, כף = כ(20)+ף(800)=820; 820-20=800) = 830 + 800 = 1630",
                "notes": "Variation of Hidden Value using final forms in names for Milui calculation.",
                "rationale": 'Why: The same principle as Hidden Value, but the Milui calculation incorporates final letter values where applicable before subtracting the simple letter value. This explores the hidden essence in its "fulfilled" or "expanded" state.\nWhen: Applied when analyzing the concealed aspects of words where the expanded nature of final letters is considered significant for the Milui calculation.',
            },
            {
                "name": "Hebrew Face Value (Mispar HaPanim)",
                "description": "Full spelled-out value (Milui) of the first letter + standard values of the rest of the letters.",
                "example": "אב = אלף(111) + ב(2) = 113. אבאה = אלף(111) + ב(2) + א(1) + ה(5) = 119. בית (name) = (Milui of ב = בית = 412) + י(10) + ת(400) = 822",
                "notes": "Emphasizes the beginning of the word.",
                "rationale": 'Why: This method highlights the first letter of a word by taking its full spelled-out value (Milui), while the remaining letters are taken at their standard value. It emphasizes the "face" or primary aspect of the word, suggesting that the initial letter sets the tone or core essence.\nWhen: Used when the initial letter of a word is considered to hold particular importance or to be the "key" to its meaning. It can show how the rest of the word unfolds from this primary essence.',
            },
            {
                "name": "Hebrew Face Value with Finals (Mispar HaPanim Sofit)",
                "description": "Milui of the first letter (using finals) + standard values of the rest.",
                "example": "אב = אלף(831, using final Pe) + ב(2) = 833. כב = כף(820, כף spelled with final Pe) + ב(2) = 822",
                "notes": "Variation of Face Value using finals for the first letter's Milui.",
                "rationale": 'Why: Similar to Face Value, but the Milui of the first letter is calculated using final letter values where applicable. This gives an expanded or fulfilled sense to the "face" of the word.\nWhen: Used when the initial letter\'s expanded potential (via final letters in its Milui) is being emphasized as the primary aspect of the word.',
            },
            {
                "name": "Hebrew Back Value (Mispar HaAchor)",
                "description": "Standard values of all but the last letter + Milui of the last letter.",
                "example": "אב = א(1) + בית(412, Milui of ב) = 413. אבאה = א(1) + ב(2) + א(1) + הא(Milui of ה = הא = 5+1=6) = 10. בית (name) = ב(2) + י(10) + תו(Milui of ת = תו = 400+6=406) = 418",
                "notes": "Emphasizes the end of the word.",
                "rationale": 'Why: This method emphasizes the final letter of a word by taking its full spelled-out value (Milui), while the preceding letters are taken at their standard value. It focuses on the outcome, conclusion, or "rear guard" aspect of the word.\nWhen: Used when the final letter is seen as the culmination or ultimate expression of the word\'s meaning. It can reveal the result or final impact.',
            },
            {
                "name": "Hebrew Back Value with Finals (Mispar HaAchor Sofit)",
                "description": "Standard values of preceding letters + Milui of the last letter (using finals).",
                "example": "אף = א(1) + פא(Milui of ף, assuming פא. If פה, value is different. Example 81 implies standard Pe for פא. If final Pe: ף(800)+א(1)=801). Doc example: אף = א(1) + פא(81) = 82. אך = א(1) + כף(Milui of ך, כף with final Pe = כ(20)+ף(800)=820) = 821",
                "notes": "Variation of Back Value using finals for the last letter's Milui.",
                "rationale": 'Why: Similar to Back Value, but the Milui of the last letter is calculated using final letter values where applicable. This gives an expanded or fulfilled sense to the "conclusion" or "back" of the word.\nWhen: Used when the final letter\'s expanded potential (via final letters in its Milui) is being emphasized as the culminating aspect of the word.',
            },
            {
                "name": "Hebrew Collective Value (Mispar Kolel - Sum + N letters)",
                "description": "The standard value of the word plus the number of letters in the word.",
                "example": "תורה = ת(400) + ו(6) + ר(200) + ה(5) = 611 + 4 letters = 615",
                "notes": "Also known as Mispar Musafi. This is different from Standard Value + 1.",
                "rationale": 'Why: Adding the number of letters in the word (or sometimes +1, see below) to its standard value. The "+ number of letters" approach suggests that the word as a whole entity, composed of its individual parts, has a collective synergy. Each letter contributes not just its value but its presence.\nWhen: Used to account for the word as a complete unit, beyond just the sum of its parts. It emphasizes the holistic nature of the word or phrase.',
            },
            {
                "name": "Hebrew Name Collective Value (Mispar Shemi Kolel)",
                "description": "Full Value (Milui) of the word + number of letters.",
                "example": "אב = אלף(111) + בית(412) = 523 + 2 letters = 525",
                "notes": "Collective version of Sum of Letter Names.",
                "rationale": "Why: Adds the number of letters to the Full Value (Milui) of the word. This combines the depth of the spelled-out letter names with the holistic sense of the word as a collective.\nWhen: Used in advanced interpretations where both the inner essence (from Milui) and the collective unity of the word are being considered.",
            },
            {
                "name": "Hebrew Name Collective Value with Finals (Mispar Shemi Kolel Sofit)",
                "description": "Full Value (Milui with finals) + number of letters.",
                "example": "אב = אלף(831) + בית(412) = 1243 + 2 letters = 1245. אך = אלף(831) + כף(820) = 1651 + 2 letters = 1653",
                "notes": "Collective version of Sum of Letter Names with finals.",
                "rationale": "Why: Adds the number of letters to the Full Value (Milui) calculated with final letter values. This emphasizes the collective unity of the word in its most expanded or fulfilled inner state.\nWhen: Used when the most expanded form of the word's inner essence, along with its collective nature, is under examination.",
            },
            {
                "name": "Hebrew Regular plus Collective (Kolel +1)",
                "description": "The standard value of the word plus one.",
                "example": "תורה = ת(400) + ו(6) + ר(200) + ה(5) = 611 + 1 = 612",
                "notes": "A simple form of Kolel, adding one to the total word value to represent the word itself as an entity.",
                "rationale": 'Why: Adding 1 to the standard value. The "+1" (Kolel) is often interpreted as representing the word itself as a single, unified entity, or sometimes as representing the divine unity or a connection to a higher source. It acknowledges the whole in addition to the sum of its parts.\nWhen: Very commonly used in many gematria calculations to find equivalencies. If two words are off by one, the Kolel is often invoked to show their connection. It\'s a flexible tool for bridging small numerical gaps.',
            },
            {
                "name": "Hebrew AtBash Substitution (AtBash)",  # Renamed from Atbash (את בש) for clarity in list
                "description": "A substitution cipher where the alphabet is reversed (א↔ת, ב↔ש). Standard value is taken after substitution.",
                "example": "אבג → תשר = ת(400) + ש(300) + ר(200) = 900",
                "notes": "א(Aleph)↔ת(Tav), ב(Bet)↔ש(Shin), ג(Gimel)↔ר(Resh), etc.",
                "rationale": 'Why: This cipher pairs the first letter of the alphabet with the last, the second with the second-to-last, and so on. It\'s believed to reveal the inverse or hidden aspect of a word, or to show a connection between seemingly opposite concepts. It reflects a principle of "as above, so below" or inner/outer correspondence.\nWhen: Used to uncover secret meanings, often in prophetic or esoteric texts. It can link words that appear unrelated on the surface. Jeremiah 25:26 and 51:41 contain famous examples ("Sheshach" for Babel).',
            },
            {
                "name": "Hebrew Albam Substitution (Albam)",  # Renamed from Albam (אלבם) for clarity
                "description": "A substitution cipher where the first letter is exchanged with the 12th, the 2nd with the 13th, etc. Standard value is taken after substitution.",
                "example": "אבג → כלמ = כ(20) + ל(30) + מ(40) = 90",
                "notes": "א(Aleph)↔כ(Kaf), ב(Bet)↔ל(Lamed), ג(Gimel)↔מ(Mem), etc. (The 1st letter swaps with the 11th, 2nd with 12th, up to י with ך. Then כ with א, etc. The example given seems to use א↔כ, ב↔ל, ג↔מ which is one specific scheme of Albam where the first half of 11 letters is swapped with the second half of 11 letters).",
                "rationale": "Why: This cipher divides the alphabet into two halves, and letters are exchanged between the halves (e.g., the 1st letter with the 12th, the 2nd with the 13th, etc.). It's another way to systematically transform words to find hidden layers of meaning or connections based on a structured permutation.\nWhen: Similar to AtBash, used for uncovering concealed meanings in scripture or other sacred texts. It's one of several traditional substitution ciphers (Temurah).",
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

        # Greek methods
        greek_methods = [
            {
                "name": "Greek Standard Value (Isopsophy / Arithmos)",
                "description": "The standard Greek numerological system. Each letter has a specific numerical value.",
                "example": "Λόγος = Λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373",
                "notes": "Most common method in Greek gematria.",
                "rationale": "Why: The fundamental method, assigning the established numerical value to each Greek letter. This is seen as the letter's inherent numerical power or identity.\nWhen: Universally used for finding equivalencies between words, names, and phrases in Greek texts, from classical literature (e.g., Homeric analysis by some) to Gnostic writings, magical papyri, and Christian scriptures (e.g., the number of the Beast in Revelation).",
            },
            {
                "name": "Greek Ordinal Value (Arithmos Taktikos)",
                "description": "Each letter is assigned a value based on its position in the alphabet.",
                "example": "Λόγος = Λ(11th letter = 11) + ό(15th letter = 15) + γ(3rd letter = 3) + ο(15th letter = 15) + ς(18th letter = 18) = 62 (assuming a 24-letter alphabet without archaic forms for ordinal count).",
                "notes": "Similar to the Hebrew Mispar Siduri.",
                "rationale": "Why: Assigns value based on the letter's position in the 24-letter classical Greek alphabet. It emphasizes the sequential or developmental aspect of concepts.\nWhen: Used to find simpler numerical patterns or to explore meanings related to order and progression. Can provide an alternative layer of meaning to the standard value.",
            },
            {
                "name": "Greek Small Reduced Value (Arithmos Mikros)",
                "description": "Reduces each letter's standard value to a single digit by summing its digits.",
                "example": "Λόγος = Λ(30→3) + ό(70→7) + γ(3) + ο(70→7) + ς(200→2) = 22→4. (This example reduces each letter first). Alternatively, Λόγος = 373 → 3+7+3 = 13 → 1+3 = 4. (This reduces the total).",
                "notes": "Similar to Hebrew Mispar Katan. The method can be applied by reducing each letter first, or by reducing the total sum.",
                "rationale": "Why: Reduces each letter's standard value to a single digit (by summing its digits, e.g., 30→3, 200→2) and then sums these, or sums the total standard value and then reduces it to a single digit. This seeks the fundamental essence or root of the word's numerical value.\nWhen: Used to simplify values and find core numerical links, similar to Hebrew Mispar Katan. Particularly useful when comparing words with large standard values or in Neopythagorean contexts focusing on the meanings of numbers 1-9 (the Ennead).",
            },
            {
                "name": "Greek Digital Value (Arithmos Psephiakos)",
                "description": "Sums the digits of each letter's standard value (not iteratively).",
                "example": "Λόγος = Λ(30→3+0=3) + ό(70→7+0=7) + γ(3) + ο(70→7+0=7) + ς(200→2+0+0=2) = 22",
                "notes": "Analogous to Hebrew Mispar Mispari.",
                "rationale": "Why: Sums the digits of each letter's standard value (e.g., Λ(30) becomes 3+0=3). This method focuses on the constituent numerical elements within each letter's value before combining them.\nWhen: A more nuanced form of reduction, used to analyze the internal numerical structure of a word's isopsephy value.",
            },
            {
                "name": "Greek Digital Ordinal Value (Arithmos Taktikos Psephiakos)",
                "description": "Sums the digits of each letter's ordinal value.",
                "example": "Λόγος = Λ(11→1+1=2) + ό(15→1+5=6) + γ(3) + ο(15→1+5=6) + ς(18→1+8=9) = 26",
                "notes": "Applies digital sum to ordinal positions.",
                "rationale": "Why: Reduces the ordinal value of each letter to a single digit by summing its digits (e.g., 11th letter → 1+1=2). It seeks the fundamental essence of the letter's sequential position.\nWhen: Used when both the order of letters and a reduced numerical essence are considered important.",
            },
            {
                "name": "Greek Square Value (Arithmos Tetragonos)",
                "description": "The square of each letter's standard value.",
                "example": "α=1², β=2², γ=3²... For 'αβγ': α(1²=1) + β(2²=4) + γ(3²=9) = 14.",
                "notes": "Multiplies each letter value by itself before summing.",
                "rationale": "Why: Squaring each letter's standard value and summing these squares. This method significantly amplifies the individual contributions of letters, especially those with higher values, highlighting their inherent power or a foundational aspect.\nWhen: Used to explore a more potent or structurally emphasized numerical value of words, often revealing connections not obvious with simple addition.",
            },
            {
                "name": "Greek Ordinal Square Value (Arithmos Taktikos Tetragonos)",
                "description": "The square of each letter's ordinal value.",
                "example": "α(1)=1², β(2)=2², κ(11)=11²... For 'αβγ': α(1²=1) + β(2²=4) + γ(3²=9) = 14.",
                "notes": "Squares the position number of each letter.",
                "rationale": "Why: Squares the ordinal (positional) value of each letter and sums these. This emphasizes the significance of a letter's placement in the sequence, amplified quadratically.\nWhen: Used when the sequential order of letters is paramount and its impact is considered to be geometrically increasing.",
            },
            {
                "name": "Greek Cubed Value (Arithmos Kyvos)",
                "description": "The cube of each letter's standard value.",
                "example": "α=1³, β=2³, γ=3³... For 'αβγ': α(1³=1) + β(2³=8) + γ(3³=27) = 36.",
                "notes": "Each letter's standard value is raised to the power of 3.",
                "rationale": "Why: Cubing each letter's standard value and summing these. This method further magnifies the individual letter values, suggesting a three-dimensional or deeply foundational power.\nWhen: Used for an even more intensified analysis of letter values, exploring volumetric or profound structural significances.",
            },
            {
                "name": "Greek Reverse Standard Values (Arithmos Antistrofos)",
                "description": "Letter values are reversed compared to standard (α=800, ω=1).",
                "example": "α=800, β=700, γ=600... For 'αβγ': α(800) + β(700) + γ(600) = 2100.",
                "notes": "Equivalent to the Hebrew Mispar Meshupach.",
                "rationale": "Why: Assigns values in reverse order based on the standard Greek system (e.g., Alpha, first, gets Omega's value; Beta, second, gets Psi's value, etc.). It explores concepts from an opposite or complementary perspective.\nWhen: Used to find inverse relationships or to highlight meanings that emerge when viewed from a reversed numerical scale.",
            },
            {
                "name": "Greek AlphaMu Substitution (Kryptos Alpha-Mu)",
                "description": "Letter substitution cipher (α↔μ, β↔ν, etc.). Standard value is taken after substitution.",
                "example": "If 'αβγ' becomes 'μνξ' through substitution, calculate value of 'μνξ'. (α=μ, β=ν, γ=ξ ... μ=α, ν=β, ξ=γ)",
                "notes": "Greek equivalent of Hebrew Albam. Divides alphabet into two halves (α-μ and ν-ω) and swaps corresponding letters.",
                "rationale": "Why: A substitution cipher where the first half of the alphabet is exchanged with the second (α with ν, β with ξ, etc., based on a 13/13 split if using 26 letters, or similar for 24/27). Value is calculated on the substituted text. It reveals hidden links by pairing distant letters.\nWhen: Used in esoteric texts or cryptography to encode messages or reveal hidden layers of meaning through systematic letter exchange.",
            },
            {
                "name": "Greek AlphaOmega Substitution (Kryptos Alpha-Omega)",
                "description": "Letter substitution cipher (α↔ω, β↔ψ, etc.). Standard value is taken after substitution.",
                "example": "If 'αβγ' becomes 'ωψχ' through substitution, calculate value of 'ωψχ'. (α=ω, β=ψ, γ=χ)",
                "notes": "Greek equivalent of Hebrew Atbash. Reverses the alphabet for substitution.",
                "rationale": "Why: A substitution cipher pairing the first letter with the last, second with second-to-last, etc. (α with ω, β with ψ). Value is calculated on the substituted text. It creates a mirrored version of the word.\nWhen: Used to find antithetical meanings or to reveal hidden connections based on reversal, similar to Hebrew Atbash.",
            },
            {
                "name": "Greek Alphabet Reversal Substitution (Atbash variant)",
                "description": "Substitutes letters with their true reverse in the alphabet (α=ω, β=ψ, etc.). Standard value of substituted text.",
                "example": "α becomes ω, β becomes ψ. Then calculate standard value. For 'αβγ': value(ωψχ).",
                "notes": "A more direct Atbash-style letter swap for Greek, using the actual alphabetical opposites.",
                "rationale": "Why: Substitutes each letter with its direct counterpart from the reversed alphabet (e.g., if the alphabet is A-Z, A becomes Z, B becomes Y). The standard value of the new, substituted word is then calculated. This is a straightforward mirror cipher.\nWhen: Used to explore meanings derived from direct opposition or reversal of letter identities within the alphabet sequence.",
            },
            {
                "name": "Greek Pair Matching Substitution (e.g., α=λ)",
                "description": "Substitutes letters based on a specific pairing scheme (e.g., α=λ, β=κ). Standard value of substituted text.",
                "example": "Requires definition of pairs. If α→λ, β→κ: 'αβ' becomes 'λκ'. Value of 'λκ'. The example 'αβγ → λκι' (alpha to lambda, beta to kappa, gamma to iota) would give the value of 'λκι'.",
                "notes": "The current implementation has a placeholder map and may need full definition for a specific desired pairing.",
                "rationale": "Why: A substitution cipher where letters are exchanged based on a predefined set of pairs (e.g., the example given is α=λ, β=κ, γ=ι; this would need to be fully defined for the whole alphabet). The standard value of the substituted word is then taken. This method depends entirely on the specific pairing key used.\nWhen: Used when a specific, arbitrary (not necessarily systematic like Atbash or Albam) set of letter correspondences is being employed for encoding or esoteric analysis. The rationale is tied to the meaning of the chosen pairs.",
            },
            {
                "name": "Greek Building Value (Arithmos Oikodomikos)",
                "description": "Cumulative sum of letter values as the word is spelled out.",
                "example": "'αβγ' = α(1) + (α+β)(1+2=3) + (α+β+γ)(1+2+3=6) = 1+3+6 = 10.",
                "notes": "Equivalent to Hebrew Mispar Boneh.",
                "rationale": "Why: Sums letter values cumulatively: value of 1st letter + value of (1st+2nd) + value of (1st+2nd+3rd), etc. It shows the accumulating numerical force as a word unfolds.\nWhen: Used to explore the developmental or progressive building of a word's meaning, highlighting the impact of each stage of its formation.",
            },
            {
                "name": "Greek Triangular Value (Arithmos Trigonikos)",
                "description": "The sum of standard values of all letters up to that letter in the alphabet.",
                "example": "α=1, β=(1+2)=3, γ=(1+2+3)=6. For 'αβγ': 1 + 3 + 6 = 10. (Note: This is based on ordinal position, not the standard value of the letter itself).",
                "notes": "Similar to Hebrew Mispar Kidmi. This refers to the sum of ordinal positions up to the letter's position, not n(n+1)/2 of its standard value.",
                "rationale": "Why: Each letter is assigned the sum of ordinal values from Alpha up to its own position (e.g., Alpha (1st)=1, Beta (2nd)=1+2=3, Gamma (3rd)=1+2+3=6). The sum of these values for each letter in the word is the result. It signifies unfolding or cumulative potential based on sequence.\nWhen: Used to explore meanings related to growth, layered development, or the sum of preceding influences in a sequence.",
            },
            {
                "name": "Greek Sum of Letter Names (Arithmos Onomatos)",
                "description": "The value of the fully spelled-out name of each letter.",
                "example": "α (Alpha/άλφα) -> standard value of άλφα. For 'αβγ': Value(Name of α) + Value(Name of β) + Value(Name of γ).",
                "notes": "Equivalent to Hebrew Mispar Shemi. Letter names are (άλφα, βήτα, γάμμα, etc.).",
                "rationale": "Why: Sums the standard isopsephy values of the spelled-out names of each letter in the word (e.g., Alpha, Beta, Gamma). It delves into the inherent meaning of the letters themselves as words.\nWhen: Used to analyze the deeper, foundational meanings embedded in the names of the letters, suggesting a richer, multi-layered significance for the word.",
            },
            {
                "name": "Greek Product of Letter Names",
                "description": "Multiplies the values of the spelled-out names of each letter.",
                "example": "Value of (Name of α) * (Name of β) * ...",
                "notes": "Product of letter name values. Can result in very large numbers.",
                "rationale": "Why: Multiplies the standard isopsephy values of the spelled-out names of each letter. This suggests an interactive or compounding effect of the letters' named essences.\nWhen: Used to explore the magnified or combined power of the letters' names, often for finding very specific or potent correspondences.",
            },
            {
                "name": "Greek Hidden Letter Name Value (Arithmos Kryptos)",
                "description": "The value of the letter name minus the letter itself.",
                "example": "α = Value(άλφα) - Value(α). Sum these for all letters in the word.",
                "notes": "Reveals hidden values within letter names.",
                "rationale": "Why: Calculates the value of a letter's spelled-out name (Arithmos Onomatos) and subtracts the standard value of the letter itself. This reveals the 'hidden' part of the letter's name value.\nWhen: Used to explore the concealed aspects or underlying components of a letter's identity as expressed through its full name.",
            },
            {
                "name": "Greek Face Value (Arithmos Prosopeio)",
                "description": "Value of the first letter's name + standard values of the rest of the letters.",
                "example": "For 'αβγ': Value(Name of α) + Value(β) + Value(γ).",
                "notes": "Emphasizes the beginning of the word.",
                "rationale": "Why: Takes the full name value (Arithmos Onomatos) of the first letter of a word and adds the standard values of the remaining letters. This highlights the initial or leading essence of the word in its fullest form.\nWhen: Used to emphasize the primary characteristic or initial impulse of a word, as defined by its first letter's complete nominal value.",
            },
            {
                "name": "Greek Back Value (Arithmos Opisthios)",
                "description": "Standard values of all but the last letter + value of the last letter's name.",
                "example": "For 'αβγ': Value(α) + Value(β) + Value(Name of γ).",
                "notes": "Emphasizes the end of the word.",
                "rationale": "Why: Sums the standard values of all letters except the last, then adds the full name value (Arithmos Onomatos) of the final letter. This highlights the concluding essence or outcome of the word in its fullest form.\nWhen: Used to emphasize the final characteristic, result, or ultimate meaning of a word, as defined by its last letter's complete nominal value.",
            },
            {
                "name": "Greek Collective Value (Arithmos Syllogikos / Prosthetikos)",
                "description": "Adds the number of letters to the standard value of the word.",
                "example": "θεος (Standard value 284) = 284 + 4 (letters) = 288.",
                "notes": "Equivalent to Hebrew Mispar Kolel/Musafi.",
                "rationale": "Why: Adds the count of letters in the word to its standard isopsephy value. This acknowledges the word as a collective entity in addition to its constituent parts.\nWhen: Used when the wholeness or unity of the word, beyond the sum of its individual letter values, is considered significant.",
            },
            {
                "name": "Greek Sum of Letter Names + Letters (Arithmos Onomatikos Syllogikos)",
                "description": "Sum of letter name values + number of letters in the word.",
                "example": "For 'αβ': (Value(Name of α) + Value(Name of β)) + 2 (letters).",
                "notes": "Collective version of Sum of Letter Names.",
                "rationale": "Why: Combines the sum of the full name values of each letter (Arithmos Onomatos) with the count of letters in the word. This signifies the collective power of the named essences plus the word's unity.\nWhen: Used when the complete named identities of the letters are considered collectively along with the word's overall structure.",
            },
            {
                "name": "Greek Standard Value + 1 (Kanonikos Syn Syllogikos)",
                "description": "The standard value of the word plus one.",
                "example": "'αβγ' (Standard value 6) -> 6 + 1 = 7.",
                "notes": "A simple form of Kolel for Greek, adding 1 to represent the word as an entity.",
                "rationale": "Why: Adds 1 to the standard isopsephy value of the word. The '1' represents the word as a single, whole entity.\nWhen: Used to find equivalencies between words differing by one, or to acknowledge the word's unity beyond its component values, similar to one form of Hebrew Kolel.",
            },
            {
                "name": "Greek Next Letter Value (Arithmos Epomenos)",
                "description": "Calculates the sum of the standard values of the letter that follows each letter of the input word in the alphabet.",
                "example": "For 'αβ': value of letter after α (β) + value of letter after β (γ) = Value(β) + Value(γ). For ω (Omega), if it's the last, there's no next letter (value 0 for that position).",
                "notes": "Value of the subsequent letter in sequence for each letter of the word.",
                "rationale": "Why: For each letter in the word, its value is taken as the standard value of the *next* letter in the Greek alphabet sequence. The sum of these 'next letter' values forms the word's total. If a letter is the last in the sequence (e.g., Omega), its 'next letter' value is often taken as zero or handled by cycling.\nWhen: Used to explore concepts of progression, consequence, or what follows from each component of a word. It can imply a forward movement or a series of subsequent states.",
            },
            {
                "name": "Greek Cyclical Permutation Value (Kyklikē Metathesē)",
                "description": 'The input text is cyclically permuted (e.g., "αβγδ" becomes "βγδα") and then its standard value is taken.',
                "example": "'αβγ' (standard 6) -> permutes to 'βγα'. Then, standard value of 'βγα' is calculated: β(2)+γ(3)+α(1) = 6.",
                "notes": "Value of a cyclically shifted word. This often results in the same value if all letters are unique and present in the value map.",
                "rationale": "Why: The letters of the word are cyclically permuted (e.g., ABC becomes BCA), and the standard isopsephy value of the new, permuted word is calculated. This explores the word's value from different starting points within its own structure.\nWhen: Used to analyze the internal symmetries or different perspectives of a word by shifting its components. If the value remains the same after permutation, it can indicate a kind of numerical stability or completeness.",
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

        # English TQ methods (potentially a list now)
        english_methods = [
            {
                "name": "English TQ Standard Value",
                "meaning": "TQ Standard (Base Values)",
                "description": (
                    "Assigns values 0-25 to English letters (I=0, U=25) based on the Trigrammaton Qabalah system. "
                    "This is the foundational TQ method."
                ),
                "example": "LIGHT = L(1) + I(0) + G(11) + H(3) + T(9) = 24",
                "chart": "I=0, L=1, C=2, H=3, P=4, A=5, X=6, J=7, W=8, T=9, O=10, G=11, F=12, E=13, R=14, S=15, Q=16, K=17, Y=18, Z=19, B=20, M=21, V=22, D=23, N=24, U=25",
                "notes": "Values are derived from the 27 trigrams of Liber Trigrammaton.",
                "rationale": "Why: This is the basic application of this specific English gematria cipher. The rationale for the specific letter assignments in TQ would be tied to the unique teachings or symbolism of the system's originators. It aims to find numerical significance in English words based on this particular key.\nWhen: Used by practitioners of the TQ system to analyze English texts, names, or concepts, seeking correspondences and hidden meanings according to its specific numerical framework.",
            },
            {
                "name": "English TQ Reduced Value",
                "meaning": "TQ Standard Sum Reduced",
                "description": "The standard TQ sum of a word is reduced to a single digit by iteratively summing its digits.",
                "example": "LIGHT = 24 → 2+4 = 6",
                "chart": "Based on standard TQ values.",
                "notes": "Continue adding digits until a single digit is reached. Provides a single-digit distillation of the TQ value.",
                "rationale": 'Why: Reduces the final TQ sum to a single digit (0-9). This seeks a more fundamental or essential numerical value within the TQ system, similar to reduction in Hebrew or Greek methods.\nWhen: Used to simplify TQ values for comparison or to find a core "digit-essence" of a word according to this cipher.',
            },
            {
                "name": "English TQ Square Value",
                "meaning": "TQ Individual Letter Squares",
                "description": "Each letter's TQ value is squared, and then these squared values are summed.",
                "example": "LIGHT = L(1²=1) + I(0²=0) + G(11²=121) + H(3²=9) + T(9²=81) = 212",
                "chart": "Based on standard TQ values.",
                "notes": "Amplifies the impact of higher-value TQ letters.",
                "rationale": "Why: Squares each letter's TQ value, then sums them. This amplifies the significance of each letter's assigned TQ value, suggesting a magnified power or foundational aspect within this system.\nWhen: Used to explore a more potent or structurally emphasized numerical value of English words according to the TQ cipher.",
            },
            {
                "name": "English TQ Triangular Value",
                "meaning": "TQ Individual Letter Triangulars",
                "description": "The triangular number of each letter's TQ value (n*(n+1)/2) is calculated, then summed.",
                "example": "LIGHT = L(triangular of 1 = 1) + I(triangular of 0 = 0) + G(triangular of 11 = 66) + H(triangular of 3 = 6) + T(triangular of 9 = 45) = 118",
                "chart": "Based on standard TQ values. Triangular number of n = n(n+1)/2. For n=0, it's 0.",
                "notes": "Uses triangular progression for each TQ letter value.",
                "rationale": "Why: Applies the triangular number formula to each letter's TQ value. This would imply an unfolding or cumulative energy associated with each letter's TQ assignment.\nWhen: A more esoteric application within the TQ system, used to explore the generative or developing potential of words based on their TQ values.",
            },
            {
                "name": "English TQ Letter Position Value",
                "meaning": "TQ Value by Position",
                "description": "Each letter's TQ value is multiplied by its position in the word (1-indexed), then summed.",
                "example": "LIGHT = L(1×1=1) + I(0×2=0) + G(11×3=33) + H(3×4=12) + T(9×5=45) = 91",
                "chart": "Based on standard TQ values. Position is counted from 1 (first letter) to n (last letter).",
                "notes": "Weights TQ values by their placement in the word.",
                "rationale": "Why: Multiplies each letter's TQ value by its position in the word. This method gives weight to where a letter appears, suggesting that its contribution is modified by its sequence.\nWhen: Used when the order and placement of letters within a word are considered significant in conjunction with their TQ values. It can highlight letters at key positions.",
            },
        ]

        for method in english_methods:
            self._add_detailed_method(content_layout, method)

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

    def _create_coptic_tab(self):
        """Create the Coptic gematria methods tab.

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
        title = QLabel("Coptic Gematria Methods")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)

        coptic_letter_chart = (
            "ⲁ=1, ⲃ=2, ⲅ=3, ⲇ=4, ⲉ=5, ⲋ=6 (Soou), ⲍ=7, ⲏ=8, ⲑ=9, "
            "ⲓ=10, ⲕ=20, ⲗ=30, ⲙ=40, ⲛ=50, ⲝ=60, ⲟ=70, ⲡ=80, "
            "ⲣ=100, ⲥ=200, ⲧ=300, ⲩ=400, ⲫ=500, ⲭ=600, ⲯ=700, ⲱ=800, "
            "ϣ=900 (Shai), ϥ=90 (Fai), ϧ=900 (Khai), ϩ=900 (Hori), ϫ=90 (Janja), ϭ=90 (Shima), ϯ=300 (Ti)"
        )

        # Coptic methods
        coptic_methods = [
            {
                "name": "Coptic Standard Value",
                "meaning": "Standard Coptic Numerology",
                "description": "Assigns numerical values to Coptic letters, largely derived from Greek Isopsophy.",
                "example": "ⲛⲟⲩⲧⲉ (God) = ⲛ(50) + ⲟ(70) + ⲩ(400) + ⲧ(300) + ⲉ(5) = 825",
                "chart": coptic_letter_chart,
                "notes": "Values for letters like Shai (ϣ), Fai (ϥ), etc., supplement the Greek-derived values.",
                "rationale": "Why: The fundamental method, assigning the established Greek-derived numerical value to each Coptic letter, including those for the Demotic additions. It represents the letter's inherent numerical power.\nWhen: Used for finding numerical equivalencies in Coptic texts, particularly Gnostic gospels, magical texts, and Christian liturgical or scriptural documents written in Coptic.",
            },
            {
                "name": "Coptic Reduced Value",
                "meaning": "Single Digit Coptic Value",
                "description": "The standard Coptic sum of a word is reduced to a single digit by iteratively summing its digits.",
                "example": "ⲛⲟⲩⲧⲉ (825) → 8+2+5 = 15 → 1+5 = 6",
                "chart": "Based on standard Coptic values.",
                "notes": "Provides a single-digit distillation of the Coptic value.",
                "rationale": "Why: Reduces the total standard Coptic value of a word to a single digit by repeatedly summing the digits of the sum. This seeks the most fundamental numerical essence of the word according to Coptic numerology.\nWhen: Used to simplify complex Coptic values and find core numerical relationships, similar to reduction methods in other traditions.",
            },
        ]

        for method in coptic_methods:
            self._add_detailed_method(content_layout, method)

        # Add note about transliteration for Coptic
        translit_note = QLabel(
            '<b>Note on Transliteration:</b> When the "Transliterate Latin" checkbox is active, Latin input will be converted to Coptic script before calculation using a defined transliteration scheme.'
        )
        translit_note.setWordWrap(True)
        translit_note.setStyleSheet("margin-top: 15px; font-style: italic;")
        content_layout.addWidget(translit_note)

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
        <h3>Delving Deeper: Understanding Gematria and Isopsophy</h3>
        <p>Gematria and Isopsophy are ancient hermeneutic techniques that assign numerical values to letters, words, or phrases. The underlying belief is that words or phrases with identical numerical values bear some relation to each other or to the number itself, potentially revealing hidden meanings, connections, or spiritual insights within texts.</p>

        <h4>Gematria: The Hebrew Tradition</h4>
        <p><strong>Origins and Core Concepts:</strong> Gematria (גימטריה) is most prominently associated with Jewish mysticism, particularly Kabbalah. It originates from the fact that the Hebrew alphabet also serves as its numerical system. Each of the 22 Hebrew letters possesses an inherent numerical value. This practice is thought to have roots in earlier Mesopotamian cultures, but it was significantly developed and systematized within Judaism, especially from the Talmudic period (c. 2nd-5th centuries CE) onwards.</p>
        <p><strong>Purpose in Exegesis and Mysticism:</strong> Gematria became a vital tool for biblical exegesis, one of the four levels of interpretation in PaRDeS (Peshat, Remez, Derash, Sod). It was used to uncover deeper, esoteric meanings (Sod - secret/mystery) within the Torah and other sacred texts. Kabbalists employed various gematria methods to explore the nature of God, the creation, divine names, and the interconnectedness of all things. It was believed that the numerical structure of the Hebrew language itself held profound spiritual truths.</p>
        <p><strong>Key Kabbalistic Texts:</strong> Works like the <em>Sefer Yetzirah</em> (Book of Formation) and the <em>Zohar</em> (Book of Splendor) are replete with gematrical interpretations, demonstrating its importance in shaping Kabbalistic thought and practice.</p>

        <h4>Isopsophy: The Greek Counterpart</h4>
        <p><strong>Greek Context and Relation to Gematria:</strong> Isopsophy (ἰσοψηφία from ísos "equal" and psêphos "pebble" or "count") is the parallel practice in the Greek language. Like Hebrew, the classical Greek alphabet also functioned as a numeral system (using letters like Alpha for 1, Beta for 2, etc.). While sharing the fundamental principle of letter-number equivalence with Gematria, Isopsophy developed within its own distinct cultural and philosophical milieu.</p>
        <p><strong>Use in Classical and Hellenistic Texts:</strong> Evidence of Isopsophy can be found in various ancient Greek contexts. It was sometimes used by poets, in inscriptions, and in philosophical and religious writings, including early Christian texts (e.g., the "number of the beast," 666, in the Book of Revelation is a famous example of Greek Isopsophy). It was also a feature in Gnostic writings and magical papyri from Egypt, where numerical values were often seen as having potent, mystical power.</p>

        <h4>Historical and Philosophical Underpinnings</h4>
        <p><strong>Ancient Roots:</strong> The idea that numbers hold symbolic meaning and that letters can represent numbers is ancient, with precedents in Babylonian and Assyrian cultures. However, the sophisticated systems of Gematria and Isopsophy flowered particularly in the Jewish and Greco-Roman worlds.</p>
        <p><strong>Pythagoreanism and Neoplatonism:</strong> Greek Isopsophy was undoubtedly influenced by Pythagorean philosophy, which held that numbers were the fundamental reality and key to understanding the cosmos. "All things are number" is a famous Pythagorean maxim. Later, Neoplatonic philosophers also engaged with numerological symbolism, seeing numbers as emanating from The One and reflecting divine order.</p>
        <p><strong>Kabbalistic Cosmology:</strong> In Jewish Kabbalah, Gematria is deeply intertwined with its complex cosmology, including the doctrine of the Sefirot (divine emanations) and the idea that the Hebrew language is the very tool of creation. The numerical values of words are seen as reflecting their place and power within this divine structure.</p>

        <h4>Varieties, Applications, and Modern Perspectives</h4>
        <p><strong>Diverse Methods:</strong> Both Gematria and Isopsophy encompass a variety of methods beyond simple summation, including ordinal values, reduced values, ciphers (like Atbash in Hebrew), and more complex calculations (as detailed in other tabs of this reference).</p>
        <p><strong>Applications:</strong> Beyond textual exegesis, these practices have historically been applied in:
            <ul>
                <li><strong>Divination:</strong> Seeking insights or predictions.</li>
                <li><strong>Theological Speculation:</strong> Exploring the attributes and names of God.</li>
                <li><strong>Magic and Theurgy:</strong> In some traditions, for constructing talismans or invoking spiritual forces (though this is a complex and often debated aspect).</li>
                <li><strong>Comparative Studies:</strong> Finding parallels between different words, concepts, or even names across texts.</li>
            </ul>
        </p>
        <p><strong>Modern Relevance and Caution:</strong> Today, Gematria and Isopsophy continue to be studied by academics in fields like religious studies, classics, and Jewish studies. They also remain important in various contemporary esoteric, mystical, and spiritual traditions. While these systems can offer profound insights and reveal fascinating textual layers, it\'s important to approach them with an understanding of their historical context and interpretative nature. The significance derived from numerical correspondences can be subjective, and scholarly debate often surrounds specific interpretations. Critical engagement and contextual awareness are key to appreciating their rich and complex heritage without falling into overly simplistic or unfounded assertions.</p>
        <p>This tool provides a means to explore these methods, but the interpretation of any results remains a deeply personal or scholarly endeavor.</p>
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
        name_label = QLabel(f"{method_data['name']}")
        name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        method_layout.addWidget(name_label)

        # Meaning (optional)
        meaning_text = method_data.get("meaning", "")
        if meaning_text:
            meaning_label = QLabel(f"<b>Meaning:</b> {meaning_text}")
            meaning_label.setStyleSheet("margin-left: 20px;")
            method_layout.addWidget(meaning_label)

        # Description
        desc_label = QLabel(method_data.get("description", "No description available."))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-left: 20px; margin-top: 5px;")
        method_layout.addWidget(desc_label)

        # Example (optional)
        example_text = method_data.get("example", "")
        if example_text:
            example_label = QLabel(f"<b>Example:</b> {example_text}")
            example_label.setWordWrap(True)
            example_label.setStyleSheet("margin-left: 20px; margin-top: 10px;")
            method_layout.addWidget(example_label)

        # Chart of values (optional)
        chart_text = method_data.get("chart", "")
        if chart_text:
            chart_label = QLabel(f"<b>Letter Values:</b> {chart_text}")
            chart_label.setWordWrap(True)
            chart_label.setStyleSheet("margin-left: 20px; margin-top: 5px;")
            method_layout.addWidget(chart_label)

        # Notes (optional)
        notes_text = method_data.get("notes", "")
        if notes_text:
            notes_label = QLabel(f"<i>Notes:</i> {notes_text}")
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet(
                "margin-left: 20px; margin-top: 5px; font-style: italic;"
            )
            method_layout.addWidget(notes_label)

        # Purpose & Application (optional) - NEW SECTION
        rationale_text = method_data.get("rationale", "")
        if rationale_text:
            rationale_title_label = QLabel("<b>Purpose & Application:</b>")
            rationale_title_label.setStyleSheet(
                "margin-left: 20px; margin-top: 10px; font-weight: bold;"
            )
            method_layout.addWidget(rationale_title_label)
            rationale_label = QLabel(rationale_text)
            rationale_label.setWordWrap(True)
            rationale_label.setStyleSheet(
                "margin-left: 30px; margin-top: 2px;"
            )  # Indent text slightly under title
            method_layout.addWidget(rationale_label)

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

    def _create_arabic_tab(self):
        """Create the Arabic Abjad methods tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        title = QLabel("Arabic Abjad Methods")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        content_layout.addWidget(title)

        # Method data
        arabic_methods = [
            {
                "name": CalculationType.ARABIC_STANDARD_ABJAD.display_name,
                "description": CalculationType.ARABIC_STANDARD_ABJAD.description,
                "example": "Kitab (كتاب - book): ك(20) + ت(400) + ا(1) + ب(2) = 423. Allah (الله): ا(1) + ل(30) + ل(30) + ه(5) = 66 (Note: Interpretations of sacred names vary).",
                "rationale": "Why: This is the foundational system of letter-number correspondence in the Arabic tradition, derived from earlier Semitic alphabets. It's used to find the numerical essence of words, names, and phrases, particularly in esoteric interpretations of the Qur'an, poetry, and historical chronograms (tarikh).\nWhen: Used extensively in classical Islamic scholarship, Sufism, and various divinatory or talismanic practices. It's also employed for creating chronograms where the sum of letters in a phrase equals a specific year.",
                "notes": "The Abjad system has several variations (e.g., Eastern Abjad), but this represents the most common Western Abjad sequence (Abjad Hawwaz). Letters are valued 1-9, 10-90, 100-1000.",
            },
            # Add more Arabic methods here if defined in CalculationType
        ]

        for method_data in arabic_methods:
            self._add_detailed_method(content_layout, method_data)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab
