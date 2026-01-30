import unittest
from unittest.mock import Mock, patch

from langgraph.graph.state import CompiledStateGraph

from pythonbridge.llm.entry import GraphBuilder


class TestGraphBuilder(unittest.TestCase):
    def test_build_graph_returns_compiled_graph(self):
        """Test that build_graph returns a CompiledStateGraph"""
        builder = GraphBuilder()
        graph = builder.build_graph()

        self.assertIsInstance(graph, CompiledStateGraph)

    def test_build_graph_with_context(self):
        """Test that build_graph accepts context parameters"""
        builder = GraphBuilder()
        graph = builder.build_graph(
            review_context="Review context", validate_context="Validate context"
        )

        self.assertIsInstance(graph, CompiledStateGraph)

    @patch("pythonbridge.llm.entry.ReviewAgent")
    @patch("pythonbridge.llm.entry.ValidateAgent")
    def test_build_graph_creates_agents_with_context(
        self, mock_validate_agent, mock_review_agent
    ):
        """Test that agents are created with the provided context"""
        builder = GraphBuilder()
        builder.build_graph(
            review_context="test review context",
            validate_context="test validate context",
        )

        mock_review_agent.assert_called_once_with("test review context")
        mock_validate_agent.assert_called_once_with("test validate context")

    @patch("pythonbridge.llm.entry.ReviewAgent")
    @patch("pythonbridge.llm.entry.ValidateAgent")
    def test_graph_invokes_review_then_validate(
        self, mock_validate_agent, mock_review_agent
    ):
        """Test that graph executes review_agent then validate_agent in order"""
        mock_review_instance = Mock()
        mock_review_instance.review.return_value = {"pr_review": "Test review"}
        mock_review_agent.return_value = mock_review_instance

        mock_validate_instance = Mock()
        mock_validate_instance.validate.return_value = {"pr_review_validation": "Valid"}
        mock_validate_agent.return_value = mock_validate_instance

        builder = GraphBuilder()
        graph = builder.build_graph()

        result = graph.invoke({"pr_input": "test patch"})

        mock_review_instance.review.assert_called_once()
        mock_validate_instance.validate.assert_called_once()

        self.assertEqual(result["pr_review"], "Test review")
        self.assertEqual(result["pr_review_validation"], "Valid")

    @patch("pythonbridge.llm.entry.ReviewAgent")
    @patch("pythonbridge.llm.entry.ValidateAgent")
    def test_graph_passes_state_between_nodes(
        self, mock_validate_agent, mock_review_agent
    ):
        """Test that state flows correctly from review to validate"""
        mock_review_instance = Mock()
        mock_review_instance.review.return_value = {
            "pr_review": "Generated review",
            "review_context": "context",
        }
        mock_review_agent.return_value = mock_review_instance

        mock_validate_instance = Mock()
        mock_validate_instance.validate.return_value = {
            "pr_review_validation": "Approved"
        }
        mock_validate_agent.return_value = mock_validate_instance

        builder = GraphBuilder()
        graph = builder.build_graph()

        _result = graph.invoke({"pr_input": "diff content"})

        # Verify validate received state with pr_review from review node
        validate_call_args = mock_validate_instance.validate.call_args[0][0]
        self.assertEqual(validate_call_args["pr_input"], "diff content")
        self.assertEqual(validate_call_args["pr_review"], "Generated review")


if __name__ == "__main__":
    unittest.main()
