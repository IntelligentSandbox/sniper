import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from pythonbridge.core.review import review_pr

TESTS_DIR = Path(__file__).parent.parent
HELLO_PATCH = (TESTS_DIR / "test_files" / "hello.patch").read_text()


class TestReview(unittest.TestCase):
    @patch("pythonbridge.core.review.load_environment")
    @patch("pythonbridge.core.review.create_reaction")
    @patch("pythonbridge.core.review.get_diff")
    @patch("pythonbridge.core.review.GraphBuilder")
    @patch("pythonbridge.core.review.post_review")
    def test_review_pr_reviews_files(
        self,
        mock_post_review,
        mock_graph_builder,
        mock_get_diff,
        mock_create_reaction,
        mock_load_env,
    ):
        # https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files
        mock_file = Mock()
        mock_file.filename = "pythonbridge/tests/hello.py"
        mock_file.status = "added"
        mock_file.patch = HELLO_PATCH

        mock_get_diff.return_value = [mock_file]

        mock_graph = Mock()
        mock_graph.invoke.return_value = {"pr_review": "Looks good, no issues found."}
        mock_graph_builder.return_value.build_graph.return_value = mock_graph

        payload = {
            "number": 1,
            "repository": {"full_name": "owner/repo"},
            "installation": {"id": "12345"},
        }

        reviews = review_pr(payload)

        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["filename"], "pythonbridge/tests/hello.py")
        self.assertEqual(reviews[0]["status"], "added")
        self.assertEqual(reviews[0]["review"], "Looks good, no issues found.")

        mock_load_env.assert_called_once()
        mock_get_diff.assert_called_once_with(payload)
        mock_graph.invoke.assert_called_once_with({"pr_input": mock_file.patch})
        mock_post_review.assert_called_once()

    @patch("pythonbridge.core.review.load_environment")
    @patch("pythonbridge.core.review.create_reaction")
    @patch("pythonbridge.core.review.get_diff")
    @patch("pythonbridge.core.review.GraphBuilder")
    @patch("pythonbridge.core.review.post_review")
    def test_review_pr_skips_files_without_patch(
        self,
        mock_post_review,
        mock_graph_builder,
        mock_get_diff,
        mock_create_reaction,
        mock_load_env,
    ):
        # Deleted files have no patch (no diff to review)
        mock_file = Mock()
        mock_file.filename = "deleted.py"
        mock_file.status = "removed"
        mock_file.patch = None

        mock_get_diff.return_value = [mock_file]

        mock_graph = Mock()
        mock_graph_builder.return_value.build_graph.return_value = mock_graph

        payload = {
            "number": 1,
            "repository": {"full_name": "owner/repo"},
            "installation": {"id": "12345"},
        }

        reviews = review_pr(payload)

        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["filename"], "deleted.py")
        self.assertIsNone(reviews[0]["review"])

        mock_load_env.assert_called_once()
        mock_get_diff.assert_called_once_with(payload)
        mock_post_review.assert_called_once()
        # LLM should NOT be called
        mock_graph.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
