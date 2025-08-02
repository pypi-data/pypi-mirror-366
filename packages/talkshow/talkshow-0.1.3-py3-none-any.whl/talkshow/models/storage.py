"""Storage interface and related models."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .chat import ChatSession


class StorageInterface(ABC):
    """Abstract interface for data storage implementations."""
    
    @abstractmethod
    def save_session(self, session: ChatSession) -> bool:
        """Save a single chat session."""
        pass
    
    @abstractmethod
    def save_sessions(self, sessions: List[ChatSession]) -> bool:
        """Save multiple chat sessions."""
        pass
    
    @abstractmethod
    def load_session(self, filename: str) -> Optional[ChatSession]:
        """Load a single chat session by filename."""
        pass
    
    @abstractmethod
    def load_all_sessions(self) -> List[ChatSession]:
        """Load all stored chat sessions."""
        pass
    
    @abstractmethod
    def session_exists(self, filename: str) -> bool:
        """Check if a session exists in storage."""
        pass
    
    @abstractmethod
    def delete_session(self, filename: str) -> bool:
        """Delete a session from storage."""
        pass
    
    @abstractmethod
    def get_session_count(self) -> int:
        """Get total number of stored sessions."""
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the storage backend."""
        pass