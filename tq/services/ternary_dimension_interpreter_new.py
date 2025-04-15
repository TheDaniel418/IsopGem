"""
Purpose: Provides interpretation services for ternary numbers through dimensional analysis

This file is part of the tq pillar and serves as a service component.
It is responsible for interpreting ternary digits and analyzing patterns of
ternary numbers through a dimensional framework.

Key components:
- TernaryDimensionInterpreter: Service class that generates interpretations of ternary numbers

Dependencies:
- typing: For type annotations

Related files:
- tq/ui/panels/cosmic_force_panel.py: Panel that uses this interpreter
- tq/utils/ternary_converter.py: For converting between decimal and ternary
"""

from typing import Dict, List, Union

# Import the potential triad meanings from the separate file
from tq.utils.potential_triad_definitions import potential_triad_meanings


class TernaryDimensionInterpreter:
    """Interprets ternary numbers using the dimensional framework."""

    # Dictionary mapping ternary digits to their dimensional meanings
    DIGIT_MEANINGS = {
        0: {
            "name": "Aperture",
            "energy": "Receptive",
            "quality": "Openness",
            "description": "Represents openings, potential, receptivity, and the unmanifest.",
        },
        1: {
            "name": "Surge",
            "energy": "Transformative",
            "quality": "Dynamic",
            "description": "Represents transformation, change, dynamic flow, and becoming.",
        },
        2: {
            "name": "Lattice",
            "energy": "Structural",
            "quality": "Stability",
            "description": "Represents structure, pattern, stability, and being.",
        },
    }

    # Position modifiers affect the interpretation based on digit position
    POSITION_MODIFIERS = [
        "Seed",
        "Resonance",
        "Echo",
        "Weave",
        "Pulse",
        "Flow",
        "Nexus",
        "Horizon",
        "Nova",
    ]

    # Pattern interpretations
    SEQUENCE_MEANINGS = {
        0: "Aperture sequences represent openings of possibility and receptive spaces for potential to emerge.",
        1: "Surge sequences indicate dynamic transformations and active flows of change.",
        2: "Lattice sequences show crystallized patterns and stable frameworks forming within the system.",
    }

    BALANCE_INTERPRETATIONS = {
        "balanced": "The elements exist in harmony, creating equilibrium between transformation and structure.",
        "transformative": "The elements favor Surge, indicating a system oriented toward change and transformation.",
        "structural": "The elements favor Lattice, indicating a system oriented toward stability and pattern.",
    }

    # Enhanced attribute: Detailed dimensional interpretations
    DIMENSIONAL_INTERPRETATIONS = {
        # Position 1: Seed
        1: {
            0: "Undifferentiated potential; the primal void from which all arises. Represents pure possibility, infinite readiness, the uncarved block awaiting the first impulse. A receptive ground zero.",
            1: "Active catalyst; the transformative spark initiating change. Represents the first motion, the drive to become, the energetic impulse that sets the system in motion. The foundation is dynamic.",
            2: "Structured blueprint; the defined pattern serving as foundation. Represents inherent order, the underlying code or structure that shapes potential from the outset. Stability is the starting point.",
        },
        # Position 2: Resonance
        2: {
            0: "Inner spaciousness; a receptive field allowing multiple internal possibilities. Represents adaptability, openness to internal shifts, a lack of fixed internal identity, allowing various frequencies.",
            1: "Self-reinforcing oscillation; growing internal momentum and energy. Represents amplifying internal dynamics, passions building, a potentially volatile or accelerating inner state.",
            2: "Stable frequency; consistent internal patterning and coherence. Represents inner harmony, self-consistency, a defined internal structure that resonates reliably.",
        },
        # Position 3: Echo
        3: {
            0: "Expanding void; an opening that grows and reverberates outward. Represents unrestricted potential for expression, broadcasting openness, influencing the environment through receptivity.",
            1: "Propagating wave; energy transferring dynamically across boundaries. Represents active influence, outward expression of internal energy, impact on the environment, communication.",
            2: "Structured replication; a pattern that reproduces itself outward. Represents organized influence, the projection of order, creating consistent external structures based on the internal pattern.",
        },
        # Position 4: Weave
        4: {
            0: "Open network; loose, flexible connections with ample space between nodes. Represents potential for connection, adaptability in relationships, freedom within the network.",
            1: "Dynamic exchange; active crossing, intermingling, and transformation of paths. Represents active networking, catalysis through connection, relationships driving change.",
            2: "Tight mesh; highly ordered, complex, and defined interconnections. Represents a strong, stable, potentially rigid network structure, established relationships.",
        },
        # Position 5: Pulse
        5: {
            0: "Pregnant pause; the potent silence between beats, holding potential timing. Represents readiness for action, strategic waiting, openness to the right moment, undefined rhythm.",
            1: "Active beat; accelerating rhythm, the decisive moment of change or action. Represents momentum, initiative, seizing the moment, a driving temporal force.",
            2: "Steady rhythm; regulated timing, predictable cycles, and temporal stability. Represents patience, persistence, measured action, adherence to established cycles.",
        },
        # Position 6: Flow
        6: {
            0: "Open channel; unrestrained potential for movement in any direction. Represents freedom of direction, many possible paths, lack of commitment to a single course.",
            1: "Directed current; purposeful, forceful movement toward or away from something. Represents clear intention, focused energy, drive, pursuit or retreat.",
            2: "Structured pathway; movement within defined channels or parameters. Represents guided progress, controlled flow, movement along established routes.",
        },
        # Position 7: Nexus
        7: {
            0: "Open intersection; a space where diverse paths or possibilities may connect. Represents potential convergence, opportunity for synthesis, a crossroads allowing multiple outcomes.",
            1: "Active fusion; energetic combining and transformation of converging elements. Represents synthesis in action, powerful integration, events reaching a critical, transformative juncture.",
            2: "Structured junction; an organized meeting point where patterns integrate coherently. Represents complex order, established intersections, a hub of stable connections.",
        },
        # Position 8: Horizon
        8: {
            0: "Open boundary; a permeable, undefined threshold to the unknown or the future. Represents limitless possibility beyond the current state, transcendence of perceived limits.",
            1: "Shifting limit; actively expanding or contracting boundaries. Represents growth or decay at the edges, evolution of scope, challenging or redefining limits.",
            2: "Defined frontier; a clear demarcation of domains, a stable and known limit. Represents mastery within boundaries, established scope, clarity about what is and isn't included.",
        },
        # Position 9: Nova
        9: {
            0: "Absolute openness; the transcendent void beyond all pattern and form. Represents ultimate potential, dissolution into pure possibility, the source or end point beyond structure.",
            1: "Total transformation; complete metamorphosis into an entirely new state or paradigm. Represents revolution, apotheosis, a fundamental shift in being or understanding.",
            2: "Ultimate pattern; the final crystallization of the highest conceivable order. Represents completion, perfection of form, the culmination of the system's potential into a stable, ultimate structure.",
        },
    }

    # Add specific triad combination meanings (can be expanded)
    TRIAD_COMBINATION_MEANINGS = {
        "Potential": potential_triad_meanings,
        "Process": {
            # TODO: Define Process Triad meanings (Key = L-to-R digits 4-5-6)
            "000": "(Dim 4-6: 000) Process Triad: Default meaning...",
            # ... other 26 meanings ...
        },
        "Emergence": {
            # TODO: Define Emergence Triad meanings (Key = L-to-R digits 7-8-9)
            "000": "(Dim 7-9: 000) Emergence Triad: Default meaning...",
            # ... other 26 meanings ...
        },
    }

    def __init__(self):
        """Initialize the ternary dimension interpreter."""
        pass

    def interpret_digit(self, digit: int, position: int = 0) -> Dict[str, str]:
        """
        Interpret a single ternary digit with position context.

        Args:
            digit: The ternary digit (0, 1, or 2)
            position: The position of the digit (0-based, right-to-left)

        Returns:
            Dictionary with the interpretation including dimensional details
        """
        if digit not in (0, 1, 2):
            raise ValueError(f"Invalid ternary digit: {digit}")

        # Basic interpretation from DIGIT_MEANINGS
        interpretation = self.DIGIT_MEANINGS[digit].copy()

        # Position modifier (Seed, Resonance, etc.)
        position_1_based = position + 1
        pos_modifier = self.POSITION_MODIFIERS[
            min(position, len(self.POSITION_MODIFIERS) - 1)
        ]
        interpretation[
            "position_name"
        ] = pos_modifier  # Use position_name for consistency with framework

        # Determine Triad
        if position_1_based <= 3:
            triad_name = "Potential"
        elif position_1_based <= 6:
            triad_name = "Process"
        else:
            triad_name = "Emergence"
        interpretation["triad_name"] = triad_name

        # Add position value
        interpretation["position_value"] = str(3**position)

        # Add the detailed dimensional interpretation
        dimensional_meaning = "Unknown position"
        if position_1_based in self.DIMENSIONAL_INTERPRETATIONS:
            if digit in self.DIMENSIONAL_INTERPRETATIONS[position_1_based]:
                dimensional_meaning = self.DIMENSIONAL_INTERPRETATIONS[
                    position_1_based
                ][digit]
        interpretation["dimensional_meaning"] = dimensional_meaning

        # Update context to include more details
        interpretation[
            "context"
        ] = f"{pos_modifier} ({triad_name}): {dimensional_meaning}"

        # Add the original digit to the interpretation dictionary
        interpretation["digit"] = digit

        return interpretation

    def analyze_ternary(
        self, ternary_digits: List[int]
    ) -> Dict[str, Union[List, Dict, str]]:
        """
        Analyze a full ternary number using the detailed interpretation framework.

        Args:
            ternary_digits: List of ternary digits (0, 1, 2)

        Returns:
            Dictionary with comprehensive analysis including triad analysis, patterns, and narrative
        """
        if not ternary_digits:
            return {"error": "Empty ternary input"}

        num_digits = len(ternary_digits)
        if num_digits > 9:
            return {"error": "Input number exceeds 9 ternary digits"}

        # 1. Dimensional Mapping & Initial Interpretation
        digits_interpretation = []
        for i, digit in enumerate(reversed(ternary_digits)):
            interpretation = self.interpret_digit(digit, i)
            digits_interpretation.append(interpretation)
        # Reverse back to original order (left-to-right) for analysis
        digits_interpretation.reverse()

        # 2. Triad Analysis
        triad_analysis = self._analyze_triads(digits_interpretation)

        # 3. Pattern Recognition
        pattern_analysis = self._recognize_patterns(ternary_digits)

        # 4. Element Counts & Balance
        counts = {0: 0, 1: 0, 2: 0}
        for digit in ternary_digits:
            counts[digit] += 1

        dominant_element_str = self._get_dominant_element(counts)
        balance_str = self._get_balance_interpretation(counts)

        # 5. Core Narrative Synthesis
        core_narrative = self._synthesize_narrative(
            digits_interpretation, triad_analysis, pattern_analysis, counts
        )

        result = {
            "digits": digits_interpretation,  # Detailed interpretation for each digit
            "triads": triad_analysis,
            "patterns": pattern_analysis,
            "distribution": {
                "counts": counts,
                "dominant_element": dominant_element_str,
                "balance": balance_str,
            },
            "narrative": core_narrative,
        }

        return result

    def _analyze_triads(self, digits_interpretation: List[Dict]) -> Dict:
        """Analyze each triad based on the framework."""
        triad_analysis = {
            "potential": {"summary": "", "positions": []},
            "process": {"summary": "", "positions": []},
            "emergence": {"summary": "", "positions": []},
        }

        num_digits = len(digits_interpretation)

        # Potential Triad (positions 1-3)
        if num_digits >= 1:
            potential_digits = digits_interpretation[
                max(0, num_digits - 3) : num_digits
            ]
            triad_analysis["potential"]["positions"] = potential_digits
            # Add summary logic based on framework (e.g., Lattice-Surge-Aperture: A structured beginning opening...)
            triad_analysis["potential"]["summary"] = self._summarize_triad(
                potential_digits, "Potential"
            )

        # Process Triad (positions 4-6)
        if num_digits >= 4:
            process_digits = digits_interpretation[
                max(0, num_digits - 6) : num_digits - 3
            ]
            triad_analysis["process"]["positions"] = process_digits
            triad_analysis["process"]["summary"] = self._summarize_triad(
                process_digits, "Process"
            )

        # Emergence Triad (positions 7-9)
        if num_digits >= 7:
            emergence_digits = digits_interpretation[0 : num_digits - 6]
            triad_analysis["emergence"]["positions"] = emergence_digits
            triad_analysis["emergence"]["summary"] = self._summarize_triad(
                emergence_digits, "Emergence"
            )

        return triad_analysis

    def _summarize_triad(self, triad_digits: List[Dict], triad_name: str) -> str:
        """Generate a summary for a given triad based on its digits."""
        if not triad_digits:
            return "Not applicable (number too short)"

        # Generate key based on LEFT-TO-RIGHT order as seen in the number
        # The input triad_digits list is already left-to-right for that triad segment
        digit_sequence = "".join(
            [str(d["digit"]) for d in triad_digits]
        )  # No reversal needed

        # Basic description (using the L-to-R key for display)
        summary = f"{triad_name} Triad ({digit_sequence}): Describes "
        if triad_name == "Potential":
            summary += "the foundational qualities and internal dynamics. "
        elif triad_name == "Process":
            summary += "how the system interacts, transforms, and develops. "
        elif triad_name == "Emergence":
            summary += "how the system culminates, transcends, and transforms. "

        # Check for specific combination meaning using the L-to-R key
        if triad_name in self.TRIAD_COMBINATION_MEANINGS:
            if digit_sequence in self.TRIAD_COMBINATION_MEANINGS[triad_name]:
                # The description fetched here MUST correspond to the correct
                # Seed-Resonance-Echo (or Weave-Pulse-Flow, etc.) pattern for this L-to-R sequence
                summary += f"**Specific Pattern:** {self.TRIAD_COMBINATION_MEANINGS[triad_name][digit_sequence]}"
            # else:
            # Optionally add a default message if a specific combo isn't defined yet
            # summary += "Specific combination meaning not yet defined."

        # TODO: Add more nuanced descriptions based on element counts within the triad

        return summary

    def _recognize_patterns(self, ternary_digits: List[int]) -> Dict:
        """Identify repetition, sequence, symmetry, and resonance patterns."""
        patterns = {
            "repetitions": [],
            "sequences": [],
            "symmetry": {
                "score": 0.0,
                "description": "No significant symmetry detected.",
            },
            "cross_triad_resonance": [],
        }

        num_digits = len(ternary_digits)
        if num_digits == 0:
            return patterns

        counts = {0: 0, 1: 0, 2: 0}
        for digit in ternary_digits:
            counts[digit] += 1

        # --- Repetition Patterns ---
        for digit, count in counts.items():
            if count >= 3:
                patterns["repetitions"].append(
                    {"element": self.DIGIT_MEANINGS[digit]["name"], "count": count}
                )
        if counts[0] == 0:
            patterns["repetitions"].append({"element": "Aperture", "absence": True})
        if counts[1] == 0:
            patterns["repetitions"].append({"element": "Surge", "absence": True})
        if counts[2] == 0:
            patterns["repetitions"].append({"element": "Lattice", "absence": True})

        # --- Sequence Patterns (Consecutive) ---
        current_sequence_digit = -1
        current_sequence_length = 0
        # Iterate left-to-right through the number as user reads it
        for i, digit in enumerate(ternary_digits):
            if digit == current_sequence_digit:
                current_sequence_length += 1
            else:
                if current_sequence_length >= 3:
                    patterns["sequences"].append(
                        {
                            "element": self.DIGIT_MEANINGS[current_sequence_digit][
                                "name"
                            ],
                            "length": current_sequence_length,
                            # Position needs mapping back to dimension number (1-based right-to-left)
                            "position": num_digits
                            - (i - current_sequence_length),  # Start dimension number
                        }
                    )
                current_sequence_digit = digit
                current_sequence_length = 1
        # Check trailing sequence
        if current_sequence_length >= 3:
            patterns["sequences"].append(
                {
                    "element": self.DIGIT_MEANINGS[current_sequence_digit]["name"],
                    "length": current_sequence_length,
                    "position": num_digits
                    - (num_digits - current_sequence_length),  # Start dimension number
                }
            )

        # --- Symmetry Analysis (Basic Palindrome Check) ---
        symmetry_matches = 0
        comparisons = num_digits // 2
        if comparisons > 0:
            for i in range(comparisons):
                # Compare digit i from left with digit i from right
                if ternary_digits[i] == ternary_digits[num_digits - 1 - i]:
                    symmetry_matches += 1
            patterns["symmetry"]["score"] = symmetry_matches / comparisons
            if patterns["symmetry"]["score"] > 0.75:
                patterns["symmetry"][
                    "description"
                ] = f"High symmetry detected (Score: {patterns['symmetry']['score']:.2f}). Suggests harmonic balance or structural reflection."
            elif patterns["symmetry"]["score"] > 0.4:
                patterns["symmetry"][
                    "description"
                ] = f"Moderate symmetry detected (Score: {patterns['symmetry']['score']:.2f}). Suggests some internal balance or mirroring."

        # --- Cross-Triad Resonance (Positions 1, 4, 7 | 2, 5, 8 | 3, 6, 9) ---
        # Map dimension number (1-based right-to-left) to digit
        pos_map = {i + 1: ternary_digits[num_digits - 1 - i] for i in range(num_digits)}

        if num_digits >= 7:
            # Check position 1, 4, 7
            if pos_map.get(1) == pos_map.get(4) == pos_map.get(7):
                patterns["cross_triad_resonance"].append(
                    f"Seed(1)-Weave(4)-Nexus(7) resonant on {self.DIGIT_MEANINGS[pos_map[1]]['name']}"
                )
            # Check position 2, 5, 8
            if pos_map.get(2) == pos_map.get(5) == pos_map.get(8):
                patterns["cross_triad_resonance"].append(
                    f"Resonance(2)-Pulse(5)-Horizon(8) resonant on {self.DIGIT_MEANINGS[pos_map[2]]['name']}"
                )
            # Check position 3, 6, 9
            if num_digits >= 9 and pos_map.get(3) == pos_map.get(6) == pos_map.get(9):
                patterns["cross_triad_resonance"].append(
                    f"Echo(3)-Flow(6)-Nova(9) resonant on {self.DIGIT_MEANINGS[pos_map[3]]['name']}"
                )
        elif num_digits >= 4:
            # Check resonance between Potential and Process triads
            if pos_map.get(1) == pos_map.get(4):
                patterns["cross_triad_resonance"].append(
                    f"Seed(1)-Weave(4) resonant on {self.DIGIT_MEANINGS[pos_map[1]]['name']}"
                )
            if num_digits >= 5 and pos_map.get(2) == pos_map.get(5):
                patterns["cross_triad_resonance"].append(
                    f"Resonance(2)-Pulse(5) resonant on {self.DIGIT_MEANINGS[pos_map[2]]['name']}"
                )
            if num_digits >= 6 and pos_map.get(3) == pos_map.get(6):
                patterns["cross_triad_resonance"].append(
                    f"Echo(3)-Flow(6) resonant on {self.DIGIT_MEANINGS[pos_map[3]]['name']}"
                )

        # TODO: Implement Progression (0->1->2), Oscillation (0->1->0) sequence detection

        return patterns

    def _get_dominant_element(self, counts: Dict[int, int]) -> str:
        """Determine the dominant element description."""
        max_count = max(counts.values()) if counts else 0
        if max_count == 0:
            return "No elements present"

        dominant_digits = [d for d, count in counts.items() if count == max_count]

        if len(dominant_digits) == 1:
            dominant = dominant_digits[0]
            return f"{self.DIGIT_MEANINGS[dominant]['name']} ({self.DIGIT_MEANINGS[dominant]['energy']})"
        else:
            return "Mixed (No clear dominance)"

    def _get_balance_interpretation(self, counts: Dict[int, int]) -> str:
        """Get the balance interpretation based on Surge vs Lattice counts."""
        if not counts:
            return "N/A"
        balance_score = counts.get(1, 0) - counts.get(2, 0)
        if balance_score > 0:
            return self.BALANCE_INTERPRETATIONS["transformative"]
        elif balance_score < 0:
            return self.BALANCE_INTERPRETATIONS["structural"]
        else:
            return self.BALANCE_INTERPRETATIONS["balanced"]

    def _synthesize_narrative(
        self,
        digits_interpretation: List[Dict],
        triad_analysis: Dict,
        pattern_analysis: Dict,
        counts: Dict,
    ) -> str:
        """Synthesize the analyses into a core narrative based on the framework."""
        narrative = "## Core Narrative Synthesis\n\n"  # Double newline after header

        num_digits = len(digits_interpretation)
        scale = (
            "Potential"
            if num_digits <= 3
            else "Process"
            if num_digits <= 6
            else "Emergence"
        )
        narrative += f"This is an **{scale}-scale** number ({num_digits} digits), activating triads up to {scale}.\n\n"  # Double newline

        # 1. Dominant Element Theme
        dominant_desc = self._get_dominant_element(counts)
        narrative += f"**Dominant Theme:** {dominant_desc}. "
        if "Aperture" in dominant_desc:
            narrative += "The primary theme revolves around potential, openness, and receptivity.\n\n"  # Double newline
        elif "Surge" in dominant_desc:
            narrative += "The primary theme revolves around transformation, dynamism, and change.\n\n"  # Double newline
        elif "Lattice" in dominant_desc:
            narrative += "The primary theme revolves around structure, stability, and defined patterns.\n\n"  # Double newline
        else:  # Mixed
            narrative += "The system shows a balance or mix of elemental influences without a single dominant theme.\n\n"  # Double newline

        # 2. Dimensional Emphasis & Triad Interaction
        narrative += "**Dimensional Emphasis & Triad Interaction:**\n"  # Single newline before list
        narrative += f"- {triad_analysis['potential']['summary']}\n"
        if num_digits >= 4:
            narrative += f"- {triad_analysis['process']['summary']}\n"
        if num_digits >= 7:
            narrative += f"- {triad_analysis['emergence']['summary']}\n"
        # Cross-Triad Resonance
        if pattern_analysis["cross_triad_resonance"]:
            narrative += (
                "- **Cross-Triad Resonance Detected:** "
                + "; ".join(pattern_analysis["cross_triad_resonance"])
                + "\n"
            )
        narrative += "\n"  # Double newline after list

        # 3. Transitional Flow & Patterns
        narrative += "**Transitional Flow & Key Patterns:**\n"
        # Sequences
        if pattern_analysis["sequences"]:
            narrative += "- Intensification through sequences: "
            # Display sequences with start dimension
            seq_descs = []
            for s in pattern_analysis["sequences"]:
                start_dim = s["position"]
                seq_descs.append(
                    f"{s['length']} {s['element']} (starting at Dim {start_dim})"
                )
            narrative += "; ".join(seq_descs) + ".\n"
        else:
            narrative += "- Frequent element shifts suggest dynamic interplay without prolonged intensification.\n"
        # Repetitions / Absences
        if pattern_analysis["repetitions"]:
            for rep in pattern_analysis["repetitions"]:
                if rep.get("absence"):
                    narrative += (
                        f"- Noteable absence of the {rep['element']} element.\n"
                    )
                elif rep["count"] / num_digits > 0.5:  # If > 50%
                    narrative += f"- Strong presence of {rep['element']} ({rep['count']} times).\n"
        # Symmetry
        if pattern_analysis["symmetry"]["score"] > 0.4:
            narrative += f"- {pattern_analysis['symmetry']['description']}\n"
        # TODO: Add Progression/Oscillation descriptions when implemented
        narrative += "\n"

        # 4. Harmonic Resolution (Balance)
        narrative += f"**Harmonic Balance:** {self._get_balance_interpretation(counts)}\n\n"  # Double newline

        # 5. Interpretive Weighting (Mention)
        narrative += "**Interpretive Weighting:** Note that Seed(1), Pulse(5), and Nova(9) dimensions often carry primary significance. Adjacency and cross-triad resonances amplify influence.\n\n"

        # TODO: Add Element Combination Meanings

        return narrative.strip()  # Use strip()
