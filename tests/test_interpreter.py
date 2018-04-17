import unittest

from pyme import Interpreter
from pyme import exceptions


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_create(self):
        result = self.interpreter.eval_str("(+ 1 2)")
        self.assertEqual(result, 3)

    def test_define(self):
        result = self.interpreter.eval_str("(define a 1) a")
        self.assertEqual(result, 1)

    def test_error(self):
        with self.assertRaises(exceptions.SchemeError) as cm:
            self.interpreter.eval_str('(error "qwerty")')
        self.assertEqual(cm.exception.object, "qwerty")

    def test_eval_file(self):
        self.interpreter.eval_file("tests/define_a_1.scm")
        result = self.interpreter.eval_str("a")
        self.assertEqual(result, 1)
