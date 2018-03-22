"""
Run tests.

Usage:
    python runtests.py
"""

import unittest


def main():
    """Tests runner entry point."""
    loader = unittest.defaultTestLoader
    tests = loader.discover("tests")
    runner = unittest.TextTestRunner()
    runner.run(tests)


if __name__ == "__main__":
    main()
