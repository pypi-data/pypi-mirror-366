"""
LLM-based summarizer for TalkShow.

Uses LiteLLM to generate intelligent summaries of questions and answers.
"""

from typing import Optional, Tuple
from litellm import completion
from ..config.manager import ConfigManager
from ..models.chat import QAPair


class LLMSummarizer:
    """LLM-based text summarizer using various LLM providers."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize LLM summarizer.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.llm_config = self.config_manager.get("summarizer.llm", {})
    
    def summarize_qa(self, qa_pair: QAPair) -> bool:
        """Summarize both question and answer in a Q&A pair."""
        try:
            # Get max lengths from config
            max_question_length = self.config_manager.get("summarizer.rule.max_question_length", 20)
            max_answer_length = self.config_manager.get("summarizer.rule.max_answer_length", 80)
            
            # Summarize question
            if not qa_pair.question_summary:
                qa_pair.question_summary = self._summarize_text(
                    qa_pair.question, 
                    max_length=max_question_length
                )
            
            # Summarize answer
            if not qa_pair.answer_summary:
                qa_pair.answer_summary = self._summarize_text(
                    qa_pair.answer,
                    max_length=max_answer_length
                )
            
            return True
        except Exception as e:
            print(f"Error summarizing Q&A: {e}")
            return False
    
    def _summarize_text(self, text: str, max_length: int = 50) -> Optional[str]:
        """Summarize text using LLM."""
        if not text or len(text.strip()) <= max_length:
            return text.strip()
        
        try:
            # Prepare prompt
            prompt = f"请将以下文本总结为不超过{max_length}个字符的简洁描述：\n\n{text}"
            
            # Get LLM configuration
            model = self.llm_config.get("model", "moonshot/kimi-k2-0711-preview")
            max_tokens = self.llm_config.get("max_tokens", 150)
            temperature = self.llm_config.get("temperature", 0.3)
            api_base = self.llm_config.get("api_base", "https://api.moonshot.cn/v1")
            api_key = self.llm_config.get("api_key")
            
            # Call LLM
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                api_base=api_base,
                api_key=api_key
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure summary doesn't exceed max_length
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            print(f"LLM summarization failed: {e}")
            return None
    
    def get_usage_info(self) -> dict:
        """Get information about LLM usage configuration."""
        return {
            "model": self.llm_config.get("model", "unknown"),
            "max_tokens": self.llm_config.get("max_tokens", 150),
            "temperature": self.llm_config.get("temperature", 0.3)
        }
    
    def test_connection(self) -> bool:
        """Test LLM connection with a simple prompt.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_prompt = "请回答：你好"
            response = self._summarize_text(test_prompt, max_length=20)
            return response is not None and len(response.strip()) > 0
        except Exception:
            return False