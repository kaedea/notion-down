import unittest
import os
import sys
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestLiveConnection(unittest.TestCase):
    def test_token_validity_and_list_pages(self):
        token = os.environ.get('NOTION_TOKEN')
        if not token:
            print("Skipping live test: NOTION_TOKEN not found in environment.")
            return

        print(f"Using Token: {token[:4]}...{token[-4:]}")
        client = Client(auth=token)

        # 1. Verify Token (Get Bot User)
        print("\n[1] Verifying Token...")
        try:
            me = client.users.me()
            print(f"Successfully authenticated as: {me.get('name')} (ID: {me.get('id')})")
            print(f"Bot Owner: {me.get('bot', {}).get('owner', {}).get('type')}")
        except Exception as e:
            self.fail(f"Token verification failed: {e}")

        # 2. List all accessible pages using Search
        print("\n[2] Listing accessible pages (Search API)...")
        has_more = True
        start_cursor = None
        page_count = 0
        
        while has_more:
            response = client.search(
                filter={"property": "object", "value": "page"},
                start_cursor=start_cursor
            )
            
            for page in response.get('results', []):
                page_count += 1
                title = "Untitled"
                # Try to extract title
                props = page.get('properties', {})
                for prop in props.values():
                    if prop.get('type') == 'title':
                        title_parts = prop.get('title', [])
                        if title_parts:
                            title = "".join([t.get('plain_text', '') for t in title_parts])
                        break
                
                print(f"- [{page_count}] {title} (ID: {page.get('id')})")
                print(f"  URL: {page.get('url')}")
            
            has_more = response.get('has_more')
            start_cursor = response.get('next_cursor')
            
        print(f"\nTotal accessible pages found: {page_count}")
        
        if page_count == 0:
            print("WARNING: No pages found. Make sure you have invited the integration to at least one page.")
            return

        # Pick the first page found to test other methods
        first_page_id = response.get('results', [])[0].get('id')
        
        # 3. Retrieve Page by ID
        print(f"\n[3] Retrieving Page by ID: {first_page_id}")
        try:
            page = client.pages.retrieve(page_id=first_page_id)
            print(f"Successfully retrieved page: {page.get('id')}")
        except Exception as e:
            print(f"Failed to retrieve page: {e}")

        # 4. List Block Children (Traversal)
        print(f"\n[4] Listing Block Children (Traversal) for: {first_page_id}")
        try:
            children = client.blocks.children.list(block_id=first_page_id)
            print(f"Found {len(children.get('results', []))} children blocks.")
            for child in children.get('results', [])[:3]: # Show first 3
                print(f"- Type: {child.get('type')} (ID: {child.get('id')})")
                if child.get('type') == 'child_page':
                    print(f"  -> Found subpage: {child.get('child_page', {}).get('title')}")
        except Exception as e:
            print(f"Failed to list children: {e}")

        # 5. Query Database (if any database found)
        # First try to find a database via search
        print("\n[5] Searching for Databases...")
        try:
            db_response = client.search(
                filter={"property": "object", "value": "database"},
                page_size=1
            )
            databases = db_response.get('results', [])
            if databases:
                db_id = databases[0].get('id')
                print(f"Found Database: {db_id}. Querying...")
                query_res = client.databases.query(database_id=db_id)
                print(f"Database Query returned {len(query_res.get('results', []))} pages.")
            else:
                print("No databases found accessible by this token.")
        except Exception as e:
            print(f"Failed to query database: {e}")

if __name__ == '__main__':
    unittest.main()
