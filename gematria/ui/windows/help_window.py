"""
Purpose: Provides a standalone window for displaying gematria help information

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for gematria help content,
allowing users to learn about gematria methods and functionality.

Key components:
- HelpWindow: Standalone window for gematria help

Dependencies:
- PyQt6: For UI components
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QTextBrowser, QVBoxLayout, QWidget


class HelpWindow(QMainWindow):
    """Standalone window for displaying gematria help information."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the help window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Help")
        self.setMinimumSize(800, 600)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Add tabs
        self._add_overview_tab()
        self._add_methods_tab()
        self._add_word_abacus_tab()
        self._add_calculator_tab()
        self._add_search_tab()
        self._add_history_tab()
        self._add_tags_tab()

        logger.debug("HelpWindow initialized")

    def _add_overview_tab(self) -> None:
        """Add the overview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Gematria Overview</h1>
            <p>Gematria is a system of assigning numerical values to letters.
            It has been used in various cultures, but is most notably associated with
            Hebrew and Jewish mysticism.</p>

            <p>In Hebrew gematria, each letter of the Hebrew alphabet has a numerical value.
            By summing these values for a word or phrase, one can derive its numerical equivalent.</p>

            <h2>Basic Principles</h2>
            <ul>
                <li>Each Hebrew letter has a numerical value</li>
                <li>Words and phrases can be represented by the sum of their letters</li>
                <li>Words with the same numerical value may have a mystical connection</li>
                <li>Various methods exist for calculating gematria values</li>
            </ul>

            <h2>IsopGem Features</h2>
            <ul>
                <li>Multiple calculation methods for Hebrew and English</li>
                <li>Word Abacus for precise calculations</li>
                <li>Comprehensive search capabilities</li>
                <li>Calculation history and tagging system</li>
            </ul>
            """
        )

        self.tab_widget.addTab(tab, "Overview")

    def _add_methods_tab(self) -> None:
        """Add the methods tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Gematria Methods</h1>

            <h2>Hebrew Methods</h2>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Method</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>Standard (Mispar Hechrechi)</td>
                    <td>The standard value of each letter</td>
                </tr>
                <tr>
                    <td>Ordinal (Mispar Siduri)</td>
                    <td>Position in the alphabet</td>
                </tr>
                <tr>
                    <td>Reduced (Mispar Katan)</td>
                    <td>Single-digit reduction</td>
                </tr>
                <tr>
                    <td>Complete (Mispar Shemi)</td>
                    <td>Value of the spelled-out name of the letter</td>
                </tr>
                <tr>
                    <td>Full (Mispar Haklali)</td>
                    <td>Sum of all letters in a word plus the word itself</td>
                </tr>
            </table>

            <h2>English Methods</h2>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Method</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>English Ordinal</td>
                    <td>A=1, B=2, ..., Z=26</td>
                </tr>
                <tr>
                    <td>English Reduced</td>
                    <td>Single-digit reduction of ordinal values</td>
                </tr>
                <tr>
                    <td>English Sumerian</td>
                    <td>A=6, B=12, ..., Z=156</td>
                </tr>
                <tr>
                    <td>English Pythagorean</td>
                    <td>A=1, B=2, ..., I=9, J=1, ...</td>
                </tr>
            </table>

            <h2>Custom Methods</h2>
            <p>You can create custom cipher methods in the application with your own value assignments.</p>
            """
        )

        self.tab_widget.addTab(tab, "Methods")

    def _add_word_abacus_tab(self) -> None:
        """Add the Word Abacus tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Word Abacus</h1>
            <p>The Word Abacus is a specialized calculator for precise gematria calculations.</p>

            <h2>Features</h2>
            <ul>
                <li>Input Hebrew or English text</li>
                <li>Choose from multiple calculation methods</li>
                <li>See the values of individual letters</li>
                <li>Save calculations to history</li>
                <li>Compare multiple calculations</li>
            </ul>

            <h2>How to Use</h2>
            <ol>
                <li>Enter text in the input field</li>
                <li>Select a calculation method</li>
                <li>Click "Calculate" to see the result</li>
                <li>Use "Save" to add the calculation to your history</li>
            </ol>

            <h2>Tips</h2>
            <ul>
                <li>Use the letter board to enter Hebrew characters if needed</li>
                <li>Hover over letters to see their individual values</li>
                <li>Multiple methods can be selected for comparison</li>
            </ul>
            """
        )

        self.tab_widget.addTab(tab, "Word Abacus")

    def _add_calculator_tab(self) -> None:
        """Add the calculator tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Quick Calculator</h1>
            <p>The Quick Calculator provides a streamlined interface for rapid gematria calculations.</p>

            <h2>Features</h2>
            <ul>
                <li>Simplified interface for fast calculations</li>
                <li>Preset calculation methods</li>
                <li>Quick save options</li>
                <li>History integration</li>
            </ul>

            <h2>How to Use</h2>
            <ol>
                <li>Enter text in the input field</li>
                <li>Choose a method from the dropdown</li>
                <li>Results appear immediately</li>
                <li>Click the save icon to store in history</li>
            </ol>
            """
        )

        self.tab_widget.addTab(tab, "Calculator")

    def _add_search_tab(self) -> None:
        """Add the search tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Gematria Search</h1>
            <p>The search functionality allows you to find words, phrases, or numbers with specific gematria values.</p>

            <h2>Search Types</h2>
            <ul>
                <li><b>Value Search</b>: Find words with a specific numerical value</li>
                <li><b>Word Search</b>: Find the gematria value of a specific word</li>
                <li><b>Range Search</b>: Find words within a numerical range</li>
                <li><b>Pattern Search</b>: Find matching patterns across calculation methods</li>
            </ul>

            <h2>Advanced Features</h2>
            <ul>
                <li>Filter by calculation method</li>
                <li>Filter by tags</li>
                <li>Sort results by different criteria</li>
                <li>Save search results</li>
            </ul>
            """
        )

        self.tab_widget.addTab(tab, "Search")

    def _add_history_tab(self) -> None:
        """Add the history tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Calculation History</h1>
            <p>The calculation history feature stores all your saved calculations for future reference.</p>

            <h2>Features</h2>
            <ul>
                <li>View all saved calculations</li>
                <li>Sort by date, value, or text</li>
                <li>Filter by calculation method or tags</li>
                <li>Add notes to calculations</li>
                <li>Mark calculations as favorites</li>
                <li>Export calculation history</li>
            </ul>

            <h2>How to Use</h2>
            <ol>
                <li>Save calculations from the Word Abacus or Calculator</li>
                <li>Open the Calculation History to view them</li>
                <li>Click on any calculation to see details</li>
                <li>Use the filter options to find specific calculations</li>
                <li>Right-click for additional options</li>
            </ol>
            """
        )

        self.tab_widget.addTab(tab, "History")

    def _add_tags_tab(self) -> None:
        """Add the tags tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        text_browser.setHtml(
            """
            <h1>Tags System</h1>
            <p>The tagging system allows you to organize and categorize your calculations.</p>

            <h2>Features</h2>
            <ul>
                <li>Create custom tags with colors</li>
                <li>Assign multiple tags to calculations</li>
                <li>Filter calculations by tags</li>
                <li>Manage tag hierarchies</li>
                <li>Bulk tag operations</li>
            </ul>

            <h2>Tag Management</h2>
            <ol>
                <li>Create tags in the Tag Management window</li>
                <li>Assign colors and descriptions to tags</li>
                <li>Organize tags in hierarchies if needed</li>
                <li>Apply tags to calculations in the History view</li>
                <li>Use tags for filtering in Search and History</li>
            </ol>
            """
        )

        self.tab_widget.addTab(tab, "Tags")
