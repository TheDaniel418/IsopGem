"""
KWIC Concordance Models for Document Manager.

This module defines the data models for Key Word In Context (KWIC) concordance
functionality, including concordance entries, tables, and their associations
with documents.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class ConcordanceEntry(BaseModel):
    """A single KWIC concordance entry representing a keyword in context."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    keyword: str = Field(..., description="The keyword being concordanced")
    left_context: str = Field(..., description="Text appearing before the keyword")
    right_context: str = Field(..., description="Text appearing after the keyword")
    position: int = Field(..., description="Character position of keyword in source text")
    line_number: Optional[int] = Field(None, description="Line number in source document")
    sentence_number: Optional[int] = Field(None, description="Sentence number in source document")
    paragraph_number: Optional[int] = Field(None, description="Paragraph number in source document")
    document_id: str = Field(..., description="ID of the source document")
    document_name: str = Field(..., description="Name of the source document")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('keyword')
    def keyword_must_not_be_empty(cls, v):
        """Validate that keyword is not empty."""
        if not v.strip():
            raise ValueError('Keyword cannot be empty')
        return v.strip()
    
    @validator('position')
    def position_must_be_non_negative(cls, v):
        """Validate that position is non-negative."""
        if v < 0:
            raise ValueError('Position must be non-negative')
        return v


class ConcordanceSettings(BaseModel):
    """Settings for generating KWIC concordances."""
    
    context_window: int = Field(default=50, description="Number of characters on each side of keyword")
    case_sensitive: bool = Field(default=False, description="Whether keyword matching is case-sensitive")
    whole_words_only: bool = Field(default=True, description="Whether to match whole words only")
    include_punctuation: bool = Field(default=True, description="Whether to include punctuation in context")
    min_keyword_length: int = Field(default=1, description="Minimum length for keywords")
    max_keyword_length: int = Field(default=100, description="Maximum length for keywords")
    exclude_common_words: bool = Field(default=False, description="Whether to exclude common stop words")
    sort_by: str = Field(default="keyword", description="Sort order: 'keyword', 'position', 'document'")
    group_by_document: bool = Field(default=False, description="Whether to group results by document")
    
    @validator('context_window')
    def context_window_must_be_positive(cls, v):
        """Validate that context window is positive."""
        if v <= 0:
            raise ValueError('Context window must be positive')
        return v
    
    @validator('sort_by')
    def sort_by_must_be_valid(cls, v):
        """Validate sort_by field."""
        valid_options = ['keyword', 'position', 'document', 'left_context', 'right_context']
        if v not in valid_options:
            raise ValueError(f'sort_by must be one of: {valid_options}')
        return v


class ConcordanceTable(BaseModel):
    """A complete KWIC concordance table with metadata."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Name of the concordance table")
    description: Optional[str] = Field(None, description="Description of the concordance")
    keywords: List[str] = Field(..., description="List of keywords used to generate this concordance")
    document_ids: List[str] = Field(..., description="List of document IDs included in this concordance")
    entries: List[ConcordanceEntry] = Field(default_factory=list, description="Concordance entries")
    settings: ConcordanceSettings = Field(default_factory=ConcordanceSettings)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="User who created this concordance")
    tags: List[str] = Field(default_factory=list, description="Tags for organizing concordances")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        """Validate that name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('keywords')
    def keywords_must_not_be_empty(cls, v):
        """Validate that keywords list is not empty."""
        if not v:
            raise ValueError('Keywords list cannot be empty')
        return [kw.strip() for kw in v if kw.strip()]
    
    def get_entry_count(self) -> int:
        """Get the total number of entries in this concordance."""
        return len(self.entries)
    
    def get_document_count(self) -> int:
        """Get the number of unique documents in this concordance."""
        return len(set(entry.document_id for entry in self.entries))
    
    def get_keyword_count(self) -> int:
        """Get the number of unique keywords in this concordance."""
        return len(set(entry.keyword for entry in self.entries))
    
    def get_entries_by_keyword(self, keyword: str) -> List[ConcordanceEntry]:
        """Get all entries for a specific keyword."""
        return [entry for entry in self.entries if entry.keyword.lower() == keyword.lower()]
    
    def get_entries_by_document(self, document_id: str) -> List[ConcordanceEntry]:
        """Get all entries from a specific document."""
        return [entry for entry in self.entries if entry.document_id == document_id]
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about this concordance table."""
        return {
            'total_entries': self.get_entry_count(),
            'unique_documents': self.get_document_count(),
            'unique_keywords': self.get_keyword_count(),
            'keywords_searched': len(self.keywords),
            'documents_searched': len(self.document_ids)
        }


class ConcordanceFilter(BaseModel):
    """Filter criteria for searching concordance entries."""
    
    keywords: Optional[List[str]] = Field(None, description="Filter by specific keywords")
    document_ids: Optional[List[str]] = Field(None, description="Filter by specific documents")
    document_names: Optional[List[str]] = Field(None, description="Filter by document names")
    left_context_contains: Optional[str] = Field(None, description="Filter by left context content")
    right_context_contains: Optional[str] = Field(None, description="Filter by right context content")
    min_position: Optional[int] = Field(None, description="Minimum position in document")
    max_position: Optional[int] = Field(None, description="Maximum position in document")
    date_from: Optional[datetime] = Field(None, description="Filter entries created after this date")
    date_to: Optional[datetime] = Field(None, description="Filter entries created before this date")
    tags: Optional[List[str]] = Field(None, description="Filter by concordance table tags")


class ConcordanceExportFormat(BaseModel):
    """Configuration for exporting concordance data."""
    
    format_type: str = Field(..., description="Export format: 'csv', 'tsv', 'json', 'html', 'txt'")
    include_metadata: bool = Field(default=True, description="Whether to include metadata")
    include_statistics: bool = Field(default=True, description="Whether to include statistics")
    sort_order: str = Field(default="keyword", description="Sort order for export")
    group_by_keyword: bool = Field(default=False, description="Whether to group by keyword")
    group_by_document: bool = Field(default=False, description="Whether to group by document")
    custom_delimiter: Optional[str] = Field(None, description="Custom delimiter for text formats")
    
    @validator('format_type')
    def format_type_must_be_valid(cls, v):
        """Validate export format type."""
        valid_formats = ['csv', 'tsv', 'json', 'html', 'txt', 'xlsx']
        if v.lower() not in valid_formats:
            raise ValueError(f'format_type must be one of: {valid_formats}')
        return v.lower()


class ConcordanceSearchResult(BaseModel):
    """Result of a concordance search operation."""
    
    entries: List[ConcordanceEntry] = Field(default_factory=list)
    total_count: int = Field(default=0, description="Total number of matching entries")
    filtered_count: int = Field(default=0, description="Number of entries after filtering")
    search_time_ms: float = Field(default=0.0, description="Search time in milliseconds")
    keywords_found: Set[str] = Field(default_factory=set, description="Keywords that had matches")
    documents_found: Set[str] = Field(default_factory=set, description="Documents that had matches")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True 