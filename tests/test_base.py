import io
import pathlib
import unittest

from pyme import base
from pyme import eval
from pyme import exceptions
from pyme import interop
from pyme import reader
from pyme.interpreter import Interpreter


class TestFuns(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()
        self.interpreter.load_paths = [
            pathlib.Path(__file__).parent.parent
        ]

    def test_nullp(self):
        self.assertTrue(base.nullp(base.null()))
        self.assertFalse(base.nullp(5))
        self.assertFalse(base.nullp(base.cons(None, base.null())))

    def test_pairp(self):
        self.assertFalse(base.pairp(base.null()))
        self.assertFalse(base.pairp(5))
        self.assertTrue(base.pairp(base.cons(None, base.null())))

    def test_listp(self):
        self.assertEqual(base.listp(base.null()), True)
        self.assertEqual(base.listp(5), False)
        self.assertEqual(base.listp(base.cons(1, base.null())), True)

    def test_plus(self):
        self.assertEqual(self.interpreter.eval_str("(+ 5)"), 5)
        self.assertEqual(self.interpreter.eval_str("(+ 5 6)"), 11)
        self.assertEqual(self.interpreter.eval_str("(+ 5 6 7)"), 18)

    def test_minus(self):
        self.assertEqual(self.interpreter.eval_str("(- 5)"), -5)
        self.assertEqual(self.interpreter.eval_str("(- 5 6)"), -1)
        self.assertEqual(self.interpreter.eval_str("(- 5 6 7)"), -8)

    def test_mult(self):
        self.assertEqual(self.interpreter.eval_str("(* 5)"), 5)
        self.assertEqual(self.interpreter.eval_str("(* 5 6)"), 30)
        self.assertEqual(self.interpreter.eval_str("(* 5 6 7)"), 210)

    def test_car_cdr(self):
        self.interpreter.eval_str("(define x (cons 5 (cons 3 '())))")
        self.assertEqual(self.interpreter.eval_str("(car x)"), 5)
        self.assertTrue(self.interpreter.eval_str("(pair? (cdr x))"))

    def test_list(self):
        self.interpreter.eval_str("(define x (list 5 7))")
        self.assertEqual(self.interpreter.eval_str("(car x)"), 5)
        self.assertEqual(self.interpreter.eval_str("(car (cdr x))"), 7)
        self.assertTrue(self.interpreter.eval_str("(null? (cdr (cdr x)))"))

    def test_arithmetic_equal(self):
        self.assertTrue(self.interpreter.eval_str("(= 5 5)"))
        self.assertTrue(self.interpreter.eval_str("(= 5 5 5)"))
        self.assertFalse(self.interpreter.eval_str("(= 5 8)"))
        self.assertFalse(self.interpreter.eval_str("(= 5 5 8)"))

    def test_less(self):
        self.assertTrue(self.interpreter.eval_str("(< 5 6)"))
        self.assertTrue(self.interpreter.eval_str("(< 5 6 7)"))
        self.assertFalse(self.interpreter.eval_str("(< 5 5)"))
        self.assertFalse(self.interpreter.eval_str("(< 5 4)"))
        self.assertFalse(self.interpreter.eval_str("(< 5 6 3)"))

    def test_greater(self):
        self.assertTrue(self.interpreter.eval_str("(> 6 5)"))
        self.assertTrue(self.interpreter.eval_str("(> 7 6 5)"))
        self.assertFalse(self.interpreter.eval_str("(> 5 5)"))
        self.assertFalse(self.interpreter.eval_str("(> 4 5)"))
        self.assertFalse(self.interpreter.eval_str("(> 5 4 8)"))

    def test_less_or_equal(self):
        self.assertTrue(self.interpreter.eval_str("(<= 5 6)"))
        self.assertTrue(self.interpreter.eval_str("(<= 5 6 7)"))
        self.assertTrue(self.interpreter.eval_str("(<= 5 5)"))
        self.assertFalse(self.interpreter.eval_str("(<= 5 4)"))
        self.assertFalse(self.interpreter.eval_str("(<= 5 6 3)"))

    def test_greater_or_equal(self):
        self.assertTrue(self.interpreter.eval_str("(>= 6 5)"))
        self.assertTrue(self.interpreter.eval_str("(>= 7 6 5)"))
        self.assertTrue(self.interpreter.eval_str("(>= 5 5)"))
        self.assertFalse(self.interpreter.eval_str("(>= 4 5)"))
        self.assertFalse(self.interpreter.eval_str("(>= 5 4 8)"))

    def test_not(self):
        self.assertFalse(self.interpreter.eval_str("(not #t)"))
        self.assertTrue(self.interpreter.eval_str("(not #f)"))
        self.assertFalse(self.interpreter.eval_str("(not 3)"))

    def test_eq(self):
        self.assertTrue(self.interpreter.eval_str(
            "(eq? '() '())"))
        self.assertTrue(self.interpreter.eval_str(
            "(eq? 'x 'x)"))
        self.assertTrue(self.interpreter.eval_str(
            "(define a 3) (eq? a a)"))
        self.assertTrue(self.interpreter.eval_str(
            '(define a "qwe") (eq? a a)'))
        self.assertTrue(self.interpreter.eval_str(
            "(define a '(x y 5)) (eq? a a)"))
        self.assertFalse(self.interpreter.eval_str(
            "(eq? 5 8)"))
        self.assertFalse(self.interpreter.eval_str(
            "(eq? '(a) '(b))"))
