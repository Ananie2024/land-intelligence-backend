# app/services/location/storage_mapper.py
"""
Storage Mapper Service
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import List, Dict, Any, Tuple
from app.models.storage_cabinet import StorageCabinet

class StorageMapper:
    """
    Handles coordinate mapping, physical layout grids, and storage utility metrics.
    """

    @staticmethod
    def map_cabinet_layout_grid(cabinets: List[StorageCabinet]) -> Dict[str, Any]:
        """
        Organizes a list of cabinets in a physical location into a row-column grid representation.
        Useful for rendering visual maps of archive rooms.
        """
        grid: Dict[int, Dict[int, Any]] = {}
        unmapped: List[Dict[str, Any]] = []
        max_row = 0
        max_col = 0
        
        for cabinet in cabinets:
            row = cabinet.row_number
            col = cabinet.column_number
            
            cabinet_data = {
                "id": str(cabinet.id),
                "cabinet_number": cabinet.cabinet_number,
                "cabinet_type": cabinet.cabinet_type,
                "current_count": cabinet.current_count,
                "max_capacity": cabinet.max_capacity,
                "utilization_percentage": (
                    round((cabinet.current_count / cabinet.max_capacity) * 100, 2)
                    if cabinet.max_capacity and cabinet.max_capacity > 0
                    else 0.0
                )
            }
            
            if row is not None and col is not None:
                max_row = max(max_row, row)
                max_col = max(max_col, col)
                if row not in grid:
                    grid[row] = {}
                grid[row][col] = cabinet_data
            else:
                unmapped.append(cabinet_data)
                
        return {
            "grid": grid,
            "unmapped": unmapped,
            "dimensions": {
                "rows": max_row,
                "columns": max_col
            }
        }
