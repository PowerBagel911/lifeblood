"""Tests for LLM client implementations."""

import pytest
from app.services.llm_client import (
    LLMClient, 
    MockLLMClient, 
    GeminiLLMClient,
    get_llm_client
)


class TestMockLLMClient:
    """Test cases for MockLLMClient."""
    
    def test_initialization_default_templates(self):
        """Test default initialization creates response templates."""
        client = MockLLMClient()
        assert len(client.response_templates) > 0
        assert all(isinstance(template, str) for template in client.response_templates)
        assert all('{topic}' in template for template in client.response_templates)
    
    def test_initialization_custom_templates(self):
        """Test custom template initialization."""
        custom_templates = [
            "Custom response about {topic}",
            "Another template for {topic}"
        ]
        client = MockLLMClient(response_templates=custom_templates)
        assert client.response_templates == custom_templates
    
    def test_generate_returns_string(self):
        """Test generate method returns a string."""
        client = MockLLMClient()
        
        response = client.generate("What is machine learning?")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_deterministic(self):
        """Test generate produces deterministic results."""
        client = MockLLMClient()
        
        prompt = "What are the benefits of blood donation?"
        response1 = client.generate(prompt)
        response2 = client.generate(prompt)
        
        assert response1 == response2
    
    def test_generate_different_prompts_different_responses(self):
        """Test different prompts produce different responses."""
        client = MockLLMClient()
        
        response1 = client.generate("What is plasma collection?")
        response2 = client.generate("How does donor screening work?")
        
        assert response1 != response2
    
    def test_generate_empty_prompt(self):
        """Test generate handles empty prompts gracefully."""
        client = MockLLMClient()
        
        response = client.generate("")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "provide a specific question" in response.lower()
    
    def test_generate_whitespace_only_prompt(self):
        """Test generate handles whitespace-only prompts."""
        client = MockLLMClient()
        
        response = client.generate("   \n\t  ")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "provide a specific question" in response.lower()
    
    def test_extract_topic_simple_question(self):
        """Test topic extraction from simple questions."""
        client = MockLLMClient()
        
        topic = client._extract_topic("What is blood donation?")
        
        assert "blood donation" in topic.lower()
    
    def test_extract_topic_complex_question(self):
        """Test topic extraction from complex questions."""
        client = MockLLMClient()
        
        topic = client._extract_topic("How do plasma collection procedures ensure safety?")
        
        # Should extract meaningful words, filtering out question words
        assert "plasma" in topic.lower() or "collection" in topic.lower()
    
    def test_extract_topic_no_meaningful_words(self):
        """Test topic extraction when no meaningful words present."""
        client = MockLLMClient()
        
        topic = client._extract_topic("What is the?")
        
        assert topic == "the requested topic"
    
    def test_extract_topic_empty_prompt(self):
        """Test topic extraction from empty prompt."""
        client = MockLLMClient()
        
        topic = client._extract_topic("")
        
        assert topic == "the requested topic"
    
    def test_generate_uses_template_format(self):
        """Test generate method uses template formatting correctly."""
        custom_templates = ["Testing topic: {topic}"]
        client = MockLLMClient(response_templates=custom_templates)
        
        response = client.generate("blood safety protocols")
        
        assert "Testing topic:" in response
        assert "{topic}" not in response  # Template should be formatted
    
    def test_generate_long_prompt_adds_detail(self):
        """Test generate adds detail comment for long prompts."""
        client = MockLLMClient()
        
        long_prompt = "What are the detailed safety procedures and protocols " * 10  # >100 chars
        response = client.generate(long_prompt)
        
        assert "detailed response" in response.lower()
    
    def test_generate_question_mark_adds_answer_note(self):
        """Test generate adds answer note for questions with question marks."""
        client = MockLLMClient()
        
        response = client.generate("What is donor eligibility?")
        
        assert "answer" in response.lower() and "question" in response.lower()
    
    def test_generate_multiple_templates_used(self):
        """Test that different templates are used for different prompts."""
        templates = [
            "Template A about {topic}",
            "Template B regarding {topic}",
            "Template C for {topic}"
        ]
        client = MockLLMClient(response_templates=templates)
        
        # Generate responses for many different prompts
        responses = []
        for i in range(20):
            prompt = f"Test prompt number {i}"
            response = client.generate(prompt)
            responses.append(response)
        
        # Should use different templates (different starting phrases)
        unique_starts = set(tuple(resp.split()[0:2]) for resp in responses if len(resp.split()) >= 2)
        assert len(unique_starts) > 1  # Multiple templates should be used
    
    def test_generate_handles_unicode(self):
        """Test generate handles unicode characters properly."""
        client = MockLLMClient()
        
        response = client.generate("What about café naïve protocols? 🩸")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_handles_very_long_prompt(self):
        """Test generate handles very long prompts."""
        client = MockLLMClient()
        
        very_long_prompt = "blooddonation " * 1000  # Very long prompt
        response = client.generate(very_long_prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_special_characters(self):
        """Test generate handles special characters in prompts."""
        client = MockLLMClient()
        
        special_prompt = "What about @#$%^&*() protocols?"
        response = client.generate(special_prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0


class TestGeminiLLMClient:
    """Test cases for GeminiLLMClient (compilation only)."""
    
    def test_gemini_client_class_exists(self):
        """Test that GeminiLLMClient class can be imported."""
        assert GeminiLLMClient is not None
        assert issubclass(GeminiLLMClient, LLMClient)
    
    def test_gemini_client_has_required_methods(self):
        """Test that GeminiLLMClient implements required methods."""
        assert hasattr(GeminiLLMClient, 'generate')
        assert callable(getattr(GeminiLLMClient, 'generate'))


class TestLLMClientInterface:
    """Test cases for LLMClient interface."""
    
    def test_interface_is_abstract(self):
        """Test that LLMClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMClient()
    
    def test_mock_client_implements_interface(self):
        """Test that MockLLMClient implements the interface."""
        client = MockLLMClient()
        assert isinstance(client, LLMClient)
    
    def test_interface_methods_exist(self):
        """Test that interface defines required methods."""
        assert hasattr(LLMClient, 'generate')


class TestGetLLMClient:
    """Test cases for get_llm_client factory function."""
    
    def test_get_llm_client_function_exists(self):
        """Test that get_llm_client function exists."""
        assert callable(get_llm_client)
    
    def test_function_signature_correct(self):
        """Test that function has correct signature."""
        import inspect
        sig = inspect.signature(get_llm_client)
        assert len(sig.parameters) == 0  # No parameters expected


class TestMockLLMClientRealWorldScenarios:
    """Test MockLLMClient with realistic medical/operational scenarios."""
    
    def setup_method(self):
        """Set up test client for scenario tests."""
        self.client = MockLLMClient()
    
    def test_medical_query_responses(self):
        """Test responses to medical-related queries."""
        medical_prompts = [
            "What are the donor eligibility criteria for blood donation?",
            "How should plasma be stored and transported?", 
            "What are the emergency procedures for adverse reactions?",
            "Explain the blood typing and cross-matching process.",
            "What infection control measures are required?"
        ]
        
        responses = []
        for prompt in medical_prompts:
            response = self.client.generate(prompt)
            responses.append(response)
            
            # Basic validation
            assert isinstance(response, str)
            assert len(response) > 20  # Should be substantive
            assert response != prompt  # Should not just echo the prompt
        
        # All responses should be different
        assert len(set(responses)) == len(responses)
    
    def test_operational_query_responses(self):
        """Test responses to operational queries."""
        operational_prompts = [
            "How do we handle equipment maintenance schedules?",
            "What is the protocol for staff training documentation?",
            "Explain the inventory management process for supplies.",
            "How should we escalate critical incidents?"
        ]
        
        for prompt in operational_prompts:
            response = self.client.generate(prompt)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # Basic validation - should be a substantive response
            assert len(response.split()) > 5  # Should have multiple words
            # Should not just echo the prompt
            assert response.lower() != prompt.lower()
    
    def test_consistency_across_similar_prompts(self):
        """Test that similar prompts get consistent response patterns."""
        base_prompt = "What are the safety protocols for"
        variations = [
            f"{base_prompt} blood collection?",
            f"{base_prompt} plasma processing?", 
            f"{base_prompt} donor screening?",
            f"{base_prompt} equipment sterilization?"
        ]
        
        responses = [self.client.generate(prompt) for prompt in variations]
        
        # Should all be strings with content
        assert all(isinstance(r, str) and len(r) > 0 for r in responses)
        
        # Each should be deterministic
        for i, prompt in enumerate(variations):
            repeat_response = self.client.generate(prompt)
            assert responses[i] == repeat_response
    
    def test_empty_and_edge_cases(self):
        """Test edge cases and error conditions."""
        edge_cases = [
            "",  # Empty
            "   ",  # Whitespace only
            "?",  # Just punctuation
            "a",  # Single character
            "What?",  # Minimal question
            "\n\n\n",  # Just newlines
        ]
        
        for case in edge_cases:
            response = self.client.generate(case)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # Should handle gracefully, not crash
