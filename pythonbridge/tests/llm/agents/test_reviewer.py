import unittest
from unittest.mock import Mock, patch

from pythonbridge.llm.agents.reviewer import ReviewAgent


class TestReviewAgent(unittest.TestCase):
    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_init_creates_llm_with_system_prompt(self, mock_groq_llm):
        """Test that ReviewAgent initializes GroqLLM with system prompt"""
        _agent = ReviewAgent("extra context")

        mock_groq_llm.assert_called_once()
        call_kwargs = mock_groq_llm.call_args[1]
        self.assertIn("system_prompt", call_kwargs)
        self.assertIn("expert PR code reviewer", call_kwargs["system_prompt"])
        self.assertIn("extra context", call_kwargs["system_prompt"])

    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_init_with_empty_context(self, mock_groq_llm):
        """Test that ReviewAgent works with empty context"""
        _agent = ReviewAgent("")

        mock_groq_llm.assert_called_once()
        call_kwargs = mock_groq_llm.call_args[1]
        self.assertIn("expert PR code reviewer", call_kwargs["system_prompt"])

    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_review_returns_pr_review_in_state(self, mock_groq_llm):
        """Test that review method returns pr_review in state dict"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = "This code looks good."
        mock_groq_llm.return_value = mock_llm_instance

        agent = ReviewAgent("context")
        state = {"pr_input": "diff --git a/file.py"}

        result = agent.review(state)

        self.assertIn("pr_review", result)
        self.assertEqual(result["pr_review"], "This code looks good.")

    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_review_returns_review_context(self, mock_groq_llm):
        """Test that review method returns review_context in state dict"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = "Review output"
        mock_groq_llm.return_value = mock_llm_instance

        agent = ReviewAgent("my custom context")
        state = {"pr_input": "some patch"}

        result = agent.review(state)

        self.assertIn("review_context", result)
        self.assertEqual(result["review_context"], "my custom context")

    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_review_invokes_llm_with_pr_input(self, mock_groq_llm):
        """Test that review passes pr_input to LLM"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = "Response"
        mock_groq_llm.return_value = mock_llm_instance

        agent = ReviewAgent("")
        state = {"pr_input": "the actual diff content"}

        agent.review(state)

        mock_llm_instance.invoke.assert_called_once_with("the actual diff content")

    @patch("pythonbridge.llm.agents.reviewer.GroqLLM")
    def test_review_raises_on_none_response(self, mock_groq_llm):
        """Test that review raises RuntimeError when LLM returns None"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = None
        mock_groq_llm.return_value = mock_llm_instance

        agent = ReviewAgent("")
        state = {"pr_input": "some patch"}

        with self.assertRaises(RuntimeError) as context:
            agent.review(state)

        self.assertIn("did not respond", str(context.exception))


if __name__ == "__main__":
    unittest.main()
