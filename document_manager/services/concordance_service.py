"""
Concordance Service for Document Manager.

This module provides business logic for generating, managing, and exporting
KWIC (Key Word In Context) concordances from document text content.
"""

import csv
import json
import re
import time
from collections import defaultdict
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional, Set, Tuple

from document_manager.models.document import Document
from document_manager.models.kwic_concordance import (
    ConcordanceEntry,
    ConcordanceExportFormat,
    ConcordanceFilter,
    ConcordanceSearchResult,
    ConcordanceSettings,
    ConcordanceTable,
)
from document_manager.repositories.concordance_repository import ConcordanceRepository
from document_manager.services.document_service import DocumentService


class ConcordanceService:
    """Service for generating and managing KWIC concordances."""
    
    # Common English stop words (can be expanded)
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'would', 'i', 'you', 'we', 'they',
        'this', 'these', 'those', 'but', 'or', 'not', 'have', 'had',
        'do', 'does', 'did', 'can', 'could', 'should', 'would', 'may',
        'might', 'must', 'shall', 'will', 'am', 'is', 'are', 'was', 'were'
    }
    
    def __init__(self, concordance_repository: ConcordanceRepository, document_service: DocumentService):
        """Initialize the concordance service.
        
        Args:
            concordance_repository: Repository for concordance data persistence
            document_service: Service for document operations
        """
        self.concordance_repository = concordance_repository
        self.document_service = document_service
    
    def generate_concordance(
        self,
        name: str,
        keywords: List[str],
        document_ids: List[str],
        settings: Optional[ConcordanceSettings] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> ConcordanceTable:
        """Generate a KWIC concordance for specified keywords and documents.
        
        Args:
            name: Name for the concordance table
            keywords: List of keywords to search for
            document_ids: List of document IDs to search in
            settings: Concordance generation settings
            description: Optional description
            tags: Optional tags for organization
            created_by: Optional user identifier
            
        Returns:
            Generated concordance table
            
        Raises:
            ValueError: If no keywords or documents provided
        """
        if not keywords:
            raise ValueError("At least one keyword must be provided")
        
        if not document_ids:
            raise ValueError("At least one document must be provided")
        
        # Use default settings if none provided
        if settings is None:
            settings = ConcordanceSettings()
        
        # Clean and validate keywords
        cleaned_keywords = self._clean_keywords(keywords, settings)
        
        # Get documents
        documents = []
        for doc_id in document_ids:
            doc = self.document_service.get_document(doc_id)
            if doc and doc.content:
                documents.append(doc)
        
        if not documents:
            raise ValueError("No valid documents with content found")
        
        # Generate concordance entries
        entries = []
        for document in documents:
            doc_entries = self._generate_document_concordance(
                document, cleaned_keywords, settings
            )
            entries.extend(doc_entries)
        
        # Sort entries according to settings
        entries = self._sort_entries(entries, settings)
        
        # Create concordance table
        concordance_table = ConcordanceTable(
            name=name,
            description=description,
            keywords=cleaned_keywords,
            document_ids=document_ids,
            entries=entries,
            settings=settings,
            created_by=created_by,
            tags=tags or []
        )
        
        return concordance_table
    
    def save_concordance(self, concordance_table: ConcordanceTable) -> str:
        """Save a concordance table to the database.
        
        Args:
            concordance_table: The concordance table to save
            
        Returns:
            The ID of the saved table
        """
        return self.concordance_repository.save_concordance_table(concordance_table)
    
    def get_concordance(self, table_id: str) -> Optional[ConcordanceTable]:
        """Retrieve a concordance table by ID.
        
        Args:
            table_id: The ID of the table to retrieve
            
        Returns:
            The concordance table if found, None otherwise
        """
        return self.concordance_repository.get_concordance_table(table_id)
    
    def get_concordance_by_name(self, name: str) -> Optional[ConcordanceTable]:
        """Retrieve a concordance table by name.
        
        Args:
            name: The name of the table to retrieve
            
        Returns:
            The concordance table if found, None otherwise
        """
        return self.concordance_repository.get_concordance_table_by_name(name)
    
    def list_concordances(self) -> List[Dict]:
        """List all concordance tables with metadata.
        
        Returns:
            List of concordance table metadata
        """
        return self.concordance_repository.list_concordance_tables()
    
    def delete_concordance(self, table_id: str) -> bool:
        """Delete a concordance table.
        
        Args:
            table_id: The ID of the table to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.concordance_repository.delete_concordance_table(table_id)
    
    def search_concordances(
        self,
        table_id: Optional[str] = None,
        filter_criteria: Optional[ConcordanceFilter] = None
    ) -> ConcordanceSearchResult:
        """Search concordance entries with filtering.
        
        Args:
            table_id: Optional table ID to limit search
            filter_criteria: Optional filter criteria
            
        Returns:
            Search results with entries and metadata
        """
        start_time = time.time()
        
        entries = self.concordance_repository.search_concordance_entries(
            table_id=table_id,
            filter_criteria=filter_criteria
        )
        
        search_time_ms = (time.time() - start_time) * 1000
        
        # Collect statistics
        keywords_found = set(entry.keyword for entry in entries)
        documents_found = set(entry.document_id for entry in entries)
        
        return ConcordanceSearchResult(
            entries=entries,
            total_count=len(entries),
            filtered_count=len(entries),
            search_time_ms=search_time_ms,
            keywords_found=keywords_found,
            documents_found=documents_found
        )
    
    def export_concordance(
        self,
        table_id: str,
        export_format: ConcordanceExportFormat
    ) -> str:
        """Export a concordance table to various formats.
        
        Args:
            table_id: ID of the concordance table to export
            export_format: Export format configuration
            
        Returns:
            Exported data as string
            
        Raises:
            ValueError: If table not found or invalid format
        """
        table = self.get_concordance(table_id)
        if not table:
            raise ValueError(f"Concordance table {table_id} not found")
        
        if export_format.format_type == 'csv':
            return self._export_to_csv(table, export_format)
        elif export_format.format_type == 'tsv':
            return self._export_to_tsv(table, export_format)
        elif export_format.format_type == 'json':
            return self._export_to_json(table, export_format)
        elif export_format.format_type == 'html':
            return self._export_to_html(table, export_format)
        elif export_format.format_type == 'txt':
            return self._export_to_txt(table, export_format)
        else:
            raise ValueError(f"Unsupported export format: {export_format.format_type}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get overall concordance statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        return self.concordance_repository.get_concordance_statistics()
    
    def extract_keywords_from_text(
        self,
        text: str,
        min_length: int = 3,
        max_length: int = 20,
        exclude_stop_words: bool = True,
        min_frequency: int = 2
    ) -> List[Tuple[str, int]]:
        """Extract potential keywords from text based on frequency.
        
        Args:
            text: Text to extract keywords from
            min_length: Minimum keyword length
            max_length: Maximum keyword length
            exclude_stop_words: Whether to exclude common stop words
            min_frequency: Minimum frequency for a word to be considered
            
        Returns:
            List of (keyword, frequency) tuples sorted by frequency
        """
        # Tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter words
        filtered_words = []
        for word in words:
            if len(word) < min_length or len(word) > max_length:
                continue
            if exclude_stop_words and word in self.STOP_WORDS:
                continue
            filtered_words.append(word)
        
        # Count frequencies
        word_counts = defaultdict(int)
        for word in filtered_words:
            word_counts[word] += 1
        
        # Filter by minimum frequency and sort
        keywords = [
            (word, count) for word, count in word_counts.items()
            if count >= min_frequency
        ]
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        return keywords
    
    def _clean_keywords(self, keywords: List[str], settings: ConcordanceSettings) -> List[str]:
        """Clean and validate keywords based on settings.
        
        Args:
            keywords: Raw keywords list
            settings: Concordance settings
            
        Returns:
            Cleaned keywords list
        """
        cleaned = []
        for keyword in keywords:
            keyword = keyword.strip()
            if not keyword:
                continue
            
            if len(keyword) < settings.min_keyword_length:
                continue
            
            if len(keyword) > settings.max_keyword_length:
                continue
            
            if settings.exclude_common_words and keyword.lower() in self.STOP_WORDS:
                continue
            
            if not settings.case_sensitive:
                keyword = keyword.lower()
            
            if keyword not in cleaned:
                cleaned.append(keyword)
        
        return cleaned
    
    def _generate_document_concordance(
        self,
        document: Document,
        keywords: List[str],
        settings: ConcordanceSettings
    ) -> List[ConcordanceEntry]:
        """Generate concordance entries for a single document.
        
        Args:
            document: Document to process
            keywords: Keywords to search for
            settings: Concordance settings
            
        Returns:
            List of concordance entries
        """
        entries = []
        text = document.content
        
        # Calculate line and paragraph positions if needed
        lines = text.split('\n')
        line_positions = self._calculate_line_positions(text)
        paragraph_positions = self._calculate_paragraph_positions(text)
        
        for keyword in keywords:
            keyword_entries = self._find_keyword_occurrences(
                text, keyword, document, settings, 
                line_positions, paragraph_positions
            )
            entries.extend(keyword_entries)
        
        return entries
    
    def _find_keyword_occurrences(
        self,
        text: str,
        keyword: str,
        document: Document,
        settings: ConcordanceSettings,
        line_positions: List[int],
        paragraph_positions: List[int]
    ) -> List[ConcordanceEntry]:
        """Find all occurrences of a keyword in text.
        
        Args:
            text: Text to search in
            keyword: Keyword to search for
            document: Source document
            settings: Concordance settings
            line_positions: Line start positions
            paragraph_positions: Paragraph start positions
            
        Returns:
            List of concordance entries for this keyword
        """
        entries = []
        
        # Build regex pattern
        if settings.whole_words_only:
            pattern = r'\b' + re.escape(keyword) + r'\b'
        else:
            pattern = re.escape(keyword)
        
        flags = 0 if settings.case_sensitive else re.IGNORECASE
        
        # Find all matches
        for match in re.finditer(pattern, text, flags):
            start_pos = match.start()
            end_pos = match.end()
            
            # Extract context
            left_start = max(0, start_pos - settings.context_window)
            right_end = min(len(text), end_pos + settings.context_window)
            
            left_context = text[left_start:start_pos]
            right_context = text[end_pos:right_end]
            
            # Clean context if needed
            if not settings.include_punctuation:
                left_context = re.sub(r'[^\w\s]', '', left_context)
                right_context = re.sub(r'[^\w\s]', '', right_context)
            
            # Calculate line and paragraph numbers
            line_number = self._find_line_number(start_pos, line_positions)
            paragraph_number = self._find_paragraph_number(start_pos, paragraph_positions)
            
            # Create entry
            entry = ConcordanceEntry(
                keyword=text[start_pos:end_pos],  # Preserve original case
                left_context=left_context.strip(),
                right_context=right_context.strip(),
                position=start_pos,
                line_number=line_number,
                paragraph_number=paragraph_number,
                document_id=document.id,
                document_name=document.name
            )
            
            entries.append(entry)
        
        return entries
    
    def _calculate_line_positions(self, text: str) -> List[int]:
        """Calculate the starting positions of each line.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of line start positions
        """
        positions = [0]
        for i, char in enumerate(text):
            if char == '\n':
                positions.append(i + 1)
        return positions
    
    def _calculate_paragraph_positions(self, text: str) -> List[int]:
        """Calculate the starting positions of each paragraph.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of paragraph start positions
        """
        positions = [0]
        lines = text.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '' and i < len(lines) - 1:
                # Empty line indicates paragraph break
                next_line_pos = current_pos + len(line) + 1
                if next_line_pos < len(text):
                    positions.append(next_line_pos)
            current_pos += len(line) + 1
        
        return positions
    
    def _find_line_number(self, position: int, line_positions: List[int]) -> int:
        """Find the line number for a given position.
        
        Args:
            position: Character position
            line_positions: List of line start positions
            
        Returns:
            Line number (1-based)
        """
        for i, line_start in enumerate(line_positions):
            if i == len(line_positions) - 1 or position < line_positions[i + 1]:
                return i + 1
        return len(line_positions)
    
    def _find_paragraph_number(self, position: int, paragraph_positions: List[int]) -> int:
        """Find the paragraph number for a given position.
        
        Args:
            position: Character position
            paragraph_positions: List of paragraph start positions
            
        Returns:
            Paragraph number (1-based)
        """
        for i, para_start in enumerate(paragraph_positions):
            if i == len(paragraph_positions) - 1 or position < paragraph_positions[i + 1]:
                return i + 1
        return len(paragraph_positions)
    
    def _sort_entries(self, entries: List[ConcordanceEntry], settings: ConcordanceSettings) -> List[ConcordanceEntry]:
        """Sort concordance entries according to settings.
        
        Args:
            entries: Entries to sort
            settings: Concordance settings
            
        Returns:
            Sorted entries
        """
        if settings.sort_by == 'keyword':
            entries.sort(key=lambda e: (e.keyword.lower(), e.position))
        elif settings.sort_by == 'position':
            entries.sort(key=lambda e: (e.document_id, e.position))
        elif settings.sort_by == 'document':
            entries.sort(key=lambda e: (e.document_name, e.keyword.lower(), e.position))
        elif settings.sort_by == 'left_context':
            entries.sort(key=lambda e: e.left_context.lower())
        elif settings.sort_by == 'right_context':
            entries.sort(key=lambda e: e.right_context.lower())
        
        return entries
    
    def _export_to_csv(self, table: ConcordanceTable, export_format: ConcordanceExportFormat) -> str:
        """Export concordance table to CSV format.
        
        Args:
            table: Concordance table to export
            export_format: Export configuration
            
        Returns:
            CSV data as string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = ['Keyword', 'Left Context', 'Right Context', 'Position', 'Document']
        if export_format.include_metadata:
            headers.extend(['Line Number', 'Paragraph Number', 'Created At'])
        writer.writerow(headers)
        
        # Sort entries if needed
        entries = table.entries
        if export_format.group_by_keyword:
            entries = sorted(entries, key=lambda e: e.keyword.lower())
        elif export_format.group_by_document:
            entries = sorted(entries, key=lambda e: e.document_name)
        
        # Write entries
        for entry in entries:
            row = [
                entry.keyword,
                entry.left_context,
                entry.right_context,
                entry.position,
                entry.document_name
            ]
            
            if export_format.include_metadata:
                row.extend([
                    entry.line_number or '',
                    entry.paragraph_number or '',
                    entry.created_at.isoformat()
                ])
            
            writer.writerow(row)
        
        # Add statistics if requested
        if export_format.include_statistics:
            writer.writerow([])
            writer.writerow(['Statistics'])
            stats = table.get_statistics()
            for key, value in stats.items():
                writer.writerow([key.replace('_', ' ').title(), value])
        
        return output.getvalue()
    
    def _export_to_tsv(self, table: ConcordanceTable, export_format: ConcordanceExportFormat) -> str:
        """Export concordance table to TSV format."""
        # Use CSV export with tab delimiter
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')
        
        # Similar to CSV but with tab delimiter
        headers = ['Keyword', 'Left Context', 'Right Context', 'Position', 'Document']
        if export_format.include_metadata:
            headers.extend(['Line Number', 'Paragraph Number', 'Created At'])
        writer.writerow(headers)
        
        entries = table.entries
        if export_format.group_by_keyword:
            entries = sorted(entries, key=lambda e: e.keyword.lower())
        elif export_format.group_by_document:
            entries = sorted(entries, key=lambda e: e.document_name)
        
        for entry in entries:
            row = [
                entry.keyword,
                entry.left_context,
                entry.right_context,
                entry.position,
                entry.document_name
            ]
            
            if export_format.include_metadata:
                row.extend([
                    entry.line_number or '',
                    entry.paragraph_number or '',
                    entry.created_at.isoformat()
                ])
            
            writer.writerow(row)
        
        if export_format.include_statistics:
            writer.writerow([])
            writer.writerow(['Statistics'])
            stats = table.get_statistics()
            for key, value in stats.items():
                writer.writerow([key.replace('_', ' ').title(), value])
        
        return output.getvalue()
    
    def _export_to_json(self, table: ConcordanceTable, export_format: ConcordanceExportFormat) -> str:
        """Export concordance table to JSON format."""
        data = {
            'concordance_table': {
                'id': table.id,
                'name': table.name,
                'description': table.description,
                'created_at': table.created_at.isoformat(),
                'updated_at': table.updated_at.isoformat(),
                'keywords': table.keywords,
                'tags': table.tags
            },
            'entries': []
        }
        
        entries = table.entries
        if export_format.group_by_keyword:
            entries = sorted(entries, key=lambda e: e.keyword.lower())
        elif export_format.group_by_document:
            entries = sorted(entries, key=lambda e: e.document_name)
        
        for entry in entries:
            entry_data = {
                'keyword': entry.keyword,
                'left_context': entry.left_context,
                'right_context': entry.right_context,
                'position': entry.position,
                'document_name': entry.document_name
            }
            
            if export_format.include_metadata:
                entry_data.update({
                    'line_number': entry.line_number,
                    'paragraph_number': entry.paragraph_number,
                    'document_id': entry.document_id,
                    'created_at': entry.created_at.isoformat()
                })
            
            data['entries'].append(entry_data)
        
        if export_format.include_statistics:
            data['statistics'] = table.get_statistics()
        
        return json.dumps(data, indent=2)
    
    def _export_to_html(self, table: ConcordanceTable, export_format: ConcordanceExportFormat) -> str:
        """Export concordance table to HTML format."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KWIC Concordance: {table.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .keyword {{ font-weight: bold; color: #d63384; }}
                .context {{ font-family: monospace; }}
                .stats {{ margin-top: 20px; background-color: #f8f9fa; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>KWIC Concordance: {table.name}</h1>
        """
        
        if table.description:
            html += f"<p><strong>Description:</strong> {table.description}</p>"
        
        html += f"""
            <p><strong>Keywords:</strong> {', '.join(table.keywords)}</p>
            <p><strong>Created:</strong> {table.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Left Context</th>
                        <th>Keyword</th>
                        <th>Right Context</th>
                        <th>Document</th>
        """
        
        if export_format.include_metadata:
            html += "<th>Position</th><th>Line</th><th>Paragraph</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        entries = table.entries
        if export_format.group_by_keyword:
            entries = sorted(entries, key=lambda e: e.keyword.lower())
        elif export_format.group_by_document:
            entries = sorted(entries, key=lambda e: e.document_name)
        
        for entry in entries:
            html += f"""
                <tr>
                    <td class="context">{entry.left_context}</td>
                    <td class="keyword">{entry.keyword}</td>
                    <td class="context">{entry.right_context}</td>
                    <td>{entry.document_name}</td>
            """
            
            if export_format.include_metadata:
                html += f"""
                    <td>{entry.position}</td>
                    <td>{entry.line_number or ''}</td>
                    <td>{entry.paragraph_number or ''}</td>
                """
            
            html += "</tr>"
        
        html += "</tbody></table>"
        
        if export_format.include_statistics:
            stats = table.get_statistics()
            html += """
                <div class="stats">
                    <h3>Statistics</h3>
                    <ul>
            """
            for key, value in stats.items():
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
            html += "</ul></div>"
        
        html += "</body></html>"
        return html
    
    def _export_to_txt(self, table: ConcordanceTable, export_format: ConcordanceExportFormat) -> str:
        """Export concordance table to plain text format."""
        lines = []
        lines.append(f"KWIC Concordance: {table.name}")
        lines.append("=" * (len(table.name) + 17))
        lines.append("")
        
        if table.description:
            lines.append(f"Description: {table.description}")
            lines.append("")
        
        lines.append(f"Keywords: {', '.join(table.keywords)}")
        lines.append(f"Created: {table.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        entries = table.entries
        if export_format.group_by_keyword:
            entries = sorted(entries, key=lambda e: e.keyword.lower())
        elif export_format.group_by_document:
            entries = sorted(entries, key=lambda e: e.document_name)
        
        # Calculate column widths
        max_left = max(len(entry.left_context) for entry in entries) if entries else 20
        max_keyword = max(len(entry.keyword) for entry in entries) if entries else 10
        max_right = max(len(entry.right_context) for entry in entries) if entries else 20
        max_doc = max(len(entry.document_name) for entry in entries) if entries else 15
        
        # Limit column widths for readability
        max_left = min(max_left, 40)
        max_right = min(max_right, 40)
        max_doc = min(max_doc, 30)
        
        # Header
        header = f"{'Left Context':<{max_left}} | {'Keyword':<{max_keyword}} | {'Right Context':<{max_right}} | {'Document':<{max_doc}}"
        lines.append(header)
        lines.append("-" * len(header))
        
        # Entries
        for entry in entries:
            left = entry.left_context[:max_left].ljust(max_left)
            keyword = entry.keyword[:max_keyword].ljust(max_keyword)
            right = entry.right_context[:max_right].ljust(max_right)
            doc = entry.document_name[:max_doc].ljust(max_doc)
            
            line = f"{left} | {keyword} | {right} | {doc}"
            lines.append(line)
        
        if export_format.include_statistics:
            lines.append("")
            lines.append("Statistics:")
            lines.append("-" * 10)
            stats = table.get_statistics()
            for key, value in stats.items():
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines) 