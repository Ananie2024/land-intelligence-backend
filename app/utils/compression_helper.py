# app/utils/compression_helper.py
"""
Compression Helper Utility
Provides functions for zip-based compression and decompression.
"""

import zipfile
from pathlib import Path
from typing import Union

def compress_directory(source_dir: Union[str, Path], output_zip: Union[str, Path], include_root: bool = False) -> None:
    """
    Compresses a directory into a ZIP archive.
    
    Args:
        source_dir: Path to directory to compress.
        output_zip: Path where the output ZIP file will be saved.
        include_root: If True, includes the root directory in the archive structure.
    """
    src_path = Path(source_dir).resolve()
    zip_path = Path(output_zip).resolve()
    
    # Create parent directories if they don't exist
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source directory {src_path} does not exist.")
    if not src_path.is_dir():
        raise NotADirectoryError(f"Source path {src_path} is not a directory.")
        
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in src_path.rglob("*"):
            if file_path.is_file():
                # Determine archive path relative to the source directory
                if include_root:
                    archive_name = src_path.name / file_path.relative_to(src_path)
                else:
                    archive_name = file_path.relative_to(src_path)
                zip_file.write(file_path, arcname=str(archive_name))

def compress_file(source_file: Union[str, Path], output_zip: Union[str, Path]) -> None:
    """
    Compresses a single file into a ZIP archive.
    
    Args:
        source_file: Path to file to compress.
        output_zip: Path where the output ZIP file will be saved.
    """
    src_path = Path(source_file).resolve()
    zip_path = Path(output_zip).resolve()
    
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source file {src_path} does not exist.")
    if not src_path.is_file():
        raise IsADirectoryError(f"Source path {src_path} is not a file.")
        
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(src_path, arcname=src_path.name)

def decompress_archive(zip_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
    """
    Extracts a ZIP archive to a destination directory.
    
    Args:
        zip_path: Path to the ZIP archive.
        output_dir: Path where the contents will be extracted.
    """
    archive_path = Path(zip_path).resolve()
    dest_path = Path(output_dir).resolve()
    
    dest_path.mkdir(parents=True, exist_ok=True)
    
    if not archive_path.exists():
        raise FileNotFoundError(f"ZIP file {archive_path} does not exist.")
    if not zipfile.is_zipfile(archive_path):
        raise zipfile.BadZipFile(f"File {archive_path} is not a valid ZIP file.")
        
    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(dest_path)
