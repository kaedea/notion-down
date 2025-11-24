import re

class NotionUtils:
    @staticmethod
    def extract_id(url_or_id: str) -> str:
        """
        Extracts the Notion UUID from a URL or returns the ID if it's already a UUID.
        """
        # Regular expression for UUID (8-4-4-4-12 hex digits)
        # We want to capture the hex digits to format them if needed
        # But simpler is to find the match and then check if it has dashes.
        
        # Pattern for 32 hex chars, optionally separated by dashes
        pattern = r'([0-9a-f]{8})-?([0-9a-f]{4})-?([0-9a-f]{4})-?([0-9a-f]{4})-?([0-9a-f]{12})'
        
        match = re.search(pattern, url_or_id, re.IGNORECASE)
        if match:
            # Reconstruct with dashes
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}-{match.group(4)}-{match.group(5)}"
            
        return url_or_id

    @staticmethod
    def get_plain_text(rich_text_list: list) -> str:
        """
        Extracts plain text from a list of rich text objects.
        """
        if not rich_text_list:
            return ""
        return "".join([item.get("plain_text", "") for item in rich_text_list])
