"""Utilities for database column ordering configuration."""

import re
from typing import Dict, List, Optional


class DatabaseColumnOrderingUtils:
    """Utilities for parsing and applying database column ordering configuration."""
    
    @staticmethod
    def parse_column_weights(description_text: str) -> Optional[Dict[str, int]]:
        """Parse column weight configuration from database description text.
        
        Format: property-order: Name=10, Age=9, Email=8
        This configuration should be on a single line in the description.
        
        Args:
            description_text: Plain text from database description
            
        Returns:
            dict: {column_name: weight} or None if no configuration found
            
        Examples:
            >>> text = "Some description\n\nproperty-order: Name=100, Email=90\n\nMore text"
            >>> DatabaseColumnOrderingUtils.parse_column_weights(text)
            {'Name': 100, 'Email': 90}
            
            >>> text = "No configuration here"
            >>> DatabaseColumnOrderingUtils.parse_column_weights(text)
            None
        """
        if not description_text:
            return None
        
        # Match format: property-order: Name=10, Age=9, ...
        # The pattern matches from start of line (or after newline) to end of line
        # This ensures we only parse one line, not the entire description
        match = re.search(r'(?:^|\n)\s*property-order:\s*(.+?)(?:\n|$)', description_text, re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        
        weights = {}
        config_str = match.group(1).strip()
        
        # Parse each column=weight pair
        for item in config_str.split(','):
            item = item.strip()
            if '=' in item:
                col_name, weight_str = item.split('=', 1)
                col_name = col_name.strip()
                try:
                    weight = int(weight_str.strip())
                    weights[col_name] = weight
                except ValueError:
                    # Ignore invalid weight values
                    continue
        
        return weights if weights else None
    
    @staticmethod
    def sort_columns_by_weight(headers: List[str], weights: Optional[Dict[str, int]]) -> List[str]:
        """Sort columns based on weight configuration.
        
        Columns with higher weights appear first. Columns not in the weights dict
        get a default weight of 0. Stable sort is used to preserve original order
        for columns with the same weight.
        
        Args:
            headers: List of column names
            weights: dict of {column_name: weight}, or None
            
        Returns:
            Sorted list of column names (higher weight first)
            
        Examples:
            >>> headers = ['ID', 'Status', 'Name', 'Age', 'Email']
            >>> weights = {'Name': 100, 'Email': 90, 'Status': 80}
            >>> DatabaseColumnOrderingUtils.sort_columns_by_weight(headers, weights)
            ['Name', 'Email', 'Status', 'ID', 'Age']
        """
        if not weights:
            return headers
        
        # Assign weight to each column (default 0 for unspecified)
        def get_weight(col_name: str) -> int:
            return weights.get(col_name, 0)
        
        # Sort by weight descending (higher weight = earlier position)
        # Use stable sort to preserve original order for same-weight columns
        sorted_headers = sorted(headers, key=get_weight, reverse=True)
        
        return sorted_headers
