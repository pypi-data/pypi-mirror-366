# NovaLang 🚀

**A modern, functional programming language designed for the future.**

[![PyPI version](https://badge.fury.io/py/novalang.svg)](https://badge.fury.io/py/novalang)
[![Python Support](https://img.shields.io/pypi/pyversions/novalang.svg)](https://pypi.org/project/novalang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **Modern Syntax**: Clean, readable syntax inspired by the best of JavaScript and Python
- **Functional Programming**: First-class functions, lambdas, higher-order functions
- **Rich Standard Library**: Built-in functions for arrays, strings, math, JSON, and more
- **VS Code Support**: Full syntax highlighting and code snippets
- **Interactive REPL**: Easy development and testing
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
pip install novalang
```

### Your First NovaLang Program

Create a file `hello.nova`:

```javascript
// Variables and functions
let name = "World";
function greet(person) {
    return "Hello, " + person + "!";
}

print greet(name);

// Higher-order functions
let numbers = [1, 2, 3, 4, 5];
let doubled = map(numbers, function(x) { return x * 2; });
print "Doubled: " + stringifyJSON(doubled);
```

Run it:

```bash
novalang hello.nova
```

### 3. Example
```nova
print("Hello, NovaLang!")
```

## Project Structure
- `main.py` — CLI entry point
- `lexer.py` — Tokenizer
- `parser.py` — AST builder
- `interpreter.py` — Code executor
- `test.nova` — Example NovaLang file

## Contributing
Pull requests and issues are welcome!

## License
MIT
