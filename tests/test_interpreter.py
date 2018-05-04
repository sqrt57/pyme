import io
import pathlib
import unittest

from pyme import Interpreter
from pyme import exceptions
from pyme import ports


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()
        self.interpreter.load_paths = [
            pathlib.Path(__file__).parent.parent
        ]

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

    def test_write(self):
        stream = io.StringIO()
        self.interpreter.stdout = ports.TextStreamPort.from_stream(stream)
        self.interpreter.eval_str('(write "abc")')
        self.assertEqual(stream.getvalue(), '"abc"')

    def test_display(self):
        stream = io.StringIO()
        self.interpreter.stdout = ports.TextStreamPort.from_stream(stream)
        self.interpreter.eval_str('(display "abc")')
        self.assertEqual(stream.getvalue(), 'abc')

    def test_call_hook(self):
        def call_hook(call_stack, stack):
            nonlocal max_depth
            max_depth = max(max_depth, len(call_stack))
        max_depth = 0
        n = 100
        self.interpreter.instrumentation["eval"]["call"] = call_hook
        result = self.interpreter.eval_str("""
            (define (sum-to n) (if (= n 0) 0 (+ n (sum-to (- n 1)))))
            (sum-to {})
        """.format(n))
        self.assertEquals(result, n * (n+1) // 2)
        self.assertGreaterEqual(max_depth, n)
