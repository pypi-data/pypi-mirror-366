import logging
import math

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  

class Calculator:
    def __init__(self):
        self.logger = logger

    def add(self, a, b):
        self.logger.debug(f"Adding {a} + {b}")
        return a + b

    def subtract(self, a, b):
        self.logger.debug(f"Subtracting {b} from {a}")
        return a - b

    def multiply(self, a, b):
        self.logger.debug(f"Multiplying {a} * {b}")
        return a * b

    def divide(self, a, b):
        self.logger.debug(f"Dividing {a} by {b}")
        if b == 0:
            self.logger.error("Attempted division by zero")
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(self, a, b):
        self.logger.debug(f"Raising {a} to the power of {b}")
        return a ** b

    def square_root(self, a):
        self.logger.debug(f"Calculating square root of {a}")
        if a < 0:
            self.logger.error("Square root of negative number requested")
            raise ValueError("Cannot calculate square root of negative number")
        return a ** 0.5
    
    def factorial(self, a):
        self.logger.debug(f"Calculating factorial of {a}")
        if not isinstance(a, int) or a < 0:
            self.logger.error("Factorial requires a non-negative integer")
            raise ValueError("Factorial requires a non-negative integer")
        return math.factorial(a)
    
    def logarithm(self, a, base=10):
        self.logger.debug(f"Calculating logarithm of {a} with base {base}")
        if a <= 0:
            self.logger.error("Log input must be positve")
            raise ValueError("Log input must be positive")
        return math.log(a, base)
    
    def sine(self, angle_degrees):
        self.logger.debug(f"Calculating sine of {angle_degrees} degrees")
        return math.sin(math.radians(angle_degrees))

    def cosine(self, angle_degrees):
        self.logger.debug(f"Calculating cosine of {angle_degrees} degrees")
        return math.cos(math.radians(angle_degrees))

    def tangent(self, angle_degrees):
        self.logger.debug(f"Calculating tangent of {angle_degrees} degrees")
        return math.tan(math.radians(angle_degrees))


def main():
    calc = Calculator()

    print("Welcome to the Furical Calculator!")
    print("Available operations: add, subtract, multiply, divide, power, sqrt, factorial, log, sin, cos, tan, quit")

    while True:
        operation = input("\nEnter operation: ").lower().strip()

        if operation == 'quit':
            print("Goodbye!")
            break

        try:
            if operation == 'sqrt':
                num = float(input("Enter number: "))
                result = calc.square_root(num)
                print(f"\u221A{num} = {result:.2f}")
            
            elif operation == 'factorial':
                num = int(input("Enter a non-negative integer: "))
                result = calc.factorial(num)
                print(f"{num}! = {result}")
            
            elif operation == 'log':
                num = float(input("Enter number: "))
                base = float(input("Enter base (default 10): ") or 10)
                result = calc.logarithm(num, base)
                print(f"log base {base} of {num} = {result:.4f}")

            elif operation in ['sin', 'cos', 'tan']:
                angle = float(input("Enter angle in degrees: "))
                if operation == 'sin':
                    result = calc.sine(angle)
                    print(f"sin{angle} = {result:.4f}")

                elif operation == 'cos':
                    result = calc.cosine(angle)
                    print(f"cos{angle} = {result:.4f}")

                elif operation == 'tan':
                    result = calc.tangent(angle)
                    print(f"tan{angle} = {result:.4f}")

            elif operation in ['add', 'subtract', 'multiply', 'divide', 'power']:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))

                if operation == 'add':
                    result = calc.add(num1, num2)
                    print(f"{num1} + {num2} = {result}")

                elif operation == 'subtract':
                    result = calc.subtract(num1, num2)
                    print(f"{num1} - {num2} = {result}")

                elif operation == 'multiply':
                    result = calc.multiply(num1, num2)
                    print(f"{num1} * {num2} = {result}")

                elif operation == 'divide':
                    result = calc.divide(num1, num2)
                    print(f"{num1} / {num2} = {result:.2f}")

                elif operation == 'power':
                    result = calc.power(num1, num2)
                    print(f"{num1} ^ {num2} = {result}")

            else:
                print("Unknown operation. Try: add, subtract, multiply, divide, power, sqrt")

        except ValueError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()