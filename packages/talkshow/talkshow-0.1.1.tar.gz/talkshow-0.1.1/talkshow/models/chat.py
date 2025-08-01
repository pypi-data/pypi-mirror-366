"""Chat data models for TalkShow."""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import re


@dataclass
class QAPair:
    """Represents a single question-answer pair in a chat session."""
    
    question: str
    answer: str
    timestamp: Optional[datetime] = None
    question_summary: Optional[str] = None
    answer_summary: Optional[str] = None
    
    def get_question_display(self, use_summary: bool = False) -> str:
        """Get display text for question."""
        if use_summary and self.question_summary:
            return self.question_summary
        return self.question
    
    def get_answer_display(self, use_summary: bool = False) -> str:
        """Get display text for answer."""
        if use_summary and self.answer_summary:
            return self.answer_summary
        return self.answer


@dataclass
class SessionMeta:
    """Metadata for a chat session."""
    
    filename: str
    theme: str
    ctime: datetime
    file_size: int
    qa_count: int
    
    @classmethod
    def from_filename(cls, filename: str, ctime: datetime, file_size: int, qa_count: int) -> 'SessionMeta':
        """Create SessionMeta from filename, extracting theme and converting timezone."""
        # Extract time and theme from filename pattern: 
        # 1. YYYY-MM-DD_HH-mmZ-description.md (with Z)
        # 2. YYYY-MM-DD_HH-mm-description.md (without Z)
        time_theme_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}Z?)-(.+)\.md$', filename)
        
        if time_theme_match:
            # Extract UTC time from filename
            utc_time_str = time_theme_match.group(1)
            theme = time_theme_match.group(2)
            
            # Remove Z from time string if present
            if utc_time_str.endswith('Z'):
                utc_time_str = utc_time_str[:-1]
            
            # Parse UTC time and keep it as UTC (don't convert to Shanghai timezone)
            try:
                # Parse the UTC time string (YYYY-MM-DD_HH-mm)
                utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%d_%H-%M')
                # Set timezone to UTC and keep it as UTC
                utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                
                # Use the UTC time as ctime (don't convert to Shanghai timezone)
                ctime = utc_dt
            except ValueError:
                # Fallback to provided ctime if parsing fails
                theme = filename
        else:
            # Fallback if filename doesn't match expected pattern
            theme = filename
        
        return cls(
            filename=filename,
            theme=theme,
            ctime=ctime,
            file_size=file_size,
            qa_count=qa_count
        )


@dataclass
class ChatSession:
    """Represents a complete chat session from a markdown file."""
    
    meta: SessionMeta
    qa_pairs: List[QAPair]
    
    def __post_init__(self):
        """Validate session data after initialization."""
        if not self.qa_pairs:
            raise ValueError("ChatSession must have at least one QA pair")
        
        # Update meta qa_count if needed
        if self.meta.qa_count != len(self.qa_pairs):
            self.meta.qa_count = len(self.qa_pairs)
    
    @property
    def start_time(self) -> datetime:
        """Get the session start time (first QA pair timestamp or meta ctime)."""
        if self.qa_pairs and self.qa_pairs[0].timestamp:
            return self.qa_pairs[0].timestamp
        return self.meta.ctime
    
    @property 
    def duration_minutes(self) -> Optional[int]:
        """Calculate session duration in minutes."""
        if len(self.qa_pairs) < 2:
            return None
            
        timestamps = [qa.timestamp for qa in self.qa_pairs if qa.timestamp]
        if len(timestamps) < 2:
            return None
            
        duration = max(timestamps) - min(timestamps)
        return int(duration.total_seconds() / 60)
    
    def get_summary(self, use_summaries: bool = False) -> str:
        """Get a text summary of the session."""
        qa_display = []
        for i, qa in enumerate(self.qa_pairs[:3]):  # Show first 3 QA pairs
            q = qa.get_question_display(use_summaries)
            a = qa.get_answer_display(use_summaries)
            qa_display.append(f"Q{i+1}: {q[:50]}{'...' if len(q) > 50 else ''}")
            qa_display.append(f"A{i+1}: {a[:80]}{'...' if len(a) > 80 else ''}")
        
        if len(self.qa_pairs) > 3:
            qa_display.append(f"... and {len(self.qa_pairs) - 3} more QA pairs")
            
        return "\n".join(qa_display)
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for serialization."""
        return {
            'meta': {
                'filename': self.meta.filename,
                'theme': self.meta.theme,
                'ctime': self.meta.ctime.isoformat(),
                'file_size': self.meta.file_size,
                'qa_count': self.meta.qa_count
            },
            'qa_pairs': [
                {
                    'question': qa.question,
                    'answer': qa.answer,
                    'timestamp': qa.timestamp.isoformat() if qa.timestamp else None,
                    'question_summary': qa.question_summary,
                    'answer_summary': qa.answer_summary
                }
                for qa in self.qa_pairs
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatSession':
        """Create session from dictionary."""
        meta_data = data['meta']
        
        # 处理ctime，确保时区一致性
        ctime_str = meta_data['ctime']
        if ctime_str:
            ctime = datetime.fromisoformat(ctime_str)
            # 如果没有时区信息，假设为UTC
            if ctime.tzinfo is None:
                ctime = ctime.replace(tzinfo=timezone.utc)
        else:
            ctime = datetime.now(timezone.utc)
        
        meta = SessionMeta(
            filename=meta_data['filename'],
            theme=meta_data['theme'],
            ctime=ctime,
            file_size=meta_data['file_size'],
            qa_count=meta_data['qa_count']
        )
        
        qa_pairs = []
        for qa_data in data['qa_pairs']:
            # 处理timestamp，确保时区一致性
            timestamp = None
            if qa_data['timestamp']:
                timestamp = datetime.fromisoformat(qa_data['timestamp'])
                # 如果没有时区信息，假设为UTC
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            qa = QAPair(
                question=qa_data['question'],
                answer=qa_data['answer'],
                timestamp=timestamp,
                question_summary=qa_data.get('question_summary'),
                answer_summary=qa_data.get('answer_summary')
            )
            qa_pairs.append(qa)
        
        return cls(meta=meta, qa_pairs=qa_pairs)