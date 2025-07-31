from basic_calculator.basic import add, subtract
from basic_calculator.medium import multiply, divide


def options():
    option = """
                  ======================
                  |   + or add         |
                  |   - or subtract    |
                  |   * or multiply    |
                  |   / or divide      |
                  ======================
 """
    return option


def main():
    menu = options()
    print(menu)

    print(
        """
                         Examples
            
                     1 + 1 or 1 add 1
                   2 - 2 or 2 subtract 2
                   3 * 3 or 3 multiply 3
                    4 / 4 or 4 divide 4

If there isn't a blank space before and after the operation type,
an error will occur and the operation will be requested again.          
"""
    )
    while True:
        try:
            number1, option, number2 = input("Operation: ").strip().split(" ")

            match option:
                case "+" | "add":
                    result = add(float(number1), float(number2))
                    print(f"Result: {number1} {option} {number2} = {result}")
                case "-" | "subtract":
                    result = subtract(float(number1), float(number2))
                    print(f"Result: {number1} {option} {number2} = {result}")
                case "*" | "multiply":
                    result = multiply(float(number1), float(number2))
                    print(f"Result: {number1} {option} {number2} = {result}")
                case "/" | "divide":
                    result = divide(float(number1), float(number2))
                    print(f"Result: {number1} {option} {number2} = {result}")
                case _:
                    print(
                        "Invalid operation type (+, -, *, / or add, subtract, multiply, divide)."
                    )
            if (
                input("Do you want to perform another operation? (yes/no) ").lower()
                != "yes"
            ):
                break

        except ValueError as exc:
            print(
                f"The operation type is incorrect. Please check the example and try again! ({exc})"
            )
            continue


if __name__ == "__main__":
    main()
