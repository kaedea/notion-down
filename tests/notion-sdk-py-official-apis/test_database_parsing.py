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
        
        # Test 1: Valid property-order configuration
        description_text_1 = "This is a test database.\n\nproperty-order: Name=100, Email=90, Status=80\n\nOther notes..."
        weights_1 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_1)
        print(f"Test 1 - Parsed weights: {weights_1}")
        self.assertIsNotNone(weights_1)
        self.assertEqual(weights_1, {'Name': 100, 'Email': 90, 'Status': 80})
        
        # Test 2: No property-order configuration
        description_text_2 = "Just a regular description"
        weights_2 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_2)
        print(f"Test 2 - No config, weights: {weights_2}")
        self.assertIsNone(weights_2)
        
        # Test 3: Empty description
        weights_3 = DatabaseColumnOrderingUtils.parse_column_weights("")
        print(f"Test 3 - Empty description, weights: {weights_3}")
        self.assertIsNone(weights_3)
        
        # Test 4: Multi-line description with property-order on one line
        description_text_4 = """This is a database for user management.
        
It contains the following information:
- User names
- Email addresses
- Status flags

property-order: Name=100, Email=90, Status=80, CreatedAt=70

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
        
        # Test 7: property-order in middle of line (should NOT match)
        description_text_7 = "Some text property-order: Name=10 more text on same line"
        weights_7 = DatabaseColumnOrderingUtils.parse_column_weights(description_text_7)
        print(f"Test 7 - Inline config (should NOT match): {weights_7}")
        # Should NOT match because property-order must be at start of line
        self.assertIsNone(weights_7)
        
        print("✓ All column ordering tests passed")

    def test_database_row_sorting(self):
        """Test database row sorting logic priority."""
        print("\n[Test] Database Row Sorting Priority")
        
        from utils.database_utils import DatabaseColumnOrderingUtils
        
        # Test 1: Default sorting (Created Time)
        props_1 = {}
        sorts_1 = DatabaseColumnOrderingUtils.get_database_sorts(props_1)
        print(f"Test 1 - Default: {sorts_1}")
        self.assertEqual(sorts_1[0]['timestamp'], 'created_time')
        
        # Test 2: Priority 2 - Name == 'Order'
        props_2 = {
            'Name': {'type': 'title'},
            'Order': {'type': 'number'},
            'Age': {'type': 'number'}
        }
        sorts_2 = DatabaseColumnOrderingUtils.get_database_sorts(props_2)
        print(f"Test 2 - Name 'Order': {sorts_2}")
        self.assertEqual(sorts_2[0]['property'], 'Order')
        
        # Test 3: Priority 1 - Description == 'order'
        props_3 = {
            'Name': {'type': 'title'},
            'CustomSort': {'type': 'number', 'description': 'order'},
            'Order': {'type': 'number'} # Should be ignored because CustomSort has higher priority
        }
        sorts_3 = DatabaseColumnOrderingUtils.get_database_sorts(props_3)
        print(f"Test 3 - Description 'order': {sorts_3}")
        self.assertEqual(sorts_3[0]['property'], 'CustomSort')
        
        # Test 4: Description check is case-insensitive? 
        # API usually returns description as is. Our logic does .lower() == 'order'.
        props_4 = {
            'MySort': {'type': 'number', 'description': 'ORDER'}
        }
        sorts_4 = DatabaseColumnOrderingUtils.get_database_sorts(props_4)
        print(f"Test 4 - Case-insensitive Desc: {sorts_4}")
        self.assertEqual(sorts_4[0]['property'], 'MySort')
        
        # Test 5: Empty properties (simulating inline database issue)
        # Should fallback to created_time
        props_5 = {}
        sorts_5 = DatabaseColumnOrderingUtils.get_database_sorts(props_5)
        print(f"Test 5 - Empty properties: {sorts_5}")
        self.assertEqual(sorts_5[0]['timestamp'], 'created_time')

        print("✓ All row sorting tests passed")

    def test_page_order_configuration(self):
        """Test parsing of page-order configuration."""
        print("\n[Test] Page Order Configuration")
        from utils.database_utils import DatabaseColumnOrderingUtils

        # Test 1: Simple page-order
        desc_1 = "Some text\npage-order: Order1, Created\nMore text"
        sorts_1 = DatabaseColumnOrderingUtils.parse_page_order(desc_1)
        print(f"Test 1 - Simple: {sorts_1}")
        self.assertEqual(len(sorts_1), 2)
        self.assertEqual(sorts_1[0]['property'], 'Order1')
        self.assertEqual(sorts_1[1]['timestamp'], 'created_time')

        # Test 2: Multi-line and case insensitive
        desc_2 = "page-order: Priority, Name, CREATED"
        sorts_2 = DatabaseColumnOrderingUtils.parse_page_order(desc_2)
        print(f"Test 2 - Multi keys: {sorts_2}")
        self.assertEqual(len(sorts_2), 3)
        self.assertEqual(sorts_2[0]['property'], 'Priority')
        self.assertEqual(sorts_2[2]['timestamp'], 'created_time')

        # Test 3: No config
        desc_3 = "Just description"
        sorts_3 = DatabaseColumnOrderingUtils.parse_page_order(desc_3)
        self.assertIsNone(sorts_3)
        
        print("✓ All page-order tests passed")

    def test_column_hiding(self):
        """Test hiding columns via negative weights."""
        print("\n[Test] Column Hiding")
        from utils.database_utils import DatabaseColumnOrderingUtils

        headers = ['Title', 'Tags', 'Secret', 'Date']
        weights = {
            'Title': 100,
            'Secret': -1,  # Should be hidden
            'Tags': 50
        }
        
        sorted_headers = DatabaseColumnOrderingUtils.sort_columns_by_weight(headers, weights)
        print(f"Original: {headers}")
        print(f"Weights: {weights}")
        print(f"Result: {sorted_headers}")
        
        self.assertNotIn('Secret', sorted_headers)
        self.assertEqual(sorted_headers[0], 'Title')
        self.assertEqual(sorted_headers[1], 'Tags')
        self.assertIn('Date', sorted_headers) # Default weight 0
        
        print("✓ Column hiding tests passed")

if __name__ == '__main__':
    unittest.main()
