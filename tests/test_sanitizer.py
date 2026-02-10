"""Unit tests for src.core.sanitizer."""

import pytest
from src.core.sanitizer import sanitize_filename


class TestSanitizeFilename:
    """Verify Windows-illegal character stripping and edge cases."""

    def test_basic_valid_name(self):
        """A clean name is returned unchanged."""
        assert sanitize_filename("My Great Video") == "My Great Video"

    def test_illegal_characters_replaced(self):
        """Characters < > : \" / \\ | ? * become underscores."""
        assert sanitize_filename('A<B>C:D"E/F\\G|H?I*J') == "A_B_C_D_E_F_G_H_I_J"

    def test_trailing_dots_stripped(self):
        """Trailing dots are removed (Windows silently strips them)."""
        assert sanitize_filename("hello...") == "hello"

    def test_trailing_spaces_stripped(self):
        """Leading/trailing whitespace is stripped."""
        assert sanitize_filename("  hello  ") == "hello"

    def test_reserved_name_prefixed(self):
        """Windows reserved names (CON, NUL, etc.) get an underscore prefix."""
        assert sanitize_filename("CON") == "_CON"
        assert sanitize_filename("nul") == "_nul"
        assert sanitize_filename("COM1") == "_COM1"

    def test_empty_string_fallback(self):
        """An empty input yields 'untitled'."""
        assert sanitize_filename("") == "untitled"

    def test_only_illegal_chars_fallback(self):
        """A string made entirely of illegal chars yields 'untitled'."""
        assert sanitize_filename(":::") == "untitled"

    def test_long_name_truncated(self):
        """Names longer than 200 characters are truncated."""
        long_name = "A" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_unicode_preserved(self):
        """Non-ASCII characters that are valid on Windows are kept."""
        assert sanitize_filename("日本語タイトル") == "日本語タイトル"
