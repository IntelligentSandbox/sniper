import unittest
from unittest.mock import Mock, patch

from pythonbridge.llm.agents.validator import ValidateAgent


class TestValidateAgent(unittest.TestCase):
    @patch("pythonbridge.llm.agents.validator.GroqLLM")
    def test_init_creates_llm_with_system_prompt(self, mock_groq_llm):
        """Test that ValidateAgent initializes GroqLLM with system prompt"""
        _agent = ValidateAgent("extra context")

        mock_groq_llm.assert_called_once()
        call_kwargs = mock_groq_llm.call_args[1]
        self.assertIn("system_prompt", call_kwargs)
        self.assertIn("PR review validator", call_kwargs["system_prompt"])
        self.assertIn("extra context", call_kwargs["system_prompt"])

    @patch("pythonbridge.llm.agents.validator.GroqLLM")
    def test_init_with_empty_context(self, mock_groq_llm):
        """Test that ValidateAgent works with empty context"""
        _agent = ValidateAgent("")

        mock_groq_llm.assert_called_once()
        call_kwargs = mock_groq_llm.call_args[1]
        self.assertIn("PR review validator", call_kwargs["system_prompt"])

    @patch("pythonbridge.llm.agents.validator.GroqLLM")
    def test_validate_returns_pr_review_validation_in_state(self, mock_groq_llm):
        """Test that validate method returns pr_review_validation in state dict"""
        mock_llm_instance = Mock()
        mock_groq_llm.return_value = mock_llm_instance

        agent = ValidateAgent("context")
        state = {"pr_input": "diff content", "pr_review": "The review content"}

        result = agent.validate(state)

        self.assertIn("pr_review_validation", result)

    @patch("pythonbridge.llm.agents.validator.GroqLLM")
    def test_validate_returns_validate_context(self, mock_groq_llm):
        """Test that validate method returns validate_context in state dict"""
        mock_llm_instance = Mock()
        mock_groq_llm.return_value = mock_llm_instance

        agent = ValidateAgent("my validation context")
        state = {"pr_input": "some patch", "pr_review": "some review"}

        result = agent.validate(state)

        self.assertIn("validate_context", result)
        self.assertEqual(result["validate_context"], "my validation context")

    @patch("pythonbridge.llm.agents.validator.GroqLLM")
    def test_validate_currently_returns_empty_validation(self, mock_groq_llm):
        """Test that validate currently returns empty string (not implemented)"""
        mock_llm_instance = Mock()
        mock_groq_llm.return_value = mock_llm_instance

        agent = ValidateAgent("")
        state = {"pr_input": "patch", "pr_review": "review"}

        result = agent.validate(state)

        # Currently not implemented - returns empty string
        self.assertEqual(result["pr_review_validation"], "")


if __name__ == "__main__":
    unittest.main()
