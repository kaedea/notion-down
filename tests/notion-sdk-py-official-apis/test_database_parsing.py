import unittest
import os
import sys
import httpx
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.notion_utils import NotionUtils
from notion_page import NotionPage, PageTableBlock

class TestDatabaseParsing(unittest.TestCase):
    def setUp(self):
        self.token = os.environ.get('NOTION_TOKEN')
        if not self.token:
            self.skipTest("NOTION_TOKEN not found.")
        
        ignore_ssl = os.environ.get('NOTION_IGNORE_SSL', 'false').lower() == 'true'
        if ignore_ssl:
            http_client = httpx.Client(verify=False)
            self.client = Client(auth=self.token, client=http_client)
        else:
            self.client = Client(auth=self.token)

    def test_parse_database_page(self):
        # Database Page ID provided by user
        # https://www.notion.so/kaedea/5e7e3401a02a4f13bc291a22870ebaa7?v=4dce74c0c289420a888a7ec3ff92b627
        page_id = "5e7e3401a02a4f13bc291a22870ebaa7"
        
        print(f"\n[Test] Parsing Database Page: {page_id}")
        
        try:
            # 1. Retrieve the block to confirm type
            block = self.client.blocks.retrieve(block_id=page_id)
            print(f"Block Type: {block.get('type')}")
            
            # 2. If it's a child_database, we treat it as a database
            if block.get('type') == 'child_database':
                db_id = block.get('id')
                print(f"Database ID: {db_id}")
                
                # 3. Retrieve Database Schema
                database = self.client.databases.retrieve(database_id=db_id)
                print(f"Database Object keys: {list(database.keys())}")
                print(f"Is inline database: {database.get('is_inline')}")
                print(f"Has data_sources: {database.get('data_sources') is not None}")
                
                properties = database.get('properties', {})
                print(f"Properties (Columns) from schema: {list(properties.keys())}")
                
                # NOTE: Inline databases with data_sources don't return properties in the schema
                # This is a known Notion API behavior, not a bug in notion-client
                # We need to infer headers from query results instead
                
                column_headers = list(properties.keys())
                
                # 4. Query Database Rows
                # Use httpx directly to query database
                http_headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                }
                url = f"https://api.notion.com/v1/databases/{db_id}/query"
                print(f"Querying URL: {url}")
                
                # Use the same http client (with SSL verify=False if needed)
                if hasattr(self.client, 'client'):
                    response = self.client.client.post(url, headers=http_headers, json={})
                else:
                    response = httpx.post(url, headers=http_headers, json={})
                
                print(f"Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    self.fail(f"Query failed: {response.text}")
                    
                results = response.json().get('results', [])
                print(f"Found {len(results)} rows.")
                
                # Infer headers from query results if schema is empty
                if not column_headers and results:
                    print("INFO: Database schema properties empty (inline database behavior)")
                    print("      Inferring headers from first row...")
                    first_row_props = results[0].get('properties', {})
                    column_headers = list(first_row_props.keys())
                    print(f"Inferred Headers (raw): {column_headers}")
                
                # Reorder headers: title column should be first (matches Notion UI)
                if column_headers and results:
                    title_col = None
                    other_cols = []
                    first_row = results[0].get('properties', {})
                    for h in column_headers:
                        if h in first_row:
                            prop = first_row[h]
                            if prop.get('type') == 'title' or prop.get('id') == 'title':
                                title_col = h
                            else:
                                other_cols.append(h)
                        else:
                            other_cols.append(h)
                    
                    if title_col:
                        column_headers = [title_col] + other_cols
                        print(f"Reordered Headers (title first): {column_headers}")
                
                # Verify we have headers either from schema or inference
                self.assertTrue(column_headers, "Should have column headers from schema or row inference")
                self.assertGreater(len(column_headers), 0, "Should have at least one column")
                
                print(f"\nFinal Headers: {column_headers}")
                print(f"Header count: {len(column_headers)}")
                
                # Print sample row data  
                for i, row in enumerate(results[:3]):
                    props = row.get('properties', {})
                    row_data = {name: prop.get('type') for name, prop in props.items()}
                    print(f"Row {i+1} property types: {row_data}")

        except Exception as e:
            self.fail(f"Failed to parse database: {e}")

    def test_parse_database_description_column_ordering(self):
        """Test parsing column weight configuration from database description"""
        print("\n[Test] Parsing Database Description for Column Ordering")
        
        # Import the shared utility class
        from utils.database_utils import DatabaseColumnOrderingUtils
        
        # Test 1: Valid column-order configuration
        description_text_1 = "This is a test database.\n\ncolumn-order: Name=100, Email=90, Status=80\n\nOther notes..."
        weights_1 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_1)
        print(f"Test 1 - Parsed weights: {weights_1}")
        self.assertIsNotNone(weights_1)
        self.assertEqual(weights_1, {'Name': 100, 'Email': 90, 'Status': 80})
        
        # Test 2: No column-order configuration
        description_text_2 = "Just a regular description"
        weights_2 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_2)
        print(f"Test 2 - No config, weights: {weights_2}")
        self.assertIsNone(weights_2)
        
        # Test 3: Empty description
        weights_3 = DatabaseColumnOrderingUtils.parse_column_weights("")
        print(f"Test 3 - Empty description, weights: {weights_3}")
        self.assertIsNone(weights_3)
        
        # Test 4: Multi-line description with column-order on one line
        description_text_4 = """This is a database for user management.
        
It contains the following information:
- User names
- Email addresses
- Status flags

column-order: Name=100, Email=90, Status=80, CreatedAt=70

Please note that this database is updated daily.
Additional notes and documentation can go here."""
        weights_4 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_4)
        print(f"Test 4 - Multi-line description, weights: {weights_4}")
        self.assertIsNotNone(weights_4)
        self.assertEqual(weights_4, {'Name': 100, 'Email': 90, 'Status': 80, 'CreatedAt': 70})
        
        # Test 5: Test sorting with weights
        headers = ['ID', 'Status', 'Name', 'Age', 'Email', 'CreatedAt']
        weights = {'Name': 100, 'Email': 90, 'Status': 80}
        sorted_headers = DatabaseColumnOrderingUtils.sort_columns_by_weight(headers, weights)
        print(f"Test 5 - Original: {headers}")
        print(f"Test 5 - Sorted: {sorted_headers}")
        # Expected: Name (100), Email (90), Status (80), then ID, Age, CreatedAt (all 0, stable order)
        self.assertEqual(sorted_headers[0], 'Name')
        self.assertEqual(sorted_headers[1], 'Email')
        self.assertEqual(sorted_headers[2], 'Status')
        # Remaining columns should maintain relative order
        remaining = sorted_headers[3:]
        self.assertIn('ID', remaining)
        self.assertIn('Age', remaining)
        self.assertIn('CreatedAt', remaining)
        
        # Test 6: Partial configuration (only some columns have weights)
        headers_6 = ['A', 'B', 'C', 'D', 'E']
        weights_6 = {'C': 10, 'A': 5}
        sorted_6 = DatabaseColumnOrderingUtils.sort_columns_by_weight(headers_6, weights_6)
        print(f"Test 6 - Partial config sorted: {sorted_6}")
        # Expected: C (10), A (5), then B, D, E (all 0, stable order)
        self.assertEqual(sorted_6[0], 'C')
        self.assertEqual(sorted_6[1], 'A')
        
        # Test 7: Column-order in middle of line (should NOT match)
        description_text_7 = "Some text column-order: Name=10 more text on same line"
        weights_7 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_7)
        print(f"Test 7 - Inline config (should NOT match): {weights_7}")
        # Should NOT match because column-order must be at start of line
        self.assertIsNone(weights_7)
        
        print("✓ All column ordering tests passed")

if __name__ == '__main__':
    unittest.main()
