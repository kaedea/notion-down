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

    @staticmethod
    def get_markdown_text(rich_text_list: list) -> str:
        """
        Converts Notion rich text to Markdown, preserving formatting.
        Supports: bold, italic, strikethrough, code, links
        """
        if not rich_text_list:
            return ""
        
        result = []
        for item in rich_text_list:
            text = item.get("plain_text", "")
            if not text:
                continue
            
            type_ = item.get("type")
            annotations = item.get("annotations", {})
            href = item.get("href")
            
            # Handle specific types first
            if type_ == "equation":
                # Notion equation: $expression$
                expression = item.get("equation", {}).get("expression", "")
                text = f"${expression}$"
                # Equations usually don't have other annotations in Notion, but just in case
            
            elif type_ == "mention":
                # Handle mentions (user, page, database, date, link_preview)
                mention = item.get("mention", {})
                mention_type = mention.get("type")
                
                if mention_type == "user":
                    user = mention.get("user", {})
                    name = user.get("name", "Unknown User")
                    text = f"@{name}"
                elif mention_type == "page":
                    # Page mention usually has a link, handled by href below
                    # But we might want to ensure the text is the page title if available
                    pass 
                elif mention_type == "database":
                    pass
                elif mention_type == "date":
                    date = mention.get("date", {})
                    start = date.get("start", "")
                    end = date.get("end", "")
                    if end:
                        text = f"{start} → {end}"
                    else:
                        text = start
                elif mention_type == "link_preview":
                    # Link preview usually has url in href
                    pass
            
            # Apply formatting
            # Priority: Code > Bold > Italic > Strikethrough > Underline
            
            if annotations.get("code"):
                text = f"`{text}`"
            else:
                # Apply other formatting only if not code
                if annotations.get("bold"):
                    text = f"**{text}**"
                
                if annotations.get("italic"):
                    text = f"*{text}*"
                
                if annotations.get("strikethrough"):
                    text = f"~~{text}~~"
                
                if annotations.get("underline"):
                    # Use HTML <u> tag for underline as it's not standard Markdown
                    text = f"<u>{text}</u>"
            
            # Link (outermost)
            if href:
                text = f"[{text}]({href})"
            
            result.append(text)
        
        return "".join(result)
