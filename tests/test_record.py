import io
import pathlib
import unittest

from pyme import Interpreter
from pyme import base
from pyme import interop
from pyme import ports


class TestCreateRecordType(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_create_record_type(self):
        self.interpreter.eval_str(
            "(define r (create-record-type 'qqq '(a b) '(c)))")
        self.assertTrue(self.interpreter.eval_str(
            "(eq? (record-type-name r) 'qqq)"))

    def test_record_write(self):
        stream = io.StringIO()
        self.interpreter.stdout = ports.TextStreamPort.from_stream(stream)
        self.interpreter.eval_str("""
            (define r (create-record-type 'qqq '(a b) '(c)))
            (write r)
        """)


class TestRecord(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()
        self.interpreter.eval_str("""
            (define r (create-record-type 'qqq '(a b) '(c)))

            (define create-r (record-constructor r))
            (define r? (record-type-checker r))

            (define get-a (record-field-getter 'a))
            (define set-a! (record-field-setter 'a))
            (define get-b (record-field-getter 'b))
            (define set-b! (record-field-setter 'b))
            (define get-c (record-field-getter 'c))
            (define set-c! (record-field-setter 'c))
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

    def test_record_write(self):
        stream = io.StringIO()
        self.interpreter.stdout = ports.TextStreamPort.from_stream(stream)
        self.interpreter.eval_str("""
            (define x (create-r 5 8))
            (write x)
        """)
