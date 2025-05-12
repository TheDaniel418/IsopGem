#!/usr/bin/env python3
"""
Generate the ditrune database.

This script creates a SQLite database containing all 729 ditrunes in the Kamea system.
Run this script to initialize or update the ditrune database.
"""

import os
import sqlite3
import sys
from typing import Dict, Optional, Tuple

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tq.services.kamea_service import KameaService
from tq.services.ternary_dimension_interpreter_new import HexagramInterpreter


def ternary_to_decimal(ternary: str) -> int:
    """Convert a ternary string to decimal."""
    return sum(int(digit) * (3**i) for i, digit in enumerate(reversed(ternary)))


# Canonical Prime Ditrunes (Hierophants)
PRIME_DITRUNES = [
    "000000",
    "010101",
    "020202",
    "101010",
    "111111",
    "121212",
    "202020",
    "212121",
    "222222",
]

PRIME_DITRUNE_SET = set(PRIME_DITRUNES)

FAMILY_BY_PRIME = {prime: i for i, prime in enumerate(PRIME_DITRUNES)}


def nuclear_mutation(sixgram: str) -> str:
    seen = set()
    while sixgram not in seen:
        seen.add(sixgram)
        top = sixgram[1:4]
        bottom = sixgram[2:5]
        new_sixgram = top + bottom
        if new_sixgram == sixgram:
            return sixgram
        sixgram = new_sixgram
    # If a cycle is detected, return the lexicographically smallest in the cycle
    return min(seen)


def determine_family(ternary: str) -> int:
    # Use nuclear mutation to find the Prime Ditrune, then map to family
    prime = nuclear_mutation(ternary)
    return FAMILY_BY_PRIME.get(prime, -1)


def is_acolyte(ternary: str, family: int) -> bool:
    # Acolyte: same family, 0 in first and last digit, not the Hierophant
    return (
        ternary[0] == "0"
        and ternary[-1] == "0"
        and ternary not in PRIME_DITRUNE_SET
        and determine_family(ternary) == family
    )


def determine_ditrune_type(ternary: str) -> Tuple[str, int, Optional[int]]:
    """
    Determine the type of a ditrune (hierophant, acolyte, or temple).

    Returns:
        Tuple of (type, family, position)
        - type: "hierophant", "acolyte", or "temple"
        - family: 0-8
        - position: None for all types
    """
    family = determine_family(ternary)
    if ternary in PRIME_DITRUNE_SET:
        return "hierophant", family, None
    if is_acolyte(ternary, family):
        return "acolyte", family, None
    return "temple", family, None


def determine_element_descriptor(ternary: str) -> str:
    """Determine the element descriptor based on the ternary value."""
    # Count elements
    aperture_count = ternary.count("0")
    surge_count = ternary.count("1")
    lattice_count = ternary.count("2")

    # Check for palindromic pattern
    if ternary == ternary[::-1]:
        return "of Perfect Reflection"

    # Check for ascending pattern (0→1→2)
    if "012" in ternary:
        return "of Rising Power"

    # Check for descending pattern (2→1→0)
    if "210" in ternary:
        return "of Deepening Wisdom"

    # Check for alternating pattern
    if "010" in ternary or "121" in ternary or "202" in ternary:
        return "of Rhythmic Exchange"

    # Check for concentrated pattern (3+ of same digit)
    if aperture_count >= 3:
        return "of Open Mystery"
    elif surge_count >= 3:
        return "of Flowing Energy"
    elif lattice_count >= 3:
        return "of Formed Pattern"

    # Default to balanced
    return "of Harmonic Balance"


def get_temple_properties(ternary: str) -> Dict[str, str]:
    """Get properties specific to temples."""
    # Determine temple type based on first bigram (positions 1 & 6)
    first_bigram_decimal = int(ternary[0]) * 3 + int(ternary[5])

    # Temple types from docs/kamea/elemental_analysis_reference.md
    temple_types = [
        "The Nexus",  # 0 - Σύνδεσμος (Syndesmos)
        "The Crucible",  # 1 - Χωνευτήριον (Choneuterion)
        "The Beacon",  # 2 - Φρυκτωρία (Phryktoria)
        "The Reservoir",  # 3 - Δεξαμενή (Dexamene)
        "The Threshold",  # 4 - Κατώφλιον (Katophlion)
        "The Conduit",  # 5 - Ὀχετός (Ochetos)
        "The Resonator",  # 6 - Ἠχεῖον (Echeion)
        "The Catalyst",  # 7 - Ἐπιταχυντής (Epitachyntes)
        "The Fulcrum",  # 8 - Ὑπομόχλιον (Hypomochlion)
    ]

    temple_type = (
        temple_types[first_bigram_decimal]
        if 0 <= first_bigram_decimal < len(temple_types)
        else "The Nexus"
    )

    # Determine element descriptor
    element_descriptor = determine_element_descriptor(ternary)

    # Get kamea locator
    kamea_locator = f"{ternary[0]}-{ternary[2]}-{ternary[5]}"  # Simplified version

    return {
        "temple_type": temple_type,
        "element_descriptor": element_descriptor,
        "kamea_locator": kamea_locator,
    }


def to_ternary(n: int) -> str:
    # Converts an integer to a 6-digit ternary string
    t = ""
    x = n
    for _ in range(6):
        t = str(x % 3) + t
        x //= 3
    return t


def nuclear_mutation(ternary: str) -> str:
    # Canonical nuclear mutation: extract digits 2-4 and 3-5, concatenate
    return ternary[1:4] + ternary[2:5]


def classify_ditrune(n: int) -> dict:
    # Classifies a number as hierophant, acolyte, or temple based on mutation steps to a multiple of 91
    path = []
    ternary = to_ternary(n)
    current = ternary
    for iteration in range(3):  # 0, 1, 2
        dec = int(current, 3)
        path.append({"ternary": current, "decimal": dec})
        if dec % 91 == 0:
            if iteration == 0:
                return {
                    "number": n,
                    "ternary": ternary,
                    "type": "hierophant",
                    "hierophant": dec,
                    "acolyte": None,
                    "steps": iteration,
                    "path": path,
                }
            elif iteration == 1:
                return {
                    "number": n,
                    "ternary": ternary,
                    "type": "acolyte",
                    "hierophant": dec,
                    "acolyte": int(path[0]["decimal"]),
                    "steps": iteration,
                    "path": path,
                }
            elif iteration == 2:
                return {
                    "number": n,
                    "ternary": ternary,
                    "type": "temple",
                    "hierophant": dec,
                    "acolyte": int(path[1]["decimal"]),
                    "steps": iteration,
                    "path": path,
                }
        current = nuclear_mutation(current)
    # If not resolved in 2 steps, classify as 'other'
    return {
        "number": n,
        "ternary": ternary,
        "type": "other",
        "hierophant": None,
        "acolyte": None,
        "steps": 3,
        "path": path,
    }


def generate_canonical_kamea_classification():
    # Returns a list of dicts for all 729 numbers
    return [classify_ditrune(n) for n in range(729)]


def family_index_from_hierophant(hierophant_decimal):
    # Hierophant dec: 0, 91, 182, ... 728 (multiples of 91)
    return hierophant_decimal // 91


def create_database(db_path: str) -> None:
    print(f"Creating ditrune database at {db_path}...")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the ditrunes table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS ditrunes (
        id INTEGER PRIMARY KEY,
        ternary TEXT NOT NULL UNIQUE,
        decimal INTEGER NOT NULL,
        type TEXT NOT NULL,
        family INTEGER NOT NULL,
        position INTEGER,
        name TEXT,
        greek TEXT,
        description TEXT,
        kamea_locator TEXT,
        temple_type TEXT,
        element_descriptor TEXT,
        bigram1 INTEGER,
        bigram2 INTEGER,
        bigram3 INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # Create indices for faster lookups
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_ditrunes_ternary ON ditrunes(ternary)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_ditrunes_decimal ON ditrunes(decimal)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ditrunes_type ON ditrunes(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ditrunes_family ON ditrunes(family)")

    all_classified = [classify_ditrune(n) for n in range(729)]

    # --- Canonical Acolyte Selection (by family, always 8 per family) ---
    acolytes_by_family = {fam: [] for fam in range(9)}
    for d in all_classified:
        if d["type"] == "acolyte" and d["hierophant"] is not None:
            fam = family_index_from_hierophant(d["hierophant"])
            acolytes_by_family[fam].append(d)
    canonical_acolyte_ids = set()
    for fam, acolytes in acolytes_by_family.items():
        # Sort by decimal value for determinism
        selected = sorted(acolytes, key=lambda x: x["number"])[:8]
        canonical_acolyte_ids.update(x["number"] for x in selected)

    kamea_service = KameaService()
    hexagram_interpreter = HexagramInterpreter()

    # Now, insert all ditrunes with correct type
    for d in all_classified:
        ternary = d["ternary"]
        decimal = d["number"]
        family = None
        if d["type"] == "hierophant" and d["hierophant"] is not None:
            family = family_index_from_hierophant(d["hierophant"])
        elif d["type"] == "acolyte" and decimal in canonical_acolyte_ids:
            family = family_index_from_hierophant(d["hierophant"])
        elif d["type"] == "temple":
            # For temples, resolve family by hierophant
            if d["hierophant"] is not None:
                family = family_index_from_hierophant(d["hierophant"])

        # Determine canonical type
        if d["type"] == "hierophant":
            ditrune_type = "hierophant"
        elif d["type"] == "acolyte" and decimal in canonical_acolyte_ids:
            ditrune_type = "acolyte"
        elif d["type"] == "temple":
            ditrune_type = "temple"
        else:
            ditrune_type = "other"

        # Use canonical bigram and locator logic
        bigram1, bigram2, bigram3 = kamea_service.extract_bigrams(ternary)
        kamea_locator = kamea_service.calculate_kamea_locator(ternary)

        # Use canonical interpretive logic
        interp = hexagram_interpreter.interpret(ternary)
        name = None
        greek = None
        description = None
        temple_type = None
        element_descriptor = None

        def require(val, field, context):
            if val in (None, "", []):
                raise ValueError(
                    f"Missing required field '{field}' for {context} (ternary={ternary})"
                )
            return val

        if ditrune_type == "hierophant":
            hiero = interp.get("Hierophant")
            if not isinstance(hiero, dict):
                raise ValueError(
                    f"Interpreter did not return a Hierophant dict for {ternary}: {interp}"
                )
            name = require(hiero.get("name"), "name", "Hierophant")
            greek = require(hiero.get("greek"), "greek", "Hierophant")
            description = require(hiero.get("description"), "description", "Hierophant")
        elif ditrune_type == "acolyte":
            acolyte = interp.get("Acolyte", {})
            name = require(acolyte.get("title"), "title", "Acolyte")
            greek = require(acolyte.get("greek"), "greek", "Acolyte")
            description = require(acolyte.get("function"), "function", "Acolyte")
        elif ditrune_type == "temple":
            temple = interp.get("Temple", {})
            temple_type = require(temple.get("temple_type"), "temple_type", "Temple")
            element_descriptor = require(
                temple.get("element_descriptor"), "element_descriptor", "Temple"
            )
            name = require(temple.get("full_name"), "full_name", "Temple")
            greek = require(
                temple.get("temple_type_greek"), "temple_type_greek", "Temple"
            )
            description = ""  # If you want to require a description, add require() here
        else:
            name = require(ternary, "name", "Other")
            greek = require("", "greek", "Other")
            description = require("", "description", "Other")

        # Insert into database
        cursor.execute(
            """
        INSERT OR REPLACE INTO ditrunes
        (ternary, decimal, type, family, position, name, greek, description,
         kamea_locator, temple_type, element_descriptor, bigram1, bigram2, bigram3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                ternary,
                decimal,
                ditrune_type,
                family,
                None,
                name,
                greek,
                description,
                kamea_locator,
                temple_type,
                element_descriptor,
                int(bigram1, 3),
                int(bigram2, 3),
                int(bigram3, 3),
            ),
        )

    conn.commit()
    conn.close()
    print("Database populated successfully")


def get_ditrune_counts(db_path: str) -> Tuple[int, int, int, int]:
    """Get counts of ditrunes in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM ditrunes")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ditrunes WHERE type = 'hierophant'")
    hierophant_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ditrunes WHERE type = 'acolyte'")
    acolyte_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ditrunes WHERE type = 'temple'")
    temple_count = cursor.fetchone()[0]

    conn.close()

    return total_count, hierophant_count, acolyte_count, temple_count


if __name__ == "__main__":
    print("Initializing ditrune database...")

    # Define the database path
    db_path = os.path.join(os.path.expanduser("~"), ".isopgem", "data", "ditrunes.db")

    # Create the database
    create_database(db_path)

    # Get counts from the database
    total_count, hierophant_count, acolyte_count, temple_count = get_ditrune_counts(
        db_path
    )

    # The Kamea system should have:
    # - 9 hierophants (Prime Ditrunes)
    # - 72 acolytes (8 per family × 9 families)
    # - 648 temples (729 total - 9 hierophants - 72 acolytes = 648)
    print(f"Database initialized with {total_count} ditrunes:")
    print(f"  - {hierophant_count} hierophants (Prime Ditrunes)")
    print(f"  - {acolyte_count} acolytes (Composite Ditrunes)")
    print(f"  - {temple_count} temples (Concurrent Ditrunes)")

    # Verify the counts
    expected_hierophants = 9
    expected_acolytes = 72
    expected_temples = 648

    if (
        hierophant_count != expected_hierophants
        or acolyte_count != expected_acolytes
        or temple_count != expected_temples
    ):
        print(
            "\nWarning: The counts don't match the expected values for the Kamea system:"
        )
        print(
            f"  - Expected: {expected_hierophants} hierophants, {expected_acolytes} acolytes, {expected_temples} temples"
        )
        print(
            f"  - Actual: {hierophant_count} hierophants, {acolyte_count} acolytes, {temple_count} temples"
        )
    print(f"Database location: {db_path}")
