# pyme
Scheme interpreter in Python

## Overview
This is a simple implementation of Scheme programming language in Python.

## Goals
- Learn how to implement Scheme interpreter in the simplest way
- Bootstrap a more ambitious Scheme interpreter/compiler "enscheme"
- Platform independence: win32, win64, linux32, linux64, macos64 targets.

## Non-goals
- REPL
- Interpretation speed
- Small memory consumption
- Completness or standards conformance
- Good error reporting
- Debugging facilities
- call-with-current-continuation

## Building instructions
pyme is written in Python 3. For now it does not require anything else. Al functionality is in discoverable tests:
```
python -m unittest
```

## Acknowledgements
- "Structure and Interpretation of Computer Programs" book
  - [https://mitpress.mit.edu/sicp/](https://mitpress.mit.edu/sicp/)
- Revised 5 Report on the Algorithmic Language Scheme
  - [http://www.schemers.org/Documents/Standards/R5RS/](http://www.schemers.org/Documents/Standards/R5RS/)
- Revised 7 Report on the Algorithmic Language Scheme
  - [http:/www.r7rs.org/](http://www.r7rs.org/)
