import unittest

from pyme import Interpreter
from pyme import exceptions


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_create(self):
        result = self.interpreter.eval_str("(+ 1 2)")
        self.assertEqual(result, 3)

    def test_error(self):
        with self.assertRaises(exceptions.SchemeError) as cm:
            self.interpreter.eval_str('(error "qwerty")')
        self.assertEqual(cm.exception.object, "qwerty")
