"""Unit tests for Golden Trisection implementation.

This module verifies that the Golden Trisection implementation correctly reflects 
the mathematical relationship of 1:ρ:σ for the three segments.
"""

import math
import pytest

from geometry.services.golden_mean_service import GoldenMeanService


def test_golden_trisection_segment_proportions():
    """Test that the Golden Trisection segments follow the 1:ρ:σ proportion."""
    service = GoldenMeanService.get_instance()
    
    # Test with different total lengths
    for length in [1, 10, 100, 1000]:
        trisection = service.calculate_golden_trisection(length)
        
        # Extract segment lengths
        first = trisection["first_segment"]
        second = trisection["second_segment"]
        third = trisection["third_segment"]
        
        # Extract constants
        RHO = trisection["rho"]      # Expected to be ≈ 1.802
        SIGMA = trisection["sigma"]  # Expected to be ≈ 2.247
        
        # Verify the key relationship: segments should be in proportion 1:ρ:σ
        assert math.isclose(first * RHO, second, rel_tol=1e-10)
        assert math.isclose(first * SIGMA, third, rel_tol=1e-10)
        
        # Verify total length is correct
        assert math.isclose(first + second + third, length, rel_tol=1e-10)
        
        # Verify the unit length calculation was done correctly
        unit_length = length / (1 + RHO + SIGMA)
        assert math.isclose(first, unit_length, rel_tol=1e-10)
        
        # Verify the mathematical properties of ρ and σ
        assert math.isclose(RHO**2, SIGMA + 1, rel_tol=1e-10)
        assert math.isclose(SIGMA**2, RHO + SIGMA + 1, rel_tol=1e-10)
        assert math.isclose(RHO * SIGMA, RHO + SIGMA, rel_tol=1e-10)


def test_golden_trisection_trigonometric_calculation():
    """Test that ρ and σ match their trigonometric formulas for heptagon diagonals."""
    service = GoldenMeanService.get_instance()
    trisection = service.calculate_golden_trisection(1.0)
    
    # Get the constants
    RHO = trisection["rho"]      # Short diagonal
    SIGMA = trisection["sigma"]  # Long diagonal
    
    # Calculate the expected values from trigonometric formulas
    # For a unit-edge heptagon:
    # ρ = sin(2π/7) / sin(π/7)
    # σ = sin(4π/7) / sin(π/7)
    expected_rho = math.sin(2 * math.pi / 7) / math.sin(math.pi / 7)
    expected_sigma = math.sin(4 * math.pi / 7) / math.sin(math.pi / 7)
    
    # Verify the constants are correct
    assert math.isclose(RHO, expected_rho, rel_tol=1e-10)
    assert math.isclose(SIGMA, expected_sigma, rel_tol=1e-10)


def test_golden_trisection_segment_ratio():
    """Test that the segment ratios to total length are correctly calculated."""
    service = GoldenMeanService.get_instance()
    trisection = service.calculate_golden_trisection(100)
    
    # Extract segment lengths
    first = trisection["first_segment"]
    second = trisection["second_segment"]
    third = trisection["third_segment"]
    total = trisection["total_length"]
    
    # Extract segment ratios
    first_ratio = trisection["rho_lowercase"]
    second_ratio = trisection["sigma_lowercase"]
    third_ratio = trisection["third_ratio"]
    
    # Verify the ratios are correctly calculated
    assert math.isclose(first_ratio, first / total, rel_tol=1e-10)
    assert math.isclose(second_ratio, second / total, rel_tol=1e-10)
    assert math.isclose(third_ratio, third / total, rel_tol=1e-10)
    
    # Ratios should add up to 1
    assert math.isclose(first_ratio + second_ratio + third_ratio, 1.0, rel_tol=1e-10)
