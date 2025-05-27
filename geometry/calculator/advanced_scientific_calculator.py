"""
Advanced Scientific Calculator for IsopGem's Geometry module.

This module provides a comprehensive scientific calculator with a wide range
of mathematical functions for use in geometry and general calculations.
"""

import math
import random
import cmath
import statistics
from typing import List, Dict, Tuple, Optional, Any, Union, Callable
import numpy as np
from loguru import logger

class AdvancedScientificCalculator:
    """
    Advanced scientific calculator with comprehensive mathematical functions.
    
    Features:
    - Basic functions: arithmetic operations, memory operations, percentage calculations
    - Advanced functions: logarithmic, exponential, trigonometric, hyperbolic
    - Scientific features: scientific notation, complex numbers, vectors, matrices
    - Programming features: boolean logic, number base conversions
    - Physical constants and unit conversions
    """

    # Constants dictionary
    CONSTANTS = {
        # Mathematical constants
        "π": math.pi,
        "pi": math.pi,
        "e": math.e,
        "φ": (1 + math.sqrt(5)) / 2,  # Golden ratio (phi)
        "phi": (1 + math.sqrt(5)) / 2,
        "γ": 0.57721566490153286,  # Euler-Mascheroni constant
        "gamma": 0.57721566490153286,
        
        # Physical constants
        "c": 299792458,  # Speed of light (m/s)
        "G": 6.67430e-11,  # Gravitational constant (m³/kg·s²)
        "h": 6.62607015e-34,  # Planck constant (J·s)
        "ℏ": 1.054571817e-34,  # Reduced Planck constant (J·s)
        "ε0": 8.8541878128e-12,  # Vacuum electric permittivity (F/m)
        "μ0": 1.25663706212e-6,  # Vacuum magnetic permeability (H/m)
        "k": 1.380649e-23,  # Boltzmann constant (J/K)
        "NA": 6.02214076e23,  # Avogadro constant (mol⁻¹)
        "R": 8.31446261815324,  # Gas constant (J/mol·K)
        "me": 9.1093837015e-31,  # Electron mass (kg)
        "mp": 1.67262192369e-27,  # Proton mass (kg)
        "mn": 1.67492749804e-27,  # Neutron mass (kg)
        "α": 7.2973525693e-3,  # Fine structure constant
        "alpha": 7.2973525693e-3,
    }
    
    # Unit conversion factors (to SI)
    UNIT_CONVERSIONS = {
        # Length
        "m_to_cm": 100,
        "m_to_mm": 1000,
        "m_to_km": 0.001,
        "m_to_in": 39.3701,
        "m_to_ft": 3.28084,
        "m_to_yd": 1.09361,
        "m_to_mi": 0.000621371,
        
        # Area
        "m2_to_cm2": 10000,
        "m2_to_mm2": 1000000,
        "m2_to_km2": 0.000001,
        "m2_to_in2": 1550.0031,
        "m2_to_ft2": 10.7639,
        "m2_to_acre": 0.000247105,
        
        # Volume
        "m3_to_L": 1000,
        "m3_to_mL": 1000000,
        "m3_to_ft3": 35.3147,
        "m3_to_gal_us": 264.172,
        "m3_to_gal_uk": 219.969,
        
        # Mass
        "kg_to_g": 1000,
        "kg_to_mg": 1000000,
        "kg_to_lb": 2.20462,
        "kg_to_oz": 35.274,
        
        # Time
        "s_to_ms": 1000,
        "s_to_min": 1/60,
        "s_to_h": 1/3600,
        "s_to_d": 1/86400,
        
        # Temperature
        "K_to_C": -273.15,  # Function needed for accurate conversion
        "K_to_F": -459.67,  # Function needed for accurate conversion
        
        # Angle
        "rad_to_deg": 180 / math.pi,
        "rad_to_grad": 200 / math.pi,
        "deg_to_rad": math.pi / 180,
        "deg_to_grad": 400/360,
        "grad_to_rad": math.pi / 200,
        "grad_to_deg": 360/400,
    }

    def __init__(self):
        """Initialize the calculator with default settings."""
        # Calculator state
        self.memory = 0.0
        self.memory_stack = []
        self.history = []
        self.precision = 10
        self.angle_mode = "deg"  # 'deg', 'rad', or 'grad'
        self.complex_mode = False
        self.base = 10  # Numeric base for calculation (10 for decimal)
        self.error = None
        
        # For storing custom functions
        self.custom_functions = {}
        
        # For vector and matrix operations
        self.vectors = {}
        self.matrices = {}
        
        logger.debug("Advanced Scientific Calculator initialized")
    
    # Basic arithmetic operations
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            self.error = "Division by zero"
            logger.error(self.error)
            return float('nan')
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to the power of exponent."""
        try:
            if base == 0 and exponent < 0:
                self.error = "Cannot raise zero to a negative power"
                logger.error(self.error)
                return float('nan')
            return math.pow(base, exponent)
        except (ValueError, OverflowError) as e:
            self.error = str(e)
            logger.error(f"Power error: {self.error}")
            return float('nan')
    
    def modulo(self, a: float, b: float) -> float:
        """Calculate remainder when a is divided by b."""
        if b == 0:
            self.error = "Modulo by zero"
            logger.error(self.error)
            return float('nan')
        return a % b
    
    def integer_divide(self, a: float, b: float) -> int:
        """Perform integer division of a by b."""
        if b == 0:
            self.error = "Integer division by zero"
            logger.error(self.error)
            return 0
        return a // b
    
    # Memory operations
    def memory_clear(self) -> None:
        """Clear the memory."""
        self.memory = 0.0
        logger.debug("Memory cleared")
    
    def memory_recall(self) -> float:
        """Recall the value stored in memory."""
        return self.memory
    
    def memory_add(self, value: float) -> None:
        """Add value to memory."""
        self.memory += value
        logger.debug(f"Added {value} to memory. Memory now: {self.memory}")
    
    def memory_subtract(self, value: float) -> None:
        """Subtract value from memory."""
        self.memory -= value
        logger.debug(f"Subtracted {value} from memory. Memory now: {self.memory}")
    
    def memory_store(self, value: float) -> None:
        """Store value in memory."""
        self.memory = value
        logger.debug(f"Stored {value} in memory")
    
    def memory_push(self, value: float) -> None:
        """Push value onto memory stack."""
        self.memory_stack.append(value)
        logger.debug(f"Pushed {value} onto memory stack")
    
    def memory_pop(self) -> float:
        """Pop value from memory stack."""
        if not self.memory_stack:
            self.error = "Memory stack is empty"
            logger.warning(self.error)
            return 0.0
        value = self.memory_stack.pop()
        logger.debug(f"Popped {value} from memory stack")
        return value
    
    # Advanced mathematical functions
    def square(self, x: float) -> float:
        """Calculate the square of x."""
        return x * x
    
    def cube(self, x: float) -> float:
        """Calculate the cube of x."""
        return x * x * x
    
    def square_root(self, x: float) -> float:
        """Calculate the square root of x."""
        if x < 0 and not self.complex_mode:
            self.error = "Cannot calculate square root of negative number in real mode"
            logger.error(self.error)
            return float('nan')
        elif x < 0 and self.complex_mode:
            return complex(0, math.sqrt(abs(x)))
        return math.sqrt(x)
    
    def cube_root(self, x: float) -> float:
        """Calculate the cube root of x."""
        if x < 0:
            return -math.pow(abs(x), 1/3)
        return math.pow(x, 1/3)
    
    def cbrt(self, x: float) -> float:
        """Alias for cube_root function - calculate the cube root of x."""
        return self.cube_root(x)
    
    def nth_root(self, x: float, n: float) -> float:
        """Calculate the nth root of x."""
        if x < 0 and n % 2 == 0 and not self.complex_mode:
            self.error = "Cannot calculate even root of negative number in real mode"
            logger.error(self.error)
            return float('nan')
        elif x < 0 and n % 2 == 0 and self.complex_mode:
            return complex(0, math.pow(abs(x), 1/n))
        elif x < 0 and n % 2 == 1:
            return -math.pow(abs(x), 1/n)
        return math.pow(x, 1/n)
    
    def reciprocal(self, x: float) -> float:
        """Calculate 1/x."""
        if x == 0:
            self.error = "Cannot calculate reciprocal of zero"
            logger.error(self.error)
            return float('nan')
        return 1 / x
    
    def factorial(self, x: float) -> float:
        """Calculate factorial of x."""
        if x < 0 or x != int(x):
            self.error = "Factorial requires a non-negative integer"
            logger.error(self.error)
            return float('nan')
        return math.factorial(int(x))
    
    def percentage(self, x: float, percentage: float) -> float:
        """Calculate percentage of x."""
        return (percentage / 100) * x
    
    def percentage_change(self, old: float, new: float) -> float:
        """Calculate percentage change from old to new."""
        if old == 0:
            self.error = "Cannot calculate percentage change from zero"
            logger.error(self.error)
            return float('nan')
        return ((new - old) / abs(old)) * 100
    
    def absolute(self, x: float) -> float:
        """Calculate absolute value of x."""
        return abs(x)
    
    def sign(self, x: float) -> float:
        """Return the sign of x (-1, 0, or 1)."""
        if x < 0:
            return -1
        elif x > 0:
            return 1
        return 0
    
    # Logarithmic and exponential functions
    def natural_log(self, x: float) -> float:
        """Calculate natural logarithm of x."""
        if x <= 0:
            self.error = "Cannot calculate logarithm of non-positive number"
            logger.error(self.error)
            return float('nan')
        return math.log(x)
    
    def ln(self, x: float) -> float:
        """Alias for natural_log function - calculate natural logarithm of x."""
        return self.natural_log(x)
    
    def log10(self, x: float) -> float:
        """Calculate base-10 logarithm of x."""
        if x <= 0:
            self.error = "Cannot calculate logarithm of non-positive number"
            logger.error(self.error)
            return float('nan')
        return math.log10(x)
    
    def log_base(self, x: float, base: float) -> float:
        """Calculate logarithm of x with specified base."""
        if x <= 0 or base <= 0 or base == 1:
            self.error = "Invalid logarithm parameters"
            logger.error(self.error)
            return float('nan')
        return math.log(x, base)
    
    def exp(self, x: float) -> float:
        """Calculate e raised to the power of x."""
        try:
            return math.exp(x)
        except OverflowError:
            self.error = "Exponential overflow"
            logger.error(self.error)
            return float('inf')
    
    # Trigonometric functions with angle mode support
    def _convert_to_radians(self, angle: float) -> float:
        """Convert angle to radians based on current angle mode."""
        if self.angle_mode == "deg":
            return math.radians(angle)
        elif self.angle_mode == "grad":
            return angle * (math.pi / 200)
        return angle  # Already in radians
    
    def _convert_from_radians(self, angle: float) -> float:
        """Convert angle from radians based on current angle mode."""
        if self.angle_mode == "deg":
            return math.degrees(angle)
        elif self.angle_mode == "grad":
            return angle * (200 / math.pi)
        return angle  # Keep in radians
    
    def sin(self, angle: float) -> float:
        """Calculate sine of angle."""
        return math.sin(self._convert_to_radians(angle))
    
    def cos(self, angle: float) -> float:
        """Calculate cosine of angle."""
        return math.cos(self._convert_to_radians(angle))
    
    def tan(self, angle: float) -> float:
        """Calculate tangent of angle."""
        rad_angle = self._convert_to_radians(angle)
        # Check for angles where tangent is undefined
        if abs(math.cos(rad_angle)) < 1e-15:
            self.error = "Tangent undefined at this angle"
            logger.error(self.error)
            return float('nan')
        return math.tan(rad_angle)
    
    def sec(self, angle: float) -> float:
        """Calculate secant of angle (1/cos(angle))."""
        rad_angle = self._convert_to_radians(angle)
        cos_value = math.cos(rad_angle)
        if abs(cos_value) < 1e-15:
            self.error = "Secant undefined at this angle"
            logger.error(self.error)
            return float('nan')
        return 1.0 / cos_value
    
    def csc(self, angle: float) -> float:
        """Calculate cosecant of angle (1/sin(angle))."""
        rad_angle = self._convert_to_radians(angle)
        sin_value = math.sin(rad_angle)
        if abs(sin_value) < 1e-15:
            self.error = "Cosecant undefined at this angle"
            logger.error(self.error)
            return float('nan')
        return 1.0 / sin_value
    
    def asin(self, x: float) -> float:
        """Calculate arcsine of x."""
        if abs(x) > 1:
            self.error = "Arcsine input must be between -1 and 1"
            logger.error(self.error)
            return float('nan')
        return self._convert_from_radians(math.asin(x))
    
    def acos(self, x: float) -> float:
        """Calculate arccosine of x."""
        if abs(x) > 1:
            self.error = "Arccosine input must be between -1 and 1"
            logger.error(self.error)
            return float('nan')
        return self._convert_from_radians(math.acos(x))
    
    def atan(self, x: float) -> float:
        """Calculate arctangent of x."""
        return self._convert_from_radians(math.atan(x))
    
    def atan2(self, y: float, x: float) -> float:
        """Calculate arctangent of y/x, with quadrant consideration."""
        return self._convert_from_radians(math.atan2(y, x))
    
    # Hyperbolic functions
    def sinh(self, x: float) -> float:
        """Calculate hyperbolic sine of x."""
        return math.sinh(x)
    
    def cosh(self, x: float) -> float:
        """Calculate hyperbolic cosine of x."""
        return math.cosh(x)
    
    def tanh(self, x: float) -> float:
        """Calculate hyperbolic tangent of x."""
        return math.tanh(x)
    
    def asinh(self, x: float) -> float:
        """Calculate inverse hyperbolic sine of x."""
        return math.asinh(x)
    
    def acosh(self, x: float) -> float:
        """Calculate inverse hyperbolic cosine of x."""
        if x < 1:
            self.error = "Inverse hyperbolic cosine input must be >= 1"
            logger.error(self.error)
            return float('nan')
        return math.acosh(x)
    
    def atanh(self, x: float) -> float:
        """Calculate inverse hyperbolic tangent of x."""
        if abs(x) >= 1:
            self.error = "Inverse hyperbolic tangent input must be between -1 and 1"
            logger.error(self.error)
            return float('nan')
        return math.atanh(x)
    
    # Statistics functions
    def mean(self, values: List[float]) -> float:
        """Calculate arithmetic mean of values."""
        if not values:
            self.error = "Cannot calculate mean of empty list"
            logger.error(self.error)
            return float('nan')
        return statistics.mean(values)
    
    def geometric_mean(self, values: List[float]) -> float:
        """Calculate geometric mean of values."""
        if not values:
            self.error = "Cannot calculate geometric mean of empty list"
            logger.error(self.error)
            return float('nan')
        for value in values:
            if value <= 0:
                self.error = "Geometric mean requires positive values"
                logger.error(self.error)
                return float('nan')
        return statistics.geometric_mean(values)
    
    def harmonic_mean(self, values: List[float]) -> float:
        """Calculate harmonic mean of values."""
        if not values:
            self.error = "Cannot calculate harmonic mean of empty list"
            logger.error(self.error)
            return float('nan')
        for value in values:
            if value <= 0:
                self.error = "Harmonic mean requires positive values"
                logger.error(self.error)
                return float('nan')
        return statistics.harmonic_mean(values)
    
    def median(self, values: List[float]) -> float:
        """Calculate median of values."""
        if not values:
            self.error = "Cannot calculate median of empty list"
            logger.error(self.error)
            return float('nan')
        return statistics.median(values)
    
    def mode(self, values: List[float]) -> Union[float, List[float]]:
        """Calculate mode of values."""
        if not values:
            self.error = "Cannot calculate mode of empty list"
            logger.error(self.error)
            return float('nan')
        try:
            return statistics.mode(values)
        except statistics.StatisticsError:
            # Multiple modes or no mode
            return self.multimode(values)
    
    def multimode(self, values: List[float]) -> List[float]:
        """Calculate all modes (most common values) in the data."""
        if not values:
            self.error = "Cannot calculate multimode of empty list"
            logger.error(self.error)
            return []
        return statistics.multimode(values)
    
    def variance(self, values: List[float], sample: bool = True) -> float:
        """Calculate variance of values (sample or population)."""
        if not values or len(values) < 2:
            self.error = "Cannot calculate variance with fewer than 2 values"
            logger.error(self.error)
            return float('nan')
        if sample:
            return statistics.variance(values)
        else:
            return statistics.pvariance(values)
    
    def std_dev(self, values: List[float], sample: bool = True) -> float:
        """Calculate standard deviation of values (sample or population)."""
        if not values or len(values) < 2:
            self.error = "Cannot calculate standard deviation with fewer than 2 values"
            logger.error(self.error)
            return float('nan')
        if sample:
            return statistics.stdev(values)
        else:
            return statistics.pstdev(values)
    
    # Combinatorial functions
    def permutations(self, n: int, r: int) -> int:
        """Calculate number of permutations of r items from n items."""
        if n < 0 or r < 0 or r > n:
            self.error = "Invalid parameters for permutation"
            logger.error(self.error)
            return 0
        return math.perm(n, r)
    
    def combinations(self, n: int, r: int) -> int:
        """Calculate number of combinations of r items from n items."""
        if n < 0 or r < 0 or r > n:
            self.error = "Invalid parameters for combination"
            logger.error(self.error)
            return 0
        return math.comb(n, r)
    
    # Number base conversions
    def decimal_to_binary(self, num: int) -> str:
        """Convert decimal integer to binary string."""
        if num < 0:
            return "-" + bin(abs(num))[2:]
        return bin(num)[2:]
    
    def decimal_to_octal(self, num: int) -> str:
        """Convert decimal integer to octal string."""
        if num < 0:
            return "-" + oct(abs(num))[2:]
        return oct(num)[2:]
    
    def decimal_to_hex(self, num: int) -> str:
        """Convert decimal integer to hexadecimal string."""
        if num < 0:
            return "-" + hex(abs(num))[2:].upper()
        return hex(num)[2:].upper()
    
    def binary_to_decimal(self, binary_str: str) -> int:
        """Convert binary string to decimal integer."""
        try:
            if binary_str.startswith("-"):
                return -int(binary_str[1:], 2)
            return int(binary_str, 2)
        except ValueError:
            self.error = "Invalid binary string"
            logger.error(self.error)
            return 0
    
    def octal_to_decimal(self, octal_str: str) -> int:
        """Convert octal string to decimal integer."""
        try:
            if octal_str.startswith("-"):
                return -int(octal_str[1:], 8)
            return int(octal_str, 8)
        except ValueError:
            self.error = "Invalid octal string"
            logger.error(self.error)
            return 0
    
    def hex_to_decimal(self, hex_str: str) -> int:
        """Convert hexadecimal string to decimal integer."""
        try:
            if hex_str.startswith("-"):
                return -int(hex_str[1:], 16)
            return int(hex_str, 16)
        except ValueError:
            self.error = "Invalid hexadecimal string"
            logger.error(self.error)
            return 0
    
    def convert_base(self, num_str: str, from_base: int, to_base: int) -> str:
        """Convert number between arbitrary bases (2-36)."""
        try:
            if from_base < 2 or from_base > 36 or to_base < 2 or to_base > 36:
                self.error = "Base must be between 2 and 36"
                logger.error(self.error)
                return ""
            
            # Handle negative numbers
            negative = num_str.startswith("-")
            if negative:
                num_str = num_str[1:]
                
            # Convert to decimal first
            decimal = int(num_str, from_base)
            
            # Then convert from decimal to target base
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            result = ""
            
            while decimal > 0:
                result = digits[decimal % to_base] + result
                decimal //= to_base
                
            if not result:
                result = "0"
                
            return "-" + result if negative else result
        except ValueError:
            self.error = f"Invalid digit for base {from_base}"
            logger.error(self.error)
            return ""
    
    # Boolean logic operations
    def boolean_and(self, a: int, b: int) -> int:
        """Perform bitwise AND operation."""
        return a & b
    
    def boolean_or(self, a: int, b: int) -> int:
        """Perform bitwise OR operation."""
        return a | b
    
    def boolean_xor(self, a: int, b: int) -> int:
        """Perform bitwise XOR operation."""
        return a ^ b
    
    def boolean_not(self, a: int) -> int:
        """Perform bitwise NOT operation (1's complement)."""
        return ~a
    
    def shift_left(self, a: int, bits: int) -> int:
        """Perform left bit shift operation."""
        return a << bits
    
    def shift_right(self, a: int, bits: int) -> int:
        """Perform right bit shift operation."""
        return a >> bits
    
    # Random number generation
    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate random integer between min_val and max_val."""
        return random.randint(min_val, max_val)
    
    def random_float(self) -> float:
        """Generate random float between 0 and 1."""
        return random.random()
    
    def random_range(self, min_val: float, max_val: float) -> float:
        """Generate random float between min_val and max_val."""
        return min_val + (max_val - min_val) * random.random()
    
    def random_normal(self, mean: float = 0.0, std_dev: float = 1.0) -> float:
        """Generate random float from normal distribution."""
        return random.normalvariate(mean, std_dev)
    
    # Complex number operations
    def complex_number(self, real: float, imag: float) -> complex:
        """Create a complex number with real and imaginary parts."""
        return complex(real, imag)
    
    def complex_abs(self, z: complex) -> float:
        """Calculate the absolute value (modulus) of a complex number."""
        return abs(z)
    
    def complex_arg(self, z: complex) -> float:
        """Calculate the argument (phase) of a complex number."""
        return self._convert_from_radians(cmath.phase(z))
    
    def complex_conjugate(self, z: complex) -> complex:
        """Calculate the complex conjugate of a complex number."""
        return z.conjugate()
    
    def complex_exp(self, z: complex) -> complex:
        """Calculate e raised to the power of a complex number."""
        return cmath.exp(z)
    
    def complex_ln(self, z: complex) -> complex:
        """Calculate natural logarithm of a complex number."""
        return cmath.log(z)
    
    def complex_sqrt(self, z: complex) -> complex:
        """Calculate square root of a complex number."""
        return cmath.sqrt(z)
    
    def complex_pow(self, z: complex, w: complex) -> complex:
        """Calculate z raised to the power of w."""
        return z ** w
    
    # Vector operations
    def vector_create(self, components: List[float], name: str = None) -> List[float]:
        """Create a vector from components and optionally store it."""
        vector = list(components)
        if name:
            self.vectors[name] = vector
        return vector
    
    def vector_dot(self, v1: List[float], v2: List[float]) -> float:
        """Calculate dot product of two vectors."""
        if len(v1) != len(v2):
            self.error = "Vectors must have the same dimension for dot product"
            logger.error(self.error)
            return float('nan')
        return sum(x * y for x, y in zip(v1, v2))
    
    def vector_cross(self, v1: List[float], v2: List[float]) -> List[float]:
        """Calculate cross product of two 3D vectors."""
        if len(v1) != 3 or len(v2) != 3:
            self.error = "Cross product requires two 3D vectors"
            logger.error(self.error)
            return [float('nan'), float('nan'), float('nan')]
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]
    
    def vector_magnitude(self, v: List[float]) -> float:
        """Calculate magnitude (length) of a vector."""
        return math.sqrt(sum(x * x for x in v))
    
    def vector_normalize(self, v: List[float]) -> List[float]:
        """Normalize a vector to unit length."""
        magnitude = self.vector_magnitude(v)
        if magnitude == 0:
            self.error = "Cannot normalize zero vector"
            logger.error(self.error)
            return [float('nan')] * len(v)
        return [x / magnitude for x in v]
    
    def vector_angle(self, v1: List[float], v2: List[float]) -> float:
        """Calculate angle between two vectors."""
        dot = self.vector_dot(v1, v2)
        mag1 = self.vector_magnitude(v1)
        mag2 = self.vector_magnitude(v2)
        
        if mag1 == 0 or mag2 == 0:
            self.error = "Cannot calculate angle with zero vector"
            logger.error(self.error)
            return float('nan')
        
        # Ensure the value is in [-1, 1] to avoid numerical errors
        cosine = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return self._convert_from_radians(math.acos(cosine))
    
    # Matrix operations
    def matrix_create(self, rows: List[List[float]], name: str = None) -> List[List[float]]:
        """Create a matrix from rows and optionally store it."""
        matrix = [list(row) for row in rows]  # Create a deep copy
        
        # Validate all rows have same length
        if not all(len(row) == len(matrix[0]) for row in matrix):
            self.error = "All matrix rows must have the same length"
            logger.error(self.error)
            return []
            
        if name:
            self.matrices[name] = matrix
        return matrix
    
    def matrix_add(self, m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
        """Add two matrices."""
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            self.error = "Matrices must have the same dimensions for addition"
            logger.error(self.error)
            return []
        
        result = []
        for i in range(len(m1)):
            row = []
            for j in range(len(m1[0])):
                row.append(m1[i][j] + m2[i][j])
            result.append(row)
        return result
    
    def matrix_subtract(self, m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
        """Subtract matrix m2 from m1."""
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            self.error = "Matrices must have the same dimensions for subtraction"
            logger.error(self.error)
            return []
        
        result = []
        for i in range(len(m1)):
            row = []
            for j in range(len(m1[0])):
                row.append(m1[i][j] - m2[i][j])
            result.append(row)
        return result
    
    def matrix_multiply(self, m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
        """Multiply two matrices."""
        if len(m1[0]) != len(m2):
            self.error = "Matrix dimensions incompatible for multiplication"
            logger.error(self.error)
            return []
        
        result = []
        for i in range(len(m1)):
            row = []
            for j in range(len(m2[0])):
                element = 0
                for k in range(len(m2)):
                    element += m1[i][k] * m2[k][j]
                row.append(element)
            result.append(row)
        return result
    
    def matrix_determinant(self, matrix: List[List[float]]) -> float:
        """Calculate determinant of a square matrix."""
        # Convert to numpy array for determinant calculation
        try:
            np_matrix = np.array(matrix, dtype=float)
            return float(np.linalg.det(np_matrix))
        except (ValueError, np.linalg.LinAlgError) as e:
            self.error = f"Error calculating determinant: {str(e)}"
            logger.error(self.error)
            return float('nan')
    
    def matrix_inverse(self, matrix: List[List[float]]) -> List[List[float]]:
        """Calculate inverse of a square matrix."""
        try:
            np_matrix = np.array(matrix, dtype=float)
            inverse = np.linalg.inv(np_matrix)
            # Convert back to list of lists
            return [list(row) for row in inverse]
        except (ValueError, np.linalg.LinAlgError) as e:
            self.error = f"Error calculating matrix inverse: {str(e)}"
            logger.error(self.error)
            return []
    
    def matrix_transpose(self, matrix: List[List[float]]) -> List[List[float]]:
        """Calculate transpose of a matrix."""
        if not matrix:
            return []
        # Create a new matrix with rows and columns swapped
        return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
    
    # Equation solving functions
    def solve_quadratic(self, a: float, b: float, c: float) -> Tuple[float, float]:
        """Solve quadratic equation of form ax² + bx + c = 0."""
        if a == 0:
            self.error = "Not a quadratic equation (a=0)"
            logger.error(self.error)
            return (float('nan'), float('nan'))
        
        discriminant = b*b - 4*a*c
        
        if discriminant < 0 and not self.complex_mode:
            self.error = "Quadratic equation has no real solutions"
            logger.error(self.error)
            return (float('nan'), float('nan'))
        elif discriminant < 0 and self.complex_mode:
            # Complex solutions
            real_part = -b / (2*a)
            imag_part = math.sqrt(abs(discriminant)) / (2*a)
            return (complex(real_part, imag_part), complex(real_part, -imag_part))
        else:
            # Real solutions
            sqrt_discriminant = math.sqrt(discriminant)
            return ((-b + sqrt_discriminant) / (2*a), (-b - sqrt_discriminant) / (2*a))
    
    def solve_cubic(self, a: float, b: float, c: float, d: float) -> Tuple[float, float, float]:
        """Solve cubic equation of form ax³ + bx² + cx + d = 0."""
        if a == 0:
            self.error = "Not a cubic equation (a=0)"
            logger.error(self.error)
            return (float('nan'), float('nan'), float('nan'))
        
        # Convert to depressed cubic t³ + pt + q = 0
        p = (3*a*c - b*b) / (3*a*a)
        q = (2*b*b*b - 9*a*b*c + 27*a*a*d) / (27*a*a*a)
        
        # Calculate discriminant
        discriminant = (q*q/4) + (p*p*p/27)
        
        # Handle different cases based on discriminant
        if discriminant > 0:
            # One real root, two complex conjugate roots
            u = self.cube_root(-q/2 + math.sqrt(discriminant))
            v = self.cube_root(-q/2 - math.sqrt(discriminant))
            
            real_root = u + v - b/(3*a)
            real_part = -(u + v)/2 - b/(3*a)
            imag_part = math.sqrt(3)*(u - v)/2
            
            if self.complex_mode:
                return (real_root, complex(real_part, imag_part), complex(real_part, -imag_part))
            else:
                return (real_root, float('nan'), float('nan'))
                
        elif discriminant == 0:
            # Three real roots, at least two are equal
            if p == 0:
                # Triple root
                root = -b/(3*a)
                return (root, root, root)
            else:
                # Double root and a single root
                double_root = 3*q/p - b/(3*a)
                single_root = -3*q/(2*p) - b/(3*a)
                return (single_root, double_root, double_root)
                
        else:
            # Three distinct real roots
            theta = math.acos(-q/2 * math.sqrt(-27/(p*p*p)))
            r = 2 * math.sqrt(-p/3)
            
            root1 = r * math.cos(theta/3) - b/(3*a)
            root2 = r * math.cos((theta + 2*math.pi)/3) - b/(3*a)
            root3 = r * math.cos((theta + 4*math.pi)/3) - b/(3*a)
            
            return (root1, root2, root3)
    
    def solve_system_linear(self, A: List[List[float]], b: List[float]) -> List[float]:
        """Solve system of linear equations Ax = b."""
        try:
            A_np = np.array(A, dtype=float)
            b_np = np.array(b, dtype=float)
            solution = np.linalg.solve(A_np, b_np)
            return solution.tolist()
        except np.linalg.LinAlgError as e:
            self.error = f"Error solving linear system: {str(e)}"
            logger.error(self.error)
            return [float('nan')] * len(b)
    
    # Numerical integration and differentiation
    def numerical_derivative(self, func: Callable[[float], float], x: float, h: float = 1e-5) -> float:
        """Calculate numerical derivative of a function at point x."""
        return (func(x + h) - func(x - h)) / (2 * h)
    
    def numerical_integral(
        self, func: Callable[[float], float], a: float, b: float, n: int = 1000
    ) -> float:
        """Calculate numerical integral of a function from a to b using Simpson's rule."""
        if n % 2 != 0:
            n += 1  # Make sure n is even
            
        h = (b - a) / n
        result = func(a) + func(b)
        
        # Sum the odd terms
        for i in range(1, n, 2):
            result += 4 * func(a + i * h)
            
        # Sum the even terms
        for i in range(2, n, 2):
            result += 2 * func(a + i * h)
            
        return result * h / 3
    
    # Unit conversion functions
    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert value between units."""
        conversion_key = f"{from_unit}_to_{to_unit}"
        
        # Handle temperature conversions specially
        if from_unit == "K" and to_unit == "C":
            return value + self.UNIT_CONVERSIONS["K_to_C"]
        elif from_unit == "K" and to_unit == "F":
            return value * 9/5 + self.UNIT_CONVERSIONS["K_to_F"]
        elif from_unit == "C" and to_unit == "K":
            return value - self.UNIT_CONVERSIONS["K_to_C"]
        elif from_unit == "C" and to_unit == "F":
            return value * 9/5 + 32
        elif from_unit == "F" and to_unit == "K":
            return (value - self.UNIT_CONVERSIONS["K_to_F"]) * 5/9
        elif from_unit == "F" and to_unit == "C":
            return (value - 32) * 5/9
            
        # Handle other conversions using conversion factors
        if conversion_key in self.UNIT_CONVERSIONS:
            return value * self.UNIT_CONVERSIONS[conversion_key]
        
        # If there's no direct conversion, try a two-step conversion via SI units
        from_to_si = f"{from_unit}_to_SI"
        si_to_to = f"SI_to_{to_unit}"
        
        if from_to_si in self.UNIT_CONVERSIONS and si_to_to in self.UNIT_CONVERSIONS:
            si_value = value * self.UNIT_CONVERSIONS[from_to_si]
            return si_value * self.UNIT_CONVERSIONS[si_to_to]
        
        self.error = f"Unknown unit conversion: {from_unit} to {to_unit}"
        logger.error(self.error)
        return float('nan')
    
    # Settings and state management
    def set_angle_mode(self, mode: str) -> None:
        """Set angle mode to 'deg', 'rad', or 'grad'."""
        if mode.lower() in ['deg', 'rad', 'grad']:
            self.angle_mode = mode.lower()
            logger.debug(f"Angle mode set to {self.angle_mode}")
        else:
            self.error = "Invalid angle mode. Use 'deg', 'rad', or 'grad'"
            logger.error(self.error)
    
    def set_precision(self, precision: int) -> None:
        """Set display precision for floating point numbers."""
        if 0 <= precision <= 15:
            self.precision = precision
            logger.debug(f"Precision set to {self.precision}")
        else:
            self.error = "Precision must be between 0 and 15"
            logger.error(self.error)
    
    def toggle_complex_mode(self) -> None:
        """Toggle complex number mode."""
        self.complex_mode = not self.complex_mode
        logger.debug(f"Complex mode {'enabled' if self.complex_mode else 'disabled'}")
    
    def set_base(self, base: int) -> None:
        """Set numeric base for calculations."""
        if 2 <= base <= 36:
            self.base = base
            logger.debug(f"Numeric base set to {self.base}")
        else:
            self.error = "Base must be between 2 and 36"
            logger.error(self.error)
    
    def clear_error(self) -> None:
        """Clear the error state."""
        self.error = None
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history = []
        logger.debug("Calculation history cleared")
    
    def get_error(self) -> Optional[str]:
        """Get the current error message, if any."""
        return self.error
    
    def add_to_history(self, expression: str, result: Any) -> None:
        """Add calculation to history."""
        self.history.append((expression, result))
    
    def get_history(self) -> List[Tuple[str, Any]]:
        """Get calculation history."""
        return self.history.copy()
    
    def format_number(self, number: float) -> str:
        """Format number according to current precision and base."""
        if isinstance(number, complex):
            real_part = self.format_number(number.real)
            imag_part = self.format_number(number.imag)
            if number.imag >= 0:
                return f"{real_part}+{imag_part}i"
            else:
                return f"{real_part}{imag_part}i"
        
        if self.base == 10:
            return f"{number:.{self.precision}g}"
        elif self.base == 2:
            return self.decimal_to_binary(int(number))
        elif self.base == 8:
            return self.decimal_to_octal(int(number))
        elif self.base == 16:
            return self.decimal_to_hex(int(number))
        else:
            return self.convert_base(str(int(number)), 10, self.base)
