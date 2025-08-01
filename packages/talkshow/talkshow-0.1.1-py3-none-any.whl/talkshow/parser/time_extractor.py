"""Time extraction utilities for MD files."""

import re
from datetime import datetime
from typing import Optional, List


class TimeExtractor:
    """Extracts timestamps from markdown content."""
    
    # Pattern for datetime in command output
    DATETIME_PATTERNS = [
        # 2025-07-28 23:16:38.431711
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)',
        # 2025-07-25 20:55:32.182798 
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)',
        # More patterns can be added as needed
    ]
    
    @classmethod
    def extract_first_timestamp(cls, content: str) -> Optional[datetime]:
        """Extract the first timestamp found in content."""
        timestamps = cls.extract_all_timestamps(content)
        return timestamps[0] if timestamps else None
    
    @classmethod
    def extract_all_timestamps(cls, content: str) -> List[datetime]:
        """Extract all timestamps found in content."""
        timestamps = []
        
        for pattern in cls.DATETIME_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    # Try to parse the datetime string
                    dt = cls._parse_datetime_string(match)
                    if dt:
                        timestamps.append(dt)
                except ValueError:
                    continue
        
        # Sort timestamps and remove duplicates
        timestamps = sorted(list(set(timestamps)))
        return timestamps
    
    @classmethod
    def _parse_datetime_string(cls, dt_str: str) -> Optional[datetime]:
        """Parse datetime string with various formats."""
        # Common datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @classmethod
    def extract_from_assistant_section(cls, assistant_content: str) -> Optional[datetime]:
        """Extract timestamp specifically from Assistant section."""
        # Look for command output patterns
        # Common pattern: python -c "from datetime import datetime;print(datetime.now())"
        # Followed by the actual timestamp
        
        lines = assistant_content.split('\n')
        found_datetime_command = False
        
        for line in lines:
            # Check if this line contains datetime command
            if 'datetime' in line and ('print' in line or 'now()' in line):
                found_datetime_command = True
                continue
            
            # If we found datetime command, next lines might contain timestamp
            if found_datetime_command:
                timestamp = cls.extract_first_timestamp(line)
                if timestamp:
                    return timestamp
        
        # Fallback: extract any timestamp from the content
        return cls.extract_first_timestamp(assistant_content)