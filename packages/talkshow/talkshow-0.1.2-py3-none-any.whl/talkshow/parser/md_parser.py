"""Markdown file parser for SpecStory chat history."""

import os
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pathlib import Path

from ..models.chat import ChatSession, QAPair, SessionMeta
from .time_extractor import TimeExtractor


class MDParser:
    """Parser for SpecStory markdown chat history files."""
    
    def __init__(self):
        self.time_extractor = TimeExtractor()
    
    def parse_file(self, file_path: str) -> Optional[ChatSession]:
        """Parse a single markdown file into a ChatSession."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path)
        
        except (FileNotFoundError, IOError, UnicodeDecodeError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def parse_content(self, content: str, file_path: str) -> Optional[ChatSession]:
        """Parse markdown content into a ChatSession."""
        filename = os.path.basename(file_path)
        file_size = len(content.encode('utf-8'))
        
        # Extract creation time from filename (converted to Shanghai timezone)
        ctime = self._extract_creation_time_from_filename(filename)
        if not ctime:
            # Fallback to file modification time
            try:
                ctime = datetime.fromtimestamp(os.path.getmtime(file_path))
                # Make timezone-aware if it's naive
                if ctime.tzinfo is None:
                    ctime = ctime.replace(tzinfo=timezone.utc)
            except OSError:
                ctime = datetime.now(timezone.utc)
        
        # Extract QA pairs with ctime for fallback
        qa_pairs = self._extract_qa_pairs(content, ctime)
        if not qa_pairs:
            print(f"No QA pairs found in {filename}")
            return None
        
        # Create session metadata
        meta = SessionMeta.from_filename(
            filename=filename,
            ctime=ctime,
            file_size=file_size,
            qa_count=len(qa_pairs)
        )
        
        return ChatSession(meta=meta, qa_pairs=qa_pairs)
    
    def _extract_qa_pairs(self, content: str, ctime: datetime) -> List[QAPair]:
        """Extract Question-Answer pairs from markdown content."""
        qa_pairs = []
        
        # Split content by the standard separator patterns
        sections = self._split_into_sections(content)
        
        current_question = None
        assistant_sections = []  # Collect multiple assistant sections
        
        for section in sections:
            section_type = self._identify_section_type(section)
            
            if section_type == 'user':
                # If we have collected assistant sections, process them
                if current_question and assistant_sections:
                    qa_pair = self._create_qa_pair(current_question, assistant_sections, ctime)
                    if qa_pair:
                        qa_pairs.append(qa_pair)
                    assistant_sections = []
                
                # Extract new user question
                current_question = self._extract_user_content(section)
            
            elif section_type == 'assistant':
                # Collect assistant sections
                assistant_sections.append(section)
            
            elif current_question and assistant_sections:
                # This is content that belongs to the current assistant response
                # Include ALL sections after assistant marker until next user question
                assistant_sections.append(section)
        
        # Process final QA pair if exists
        if current_question and assistant_sections:
            qa_pair = self._create_qa_pair(current_question, assistant_sections, ctime)
            if qa_pair:
                qa_pairs.append(qa_pair)
        
        return qa_pairs
    
    def _create_qa_pair(self, question: str, assistant_sections: List[str], ctime: datetime) -> Optional[QAPair]:
        """Create a QA pair from question and multiple assistant sections."""
        if not question or not assistant_sections:
            return None
        
        # Combine all assistant sections
        combined_content = '\n---\n'.join(assistant_sections)
        
        # Extract answer content and timestamp from combined content
        answer_content = self._extract_assistant_content(combined_content)
        
        # Extract timestamp from the complete combined content (not just assistant content)
        # This allows finding timestamps in command output sections
        timestamp = self.time_extractor.extract_from_assistant_section(combined_content)
        if not timestamp:
            # Fallback: try to extract any timestamp from the combined sections
            timestamp = self.time_extractor.extract_first_timestamp(combined_content)
        
        # If still no timestamp found, use ctime as fallback
        if not timestamp:
            timestamp = ctime
        else:
            # Ensure timestamp is timezone-aware
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        if answer_content:  # Only create QA pair if we have actual answer content
            return QAPair(
                question=question,
                answer=answer_content,
                timestamp=timestamp
            )
        
        return None
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into logical sections."""
        # Split by the standard markdown separator: ---
        sections = content.split('---')
        
        # Clean up sections - remove empty ones and strip whitespace
        sections = [section.strip() for section in sections if section.strip()]
        
        return sections
    
    def _identify_section_type(self, section: str) -> str:
        """Identify if section is user, assistant, or other."""
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('_**User**_'):
                return 'user'
            elif line.startswith('_**Assistant**_'):
                return 'assistant'
        
        return 'other'
    
    def _extract_user_content(self, section: str) -> str:
        """Extract user content from a user section."""
        lines = section.split('\n')
        content_lines = []
        found_user_marker = False
        
        for line in lines:
            line = line.strip()
            if line == '_**User**_':
                found_user_marker = True
                continue
            
            if found_user_marker and line:
                content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def _extract_assistant_content(self, section: str) -> str:
        """Extract assistant content from an assistant section."""
        lines = section.split('\n')
        content_lines = []
        skip_command_blocks = False
        
        for line in lines:
            # Skip the assistant marker
            if line.strip() == '_**Assistant**_':
                continue
            
            # Skip command execution blocks (bash/python commands and their outputs)
            if line.strip().startswith('```'):
                skip_command_blocks = not skip_command_blocks
                continue
            
            if skip_command_blocks:
                continue
            
            # Skip section separators
            if line.strip() == '---':
                continue
            
            # Skip empty lines at the beginning
            if not content_lines and not line.strip():
                continue
            
            content_lines.append(line)
        
        # Clean up the content
        content = '\n'.join(content_lines).strip()
        
        # Remove any remaining command artifacts
        content = self._clean_assistant_content(content)
        
        return content
    
    def _clean_assistant_content(self, content: str) -> str:
        """Clean up assistant content from command artifacts."""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like command prompts
            if re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+:', line.strip()):
                continue
            
            # Skip lines that are just timestamps
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line.strip()):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _extract_creation_time_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract creation time from filename, converting UTC to Shanghai timezone."""
        import re
        from datetime import datetime, timezone, timedelta
        
        # Try to match both patterns:
        # 1. YYYY-MM-DD_HH-mmZ-description.md (with Z)
        # 2. YYYY-MM-DD_HH-mm-description.md (without Z)
        time_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})(?:Z)?-', filename)
        
        if time_match:
            try:
                # Parse the UTC time string (YYYY-MM-DD_HH-mm)
                utc_time_str = time_match.group(1)
                utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%d_%H-%M')
                # Set timezone to UTC
                utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                # Convert to Shanghai timezone (UTC+8)
                shanghai_tz = timezone(timedelta(hours=8))
                shanghai_dt = utc_dt.astimezone(shanghai_tz)
                
                return shanghai_dt
            except ValueError:
                return None
        
        return None
    
    def _extract_creation_time(self, qa_pairs: List[QAPair]) -> Optional[datetime]:
        """Extract creation time from the first QA pair with timestamp."""
        for qa in qa_pairs:
            if qa.timestamp:
                return qa.timestamp
        return None
    
    def parse_directory(self, directory_path: str) -> List[ChatSession]:
        """Parse all markdown files in a directory."""
        sessions = []
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            print(f"Directory not found: {directory_path}")
            return sessions
        
        # Find all .md files
        md_files = list(directory.glob("*.md"))
        
        for md_file in md_files:
            session = self.parse_file(str(md_file))
            if session:
                sessions.append(session)
        
        # Sort sessions by creation time
        sessions.sort(key=lambda s: s.meta.ctime)
        
        return sessions