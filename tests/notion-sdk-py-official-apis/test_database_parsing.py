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

if __name__ == '__main__':
    unittest.main()
