import unittest

from pyme import Interpreter


class TestInterpreter(unittest.TestCase):

    def test_create(self):
        interpreter = Interpreter()
        result = interpreter.eval_str("(+ 1 2)")
        self.assertEqual(result, 3)
