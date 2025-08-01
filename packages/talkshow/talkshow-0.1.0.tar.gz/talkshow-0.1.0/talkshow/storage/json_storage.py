"""JSON-based storage implementation."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.chat import ChatSession
from ..models.storage import StorageInterface


class JSONStorage(StorageInterface):
    """JSON file-based storage for chat sessions."""
    
    def __init__(self, storage_path: str = "data/sessions.json"):
        """Initialize JSON storage.
        
        Args:
            storage_path: Path to the JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty storage if file doesn't exist
        if not self.storage_path.exists():
            self._save_data({})
    
    def save_session(self, session: ChatSession) -> bool:
        """Save a single chat session."""
        try:
            data = self._load_data()
            data[session.meta.filename] = session.to_dict()
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error saving session {session.meta.filename}: {e}")
            return False
    
    def save_sessions(self, sessions: List[ChatSession]) -> bool:
        """Save multiple chat sessions."""
        try:
            data = self._load_data()
            for session in sessions:
                data[session.meta.filename] = session.to_dict()
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error saving sessions: {e}")
            return False
    
    def load_session(self, filename: str) -> Optional[ChatSession]:
        """Load a single chat session by filename."""
        try:
            data = self._load_data()
            if filename in data:
                return ChatSession.from_dict(data[filename])
            return None
        except Exception as e:
            print(f"Error loading session {filename}: {e}")
            return None
    
    def load_all_sessions(self) -> List[ChatSession]:
        """Load all stored chat sessions."""
        try:
            data = self._load_data()
            sessions = []
            for session_data in data.values():
                session = ChatSession.from_dict(session_data)
                sessions.append(session)
            
            # Sort by creation time
            sessions.sort(key=lambda s: s.meta.ctime)
            return sessions
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return []
    
    def session_exists(self, filename: str) -> bool:
        """Check if a session exists in storage."""
        try:
            data = self._load_data()
            return filename in data
        except Exception:
            return False
    
    def delete_session(self, filename: str) -> bool:
        """Delete a session from storage."""
        try:
            data = self._load_data()
            if filename in data:
                del data[filename]
                self._save_data(data)
                return True
            return False
        except Exception as e:
            print(f"Error deleting session {filename}: {e}")
            return False
    
    def get_session_count(self) -> int:
        """Get total number of stored sessions."""
        try:
            data = self._load_data()
            return len(data)
        except Exception:
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the storage backend."""
        info = {
            'storage_type': 'JSON',
            'storage_path': str(self.storage_path),
            'file_exists': self.storage_path.exists(),
            'session_count': self.get_session_count()
        }
        
        if self.storage_path.exists():
            stat = self.storage_path.stat()
            info.update({
                'file_size_bytes': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return info
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def backup_storage(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the storage file."""
        if not self.storage_path.exists():
            return False
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.storage_path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.storage_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore storage from a backup file."""
        try:
            if not Path(backup_path).exists():
                print(f"Backup file not found: {backup_path}")
                return False
            
            import shutil
            shutil.copy2(backup_path, self.storage_path)
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all stored sessions."""
        try:
            self._save_data({})
            return True
        except Exception as e:
            print(f"Error clearing storage: {e}")
            return False