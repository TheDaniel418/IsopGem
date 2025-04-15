"""
Image storage utilities for the RTF editor.

This module provides functions for efficiently storing and retrieving images
used in RTF documents. Instead of embedding images as data URIs, it stores
them as files and references them by path.

Key features:
- Stores images in a dedicated directory
- Generates unique filenames to avoid conflicts
- Handles image conversion and optimization
- Provides functions for cleaning up unused images
"""

import os
import uuid
import base64
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, List

from PIL import Image
from PyQt6.QtCore import QBuffer, Qt
from PyQt6.QtGui import QImage

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
IMAGE_DIR = Path(os.path.expanduser("~")) / ".isopgem" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Cache for image dimensions
image_dimensions_cache: Dict[str, Tuple[int, int]] = {}


def get_image_storage_dir(document_id: str = None) -> Path:
    """Get the directory for storing images.
    
    If a document_id is provided, images will be stored in a subdirectory
    specific to that document.
    
    Args:
        document_id (str, optional): The document ID to create a subdirectory for
        
    Returns:
        Path: The path to the image storage directory
    """
    if document_id:
        # Create a document-specific subdirectory
        doc_dir = IMAGE_DIR / document_id
        doc_dir.mkdir(exist_ok=True)
        return doc_dir
    return IMAGE_DIR


def generate_unique_filename(original_path: str, document_id: str = None) -> str:
    """Generate a unique filename for an image.
    
    Creates a filename based on the original filename, current timestamp,
    and a UUID to ensure uniqueness.
    
    Args:
        original_path (str): The original path of the image
        document_id (str, optional): The document ID for organizing images
        
    Returns:
        str: A unique filename for the image
    """
    # Get the original extension
    path_obj = Path(original_path)
    extension = path_obj.suffix.lower()
    
    # Generate a unique name using timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # Use original filename as a base (without extension)
    base_name = path_obj.stem
    
    # Combine to create unique filename
    unique_name = f"{base_name}_{timestamp}_{unique_id}{extension}"
    
    return unique_name


def save_image_to_storage(
    image_path: str, 
    document_id: str = None,
    max_width: int = 2000,
    max_height: int = 2000,
    quality: int = 85
) -> Tuple[str, int, int]:
    """Save an image to the storage directory with optimization.
    
    Loads the image, optionally resizes it if it exceeds maximum dimensions,
    and saves it to the storage directory with the specified quality.
    
    Args:
        image_path (str): Path to the original image
        document_id (str, optional): Document ID for organizing images
        max_width (int): Maximum width for the image
        max_height (int): Maximum height for the image
        quality (int): JPEG quality (0-100) for compression
        
    Returns:
        Tuple[str, int, int]: Tuple containing (storage_path, width, height)
        
    Raises:
        ValueError: If the image cannot be loaded or saved
    """
    try:
        # Get storage directory
        storage_dir = get_image_storage_dir(document_id)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(image_path, document_id)
        
        # Full path for the stored image
        storage_path = storage_dir / unique_filename
        
        # Load the image with PIL
        with Image.open(image_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            
            # Check if resizing is needed
            if original_width > max_width or original_height > max_height:
                # Calculate new dimensions maintaining aspect ratio
                if original_width > original_height:
                    new_width = max_width
                    new_height = int(original_height * (max_width / original_width))
                else:
                    new_height = max_height
                    new_width = int(original_width * (max_height / original_height))
                
                # Resize the image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = new_width, new_height
                logger.info(f"Resized image from {original_width}x{original_height} to {width}x{height}")
            else:
                width, height = original_width, original_height
            
            # Determine format for saving
            save_format = "PNG"
            save_options = {}
            
            # Use original format if possible, with optimization
            if img.format == "JPEG":
                save_format = "JPEG"
                save_options = {"quality": quality, "optimize": True}
            elif img.format == "PNG":
                save_format = "PNG"
                save_options = {"optimize": True}
            
            # Save the image
            img.save(storage_path, format=save_format, **save_options)
            
            # Store dimensions in cache
            image_dimensions_cache[str(storage_path)] = (width, height)
            
            logger.info(f"Saved image to {storage_path}")
            return str(storage_path), width, height
            
    except Exception as e:
        logger.error(f"Error saving image to storage: {str(e)}", exc_info=True)
        raise ValueError(f"Could not save image: {str(e)}")


def data_uri_to_image_file(
    data_uri: str,
    document_id: str = None
) -> Tuple[str, int, int]:
    """Convert a data URI to an image file and save it to storage.
    
    Extracts the image data from a data URI, saves it to a temporary file,
    then processes it with save_image_to_storage.
    
    Args:
        data_uri (str): The data URI containing the image data
        document_id (str, optional): Document ID for organizing images
        
    Returns:
        Tuple[str, int, int]: Tuple containing (storage_path, width, height)
        
    Raises:
        ValueError: If the data URI is invalid or the image cannot be saved
    """
    try:
        # Check if it's a valid data URI
        if not data_uri.startswith("data:image/"):
            raise ValueError("Invalid data URI format")
        
        # Extract mime type and base64 data
        mime_type = data_uri.split(";")[0].split(":")[1]
        base64_data = data_uri.split(",")[1]
        
        # Determine file extension from mime type
        extension = ".png"  # Default
        if mime_type == "image/jpeg":
            extension = ".jpg"
        elif mime_type == "image/gif":
            extension = ".gif"
        
        # Create a temporary file
        temp_dir = Path(os.path.expanduser("~")) / ".isopgem" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = temp_dir / f"temp_image_{uuid.uuid4()}{extension}"
        
        # Decode and save the base64 data
        with open(temp_file, "wb") as f:
            f.write(base64.b64decode(base64_data))
        
        # Now save to storage with optimization
        try:
            result = save_image_to_storage(str(temp_file), document_id)
            
            # Clean up the temporary file
            if temp_file.exists():
                temp_file.unlink()
                
            return result
        except Exception as e:
            logger.error(f"Error processing data URI image: {str(e)}", exc_info=True)
            raise
            
    except Exception as e:
        logger.error(f"Error converting data URI to image: {str(e)}", exc_info=True)
        raise ValueError(f"Could not convert data URI: {str(e)}")


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """Get the dimensions of an image.
    
    Checks the cache first, then loads the image to get its dimensions.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        Tuple[int, int]: Width and height of the image
        
    Raises:
        ValueError: If the image cannot be loaded
    """
    # Check cache first
    if image_path in image_dimensions_cache:
        return image_dimensions_cache[image_path]
    
    try:
        # Load with PIL to get dimensions
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Cache the dimensions
            image_dimensions_cache[image_path] = (width, height)
            
            return width, height
    except Exception as e:
        logger.error(f"Error getting image dimensions: {str(e)}", exc_info=True)
        raise ValueError(f"Could not get image dimensions: {str(e)}")


def cleanup_unused_images(document_id: str, used_images: List[str]) -> int:
    """Clean up unused images for a document.
    
    Removes images that are no longer referenced by the document.
    
    Args:
        document_id (str): The document ID
        used_images (List[str]): List of image paths still in use
        
    Returns:
        int: Number of images removed
    """
    try:
        # Get the document's image directory
        doc_dir = get_image_storage_dir(document_id)
        
        # Skip if directory doesn't exist
        if not doc_dir.exists():
            return 0
        
        # Convert used_images to absolute paths
        used_images_abs = [str(Path(path).absolute()) for path in used_images]
        
        # Find all images in the directory
        all_images = list(doc_dir.glob("*.*"))
        
        # Identify unused images
        removed_count = 0
        for img_path in all_images:
            abs_path = str(img_path.absolute())
            if abs_path not in used_images_abs:
                # Remove the unused image
                img_path.unlink()
                removed_count += 1
                
                # Remove from cache if present
                if abs_path in image_dimensions_cache:
                    del image_dimensions_cache[abs_path]
        
        logger.info(f"Cleaned up {removed_count} unused images for document {document_id}")
        return removed_count
        
    except Exception as e:
        logger.error(f"Error cleaning up unused images: {str(e)}", exc_info=True)
        return 0


def export_document_with_images(document_id: str, export_dir: Path) -> List[str]:
    """Export all images for a document to a specified directory.
    
    Copies all images associated with a document to the export directory,
    maintaining the same filenames.
    
    Args:
        document_id (str): The document ID
        export_dir (Path): Directory to export images to
        
    Returns:
        List[str]: List of exported image paths
    """
    try:
        # Get the document's image directory
        doc_dir = get_image_storage_dir(document_id)
        
        # Skip if directory doesn't exist
        if not doc_dir.exists():
            return []
        
        # Create images subdirectory in export directory
        export_images_dir = export_dir / "images"
        export_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all images in the document directory
        all_images = list(doc_dir.glob("*.*"))
        
        # Copy each image to the export directory
        exported_paths = []
        for img_path in all_images:
            # Destination path
            dest_path = export_images_dir / img_path.name
            
            # Copy the file
            shutil.copy2(img_path, dest_path)
            
            # Add to list of exported paths
            exported_paths.append(str(dest_path))
        
        logger.info(f"Exported {len(exported_paths)} images for document {document_id}")
        return exported_paths
        
    except Exception as e:
        logger.error(f"Error exporting document images: {str(e)}", exc_info=True)
        return []