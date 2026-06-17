# app/services/qr/qr_generator.py
"""
QR Code Generator Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import os
import uuid
import json
import logging
import qrcode
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class QRGenerator:
    """
    Handles generation of QR code images.
    
    Creates high-quality QR codes with data payloads and saves them 
    to the configured file storage.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize QR generator.
        
        Args:
            storage_path: Base path for storing QR images
        """
        self.base_path = Path(storage_path or settings.FILE_STORAGE_PATH) / "qr_codes"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def generate(
        self, 
        data: Dict[str, Any], 
        prefix: str = "QR",
        error_correction: int = qrcode.constants.ERROR_CORRECT_H,
        box_size: int = 10,
        border: int = 4
    ) -> tuple[str, str]:
        """
        Generate a QR code image from a data dictionary.
        
        Args:
            data: Dictionary to encode in QR (will be converted to JSON)
            prefix: Prefix for the unique code
            error_correction: QR error correction level
            box_size: Size of each box in the QR grid
            border: Border width
            
        Returns:
            Tuple of (unique_code, file_path)
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Generate unique identifier for this QR
            unique_id = str(uuid.uuid4())
            qr_code_str = f"{prefix}_{unique_id[:8].upper()}_{datetime.now().strftime('%Y%m%d')}"
            
            # Prepare data payload (JSON)
            payload = json.dumps(data)
            
            # Configure QR generator
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=error_correction,
                box_size=box_size,
                border=border,
            )
            
            qr.add_data(payload)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Define file path
            filename = f"{qr_code_str}.png"
            file_path = self.base_path / filename
            
            # Save image
            img.save(file_path)
            
            logger.info(f"QR code generated: {qr_code_str} saved to {file_path}")
            
            return qr_code_str, str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {str(e)}")
            raise

    def delete_image(self, file_path: str) -> bool:
        """
        Delete a QR code image file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                os.remove(path)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete QR image {file_path}: {str(e)}")
            return False
