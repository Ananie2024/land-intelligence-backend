# app/utils/date_helpers.py
"""
Date Helpers Utility
Provides common utility functions for date calculations, string parsing, and formatting.
"""

from datetime import datetime, date
from typing import Union, Optional

def parse_date_string(date_str: Optional[str]) -> Optional[date]:
    """
    Parses a string in ISO or standard format into a python date object.
    
    Args:
        date_str: The date string (e.g., 'YYYY-MM-DD').
        
    Returns:
        A date object, or None if the input was empty or invalid.
    """
    if not date_str:
        return None
        
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
            
    # Try parsing first 10 characters if it's a long datetime string
    if len(date_str) > 10:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
            
    return None

def format_date_to_iso(d: Optional[Union[date, datetime]]) -> Optional[str]:
    """
    Formats a date or datetime object into ISO YYYY-MM-DD string.
    """
    if not d:
        return None
    return d.strftime("%Y-%m-%d")

def get_current_year() -> int:
    """
    Returns the current calendar year.
    """
    return date.today().year

def calculate_years_difference(start_date: date, end_date: date) -> int:
    """
    Calculates the absolute difference in full years between two dates.
    """
    return abs(end_date.year - start_date.year)
