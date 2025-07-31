from .state import State


def add(state: State, a: int, b: int):
    """Add two numbers"""
    return {"result": a + b}
def subtract(state: State, a: int, b: int):
    """Subtract two numbers"""
    return {"result": a - b}
def multiply(state: State, a: int, b: int):
    """Multiply two numbers"""
    return {"result": a * b}
def divide(state: State, a: int, b: int):
    """Divide two numbers"""
    return {"result": a / b}

tools = [add, subtract, multiply, divide]