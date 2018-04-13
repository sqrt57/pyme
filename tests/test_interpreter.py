import unittest

from pyme import Interpreter


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_create(self):
        result = self.interpreter.eval_str("(+ 1 2)")
        self.assertEqual(result, 3)
