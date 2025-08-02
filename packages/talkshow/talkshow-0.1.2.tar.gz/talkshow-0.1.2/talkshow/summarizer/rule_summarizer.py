"""Rule-based text summarization."""

import re
from typing import Optional
from ..models.chat import QAPair


class RuleSummarizer:
    """Simple rule-based text summarizer."""
    
    def __init__(self, max_question_length: int = 60, max_answer_length: int = 120):
        """Initialize rule summarizer.
        
        Args:
            max_question_length: Maximum length for question summaries
            max_answer_length: Maximum length for answer summaries
        """
        self.max_question_length = max_question_length
        self.max_answer_length = max_answer_length
    
    def summarize_qa(self, qa_pair: QAPair) -> bool:
        """Summarize both question and answer in a Q&A pair.
        
        Args:
            qa_pair: QAPair object to summarize
            
        Returns:
            bool: True if summarization was successful, False otherwise
        """
        try:
            # Summarize question if not already summarized
            if not qa_pair.question_summary:
                qa_pair.question_summary = self.summarize_question(qa_pair.question)
            
            # Summarize answer if not already summarized
            if not qa_pair.answer_summary:
                qa_pair.answer_summary = self.summarize_answer(qa_pair.answer)
            
            return True
        except Exception as e:
            print(f"Error summarizing Q&A: {e}")
            return False
    
    def summarize_question(self, question: str) -> Optional[str]:
        """Summarize a question using rule-based approach."""
        if not question:
            return None
        
        # Clean the question text
        cleaned = self._clean_text(question)
        
        # If already short enough, return as is
        if len(cleaned) <= self.max_question_length:
            return None  # No summary needed
        
        # Extract the core question part
        summary = self._extract_question_core(cleaned)
        
        # Truncate if still too long
        if len(summary) > self.max_question_length:
            summary = summary[:self.max_question_length - 3] + "..."
        
        return summary
    
    def summarize_answer(self, answer: str) -> Optional[str]:
        """Summarize an answer using rule-based approach."""
        if not answer:
            return None
        
        # Clean the answer text
        cleaned = self._clean_text(answer)
        
        # If already short enough, return as is
        if len(cleaned) <= self.max_answer_length:
            return None  # No summary needed
        
        # Extract key sentences
        summary = self._extract_answer_key_content(cleaned)
        
        # Truncate if still too long
        if len(summary) > self.max_answer_length:
            summary = summary[:self.max_answer_length - 3] + "..."
        
        return summary
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and formatting."""
        # Remove multiple spaces and newlines
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned)  # Bold
        cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)     # Italic
        cleaned = re.sub(r'`(.+?)`', r'\1', cleaned)       # Code
        
        # Remove URLs
        cleaned = re.sub(r'https?://\S+', '[URL]', cleaned)
        
        return cleaned.strip()
    
    def _extract_question_core(self, question: str) -> str:
        """Extract the core part of a question."""
        # Common question patterns
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'can', 'could', 'should', 'would']
        
        sentences = self._split_sentences(question)
        
        # Find the first sentence with question words or ending with ?
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if (any(word in sentence_lower for word in question_words) or 
                sentence.strip().endswith('?')):
                return sentence.strip()
        
        # Fallback: return first sentence
        return sentences[0] if sentences else question
    
    def _extract_answer_key_content(self, answer: str) -> str:
        """Extract key content from an answer."""
        sentences = self._split_sentences(answer)
        
        if not sentences:
            return answer
        
        # Strategy: Take first sentence + key actionable sentences
        key_sentences = [sentences[0]]  # Always include first sentence
        
        # Look for sentences with key indicators
        key_indicators = [
            '解决', '方案', '问题', '建议', '需要', '可以', '应该', '实现', '配置', '设置',
            'solution', 'issue', 'problem', 'need', 'should', 'can', 'implement', 'configure'
        ]
        
        for sentence in sentences[1:]:
            if any(indicator in sentence.lower() for indicator in key_indicators):
                key_sentences.append(sentence)
                break  # Only take one additional key sentence
        
        summary = ' '.join(key_sentences)
        
        # If still too long, try to get just the essential part
        if len(summary) > self.max_answer_length * 1.2:  # Allow 20% overflow before aggressive truncation
            # Take just the first sentence and truncate
            summary = sentences[0]
        
        return summary
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[。！？.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def summarize_both(self, question: str, answer: str) -> tuple:
        """Summarize both question and answer.
        
        Returns:
            tuple: (question_summary, answer_summary)
        """
        question_summary = self.summarize_question(question)
        answer_summary = self.summarize_answer(answer)
        return question_summary, answer_summary