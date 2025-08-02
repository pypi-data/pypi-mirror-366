"""Tests for the MD parser module."""

import pytest
from datetime import datetime, timezone, timedelta
from talkshow.parser.md_parser import MDParser
from talkshow.parser.time_extractor import TimeExtractor
from talkshow.models.chat import SessionMeta


class TestTimeExtractor:
    """Test the TimeExtractor class."""
    
    def test_extract_timestamp_basic(self):
        """Test basic timestamp extraction."""
        content = "Some content with timestamp 2025-07-28 23:16:38.431711"
        timestamp = TimeExtractor.extract_first_timestamp(content)
        assert timestamp is not None
        assert timestamp.year == 2025
        assert timestamp.month == 7
        assert timestamp.day == 28
    
    def test_extract_from_command_output(self):
        """Test timestamp extraction from command output."""
        content = """
        _**Assistant**_
        python -c "from datetime import datetime;print(datetime.now())"
        2025-07-28 23:16:38.431711
        """
        timestamp = TimeExtractor.extract_from_assistant_section(content)
        assert timestamp is not None
        assert timestamp.year == 2025
    
    def test_no_timestamp_found(self):
        """Test when no timestamp is found."""
        content = "No timestamp in this content"
        timestamp = TimeExtractor.extract_first_timestamp(content)
        assert timestamp is None


class TestMDParser:
    """Test the MDParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MDParser()
    
    def test_parse_simple_content(self):
        """Test parsing simple content."""
        content = """
        ---
        _**User**_
        Hello
        
        ---
        _**Assistant**_
        Hi there!
        """
        session = self.parser.parse_content(content, "test.md")
        assert session is not None
        assert len(session.qa_pairs) == 1
        assert session.qa_pairs[0].question == "Hello"
        assert session.qa_pairs[0].answer == "Hi there!"
    
    def test_extract_theme_from_filename(self):
        """Test theme extraction from filename."""
        filename = "2025-07-28_15-30Z-test-theme.md"
        ctime = datetime.now()
        meta = SessionMeta.from_filename(filename, ctime, 1000, 5)
        assert meta.theme == "test-theme"
    
    def test_multiple_qa_pairs(self):
        """Test parsing multiple QA pairs."""
        content = """
        ---
        _**User**_
        First question
        
        ---
        _**Assistant**_
        First answer
        
        ---
        _**User**_
        Second question
        
        ---
        _**Assistant**_
        Second answer
        """
        session = self.parser.parse_content(content, "test.md")
        assert session is not None
        assert len(session.qa_pairs) == 2
        assert session.qa_pairs[0].question == "First question"
        assert session.qa_pairs[1].question == "Second question"
    
    def test_timezone_conversion_from_filename(self):
        """Test timezone conversion from filename."""
        filename = "2025-07-28_15-30Z-test-theme.md"
        ctime = self.parser._extract_creation_time_from_filename(filename)
        
        assert ctime is not None
        # Should be converted from UTC to Shanghai timezone (UTC+8)
        # UTC 15:30 should become Shanghai 23:30 (15:30 + 8 hours)
        assert ctime.hour == 23
        assert ctime.minute == 30
        assert ctime.day == 28
    
    def test_timezone_conversion_from_filename_without_z(self):
        """Test timezone conversion from filename without Z suffix."""
        filename = "2025-06-19_03-51-dataclass-usage-differences-in-python.md"
        ctime = self.parser._extract_creation_time_from_filename(filename)
        
        assert ctime is not None
        # Should be converted from UTC to Shanghai timezone (UTC+8)
        # UTC 03:51 should become Shanghai 11:51 (03:51 + 8 hours)
        assert ctime.hour == 11
        assert ctime.minute == 51
        assert ctime.day == 19
    
    def test_qa_pair_timestamp_fallback(self):
        """Test that QA pairs use CTime as fallback when no timestamp is found."""
        content = """
        ---
        _**User**_
        Question without timestamp
        
        ---
        _**Assistant**_
        Answer without timestamp
        """
        
        # Create a specific CTime for testing
        test_ctime = datetime(2025, 7, 28, 15, 30, 0, tzinfo=timezone(timedelta(hours=8)))
        
        # Mock the filename to return our test CTime
        original_method = self.parser._extract_creation_time_from_filename
        self.parser._extract_creation_time_from_filename = lambda x: test_ctime
        
        try:
            session = self.parser.parse_content(content, "2025-07-28_07-30Z-test.md")
            assert session is not None
            assert len(session.qa_pairs) == 1
            
            # The QA pair should have the CTime as its timestamp
            qa_pair = session.qa_pairs[0]
            assert qa_pair.timestamp is not None
            assert qa_pair.timestamp == test_ctime
        finally:
            # Restore original method
            self.parser._extract_creation_time_from_filename = original_method