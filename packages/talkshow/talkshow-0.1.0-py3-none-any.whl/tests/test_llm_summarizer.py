"""
Tests for LLM summarizer functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from talkshow.summarizer.llm_summarizer import LLMSummarizer
from talkshow.config.manager import ConfigManager
from talkshow.models.chat import QAPair


class TestLLMSummarizer:
    """Test LLMSummarizer functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration manager."""
        config = {
            'summarizer': {
                'llm': {
                    'provider': 'moonshot',
                    'model': 'moonshot/kimi-k2-0711-preview',
                    'api_base': 'https://api.moonshot.cn/v1',
                    'max_tokens': 150,
                    'temperature': 0.3,
                    'api_key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                },
                'rule': {
                    'max_question_length': 20,
                    'max_answer_length': 80
                }
            }
        }
        
        config_manager = MagicMock(spec=ConfigManager)
        
        # Configure mock to return different values based on the key
        def mock_get(key, default=None):
            if key == "summarizer.llm":
                return config['summarizer']['llm']
            elif key == "summarizer.rule.max_question_length":
                return 20
            elif key == "summarizer.rule.max_answer_length":
                return 80
            else:
                return default
        
        config_manager.get.side_effect = mock_get
        
        return config_manager
    
    @pytest.fixture
    def summarizer(self, mock_config):
        """Create LLMSummarizer instance with mock config."""
        return LLMSummarizer(config_manager=mock_config)
    
    def test_initialization(self, summarizer):
        """Test that initialization works correctly."""
        assert summarizer.config_manager is not None
        assert summarizer.llm_config is not None
    
    def test_short_text_no_summary(self, summarizer):
        """Test that short text doesn't get summarized."""
        short_text = "Hello"
        result = summarizer._summarize_text(short_text, max_length=50)
        assert result == "Hello"
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_summarize_text_success(self, mock_completion, summarizer):
        """Test successful text summarization."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "如何实现功能？"
        mock_completion.return_value = mock_response
        
        long_text = "请问在Python中如何实现一个复杂的功能，需要考虑哪些方面的问题？"
        result = summarizer._summarize_text(long_text, max_length=20)
        
        assert result == "如何实现功能？"
        mock_completion.assert_called_once()
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_summarize_text_failure(self, mock_completion, summarizer):
        """Test text summarization failure handling."""
        # Mock LLM failure
        mock_completion.side_effect = Exception("API Error")
        
        # Use a text that's definitely longer than max_length
        long_text = "这是一个非常长的文本，包含了很多内容，需要进行摘要处理，这个文本的长度超过了最大长度限制，应该会触发LLM调用"
        result = summarizer._summarize_text(long_text, max_length=10)
        
        assert result is None
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_summarize_qa_pair(self, mock_completion, summarizer):
        """Test summarizing Q&A pair."""
        # Mock LLM responses
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "摘要内容"
        mock_completion.return_value = mock_response
        
        qa_pair = QAPair(
            question="这是一个需要摘要的长问题，包含很多细节信息，这个问题的长度超过了20个字符的限制，应该会触发LLM摘要功能",
            answer="这是一个非常详细的回答，包含了多个方面的解释和说明，需要进行摘要处理以便更好地展示给用户。这个回答涵盖了技术实现细节、最佳实践建议、常见问题解决方案等内容，具有较高的参考价值。回答中包含了大量的技术术语和具体的实现步骤，需要经过LLM处理来生成简洁的摘要。"
        )
        
        result = summarizer.summarize_qa(qa_pair)
        
        assert result is True
        assert qa_pair.question_summary == "摘要内容"
        assert qa_pair.answer_summary == "摘要内容"
        assert mock_completion.call_count == 2
    
    def test_get_usage_info(self, summarizer):
        """Test getting usage information."""
        info = summarizer.get_usage_info()
        
        assert 'model' in info
        assert 'max_tokens' in info
        assert 'temperature' in info
        assert info['model'] == 'moonshot/kimi-k2-0711-preview'
        assert info['max_tokens'] == 150
        assert info['temperature'] == 0.3
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_summarize_text_truncation(self, mock_completion, summarizer):
        """Test that long summaries are truncated."""
        # Mock LLM response that's too long
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "这是一个非常长的摘要内容，超过了最大长度限制"
        mock_completion.return_value = mock_response
        
        long_text = "这是一个很长的文本，需要进行摘要处理"
        result = summarizer._summarize_text(long_text, max_length=10)
        
        assert result == "这是一个非常长的摘要内容，超过了最大长度限制"[:7] + "..."
    
    def test_summarize_qa_with_existing_summaries(self, summarizer):
        """Test that existing summaries are not overwritten."""
        qa_pair = QAPair(
            question="问题",
            answer="回答",
            question_summary="已有问题摘要",
            answer_summary="已有回答摘要"
        )
        
        result = summarizer.summarize_qa(qa_pair)
        
        assert result is True
        assert qa_pair.question_summary == "已有问题摘要"
        assert qa_pair.answer_summary == "已有回答摘要"