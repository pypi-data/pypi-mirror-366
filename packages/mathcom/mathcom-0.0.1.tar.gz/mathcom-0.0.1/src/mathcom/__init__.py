# Version 1.5 (Beta)


""" Mathcom is the most understand modules of math. It contains all code for Scratch 3.0 (https://scratch.mit.edu) - Operaters Selection """


from math import *
from random import *
from fractions import *
# Custom Error
class ErrorAlert(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Syntax Bool
def even(a: int) -> int:
    if type(a) != int:
        raise ErrorAlert("Error syntax: 'int' only")
        pass
    elif a%2 == 0:
        return True
    else:
        return False
    
def odd(b):
    if type(b) != int:
        raise ErrorAlert("Error syntax: 'int' only")
        pass
    elif b%2 == 1:
        return True
    else:
        return False

def nev(c):
    if not isinstance(c, (int, float)):
        raise ErrorAlert("Error syntax: 'int' or 'float' only")
    elif c < 0:
        return True
    else:
        return False
# Syntax problem
def join(a: str, b: str) -> str:
    a, b = str(a), str(b)
    return a + b

class Area:
    def __init__(self):
        pass

    @staticmethod
    def rect(a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ErrorAlert("Error syntax: Numbers only")
        return a * b

    @staticmethod
    def sqr(a: float) -> float:
        if not isinstance(a, (int, float)):
            raise ErrorAlert("Error syntax: Numbers only")
        return a ** 2

    @staticmethod
    def cir(d: float) -> float:
        if not isinstance(d, (int, float)):
            raise ErrorAlert("Error syntax: Value 'd' must be a number")
        else:
            return d*d*3.14
        
    @staticmethod
    def tria(a: float, h: float) -> float:
        if isinstance(a and h, (int, float)):
            return a*h/2
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
    @staticmethod
    def diam(m: float, n: float) -> float:
        if isinstance(m and n, (int, float)):
            return m*n/2
        else:
            raise ErrorAlert("Error syntax: Numbers only")
    
    @staticmethod
    def trape(a: float, b: float, h:float) -> float:
        if isinstance(a and b and h, (int, float)):
            return (a+b)*h/2
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
    @staticmethod
    def paralle(a: float, h: float):
        if isinstance(a and h, (int, float)):
            return a*h
        else:
            raise ErrorAlert("Error syntax: Numbers only")

class Round:
    @staticmethod
    def roundDown(a: float)-> float:
        if isinstance(a, (int, float)):
            return floor(a)
        else:
            raise ErrorAlert("Error syntax: Numbers only")
    @staticmethod
    def roundUp(a: float) -> float:
        if isinstance(a, (int, float)):
            return ceil(a)
        else:
            raise ErrorAlert("Error syntax: Numbers only")
    @staticmethod
    def roundNormal(a: float) -> float:
        if isinstance(a, (int, float)):
            return round(a)
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
def digitDemical(a: float, digit: int):
    if not isinstance(a, (int, float)):
        raise ErrorAlert("Error syntax: Value 'a' must be numbers")
    else:
        if not isinstance(digit, int):
            raise ErrorAlert("Error syntax: Numbers only")
        else:
            return round(a, digit)
        
class Peri:
    def __init__(self):
        pass

    @staticmethod
    def rect(a: float, b: float) -> float:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ErrorAlert("Error syntax: Numbers only")
        return 2*(a+b)

    @staticmethod
    def sqr(a: float) -> float:
        if not isinstance(a, (int, float)):
            raise ErrorAlert("Error syntax: Numbers only")
        return 4*a

    @staticmethod
    def cir(type_: int, d: float) -> float:
        if not isinstance(d, (int, float)):
            raise ErrorAlert("Error syntax: Value 'd' must be a number")
        if type_ == 1:
            return d * 2 * 3.14
        elif type_ == 2:
            return d * 3.14
        else:
            raise ErrorAlert("Syntax Error: Value 'type' must be 1 or 2")
        
    @staticmethod
    def tria(a: float, b: float, c: float) -> float:
        if isinstance(a and b and c, (int, float)):
            return a+b+c
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
    @staticmethod
    def diam(a:float) -> float:
        if isinstance(a, (int, float)):
            return 4*a
        else:
            raise ErrorAlert("Error syntax: Numbers only")
    
    @staticmethod
    def trape(a: float, b: float, c:float, d:float) -> float:
        if isinstance(a and b and c and d, (int, float)):
            return a+b+c+d
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
    @staticmethod
    def paralle(a: float, b: float):
        if isinstance(a and b, (int, float)):
            return 2*(a+b)
        else:
            raise ErrorAlert("Error syntax: Numbers only")

def randomrage(start: float, end: float, range: float):
    if isinstance(start and end and range, (int, float)):
        return randrange(start, end, range)
    elif range <= 0:
        raise ErrorAlert("Error syntax: Value 'range' bigger than 0")
    else:
        raise ErrorAlert("Error syntax: Numbers only")


def fracWhole(up: int, down: int):
    if isinstance(up and down, int):
        return Fraction(up, down)
    else:
        raise ErrorAlert("Error syntax: Numbers 'int' only")
    

class Cube:
    def cube_around(P: float, h: float) -> float:
        if isinstance(P and h,(int, float)):
                return P * h
        else:
            raise ErrorAlert("Error syntax: Numbers only")
        
    def cube_3(S: float, h: float) -> float:
        if isinstance(S and h,(int, float)):
                return S * h
        else:
            raise ErrorAlert("Error syntax: Numbers only")

# Simple function
def power(a: float, n: int) -> float:
    if isinstance(a and n,(int, float)):
            return a**n
    else:
        raise ErrorAlert("Error syntax: Numbers only")

def sqrt(a: float, n: int) -> float:
    if isinstance(a and n,(int, float)):
            return round(a**(1/n), 5)
    else:
        raise ErrorAlert("Error syntax: Numbers only")
    
def mod(a: float, b = float) -> float:
    if isinstance(a and b,(int, float)):
            return a%b
    else:
        raise ErrorAlert("Error syntax: Numbers only")

def expert(func: str, a: float) -> float:
    if isinstance(a, float):
        if func == "sin":
            return sin(a)
        elif func == "cos":
            return cos(a)
        elif func == "tan":
            return tan(a)
        elif func == "sinh":
            return sinh(a)
        elif func == "cosh":
            return cosh(a)
        elif func == "tanh":
            return tanh(a)
        else:
            raise ErrorAlert(f"Error Syntax: Value 'type' has no function {func}")
    else:
        raise ErrorAlert("Error Syntax: Value 'a' must be a number")

def percent(a: float):
    if isinstance(a, float):
        return a/100
    else:
        raise ErrorAlert("Error syntax: Numbers only")