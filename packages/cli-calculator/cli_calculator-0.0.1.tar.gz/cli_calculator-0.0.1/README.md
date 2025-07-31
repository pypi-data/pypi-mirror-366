# CLI Calculator

A simple terminal-based calculator that supports basic arithmetic operations: **addition**, **subtraction**, **multiplication**, and **division.**


## 📦 Features

- [+] Addition (```+``` or ```add```)

- [-] Subtraction (```-``` or ```subtract```)
 
- [x] Multiplication (```*``` or ```multiply```)

- [÷] Division (```/``` or ```divide```) - includes zero division handling

- User-friendly terminal interface with clear examples

- Modular structure with organized codebase

## 🚀 Usage

Run the calculator from the terminal:
```
python main.py
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
├── main.py               # Entry point for the calculator
├── requirements.txt      # Project dependencies (currently empty)
├── setup.py              # Package configuration
├── .gitignore            # Git exclusions
└── README.md             # Project documentation
```

## 📜 Requirements

- Python 3.8+

- No external dependencies currently

## 👨‍💻 Author 

Developed with care by **Robson Barbiere** 🧠💻 GitHub: [robson-k](https://github.com/robson-k)