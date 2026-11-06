"""Unit tests for LayaDecisionEngine interface and state formatting."""

import unittest
from laya_service import LayaDecisionEngine


class TestLayaDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LayaDecisionEngine()

    def test_build_state(self):
        text = "Hello world"
        state = self.engine._build_state(text)
        self.assertEqual(state["text"], text)
        self.assertEqual(state["prompt"], text)
        self.assertEqual(state["message"], text)
        self.assertEqual(state["body"], text)
        self.assertEqual(state["ticket"], text)

    def test_lazy_initialization(self):
        self.assertIsNone(self.engine._router)
        # Verify unload when not loaded doesn't crash
        self.engine.unload()
        self.assertIsNone(self.engine._router)


if __name__ == "__main__":
    unittest.main()
