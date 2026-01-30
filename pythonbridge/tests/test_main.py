import unittest
from unittest.mock import patch

from pythonbridge.main import handle_msg


class TestMain(unittest.TestCase):
    def test_handle_msg_hello(self):
        """Test hello message type"""
        msg = {"type": "hello", "count": 42}
        response = handle_msg(msg)

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.response, "hello from python 42")
        self.assertIsNone(response.error)

    def test_handle_msg_hello_default_count(self):
        """Test hello message type with default count"""
        msg = {"type": "hello"}
        response = handle_msg(msg)

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.response, "hello from python 0")

    def test_handle_msg_unknown_type(self):
        """Test unknown message type returns error"""
        msg = {"type": "unknown"}
        response = handle_msg(msg)

        self.assertEqual(response.status, "error")
        self.assertEqual(response.error, "Unknown message type: unknown")
        self.assertIsNone(response.response)

    def test_handle_msg_main_missing_payload(self):
        """Test main message type without payload returns error"""
        msg = {"type": "main"}
        response = handle_msg(msg)

        self.assertEqual(response.status, "error")
        self.assertEqual(response.error, "Missing payload")

    @patch("pythonbridge.main.review_pr")
    def test_handle_msg_main_success(self, mock_review_pr):
        """Test main message type calls review_pr"""
        mock_review_pr.return_value = [{"filename": "test.py", "review": "Looks good"}]

        msg = {
            "type": "main",
            "payload": {
                "number": 1,
                "repository": {"full_name": "owner/repo"},
                "installation": {"id": "12345"},
            },
        }
        response = handle_msg(msg)

        self.assertEqual(response.status, "ok")
        self.assertEqual(
            response.response, [{"filename": "test.py", "review": "Looks good"}]
        )
        mock_review_pr.assert_called_once_with(msg["payload"])

    @patch("pythonbridge.main.review_pr")
    def test_handle_msg_main_exception(self, mock_review_pr):
        """Test main message type handles exceptions"""
        mock_review_pr.side_effect = Exception("Something went wrong")

        msg = {
            "type": "main",
            "payload": {
                "number": 1,
                "repository": {"full_name": "owner/repo"},
                "installation": {"id": "12345"},
            },
        }
        response = handle_msg(msg)

        self.assertEqual(response.status, "error")
        self.assertEqual(response.error, "Something went wrong")


if __name__ == "__main__":
    unittest.main()
