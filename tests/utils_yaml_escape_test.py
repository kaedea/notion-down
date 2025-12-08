# -*- coding: utf-8 -*-

import unittest
from utils.utils import Utils


class UtilsYamlEscapeTest(unittest.TestCase):
    """Test cases for Utils.escape_yaml_string method"""

    def test_simple_string_no_escaping(self):
        """Simple strings without special characters should not be quoted"""
        self.assertEqual(Utils.escape_yaml_string("simple"), "simple")
        self.assertEqual(Utils.escape_yaml_string("hello"), "hello")
        self.assertEqual(Utils.escape_yaml_string("test123"), "test123")
        self.assertEqual(Utils.escape_yaml_string("under_score"), "under_score")

    def test_empty_and_none_values(self):
        """Empty and None values should return empty quoted string"""
        self.assertEqual(Utils.escape_yaml_string(""), '""')
        self.assertEqual(Utils.escape_yaml_string(None), '""')

    def test_colon_requires_quoting(self):
        """Strings with colons must be quoted"""
        self.assertEqual(
            Utils.escape_yaml_string("title: with colon"),
            '"title: with colon"'
        )
        self.assertEqual(
            Utils.escape_yaml_string("AOSP Bug 报告: AMS#getRunningAppProcesses NPE 异常"),
            '"AOSP Bug 报告: AMS#getRunningAppProcesses NPE 异常"'
        )

    def test_hash_requires_quoting(self):
        """Strings with hash symbols must be quoted"""
        self.assertEqual(
            Utils.escape_yaml_string("AMS#getRunningAppProcesses"),
            '"AMS#getRunningAppProcesses"'
        )
        self.assertEqual(
            Utils.escape_yaml_string("comment # here"),
            '"comment # here"'
        )

    def test_quotes_require_escaping(self):
        """Strings with quotes must be escaped and quoted"""
        self.assertEqual(
            Utils.escape_yaml_string('has "quotes"'),
            '"has \\"quotes\\""'
        )
        self.assertEqual(
            Utils.escape_yaml_string("single 'quote'"),
            '"single \'quote\'"'
        )

    def test_backslash_escaping(self):
        """Backslashes must be escaped"""
        self.assertEqual(
            Utils.escape_yaml_string("path\\to\\file"),
            '"path\\\\to\\\\file"'
        )
        self.assertEqual(
            Utils.escape_yaml_string('quote\\"test'),
            '"quote\\\\\\"test"'
        )

    def test_special_yaml_characters(self):
        """Various YAML special characters should trigger quoting"""
        # At sign
        self.assertEqual(Utils.escape_yaml_string("email@example.com"), '"email@example.com"')
        
        # Backtick
        self.assertEqual(Utils.escape_yaml_string("code `snippet`"), '"code `snippet`"')
        
        # Exclamation mark
        self.assertEqual(Utils.escape_yaml_string("Hello!"), '"Hello!"')
        
        # Percent
        self.assertEqual(Utils.escape_yaml_string("50%"), '"50%"')
        
        # Ampersand
        self.assertEqual(Utils.escape_yaml_string("A & B"), '"A & B"')
        
        # Asterisk
        self.assertEqual(Utils.escape_yaml_string("*wildcard*"), '"*wildcard*"')
        
        # Braces and brackets
        self.assertEqual(Utils.escape_yaml_string("{key}"), '"{key}"')
        self.assertEqual(Utils.escape_yaml_string("[array]"), '"[array]"')
        
        # Pipe and angle brackets
        self.assertEqual(Utils.escape_yaml_string("a | b"), '"a | b"')
        self.assertEqual(Utils.escape_yaml_string("a > b"), '"a > b"')
        self.assertEqual(Utils.escape_yaml_string("a < b"), '"a < b"')
        
        # Question mark
        self.assertEqual(Utils.escape_yaml_string("What?"), '"What?"')
        
        # Dash (hyphen)
        self.assertEqual(Utils.escape_yaml_string("dash-separated"), '"dash-separated"')
        
        # Comma
        self.assertEqual(Utils.escape_yaml_string("a, b, c"), '"a, b, c"')

    def test_whitespace_requires_quoting(self):
        """Strings with leading/trailing whitespace must be quoted"""
        self.assertEqual(Utils.escape_yaml_string(" leading"), '" leading"')
        self.assertEqual(Utils.escape_yaml_string("trailing "), '"trailing "')
        self.assertEqual(Utils.escape_yaml_string(" both "), '" both "')

    def test_boolean_like_strings(self):
        """Strings that look like booleans must be quoted"""
        self.assertEqual(Utils.escape_yaml_string("true"), '"true"')
        self.assertEqual(Utils.escape_yaml_string("false"), '"false"')
        self.assertEqual(Utils.escape_yaml_string("True"), '"True"')
        self.assertEqual(Utils.escape_yaml_string("FALSE"), '"FALSE"')
        self.assertEqual(Utils.escape_yaml_string("yes"), '"yes"')
        self.assertEqual(Utils.escape_yaml_string("no"), '"no"')
        self.assertEqual(Utils.escape_yaml_string("on"), '"on"')
        self.assertEqual(Utils.escape_yaml_string("off"), '"off"')
        self.assertEqual(Utils.escape_yaml_string("null"), '"null"')
        self.assertEqual(Utils.escape_yaml_string("~"), '"~"')

    def test_numeric_strings(self):
        """Pure numeric strings should not be quoted (they're valid YAML)"""
        # These are actually fine in YAML without quotes
        self.assertEqual(Utils.escape_yaml_string("123"), "123")
        self.assertEqual(Utils.escape_yaml_string("456.78"), "456.78")

    def test_chinese_characters(self):
        """Chinese characters should work correctly"""
        self.assertEqual(Utils.escape_yaml_string("中文标题"), "中文标题")
        self.assertEqual(
            Utils.escape_yaml_string("中文: 标题"),
            '"中文: 标题"'
        )

    def test_mixed_special_characters(self):
        """Complex strings with multiple special characters"""
        self.assertEqual(
            Utils.escape_yaml_string('Title: "Complex" & Special!'),
            '"Title: \\"Complex\\" & Special!"'
        )
        self.assertEqual(
            Utils.escape_yaml_string("Path: C:\\Users\\test"),
            '"Path: C:\\\\Users\\\\test"'
        )

    def test_integer_input(self):
        """Non-string inputs should be converted to strings"""
        self.assertEqual(Utils.escape_yaml_string(123), "123")
        self.assertEqual(Utils.escape_yaml_string(45.67), "45.67")

    def test_real_world_hexo_titles(self):
        """Test with real-world Hexo blog post titles"""
        # Title with colon
        self.assertEqual(
            Utils.escape_yaml_string("Android: Best Performance Tips"),
            '"Android: Best Performance Tips"'
        )
        
        # Title with hash
        self.assertEqual(
            Utils.escape_yaml_string("C# Programming Guide"),
            '"C# Programming Guide"'
        )
        
        # Title with quotes
        self.assertEqual(
            Utils.escape_yaml_string('The "Ultimate" Guide'),
            '"The \\"Ultimate\\" Guide"'
        )
        
        # Complex title
        self.assertEqual(
            Utils.escape_yaml_string("AOSP Bug 报告: AMS#getRunningAppProcesses NPE 异常"),
            '"AOSP Bug 报告: AMS#getRunningAppProcesses NPE 异常"'
        )


if __name__ == '__main__':
    unittest.main()
