# 🧮 CLI Calculator

A simple terminal-based calculator that supports basic arithmetic operations: **addition**, **subtraction**, **multiplication**, and **division.**

## Calculator on PyPI 
[cli_calculator 0.0.1](https://pypi.org/project/cli-calculator/)

**How to install:**
You can install the calculator directly from PyPI using pip:

```
pip install cli_calculator
```

## 📦 Features

- [+] Addition (```+``` or ```add```)

- [-] Subtraction (```-``` or ```subtract```)
 
- [*] Multiplication (```*``` or ```multiply```)

- [÷] Division (```/``` or ```divide```) - includes zero division handling

- User-friendly terminal interface with clear examples

- Modular structure with organized codebase

## 🚀 Usage

Run the calculator from the terminal:
```
cli_calculator
```

You'll see the operation menu and example inputs:
```
======================
|   + or add         |
|   - or subtract    |
|   * or multiply    |
|   / or divide      |
======================

Examples:
1 + 1 or 1 add 1
2 - 2 or 2 subtract 2
3 * 3 or 3 multiply 3
4 / 4 or 4 divide 4
```
**Note:** Operations must have a space before and after the operator (e.g., ```3 + 2```, not ```3+2```).

## 📁 Project Structure

```
cli_calculator/
├── basic_calculator/
│   ├── __init__.py
│   ├── basic.py          # Contains add & subtract functions
│   └── medium.py         # Contains multiply & divide functions
├── cli_calculator
    ├──__init__.py
    └── main.py           # Entry point for the calculator
├── requirements.txt      # Project dependencies (currently empty)
├── setup.py              # Package configuration
├── .gitignore            # Git exclusions
├── LICENSE               # 
└── README.md             # Project documentation
```

## 📜 Requirements

- Python 3.8+

- No external dependencies currently

## 👨‍💻 Author 

Developed with care by **Robson Barbiere** 🧠💻 GitHub: [robson-k](https://github.com/robson-k)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)