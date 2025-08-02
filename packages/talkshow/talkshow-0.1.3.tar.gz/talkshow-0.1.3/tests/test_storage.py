"""Tests for storage functionality."""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from talkshow.models.chat import ChatSession, QAPair, SessionMeta
from talkshow.storage.json_storage import JSONStorage


class TestJSONStorage:
    """Test JSONStorage functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = os.path.join(temp_dir, "test_sessions.json")
            yield JSONStorage(storage_path)
    
    @pytest.fixture
    def sample_session(self):
        """Create a sample ChatSession for testing."""
        meta = SessionMeta(
            filename="test.md",
            theme="test-chat",
            ctime=datetime(2025, 7, 28, 15, 16, 0),
            file_size=1000,
            qa_count=2
        )
        
        qa_pairs = [
            QAPair(
                question="Hello",
                answer="Hi there!",
                timestamp=datetime(2025, 7, 28, 15, 16, 30)
            ),
            QAPair(
                question="How are you?",
                answer="I'm doing well, thank you!",
                timestamp=datetime(2025, 7, 28, 15, 17, 0)
            )
        ]
        
        return ChatSession(meta=meta, qa_pairs=qa_pairs)
    
    def test_save_and_load_session(self, temp_storage, sample_session):
        """Test saving and loading a session."""
        # Save session
        result = temp_storage.save_session(sample_session)
        assert result is True
        
        # Load session
        loaded_session = temp_storage.load_session("test.md")
        assert loaded_session is not None
        assert loaded_session.meta.filename == sample_session.meta.filename
        assert loaded_session.meta.theme == sample_session.meta.theme
        assert len(loaded_session.qa_pairs) == len(sample_session.qa_pairs)
        assert loaded_session.qa_pairs[0].question == sample_session.qa_pairs[0].question
    
    def test_session_exists(self, temp_storage, sample_session):
        """Test checking if session exists."""
        assert temp_storage.session_exists("test.md") is False
        
        temp_storage.save_session(sample_session)
        assert temp_storage.session_exists("test.md") is True
    
    def test_delete_session(self, temp_storage, sample_session):
        """Test deleting a session."""
        temp_storage.save_session(sample_session)
        assert temp_storage.session_exists("test.md") is True
        
        result = temp_storage.delete_session("test.md")
        assert result is True
        assert temp_storage.session_exists("test.md") is False
    
    def test_load_all_sessions(self, temp_storage):
        """Test loading all sessions."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            meta = SessionMeta(
                filename=f"test{i}.md",
                theme=f"test-chat-{i}",
                ctime=datetime(2025, 7, 28, 15, 16 + i, 0),
                file_size=1000,
                qa_count=1
            )
            qa_pair = QAPair(
                question=f"Question {i}",
                answer=f"Answer {i}",
                timestamp=datetime(2025, 7, 28, 15, 16 + i, 30)
            )
            session = ChatSession(meta=meta, qa_pairs=[qa_pair])
            sessions.append(session)
        
        # Save all sessions
        temp_storage.save_sessions(sessions)
        
        # Load all sessions
        loaded_sessions = temp_storage.load_all_sessions()
        assert len(loaded_sessions) == 3
        
        # Check they're sorted by creation time
        for i in range(len(loaded_sessions) - 1):
            assert loaded_sessions[i].meta.ctime <= loaded_sessions[i + 1].meta.ctime
    
    def test_get_storage_info(self, temp_storage, sample_session):
        """Test getting storage information."""
        info = temp_storage.get_storage_info()
        assert info['storage_type'] == 'JSON'
        assert info['session_count'] == 0
        
        temp_storage.save_session(sample_session)
        info = temp_storage.get_storage_info()
        assert info['session_count'] == 1