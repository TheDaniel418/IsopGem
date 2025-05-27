"""
Utility functions for astronomical calculations relevant to the astrology pillar.

Author: IsopGemini
Created: 2024-07-30
Last Modified: 2024-07-30
Dependencies: None (math module is built-in)
"""


DEFAULT_NUM_AUBREY_HOLES = 56
DEGREES_PER_HOLE = 360.0 / DEFAULT_NUM_AUBREY_HOLES  # Approx 6.42857 degrees

# Standard astronomical convention: 0 degrees ecliptic longitude = First Point of Aries (often depicted as East).
# If Hole 0 in the UI is at the North point:
# North corresponds to 90 degrees ecliptic longitude (if Aries is East).
# So, an astronomical longitude of 90 degrees should map to Hole 0.
ASTRO_LONGITUDE_FOR_HOLE_0 = (
    90.0  # Degrees (e.g., Cancer ingress if Aries is 0 deg East)
)


def longitude_to_aubrey_hole(
    longitude_deg: float,
    num_holes: int = DEFAULT_NUM_AUBREY_HOLES,
    hole_0_astro_ref_deg: float = ASTRO_LONGITUDE_FOR_HOLE_0,
) -> int:
    """
    Converts an astronomical longitude (0-360 degrees) to the nearest Aubrey Hole number (0 to num_holes-1).

    Assumes Hole 0 is at a specific astronomical reference point (e.g., North, which might be 90 degrees
    ecliptic longitude if 0 degrees Aries is East), and hole numbers increase counter-clockwise.
    Astronomical longitudes also typically increase counter-clockwise.

    Args:
        longitude_deg (float): The astronomical longitude in degrees (0-360).
        num_holes (int): The total number of holes in the circle. Defaults to 56.
        hole_0_astro_ref_deg (float): The astronomical longitude that corresponds to Hole 0.
                                      Defaults to 90.0 degrees (e.g., North if Aries is East).

    Returns:
        int: The calculated Aubrey Hole number (0 to num_holes-1).
    """
    if num_holes <= 0:
        raise ValueError("Number of holes must be positive.")

    degrees_per_hole_calc = 360.0 / num_holes

    # Normalize the input longitude to be 0-360
    normalized_longitude_deg = longitude_deg % 360.0
    if normalized_longitude_deg < 0:  # Ensure positive
        normalized_longitude_deg += 360.0

    # Adjust the longitude so that hole_0_astro_ref_deg becomes the new 0 point for calculation.
    # If astro_long is 90 and hole_0_ref is 90, adjusted_deg is 0.
    # If astro_long is 97 and hole_0_ref is 90, adjusted_deg is 7.
    # This measures how far past the hole_0_astro_ref_deg the current longitude is, in CCW direction.
    adjusted_deg = (normalized_longitude_deg - hole_0_astro_ref_deg + 360.0) % 360.0

    # Calculate hole number by dividing by degrees per hole and rounding.
    # Example: if adjusted_deg is 3.0 (slightly past Hole 0 ref), and deg_per_hole is 6.4, then 3.0/6.4 = 0.46 -> rounds to 0.
    # if adjusted_deg is 8.0, and deg_per_hole is 6.4, then 8.0/6.4 = 1.25 -> rounds to 1.
    hole_number_float = adjusted_deg / degrees_per_hole_calc

    # Round to nearest whole number for the hole index
    hole_number = int(round(hole_number_float))

    # Ensure the result is within the valid range [0, num_holes-1]
    # This handles cases where rounding might push it to num_holes (e.g. exactly on the seam for the last hole)
    final_hole_number = hole_number % num_holes

    return final_hole_number


# Example Usage:
if __name__ == "__main__":
    print(
        f"Degrees per hole for {DEFAULT_NUM_AUBREY_HOLES} holes: {DEGREES_PER_HOLE:.3f}"
    )
    print(f"Assuming Hole 0 is at {ASTRO_LONGITUDE_FOR_HOLE_0} degrees (e.g., North).")

    # Test cases
    test_longitudes = {
        ASTRO_LONGITUDE_FOR_HOLE_0: 0,  # Should be Hole 0
        ASTRO_LONGITUDE_FOR_HOLE_0
        + DEGREES_PER_HOLE / 2
        - 0.1: 0,  # Just before midpoint to Hole 1, should be Hole 0
        ASTRO_LONGITUDE_FOR_HOLE_0
        + DEGREES_PER_HOLE / 2
        + 0.1: 1,  # Just after midpoint to Hole 1, should be Hole 1
        ASTRO_LONGITUDE_FOR_HOLE_0 + DEGREES_PER_HOLE: 1,  # Should be Hole 1
        (ASTRO_LONGITUDE_FOR_HOLE_0 + 13 * DEGREES_PER_HOLE): 13,  # Should be Hole 13
        (
            ASTRO_LONGITUDE_FOR_HOLE_0 + 27 * DEGREES_PER_HOLE
        ): 27,  # Should be Hole 27 (approx South)
        (ASTRO_LONGITUDE_FOR_HOLE_0 + 55 * DEGREES_PER_HOLE): 55,  # Should be Hole 55
        (
            ASTRO_LONGITUDE_FOR_HOLE_0 - DEGREES_PER_HOLE / 2 + 0.1
        ): 55,  # Just before midpoint to Hole 0 (from CCW), should be Hole 55
        (
            ASTRO_LONGITUDE_FOR_HOLE_0 - DEGREES_PER_HOLE / 2 - 0.1
        ): 55,  # Further into Hole 55 range
        0.0: None,  # Aries 0 (East)
        89.0: None,  # Almost North
        90.0: 0,  # North
        93.0: 0,  # Slightly past North, still Hole 0
        96.0: 0,  # Midpoint-ish is 90 + 3.21 = 93.21. So 96 should be 1. Let's check this.
        # 96 - 90 = 6. 6 / 6.428 = 0.93. round(0.93) = 1. Correct.
        180.0: None,  # Libra (West)
        270.0: None,  # Capricorn (South)
        359.0: None,  # Almost Aries 0 again
    }

    print("\nTest conversions:")
    for lon, expected_hole in test_longitudes.items():
        # For None cases, calculate expected based on logic
        if expected_hole is None:
            # (lon - 90 + 360) % 360 / DEGREES_PER_HOLE
            adj_lon = (lon - ASTRO_LONGITUDE_FOR_HOLE_0 + 360.0) % 360.0
            calc_expected_float = adj_lon / DEGREES_PER_HOLE
            calc_expected_int = (
                int(round(calc_expected_float)) % DEFAULT_NUM_AUBREY_HOLES
            )
            expected_hole_val = calc_expected_int
        else:
            expected_hole_val = expected_hole

        calculated_hole = longitude_to_aubrey_hole(lon)
        status = (
            "PASS"
            if calculated_hole == expected_hole_val
            else f"FAIL (Expected {expected_hole_val})"
        )
        print(f"  Longitude {lon:6.1f} deg -> Hole {calculated_hole:2} ({status})")

    # Test edge case: longitude that rounds up to num_holes
    # e.g., if hole 0 is 90 deg, and Hole 55 ends just before 90 deg again (like 90 - epsilon)
    # Longitude slightly less than hole_0_astro_ref_deg should map to num_holes-1
    lon_just_before_hole0_ccw = (
        ASTRO_LONGITUDE_FOR_HOLE_0 - DEGREES_PER_HOLE / 4 + 360.0
    ) % 360.0
    calculated_hole = longitude_to_aubrey_hole(lon_just_before_hole0_ccw)
    expected = DEFAULT_NUM_AUBREY_HOLES - 1
    status = "PASS" if calculated_hole == expected else f"FAIL (Expected {expected})"
    print(
        f"  Longitude {lon_just_before_hole0_ccw:6.1f} deg (just before Hole 0 CCW) -> Hole {calculated_hole:2} ({status})"
    )
