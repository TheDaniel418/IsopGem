"""
Purpose: Exports the RTF Editor model components.

This file is part of the shared UI widgets and serves as the models package initialization.
It provides access to data models used by the RTF Editor components.
"""

from shared.ui.widgets.rtf_editor.models.document_format import (
    AnnotationMetadata,
    DocumentFormat,
    ImageMetadata,
    TableMetadata,
)

__all__ = [
    "DocumentFormat",
    "AnnotationMetadata",
    "ImageMetadata",
    "TableMetadata",
]
