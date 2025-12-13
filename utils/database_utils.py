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
    def parse_page_order(description_text: str) -> Optional[List[Dict[str, str]]]:
        """
        Parses page-order configuration from description text.
        Format: page-order: Order1, Order2, Created
        Returned format: Notion API sorts parameter
        """
        if not description_text:
            return None
            
        pattern = r'(?:^|\n)\s*page-order:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, description_text, re.IGNORECASE | re.MULTILINE)
        
        if not match:
            return None
            
        config_line = match.group(1).strip()
        if not config_line:
            return None
            
        sorts = []
        parts = [p.strip() for p in config_line.split(',')]
        
        for part in parts:
            if not part:
                continue
                
            if part.lower() == 'created':
                sorts.append({
                    "timestamp": "created_time",
                    "direction": "ascending"
                })
            else:
                sorts.append({
                    "property": part,
                    "direction": "ascending"
                })
                
        return sorts if sorts else None

    @staticmethod
    def sort_columns_by_weight(headers: List[str], weights: Optional[Dict[str, int]]) -> List[str]:
        """
        Sorts the headers based on the weights.
        
        If weights is provided, headers are sorted descending by weight.
        Headers not in weights get a default weight of 0.
        Negative weights mean the column should be hidden (removed).
        
        Args:
            headers: List of column names
            weights: dict of {column_name: weight}
            
        Returns:
            Sorted and filtered list of column names
            
        Example: 
            >>> headers = ['Title', 'Tags', 'Secret']
            >>> weights = {'Title': 100, 'Secret': -1}
            >>> result = sort_columns_by_weight(headers, weights)
            ['Title', 'Tags']
        """
        if not weights:
            return headers

        # Default weight for unassigned headers is 0
        def get_weight(header):
            return weights.get(header, 0)
        
        # Filter out headers with negative weights
        visible_headers = [
            h for h in headers 
            if get_weight(h) >= 0
        ]

        # Use a stable sort to keep relative order of items with same weight
        sorted_headers = sorted(visible_headers, key=get_weight, reverse=True)
        return sorted_headers

    @staticmethod
    def get_database_sorts(properties: Dict) -> List[Dict]:
        """Determine database row sorting configuration.
        
        Priority:
        1. Number property with description == 'order'
        2. Number property with name == 'Order' (case-insensitive)
        3. Created time (default)
        
        Args:
            properties: Database properties schema from Notion API
            
        Returns:
            List of sort objects for Notion API query
        """
        # Default sort
        sorts = [
            {
                "timestamp": "created_time",
                "direction": "ascending"
            }
        ]
        
        if not properties:
            return sorts
            
        candidate_prop = None
        # Priority level: 0=None, 1=Name Match, 2=Description Match
        priority = 0
        
        for name, prop in properties.items():
            if prop.get('type') == 'number':
                # Check description (Highest priority)
                description = prop.get('description', '')
                if description and description.lower() == 'order':
                    candidate_prop = name
                    priority = 2
                    break
                
                # Check name (Secondary priority)
                # Matches 'Order' (case-insensitive)
                if priority < 1 and name.lower() == 'order':
                    candidate_prop = name
                    priority = 1
        
        if candidate_prop:
            sorts = [
                {
                    "property": candidate_prop,
                    "direction": "ascending"
                }
            ]
            
        return sorts
