#!/usr/bin/env python3
"""
Test script for the HexagramInterpreter class.
"""

from tq.services.ternary_dimension_interpreter_new import HexagramInterpreter

def test_interpret_digit():
    """Test the interpret_digit method."""
    interpreter = HexagramInterpreter()

    # Test digit 0 at position 0 (Seed)
    result = interpreter.interpret_digit(0, 0)
    print("Digit 0 at position 0 (Seed):")
    print(f"  Position: {result['position']}")
    print(f"  Position Name: {result['position_name']}")
    print(f"  Element: {result['name']}")
    print(f"  Description: {result['description']}")
    print()

    # Test digit 1 at position 3 (Weave)
    result = interpreter.interpret_digit(1, 3)
    print("Digit 1 at position 3 (Weave):")
    print(f"  Position: {result['position']}")
    print(f"  Position Name: {result['position_name']}")
    print(f"  Element: {result['name']}")
    print(f"  Description: {result['description']}")
    print()

def test_analyze_ternary():
    """Test the analyze_ternary method."""
    interpreter = HexagramInterpreter()

    # Test a simple ternary number
    ternary_digits = [0, 1, 2, 1, 0, 2]
    result = interpreter.analyze_ternary(ternary_digits)

    print("Analysis of ternary number 012102:")
    print(f"  Distribution: {result['distribution']['counts']}")
    print(f"  Dominant Element: {result['distribution']['dominant_element']}")
    print(f"  Balance: {result['distribution']['balance']}")
    print()
    print("Narrative:")
    print(result['narrative'])
    print()
    print("Holistic Interpretation:")
    print(result['holistic'])
    print()

def test_get_trigram_meanings():
    """Test the get_trigram_meanings method."""
    interpreter = HexagramInterpreter()

    # Test a 6-digit ternary number
    ditrune = "012102"
    result = interpreter.get_trigram_meanings(ditrune)

    print("Trigram meanings for 012102:")
    print("Upper Trigram:")
    print(f"  Trigram: {result['Upper Trigram']['trigram']}")
    print(f"  English Name: {result['Upper Trigram']['english_name']}")
    print(f"  Hebrew Name: {result['Upper Trigram']['name']}")
    print()
    print("Lower Trigram:")
    print(f"  Trigram: {result['Lower Trigram']['trigram']}")
    print(f"  English Name: {result['Lower Trigram']['english_name']}")
    print(f"  Hebrew Name: {result['Lower Trigram']['name']}")
    print()

def test_interpret():
    """Test the interpret method."""
    interpreter = HexagramInterpreter()

    # Test a 6-digit ternary number
    ditrune = "012102"
    result = interpreter.interpret(ditrune)

    print("Full interpretation of 012102:")
    print(f"  Ditrune Type: {result['ditrune_type']}")
    print(f"  Decimal Value: {result['Decimal Value']}")
    print(f"  Family: {result['Family']}")
    print(f"  Level: {result['Level']}")
    print()

    # Check if we have Hierophant, Acolyte, or Temple information
    if 'Hierophant' in result and result['Hierophant']:
        print("  Hierophant Information:")
        print(f"    Name: {result['Hierophant']['name']}")
    if 'Acolyte' in result and result['Acolyte']:
        print("  Acolyte Information:")
        print(f"    Title: {result['Acolyte']['title']}")
    if 'Temple' in result and result['Temple']:
        print("  Temple Information:")
        print(f"    Full Name: {result['Temple']['full_name']}")
    print()

if __name__ == "__main__":
    print("Testing HexagramInterpreter class...\n")
    test_interpret_digit()
    test_analyze_ternary()
    test_get_trigram_meanings()
    test_interpret()
    print("All tests completed.")
