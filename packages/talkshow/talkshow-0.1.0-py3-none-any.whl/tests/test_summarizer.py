"""Tests for summarizer functionality."""

import pytest
from talkshow.summarizer.rule_summarizer import RuleSummarizer
from talkshow.models.chat import QAPair


class TestRuleSummarizer:
    """Test RuleSummarizer functionality."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a RuleSummarizer instance."""
        return RuleSummarizer(max_question_length=20, max_answer_length=80)
    
    def test_summarize_qa_pair(self, summarizer):
        """Test summarize_qa method with a QAPair object."""
        qa_pair = QAPair(
            question="This is a very long question that should be summarized",
            answer="This is a very long answer that contains multiple sentences and should be summarized to fit within the length limit"
        )
        
        result = summarizer.summarize_qa(qa_pair)
        
        assert result is True
        assert qa_pair.question_summary is not None
        assert qa_pair.answer_summary is not None
        assert len(qa_pair.question_summary) <= 20
        assert len(qa_pair.answer_summary) <= 80
    
    def test_summarize_qa_with_existing_summaries(self, summarizer):
        """Test summarize_qa method when summaries already exist."""
        qa_pair = QAPair(
            question="Short question",
            answer="Short answer"
        )
        qa_pair.question_summary = "Existing summary"
        qa_pair.answer_summary = "Existing answer summary"
        
        result = summarizer.summarize_qa(qa_pair)
        
        assert result is True
        assert qa_pair.question_summary == "Existing summary"
        assert qa_pair.answer_summary == "Existing answer summary"
    
    def test_short_question_no_summary(self, summarizer):
        """Test that short questions don't get summarized."""
        question = "Hello"
        summary = summarizer.summarize_question(question)
        assert summary is None  # No summary needed for short text
    
    def test_long_question_gets_summarized(self, summarizer):
        """Test that long questions get summarized."""
        question = "This is a very long question that exceeds the maximum length limit and should be summarized"
        summary = summarizer.summarize_question(question)
        assert summary is not None
        assert len(summary) <= 20
        assert summary.endswith("...")
    
    def test_short_answer_no_summary(self, summarizer):
        """Test that short answers don't get summarized."""
        answer = "Short answer"
        summary = summarizer.summarize_answer(answer)
        assert summary is None  # No summary needed for short text
    
    def test_long_answer_gets_summarized(self, summarizer):
        """Test that long answers get summarized."""
        answer = ("This is a very long answer that contains multiple sentences. "
                 "It discusses various topics and provides detailed explanations. "
                 "The answer should be summarized to fit within the length limit. "
                 "This is additional content to make it even longer.")
        
        summary = summarizer.summarize_answer(answer)
        assert summary is not None
        assert len(summary) <= 80
    
    def test_question_core_extraction(self, summarizer):
        """Test extraction of question core."""
        question = "I have a problem with my code. How can I fix this issue?"
        summary = summarizer.summarize_question(question)
        # Should extract the actual question part
        assert summary is not None
        assert "How can I fix" in summary or summary.endswith("...")
    
    def test_answer_key_content_extraction(self, summarizer):
        """Test extraction of key content from answers."""
        answer = ("There are several ways to approach this. "
                 "The main solution is to check your configuration. "
                 "You should also verify your dependencies. "
                 "Additional details can be found in the documentation.")
        
        summary = summarizer.summarize_answer(answer)
        assert summary is not None
        assert "solution" in summary.lower() or "check" in summary.lower()
    
    def test_text_cleaning(self, summarizer):
        """Test that markdown formatting is cleaned."""
        question = "**How** can I *implement* `this function`?"
        # Even though it might not need summarizing, test the cleaning
        cleaned_result = summarizer._clean_text(question)
        assert "**" not in cleaned_result
        assert "*" not in cleaned_result
        assert "`" not in cleaned_result
    
    def test_url_cleaning(self, summarizer):
        """Test that URLs are cleaned from text."""
        text = "Check this link https://example.com for more info"
        cleaned = summarizer._clean_text(text)
        assert "https://example.com" not in cleaned
        assert "[URL]" in cleaned
    
    def test_summarize_both(self, summarizer):
        """Test summarizing both question and answer together."""
        question = "This is a moderately long question about implementation details"
        answer = "This is a comprehensive answer that provides multiple solutions and detailed explanations for the implementation"
        
        q_summary, a_summary = summarizer.summarize_both(question, answer)
        
        if q_summary:
            assert len(q_summary) <= 20
        if a_summary:
            assert len(a_summary) <= 80