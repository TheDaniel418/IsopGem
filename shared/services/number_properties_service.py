"""
Purpose: Provides numerical analysis services for examining properties of integers

This file is part of the shared services and provides number analysis functionality.
It calculates and provides access to various number properties such as primality,
factors, divisors, binary/ternary representations, and mathematical relationships.

Key components:
- NumberPropertiesService: Service class for analyzing and caching number properties

Dependencies:
- math: Standard Python math library for mathematical operations
- sympy: For advanced mathematical operations and prime checking

Related files:
- tq/ui/widgets/tq_grid_panel.py: Uses this service for TQ quadset analysis
- geometry/ui/panels/number_geometry_panel.py: Will use this for geometric properties
"""

import math
import time
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Set, Tuple, Optional, Union, Any, cast
import logging

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

logger = logging.getLogger(__name__)

class NumberPropertiesService:
    """
    Service for analyzing and retrieving properties of numbers.
    
    This service provides methods to check various mathematical properties of numbers,
    such as primality, factors, and polygonal numbers.
    
    The service is designed as a singleton to ensure consistent behavior across the application.
    
    Key functionalities:
    - Get comprehensive properties of a number (primality, factors, etc.)
    - Check if a number is a polygonal number of various types (triangular, square, etc.)
    - Check if a number is a centered polygonal number
    - Find indices for polygonal numbers
    - Various utilities for prime-related calculations
    - Utilities for ternary number operations
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'NumberPropertiesService':
        """Get the singleton instance of the service.
        
        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = NumberPropertiesService()
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the service.
        
        Raises:
            RuntimeError: If an attempt is made to create a second instance
        """
        if NumberPropertiesService._instance is not None:
            raise RuntimeError("Use get_instance() to get the singleton instance")
        
        NumberPropertiesService._instance = self
        
        # Initialize caches - use list for ordered prime cache
        self._prime_list: List[int] = []  # Ordered list of known primes
        self._prime_cache: Dict[int, bool] = {}  # Cache of primality tests
        self._factors_cache: Dict[int, List[int]] = {}
        self._divisors_cache: Dict[int, List[int]] = {}
        self._prime_ordinal_cache: Dict[int, int] = {}
        
        # Initialize prime cache with first few primes
        for n in range(2, 100):
            if self.is_prime(n):
                self._prime_list.append(n)
        
        logger.debug("NumberPropertiesService initialized")
        
    def get_number_properties(self, number: int) -> Dict[str, Any]:
        """Get comprehensive properties of a number.
        
        Args:
            number: Integer to analyze
            
        Returns:
            Dictionary of number properties
        """
        if not isinstance(number, int):
            try:
                number = int(number)
            except (ValueError, TypeError):
                raise ValueError("Input must be convertible to an integer")
        
        properties = {
            "number": number,
            "is_prime": self.is_prime(number) if number > 0 else False,
        }
        
        # Add prime ordinal if prime
        if properties["is_prime"]:
            properties["prime_ordinal"] = self.get_prime_ordinal(number)
        
        # Add properties that only apply to non-zero numbers
        if number != 0:
            # Get factors and calculate sums
            factors = self.get_factors(number)
            properties["factors"] = factors
            properties["factor_sum"] = sum(factors)
            
            # Calculate aliquot sum (sum of proper divisors)
            proper_divisors = [d for d in factors if d != number]
            aliquot_sum = sum(proper_divisors)
            properties["aliquot_sum"] = aliquot_sum
            
            # Determine abundance/deficiency
            properties["is_perfect"] = aliquot_sum == number
            properties["is_abundant"] = aliquot_sum > number
            properties["is_deficient"] = aliquot_sum < number
        
        # Add polygonal number properties
        if number > 0:
            # Regular polygonal numbers with indices
            for k in range(3, 11):  # triangular through decagonal
                if self.is_polygonal(number, k):
                    properties[f"polygonal_{k}_index"] = self.get_polygonal_index(number, k)
            
            # Centered polygonal numbers with indices
            for k in range(3, 11):
                if self.is_centered_polygonal(number, k):
                    properties[f"centered_{k}_index"] = self.get_centered_polygonal_index(number, k)
        
        return properties
    
    def is_prime(self, n: int) -> bool:
        """Check if a number is prime.
        
        Args:
            n: Number to check
            
        Returns:
            True if the number is prime, False otherwise
        """
        if n < 2:
            return False
            
        # Check cache first
        if n in self._prime_cache:
            return self._prime_cache[n]
            
        # Use sympy for primality testing
        result = sympy.isprime(n)
        self._prime_cache[n] = result
        return result
    
    def get_factors(self, n: int) -> List[int]:
        """Get the factors of a number.
        
        Args:
            n: Number to factorize
            
        Returns:
            List of factors
        """
        if n < 1:
            return []
            
        # Check cache first
        if n in self._factors_cache:
            return self._factors_cache[n]
            
        # Calculate factors
        factors = []
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                factors.append(i)
                if i != n // i:
                    factors.append(n // i)
                    
        factors.sort()
        self._factors_cache[n] = factors
        return factors
    
    def get_prime_factors(self, n: int) -> List[Tuple[int, int]]:
        """Get the prime factorization of a number.
        
        Args:
            n: Number to factorize
            
        Returns:
            List of (prime factor, exponent) tuples
        """
        if n < 2:
            return []
            
        # Use sympy for prime factorization
        factors = sympy.factorint(n)
        return [(p, e) for p, e in factors.items()]
    
    @lru_cache(maxsize=1000)
    def is_perfect(self, n: int) -> bool:
        """
        Check if a number is perfect (sum of proper divisors equals the number).
        
        Args:
            n: The number to check
            
        Returns:
            True if the number is perfect, False otherwise
        """
        if n <= 1:
            return False
        
        factors = self.get_factors(n)
        # Remove the number itself from factors
        factors.remove(n)
        return sum(factors) == n
    
    @lru_cache(maxsize=1000)
    def is_fibonacci(self, n: int) -> bool:
        """
        Check if a number is a Fibonacci number.
        
        Args:
            n: The number to check
            
        Returns:
            True if the number is a Fibonacci number, False otherwise
        """
        if n < 0:
            return False
        
        # A number is a Fibonacci number if and only if 5n² + 4 or 5n² - 4 is a perfect square
        check1 = 5 * n * n + 4
        check2 = 5 * n * n - 4
        
        sqrt1 = int(math.sqrt(check1))
        sqrt2 = int(math.sqrt(check2))
        
        return sqrt1 * sqrt1 == check1 or sqrt2 * sqrt2 == check2
    
    def get_prime_ordinal(self, n: int) -> Optional[int]:
        """
        Get the ordinal position of a prime number.
        
        Args:
            n: The prime number to look up
            
        Returns:
            The ordinal position if the number is prime, None otherwise
        """
        if not self.is_prime(n):
            return None
        
        # Check cache first
        if n in self._prime_ordinal_cache:
            return self._prime_ordinal_cache[n]
        
        # For larger primes we need to compute
        # Calculate up to n + 1000 to ensure we find the ordinal
        threshold = n + 1000
        
        # Update primes cache if needed
        if not self._prime_list or self._prime_list[-1] < n:
            last_known = self._prime_list[-1] if self._prime_list else 1
            for candidate in range(last_known + 1, threshold + 1):
                if self.is_prime(candidate):
                    self._prime_list.append(candidate)
                    
        # Find ordinal in prime list
        try:
            ordinal = self._prime_list.index(n) + 1
            self._prime_ordinal_cache[n] = ordinal
            return ordinal
        except ValueError:
            # This shouldn't happen since we already checked is_prime
            logger.error(f"Prime {n} not found in prime list despite being prime")
            return None
    
    @lru_cache(maxsize=1000)
    def is_polygonal(self, n: int, k: int) -> bool:
        """
        Check if a number is a k-gonal number.
        
        Args:
            n: The number to check
            k: The number of sides (k >= 3)
            
        Returns:
            True if the number is a k-gonal number, False otherwise
        """
        if n <= 0 or k < 3:
            return False
        
        # Optimize common cases
        if k == 3:  # Triangular
            n = int((math.sqrt(8 * n + 1) - 1) / 2)
            return n * (n + 1) // 2 == n
        elif k == 4:  # Square
            n = int(math.sqrt(n))
            return n * n == n
        elif k == 5:  # Pentagonal
            n = int((math.sqrt(24 * n + 1) + 1) / 6)
            return n * (3 * n - 1) // 2 == n
        elif k == 6:  # Hexagonal
            n = int((math.sqrt(8 * n + 1) + 1) / 4)
            return n * (2 * n - 1) == n
        
        # General case for other polygonal numbers
        # Solve the equation: n = r * ((k-2)*r - (k-4)) / 2
        # This is a quadratic: (k-2)*r² - (k-4)*r - 2*n = 0
        a = k - 2
        b = -(k - 4)
        c = -2 * n
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return False
        
        # We need a positive integer solution
        r = (-b + math.sqrt(discriminant)) / (2 * a)
        return r > 0 and r.is_integer()
    
    def get_polygonal_index(self, n: int, k: int) -> Optional[int]:
        """
        Get the index of a polygonal number.
        
        Args:
            n: The number to check
            k: The number of sides (k >= 3)
            
        Returns:
            The index if the number is a k-gonal number, None otherwise
        """
        if n <= 0 or k < 3:
            return None
        
        # Optimize common cases
        if k == 3:  # Triangular
            n = int((math.sqrt(8 * n + 1) - 1) / 2)
            return n if n * (n + 1) // 2 == n else None
        elif k == 4:  # Square
            n = int(math.sqrt(n))
            return n if n * n == n else None
        elif k == 5:  # Pentagonal
            n = int((math.sqrt(24 * n + 1) + 1) / 6)
            return n if n * (3 * n - 1) // 2 == n else None
        elif k == 6:  # Hexagonal
            n = int((math.sqrt(8 * n + 1) + 1) / 4)
            return n if n * (2 * n - 1) == n else None
        
        # General case for other polygonal numbers
        a = k - 2
        b = -(k - 4)
        c = -2 * n
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        
        r = (-b + math.sqrt(discriminant)) / (2 * a)
        if r > 0 and r.is_integer():
            return int(r)
        
        return None
    
    @lru_cache(maxsize=1000)
    def is_centered_polygonal(self, n: int, k: int) -> bool:
        """
        Check if a number is a centered k-gonal number.
        
        Centered polygonal numbers are those that represent points arranged in a regular polygon
        with a point at the center.
        
        Args:
            n: The number to check
            k: The number of sides (k >= 3)
            
        Returns:
            True if the number is a centered k-gonal number, False otherwise
        """
        if n <= 0 or k < 3:
            return False
        
        if n == 1:
            return True  # 1 is a centered polygonal number for all k
        
        # Formula for centered k-gonal number: C_k(n) = (k*n^2 - k*n)/2 + 1
        # Solve for n: k*n^2 - k*n - 2*(n-1) = 0
        # This is a quadratic: a*n^2 + b*n + c = 0
        a = k
        b = -k
        c = -2 * (n - 1)
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return False
        
        # We need a positive integer solution
        n = (-b + math.sqrt(discriminant)) / (2 * a)
        return n > 0 and n.is_integer()
    
    def get_centered_polygonal_index(self, n: int, k: int) -> Optional[int]:
        """
        Get the index of a centered polygonal number.
        
        Args:
            n: The number to check
            k: The number of sides (k >= 3)
            
        Returns:
            The index if the number is a centered k-gonal number, None otherwise
        """
        if n <= 0 or k < 3:
            return None
        
        if n == 1:
            return 1  # 1 is always the first centered polygonal number
        
        # Formula for centered k-gonal number: C_k(n) = (k*n^2 - k*n)/2 + 1
        # Solve for n: k*n^2 - k*n - 2*(n-1) = 0
        a = k
        b = -k
        c = -2 * (n - 1)
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        
        n = (-b + math.sqrt(discriminant)) / (2 * a)
        if n > 0 and n.is_integer():
            return int(n)
        
        return None
    
    def ternary_to_conrune(self, ternary_str: str) -> int:
        """
        Convert a ternary string to its conrune value.
        
        Args:
            ternary_str: The ternary representation as a string
            
        Returns:
            The conrune value
        """
        if not ternary_str:
            return 0
        
        conrune = 0
        for digit in ternary_str:
            if digit == '1':
                conrune += 1
            elif digit == '2':
                conrune -= 1
        
        return conrune
    
    def get_reverse_ternary_decimal(self, number: int) -> int:
        """
        Get the decimal value of the reversed ternary representation of a number.
        
        Args:
            number: The original number
            
        Returns:
            The decimal value of the reversed ternary representation
        """
        if number < 0:
            return 0
        
        # Convert to ternary
        ternary = ""
        n = number
        while n > 0:
            remainder = n % 3
            ternary = str(remainder) + ternary
            n //= 3
        
        # Reverse the ternary representation
        reversed_ternary = ternary[::-1] if ternary else "0"
        
        # Convert back to decimal
        result = 0
        for i, digit in enumerate(reversed_ternary):
            result += int(digit) * (3 ** (len(reversed_ternary) - i - 1))
        
        return result
    
    def get_quadset_properties(self, number: int) -> Dict[str, Any]:
        """
        Get the quadset properties for a given number.
        
        A quadset consists of:
        1. The original number
        2. Its conrune value
        3. The reverse ternary value
        4. The conrune of the reverse ternary value
        
        Args:
            number: The number to analyze
            
        Returns:
            A dictionary containing the quadset properties
        """
        # Convert to ternary
        ternary = ""
        n = number
        while n > 0:
            remainder = n % 3
            ternary = str(remainder) + ternary
            n //= 3
        
        if not ternary:
            ternary = "0"
        
        # Calculate conrune
        conrune = self.ternary_to_conrune(ternary)
        
        # Calculate reverse ternary decimal
        reverse_ternary_decimal = self.get_reverse_ternary_decimal(number)
        
        # Calculate reverse ternary
        reverse_ternary = ""
        n = reverse_ternary_decimal
        while n > 0:
            remainder = n % 3
            reverse_ternary = str(remainder) + reverse_ternary
            n //= 3
        
        if not reverse_ternary:
            reverse_ternary = "0"
        
        # Calculate conrune of reverse ternary
        reverse_conrune = self.ternary_to_conrune(reverse_ternary)
        
        return {
            "number": number,
            "ternary": ternary,
            "conrune": conrune,
            "reverse_ternary_decimal": reverse_ternary_decimal,
            "reverse_ternary": reverse_ternary,
            "reverse_conrune": reverse_conrune
        }
    
    def is_in_quadset(self, number: int) -> Tuple[bool, Optional[int]]:
        """
        Check if a number is part of a quadset and identify the base number.
        
        Args:
            number: The number to check
            
        Returns:
            A tuple (is_in_quadset, base_number) where:
                - is_in_quadset: True if the number is part of a quadset
                - base_number: The base number that generates the quadset containing the input number,
                  or None if the number is not in any quadset
        """
        # Check if the number is a base number by examining its own quadset
        quadset = self.get_quadset_properties(number)
        if number in [
            quadset["number"],
            quadset["conrune"],
            quadset["reverse_ternary_decimal"],
            quadset["reverse_conrune"]
        ]:
            return True, number
        
        # Try to find by brute force if the number appears in another quadset
        # This approach has limitations for large numbers
        # For better performance, a database of pre-computed quadsets could be used
        
        # Check reasonable bounds around the number
        lower_bound = max(1, number // 10)
        upper_bound = number * 10
        
        for base in range(lower_bound, upper_bound):
            quadset = self.get_quadset_properties(base)
            if number in [
                quadset["conrune"],
                quadset["reverse_ternary_decimal"],
                quadset["reverse_conrune"]
            ]:
                return True, base
        
        return False, None
    
    def get_conrune(self, ternary: str) -> int:
        """Convert a ternary string to its conrune decimal value.
        
        The conrune transformation replaces each digit in ternary:
        0 -> 1
        1 -> 2
        2 -> 0
        
        Args:
            ternary: Ternary string to transform
            
        Returns:
            Decimal value of the conrune transformation
        """
        if not ternary or ternary == "0":
            return 1  # Special case: 0 becomes 1
            
        # Handle negative numbers
        is_negative = ternary.startswith("-")
        if is_negative:
            ternary = ternary[1:]
            
        # Apply conrune transformation
        conrune = ""
        for digit in ternary:
            if digit == "0":
                conrune += "1"
            elif digit == "1":
                conrune += "2"
            elif digit == "2":
                conrune += "0"
                
        # Convert back to decimal
        result = 0
        for digit in conrune:
            result = result * 3 + int(digit)
            
        return -result if is_negative else result
    
    def get_ternary_reversal(self, number: int) -> int:
        """Get the decimal value of a number's reversed ternary representation.
        
        Args:
            number: Number to get ternary reversal for
            
        Returns:
            Decimal value of the reversed ternary
        """
        ternary = self.get_ternary(number)
        
        # Handle negative numbers
        is_negative = ternary.startswith("-")
        if is_negative:
            ternary = ternary[1:]
            
        # Reverse the ternary digits
        reversed_ternary = ternary[::-1]
        
        # Convert back to decimal
        result = 0
        for digit in reversed_ternary:
            result = result * 3 + int(digit)
            
        return -result if is_negative else result
    
    def get_quadset_properties(self, number: int) -> Dict:
        """Get properties of a number's TQ quadset.
        
        The quadset consists of:
        1. The base number
        2. Its conrune (decimal value after conrune transformation of ternary)
        3. Its ternary reversal (decimal value after reversing ternary)
        4. The conrune of the ternary reversal
        
        Args:
            number: Base integer to analyze
            
        Returns:
            Dictionary of quadset properties
        """
        if not isinstance(number, int):
            try:
                number = int(number)
            except (ValueError, TypeError):
                raise ValueError("Input must be convertible to an integer")
                
        # Get the ternary representation
        ternary = self.get_ternary(number)
        
        # Calculate the quadset values
        conrune = self.get_conrune(ternary)
        ternary_reversal = self.get_ternary_reversal(number)
        reversal_conrune = self.get_conrune(self.get_ternary(ternary_reversal))
        
        # Get properties for each number
        base_props = self.get_number_properties(number)
        conrune_props = self.get_number_properties(conrune)
        reversal_props = self.get_number_properties(ternary_reversal)
        reversal_conrune_props = self.get_number_properties(reversal_conrune)
        
        # Combine into a quadset result
        quadset = {
            "base": {
                "number": number,
                "ternary": ternary,
                "properties": base_props
            },
            "conrune": {
                "number": conrune,
                "ternary": self.get_ternary(conrune),
                "properties": conrune_props
            },
            "ternary_reversal": {
                "number": ternary_reversal,
                "ternary": self.get_ternary(ternary_reversal),
                "properties": reversal_props
            },
            "reversal_conrune": {
                "number": reversal_conrune,
                "ternary": self.get_ternary(reversal_conrune),
                "properties": reversal_conrune_props
            },
            "quadset_sum": number + conrune + ternary_reversal + reversal_conrune,
            "ternary_sequence": [
                ternary,
                self.get_ternary(conrune),
                self.get_ternary(ternary_reversal),
                self.get_ternary(reversal_conrune)
            ]
        }
        
        return quadset
    
    @lru_cache(maxsize=1000)
    def is_perfect(self, number: int) -> bool:
        """Check if a number is perfect (sum of proper divisors equals the number).
        
        Args:
            number: Number to check
            
        Returns:
            True if perfect, False otherwise
        """
        if number <= 1:
            return False
            
        divisors = self.get_divisors(number)
        return sum(divisors) - number == number
    
    def is_abundant(self, number: int) -> bool:
        """Check if a number is abundant (sum of proper divisors exceeds the number).
        
        Args:
            number: Number to check
            
        Returns:
            True if abundant, False otherwise
        """
        if number <= 1:
            return False
            
        divisors = self.get_divisors(number)
        return sum(divisors) - number > number
    
    def is_deficient(self, number: int) -> bool:
        """Check if a number is deficient (sum of proper divisors is less than the number).
        
        Args:
            number: Number to check
            
        Returns:
            True if deficient, False otherwise
        """
        if number <= 1:
            return True
            
        divisors = self.get_divisors(number)
        return sum(divisors) - number < number
    
    def is_triangular(self, number: int) -> bool:
        """Check if a number is triangular (can be written as n*(n+1)/2).
        
        Args:
            number: Number to check
            
        Returns:
            True if triangular, False otherwise
        """
        if number < 0:
            return False
            
        # A number is triangular if 8*n+1 is a perfect square
        test = 8 * number + 1
        root = int(math.sqrt(test))
        return root * root == test
    
    def is_square(self, number: int) -> bool:
        """Check if a number is a perfect square.
        
        Args:
            number: Number to check
            
        Returns:
            True if square, False otherwise
        """
        if number < 0:
            return False
            
        root = math.sqrt(number)
        return root.is_integer()
    
    def get_binary(self, number: int) -> str:
        """Get binary representation of a number (without '0b' prefix).
        
        Args:
            number: Number to convert
            
        Returns:
            Binary string
        """
        if number < 0:
            # For negative numbers, use the absolute value with a minus sign
            return f"-{bin(abs(number))[2:]}"
        return bin(number)[2:]
    
    def get_ternary(self, number: int) -> str:
        """Get ternary (base-3) representation of a number.
        
        Args:
            number: Number to convert
            
        Returns:
            Ternary string
        """
        if number == 0:
            return "0"
            
        is_negative = number < 0
        n = abs(number)
        
        digits = []
        while n > 0:
            digits.append(str(n % 3))
            n //= 3
            
        ternary = "".join(reversed(digits))
        
        if is_negative:
            ternary = f"-{ternary}"
            
        return ternary
    
    def get_digits_sum(self, number: int) -> int:
        """Calculate the sum of all digits in the number.
        
        Args:
            number: Number to sum digits for
            
        Returns:
            Sum of digits
        """
        return sum(int(digit) for digit in str(abs(number)))
    
    def get_divisors(self, number: int) -> List[int]:
        """Get all divisors of a number, including 1 and itself.
        
        Args:
            number: Number to find divisors for
            
        Returns:
            Sorted list of divisors
        """
        if number in self._divisors_cache:
            return self._divisors_cache[number]
            
        if number <= 0:
            return []
            
        if number == 1:
            return [1]
            
        # Efficiently find divisors
        divisors = set()
        for i in range(1, int(math.sqrt(number)) + 1):
            if number % i == 0:
                divisors.add(i)
                divisors.add(number // i)
                
        result = sorted(list(divisors))
        
        # Cache the result
        self._divisors_cache[number] = result
        return result
    
    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._prime_cache.clear()
        self._factors_cache.clear()
        self._divisors_cache.clear()
        # Also clear the lru_cache for the methods
        self.is_prime.cache_clear()
        self.get_prime_factors.cache_clear()
        self.get_divisors.cache_clear()
        self._prime_ordinal_cache.clear()
    
    @lru_cache(maxsize=500)
    def is_pentagonal(self, number: int) -> bool:
        """Check if a number is pentagonal.
        
        Args:
            number: Number to check
            
        Returns:
            True if pentagonal, False otherwise
        """
        if number < 1:
            return False
            
        # A number is pentagonal if (sqrt(24n + 1) + 1) / 6 is an integer
        test = (math.sqrt(24 * number + 1) + 1) / 6
        return test.is_integer()
    
    @lru_cache(maxsize=500)
    def get_pentagonal_index(self, number: int) -> Optional[int]:
        """Get the index of a pentagonal number.
        
        Args:
            number: Number to get index for
            
        Returns:
            Index if pentagonal, None otherwise
        """
        if not self.is_pentagonal(number):
            return None
            
        return int((math.sqrt(24 * number + 1) + 1) / 6)
    
    @lru_cache(maxsize=500)
    def is_hexagonal(self, number: int) -> bool:
        """Check if a number is hexagonal.
        
        Args:
            number: Number to check
            
        Returns:
            True if hexagonal, False otherwise
        """
        if number < 1:
            return False
            
        # A number is hexagonal if (sqrt(8n + 1) + 1) / 4 is an integer
        test = (math.sqrt(8 * number + 1) + 1) / 4
        return test.is_integer()
    
    @lru_cache(maxsize=500)
    def get_hexagonal_index(self, number: int) -> Optional[int]:
        """Get the index of a hexagonal number.
        
        Args:
            number: Number to get index for
            
        Returns:
            Index if hexagonal, None otherwise
        """
        if not self.is_hexagonal(number):
            return None
            
        return int((math.sqrt(8 * number + 1) + 1) / 4)
    
    @lru_cache(maxsize=500)
    def get_triangular_index(self, number: int) -> Optional[int]:
        """Get the index of a triangular number.
        
        Args:
            number: Number to get index for
            
        Returns:
            Index if triangular, None otherwise
        """
        if not self.is_triangular(number):
            return None
            
        # For triangular number n, index k is: k = (-1 + sqrt(1 + 8n)) / 2
        return int((-1 + math.sqrt(1 + 8 * number)) / 2)
    
    @lru_cache(maxsize=500)
    def get_fibonacci_index(self, number: int) -> Optional[int]:
        """Get the index of a Fibonacci number.
        
        Args:
            number: Number to get index for
            
        Returns:
            Index if Fibonacci, None otherwise
        """
        if not self.is_fibonacci(number):
            return None
            
        if number <= 1:
            return number
            
        # For Fibonacci numbers > 1, calculate index
        # Using Binet's formula inverse
        phi = (1 + math.sqrt(5)) / 2
        index = round(math.log(number * math.sqrt(5) + 0.5, phi))
        return index