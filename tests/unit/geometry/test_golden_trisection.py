#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for Golden Trisection functionality."""

import pytest
from math import isclose

from geometry.services.golden_mean_service import GoldenMeanService


class TestGoldenTrisection:
    """Test cases for the Golden Trisection implementation."""

    def test_golden_trisection_calculation(self):
        """Test that the golden trisection calculation works correctly."""
        # Get the Golden Mean service
        service = GoldenMeanService.get_instance()
        
        # Use a test length of 1.0
        trisection = service.calculate_golden_trisection(1.0)
        
        # Test the key constants for segment ratios
        assert isclose(trisection["alpha"], 0.246979603717467, abs_tol=1e-9)           # Alpha - X segment
        assert isclose(trisection["sigma_lowercase"], 0.445041867912629, abs_tol=1e-9) # sigma - Y segment
        assert isclose(trisection["rho_lowercase"], 0.554958132087371, abs_tol=1e-9)   # rho - Z segment
        
        # Test the heptagon diagonals
        assert isclose(trisection["sigma"], 2.24697960371747, abs_tol=1e-9)   # SIGMA uppercase - long diagonal 
        assert isclose(trisection["rho"], 1.80193773580484, abs_tol=1e-9)     # RHO uppercase - short diagonal
        
        # Test that segment values are calculated correctly for the normalized case (length=1)
        assert isclose(trisection["first_segment"], 0.246979603717467, abs_tol=1e-9)
        assert isclose(trisection["second_segment"], 0.445041867912629, abs_tol=1e-9)
        assert isclose(trisection["third_segment"], 0.554958132087371, abs_tol=1e-9)
        
        # Test that the segments sum to the total length
        total_segments = (
            trisection["first_segment"] + 
            trisection["second_segment"] + 
            trisection["third_segment"]
        )
        assert isclose(total_segments, 1.0, abs_tol=1e-9)
        
        # Test with another length to verify scaling
        trisection_100 = service.calculate_golden_trisection(100.0)
        assert isclose(trisection_100["first_segment"], 24.6979603717467, abs_tol=1e-9)
        assert isclose(trisection_100["second_segment"], 44.5041867912629, abs_tol=1e-9)
        assert isclose(trisection_100["third_segment"], 55.4958132087371, abs_tol=1e-9)
        
        # Verify that segments still sum to the total length
        total_segments = (
            trisection_100["first_segment"] + 
            trisection_100["second_segment"] + 
            trisection_100["third_segment"]
        )
        assert isclose(total_segments, 100.0, abs_tol=1e-9)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
