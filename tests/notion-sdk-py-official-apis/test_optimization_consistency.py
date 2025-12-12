import unittest
import os
import time

from config import Config
from notion_reader import NotionReader
from utils.utils import Utils

class OptimizationConsistencyTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        # Use the standard sample blog URL used in other tests/jobs
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.check_required_args()
        
    def test_job_parse_sample_posts(self):
        """
        Job: jobs/parse_sample_posts/main.py
        Config: Default (blog_url set, page_titles=['all'])
        """
        print("\n=== Test Job: parse_sample_posts ===")
        # Config already set in setUp
        self._verify_strategies()

    def test_job_parse_sample_posts_for_hexo(self):
        """
        Job: jobs/parse_sample_posts_for_hexo/main.py
        Config: blog_url set, page_titles_match=["^(Hexo page -)"]
        """
        print("\n=== Test Job: parse_sample_posts_for_hexo ===")
        Config.set_page_titles_match(["^(Hexo page -)"])
        self._verify_strategies()

    def test_job_parse_readme(self):
        """
        Job: jobs/parse_readme/main.py
        Config: blog_url set, search specific titles manually.
        Note: This job calls read_page_with_title multiple times. 
        We verify that read_page_with_title uses the scoped optimization.
        """
        print("\n=== Test Job: parse_readme ===")
        target_titles = [
            "NotionDown README",
            "NotionDown GetTokenV2",
            "NotionDown Custom Config",
        ]
        
        # 1. Optimized
        print("\n[Optimized Strategy] Running...")
        start_time = time.time()
        optimized_pages = []
        for title in target_titles:
            p = NotionReader.read_page_with_title(title)
            if p: optimized_pages.append(p)
        print(f"[Optimized Strategy] Done in {time.time() - start_time:.2f}s. Found {len(optimized_pages)} pages.")

        # 2. Legacy (Simulated)
        # Old read_page_with_title would call read_all_pages() -> _read_post_pages() -> recurse
        # And then find_one.
        print("\n[Legacy Strategy] Running...")
        start_time = time.time()
        legacy_pages = []
        
        # Simulate fetch all recursively
        main_page = NotionReader.read_main_page()
        all_recurse_pages = []
        if main_page:
            NotionReader._recurse_read_page(all_recurse_pages, main_page)
            
        for title in target_titles:
            # Find in all_recurse_pages
            p = Utils.find_one(all_recurse_pages, lambda it: NotionReader._get_page_title(it) == title)
            if p: legacy_pages.append(p)
            
        print(f"[Legacy Strategy] Done in {time.time() - start_time:.2f}s. Found {len(legacy_pages)} pages.")
        
        self._compare_page_lists(optimized_pages, legacy_pages)


    def _verify_strategies(self):
        # 1. Run Optimized
        print("\n[Optimized Strategy] Running...")
        start_time = time.time()
        optimized_pages = NotionReader._read_post_pages()
        print(f"[Optimized Strategy] Done in {time.time() - start_time:.2f}s. Found {len(optimized_pages)} pages.")
        
        # 2. Run Legacy
        print("\n[Legacy Strategy] Running...")
        start_time = time.time()
        main_page = NotionReader.read_main_page()
        legacy_pages = []
        if main_page:
            NotionReader._recurse_read_page(legacy_pages, main_page)
            # Apply same filter as _read_post_pages does
            legacy_pages = self._apply_title_filter(legacy_pages)
            
        print(f"[Legacy Strategy] Done in {time.time() - start_time:.2f}s. Found {len(legacy_pages)} pages.")
        
        # 3. Compare
        self._compare_page_lists(optimized_pages, legacy_pages)


    def _apply_title_filter(self, page_blocks):
        # Replicating the filter logic from NotionReader._read_post_pages
        import re
        titles = Config.page_titles()
        titles_match = Config.page_titles_match() or []
        
        if titles == ['all'] and (not titles_match or len(titles_match) == 0):
            return page_blocks

        filter_by_titles = [it for it in page_blocks if NotionReader._get_page_title(it) in titles]
        filter_by_titles_match = [it for it in page_blocks if Utils.find_one(
            titles_match,
            lambda match: re.compile(match).match(NotionReader._get_page_title(it))
        )]
        filter_by_titles.extend([it for it in filter_by_titles_match if it not in filter_by_titles])
        return filter_by_titles

    def _compare_page_lists(self, list_a, list_b):
        """
        Asserts that two lists of Notion pages contain identical sets of pages by ID.
        """
        ids_a = sorted([p['id'].replace('-', '') for p in list_a])
        ids_b = sorted([p['id'].replace('-', '') for p in list_b])
        
        # Check count
        self.assertEqual(len(ids_a), len(ids_b), f"Page count mismatch! Optimized: {len(ids_a)}, Legacy: {len(ids_b)}")
        
        # Check IDs
        for id_a, id_b in zip(ids_a, ids_b):
            self.assertEqual(id_a, id_b, f"Mismatch found! ID {id_a} vs {id_b}")
            
        print("Verification Successful: Both strategies returned identical page sets.")
