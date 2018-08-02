import io
import pathlib
import unittest

from pyme import Interpreter
from pyme import base
from pyme import interop


class TestCreateRecordType(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_create_record_type(self):
        self.interpreter.eval_str(
            "(define r (create-record-type 'qqq '(a b) '(c)))")
        result = self.interpreter.eval_str("r")
        result, rest = interop.from_scheme_list(result)
        # Constructor, type checker and 3 field accessors
        self.assertEqual(len(result), 5)
        self.assertTrue(base.nullp(rest))
        self.assertEqual(result[2].car.name, "a")
        self.assertEqual(result[3].car.name, "b")
        self.assertEqual(result[4].car.name, "c")


class TestRecord(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()
        self.interpreter.eval_str("""
            (define r (create-record-type 'qqq '(a b) '(c)))

            (define create-r (car r))
            (define r? (car (cdr r)))
            (define a (car (cdr (cdr r))))
            (define b (car (cdr (cdr (cdr r)))))
            (define c (car (cdr (cdr (cdr (cdr r))))))

            (define get-a (car (cdr a)))
            (define set-a! (car (cdr (cdr a))))
            (define get-b (car (cdr b)))
            (define set-b! (car (cdr (cdr b))))
            (define get-c (car (cdr c)))
            (define set-c! (car (cdr (cdr c))))
        """)

    def test_record_type(self):
        self.interpreter.eval_str("""
            (define x (create-r 5 8))
        """)
        self.assertTrue(self.interpreter.eval_str("(r? x)"))

    def test_create(self):
        self.interpreter.eval_str("""
            (define x (create-r 5 8))
        """)
        self.assertEqual(self.interpreter.eval_str("(get-a x)"), 5)
        self.assertEqual(self.interpreter.eval_str("(get-b x)"), 8)
        self.assertEqual(self.interpreter.eval_str("(get-c x)"), False)

    def test_set(self):
        self.interpreter.eval_str("""
            (define x (create-r 5 8))
            (set-a! x 30)
            (set-c! x 35)
        """)
        self.assertEqual(self.interpreter.eval_str("(get-a x)"), 30)
        self.assertEqual(self.interpreter.eval_str("(get-c x)"), 35)
