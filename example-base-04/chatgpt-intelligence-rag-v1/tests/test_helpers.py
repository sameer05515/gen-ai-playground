import unittest

from app.data_loader import chunk_text
from app.rag import build_where, snapshot_number, tokenize


class RAGHelperTests(unittest.TestCase):
    def test_build_where_empty(self):
        self.assertIsNone(build_where(None, None))

    def test_build_where_single_filter(self):
        self.assertEqual(
            build_where("conversation-1", None),
            {"conv_id": "conversation-1"},
        )

    def test_build_where_combined_filter(self):
        self.assertEqual(
            build_where("conversation-1", "message-1"),
            {"$and": [
                {"conv_id": "conversation-1"},
                {"message_id": "message-1"},
            ]},
        )

    def test_snapshot_number(self):
        self.assertEqual(snapshot_number("v51"), 51)
        self.assertEqual(snapshot_number("v9"), 9)
        self.assertEqual(snapshot_number("unknown"), -1)

    def test_tokenize_removes_common_words(self):
        tokens = tokenize("How did I use JWT refresh-token in Spring Boot?")
        self.assertIn("jwt", tokens)
        self.assertIn("refresh-token", tokens)
        self.assertIn("spring", tokens)
        self.assertNotIn("how", tokens)

    def test_chunk_text_overlap_and_validation(self):
        text = "A" * 100
        chunks = chunk_text(text, chunk_size=40, overlap=10)
        self.assertGreater(len(chunks), 1)
        with self.assertRaises(ValueError):
            chunk_text(text, chunk_size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
