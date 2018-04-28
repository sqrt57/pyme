import argparse
import sys

from pyme import base
from pyme import eval
from pyme import write
from pyme.interpreter import Interpreter
from pyme.reader import Reader


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=""
        " Run Pyme interpreter. If no script is specified"
        " or --interactive is present"
        " enter Read-Eval-Print loop.")
    parser.add_argument("-e", "--eval", dest="code", action="append",
                        help="Evaluate CODE before script")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after running script")
    parser.add_argument("script", nargs="?",
                        help='Execute script, "-" for stdin')
    parser.add_argument("args", nargs=argparse.REMAINDER,
                        help="Script command-line arguments")
    return parser


INTRO = """Pyme interpreter.
"""


PROMPT = "Pyme> "


def repl(interpreter):
    interpreter.stdout.write(INTRO)
    interpreter.stdout.flush_output()
    while True:
        interpreter.stdout.write(PROMPT)
        interpreter.stdout.flush_output()
        expr = interpreter.reader.read(interpreter.stdin)
        if base.eofp(expr):
            interpreter.stdout.newline()
            return
        result = eval.eval(expr, env=interpreter.global_env)
        write.write_to(result, interpreter.stdout)
        interpreter.stdout.newline()


def main(args=None):
    parser = cmdline_parser()
    args = parser.parse_args(args)
    interpreter = Interpreter()

    if args.code is not None:
        for code in args.code:
            interpreter.eval_str(code)

    if args.script == "-":
        interpreter.eval_stream(sys.stdin)
    else:
        if args.script is not None:
            interpreter.eval_file(args.script)
        if args.interactive or args.script is None:
            repl(interpreter)


if __name__ == "__main__":
    main()
