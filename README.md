## Verba — A Natural English Programming Language

Verba is a tiny interpreter where programs read like natural English sentences.

### Key constraint

In Verba source files, the only allowed symbols are:

- comma `,` (separator)
- period `.` (statement terminator)

Everything else is expressed using English words.

### Install (optional)

From the repo root:

```bash
python -m pip install -e .
```

### Run a Verba program

```bash
python -m verba examples/full_example.vb
```

Or, if installed:

```bash
verba examples/full_example.vb
```

### Start the REPL

```bash
python -m verba --repl
```

Type `end.` on its own line to exit.

### Supported language features (v0.2)

- Variables: `let`, `set`, `increase`, `decrease`
- Output: `say`, `display`
- Input: `ask`
- Conditions: `if ... do the following. ... end if.`, with optional `otherwise do the following.`
- Loops: `repeat ... times`, `keep doing the following while ...`, `for each ... in ...`
- Lists: `a list of ...`, `add ... to ...`, `remove ... from ...`, `item N of ...`
- Functions: `define ... as follows. ... end define.`, `give back ...`, `run ...`
- Math: `plus`, `minus`, `times`, `divided by`, `remainder after dividing by`
 - File I/O: `save [text] to file called [filename].`, `load file called [filename] into [variable].`

### Not yet implemented

- Simple standard library helpers like `run show length of [list]` or `run convert [var] to number`.

### Notes

- Verba detects blocks by indentation (4 spaces or a tab).
- When Verba cannot understand a line, it throws a plain-English error pointing at the line number.
