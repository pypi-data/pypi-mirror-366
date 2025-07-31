def multiply(a, b):
    return a * b


def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as exc:
        return f"Error: Cannot divide by 0 ({exc})"
