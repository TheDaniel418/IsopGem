"""
Purpose: Provides holistic interpretation functionality for ternary patterns

This file is part of the tq pillar and serves as a utility component.
It is responsible for synthesizing comprehensive interpretations of ternary numbers
by analyzing patterns across individual digits and triads.

Key components:
- HolisticInterpreter: Class that generates holistic interpretations of ternary patterns

Dependencies:
- typing: For type annotations

Related files:
- tq/services/ternary_dimension_interpreter.py: Uses this module for holistic interpretations
"""

from typing import Dict, List, Optional


class HolisticInterpreter:
    """Generates holistic interpretations of ternary patterns."""

    # Element names for reference
    ELEMENT_NAMES = {0: "Aperture", 1: "Surge", 2: "Lattice"}

    # Element qualities for reference
    ELEMENT_QUALITIES = {
        0: {"energy": "Receptive", "quality": "Openness"},
        1: {"energy": "Transformative", "quality": "Dynamic"},
        2: {"energy": "Structural", "quality": "Stability"},
    }

    def __init__(self):
        """Initialize the holistic interpreter."""
        pass

    def generate_holistic_interpretation(
        self,
        ternary_digits: List[int],
        _digit_interpretations: List[
            Dict
        ],  # Not used directly but kept for API compatibility
        triad_analysis: Dict,
    ) -> Dict[str, str]:
        """
        Generate a comprehensive holistic interpretation of the ternary pattern.

        Args:
            ternary_digits: The ternary digits to interpret
            digit_interpretations: Detailed interpretations of each digit
            triad_analysis: Analysis of the triads in the pattern

        Returns:
            Dictionary containing different aspects of the holistic interpretation
        """
        # Ensure we have valid input
        if not ternary_digits:
            return {"error": "No digits to interpret"}

        # Generate the component analyses
        pattern_identity = self._determine_pattern_identity(ternary_digits)
        flow_analysis = self._analyze_dimensional_flow(ternary_digits)
        meta_patterns = self._identify_meta_patterns(ternary_digits)

        # Generate triad integration analysis if we have multiple triads
        triad_integration = None
        if len(ternary_digits) >= 4 and triad_analysis.get("process", {}).get(
            "positions"
        ):
            triad_integration = self._analyze_triad_integration(
                ternary_digits, triad_analysis
            )

        # Create the overall synthesis
        synthesis = self._synthesize_overall_interpretation(
            ternary_digits,
            pattern_identity,
            flow_analysis,
            triad_integration,
            meta_patterns,
        )

        # Assemble the complete interpretation
        interpretation = {
            "pattern_identity": pattern_identity,
            "flow_analysis": flow_analysis,
            "meta_patterns": meta_patterns,
            "synthesis": synthesis,
        }

        if triad_integration:
            interpretation["triad_integration"] = triad_integration

        return interpretation

    def _determine_pattern_identity(self, ternary_digits: List[int]) -> Dict[str, str]:
        """
        Determine the fundamental character or archetype of the pattern.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Dictionary with pattern identity information
        """
        # Calculate various metrics
        stability_score = self._calculate_stability_score(ternary_digits)
        dynamism_score = self._calculate_dynamism_score(ternary_digits)
        complexity_score = self._calculate_complexity_score(ternary_digits)

        # Determine primary and secondary characteristics
        scores = [
            ("Stable", stability_score),
            ("Dynamic", dynamism_score),
            ("Complex", complexity_score),
        ]

        # Sort by score in descending order
        scores.sort(key=lambda x: x[1], reverse=True)
        primary_trait = scores[0][0]
        secondary_trait = scores[1][0]

        # Generate descriptive identity
        title = ""
        description = ""

        if primary_trait == "Stable":
            title = "Crystalline Pattern"
            description = (
                "A highly ordered system with clear structure and predictable behavior."
            )
            if secondary_trait == "Dynamic":
                title = "Evolving Structure"
                description += " While primarily stable, it contains elements of change and adaptation."
            elif secondary_trait == "Complex":
                title = "Intricate Framework"
                description += " Its stability comes from a sophisticated arrangement of interconnected elements."
        elif primary_trait == "Dynamic":
            title = "Transformative Pattern"
            description = "A system in flux, characterized by change and evolution."
            if secondary_trait == "Stable":
                title = "Directed Change"
                description += " Its transformations follow consistent principles, creating reliable progression."
            elif secondary_trait == "Complex":
                title = "Adaptive Process"
                description += " Its changes respond to and generate complex interactions across multiple dimensions."
        else:  # Complex
            title = "Integrative Pattern"
            description = "A complex system balancing multiple forces and tendencies."
            if secondary_trait == "Stable":
                title = "Harmonious Complexity"
                description += " Despite its intricacy, it maintains a fundamental order and coherence."
            elif secondary_trait == "Dynamic":
                title = "Emergent System"
                description += " Its complexity generates ongoing transformations and novel properties."

        return {
            "title": title,
            "description": description,
            "primary_trait": primary_trait,
            "secondary_trait": secondary_trait,
            "stability_score": f"{stability_score:.2f}",
            "dynamism_score": f"{dynamism_score:.2f}",
            "complexity_score": f"{complexity_score:.2f}",
        }

    def _calculate_stability_score(self, ternary_digits: List[int]) -> float:
        """
        Calculate a stability score for the pattern.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Stability score between 0.0 and 1.0
        """
        if not ternary_digits:
            return 0.0

        # Count Lattice (2) elements which contribute to stability
        lattice_count = ternary_digits.count(2)

        # Count repeating sequences which contribute to stability
        repeats = 0
        for i in range(len(ternary_digits) - 1):
            if ternary_digits[i] == ternary_digits[i + 1]:
                repeats += 1

        # Check for symmetry which contributes to stability
        symmetry_score = self._calculate_symmetry_score(ternary_digits)

        # Combine factors
        lattice_factor = lattice_count / len(ternary_digits)
        repeat_factor = (
            repeats / (len(ternary_digits) - 1) if len(ternary_digits) > 1 else 0
        )

        # Weight the factors
        stability_score = (
            (0.5 * lattice_factor) + (0.3 * repeat_factor) + (0.2 * symmetry_score)
        )

        return min(1.0, stability_score * 1.5)  # Scale up slightly but cap at 1.0

    def _calculate_dynamism_score(self, ternary_digits: List[int]) -> float:
        """
        Calculate a dynamism score for the pattern.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Dynamism score between 0.0 and 1.0
        """
        if not ternary_digits:
            return 0.0

        # Count Surge (1) elements which contribute to dynamism
        surge_count = ternary_digits.count(1)

        # Count transitions which contribute to dynamism
        transitions = 0
        for i in range(len(ternary_digits) - 1):
            if ternary_digits[i] != ternary_digits[i + 1]:
                transitions += 1

        # Check for progressive sequences (0->1->2 or 2->1->0)
        progressions = 0
        for i in range(len(ternary_digits) - 2):
            if (
                ternary_digits[i] == 0
                and ternary_digits[i + 1] == 1
                and ternary_digits[i + 2] == 2
            ) or (
                ternary_digits[i] == 2
                and ternary_digits[i + 1] == 1
                and ternary_digits[i + 2] == 0
            ):
                progressions += 1

        # Combine factors
        surge_factor = surge_count / len(ternary_digits)
        transition_factor = (
            transitions / (len(ternary_digits) - 1) if len(ternary_digits) > 1 else 0
        )
        progression_factor = (
            progressions / (len(ternary_digits) - 2) if len(ternary_digits) > 2 else 0
        )

        # Weight the factors
        dynamism_score = (
            (0.4 * surge_factor)
            + (0.4 * transition_factor)
            + (0.2 * progression_factor)
        )

        return min(1.0, dynamism_score * 1.5)  # Scale up slightly but cap at 1.0

    def _calculate_complexity_score(self, ternary_digits: List[int]) -> float:
        """
        Calculate a complexity score for the pattern.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Complexity score between 0.0 and 1.0
        """
        if not ternary_digits:
            return 0.0

        # Calculate element diversity (higher diversity = more complex)
        unique_elements = len(set(ternary_digits))
        diversity_factor = (unique_elements - 1) / 2  # Normalize to 0-1 range

        # Calculate pattern entropy (higher entropy = more complex)
        # Use a simplified entropy calculation based on transitions
        transitions = 0
        for i in range(len(ternary_digits) - 1):
            if ternary_digits[i] != ternary_digits[i + 1]:
                transitions += 1

        entropy_factor = (
            transitions / (len(ternary_digits) - 1) if len(ternary_digits) > 1 else 0
        )

        # Check for balanced distribution (more balance = more complex)
        counts = [ternary_digits.count(i) for i in range(3)]
        max_count = max(counts)
        balance_factor = 1.0 - (max_count / len(ternary_digits))

        # Weight the factors
        complexity_score = (
            (0.3 * diversity_factor) + (0.4 * entropy_factor) + (0.3 * balance_factor)
        )

        return min(1.0, complexity_score * 1.5)  # Scale up slightly but cap at 1.0

    def _calculate_symmetry_score(self, ternary_digits: List[int]) -> float:
        """
        Calculate a symmetry score for the pattern.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Symmetry score between 0.0 and 1.0
        """
        if len(ternary_digits) <= 1:
            return 1.0  # A single digit is trivially symmetric

        # Check for palindromic symmetry
        matches = 0
        for i in range(len(ternary_digits) // 2):
            if ternary_digits[i] == ternary_digits[len(ternary_digits) - 1 - i]:
                matches += 1

        return matches / (len(ternary_digits) // 2) if len(ternary_digits) > 1 else 1.0

    def _analyze_dimensional_flow(self, ternary_digits: List[int]) -> Dict[str, str]:
        """
        Analyze how energy or information flows through the dimensions.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Dictionary with flow analysis information
        """
        if len(ternary_digits) <= 1:
            return {
                "pattern": "Singular",
                "description": "With only one dimension active, the pattern represents a single point of focus.",
            }

        # Identify transitions
        transitions = []
        for i in range(len(ternary_digits) - 1):
            if ternary_digits[i] != ternary_digits[i + 1]:
                transitions.append(i)

        # Analyze flow pattern
        if not transitions:
            return {
                "pattern": "Uniform",
                "description": "Energy moves consistently through the system with minimal transformation.",
            }

        # Calculate transition density
        transition_density = len(transitions) / (len(ternary_digits) - 1)

        # Analyze transition positions
        first_third = len(ternary_digits) // 3
        last_third = 2 * len(ternary_digits) // 3

        early_transitions = sum(1 for t in transitions if t < first_third)
        middle_transitions = sum(
            1 for t in transitions if first_third <= t < last_third
        )
        late_transitions = sum(1 for t in transitions if t >= last_third)

        # Determine flow pattern based on transition distribution
        if transition_density > 0.7:
            pattern = "Oscillating"
            description = "The pattern shows frequent alternation between states, creating a rhythmic, wave-like flow."
        elif (
            early_transitions > middle_transitions
            and early_transitions > late_transitions
        ):
            pattern = "Initiating"
            description = "The pattern establishes its dynamic early, then maintains a more consistent trajectory."
        elif (
            late_transitions > early_transitions
            and late_transitions > middle_transitions
        ):
            pattern = "Culminating"
            description = "The pattern maintains consistency before transforming significantly in its final stages."
        elif (
            middle_transitions > early_transitions
            and middle_transitions > late_transitions
        ):
            pattern = "Transformative"
            description = "The pattern pivots at its core, with relatively stable entry and exit points."
        else:
            pattern = "Balanced"
            description = (
                "Transitions are distributed relatively evenly throughout the pattern."
            )

        # Check for progressive flow (0->1->2 or 2->1->0)
        has_ascending = False
        has_descending = False

        for i in range(len(ternary_digits) - 2):
            if (
                ternary_digits[i] == 0
                and ternary_digits[i + 1] == 1
                and ternary_digits[i + 2] == 2
            ):
                has_ascending = True
            elif (
                ternary_digits[i] == 2
                and ternary_digits[i + 1] == 1
                and ternary_digits[i + 2] == 0
            ):
                has_descending = True

        if has_ascending and not has_descending:
            pattern = "Ascending"
            description += " There is a clear progression from potential to structure."
        elif has_descending and not has_ascending:
            pattern = "Descending"
            description += " There is a clear dissolution from structure to potential."
        elif has_ascending and has_descending:
            pattern = "Cyclical"
            description += (
                " The pattern shows both building up and breaking down phases."
            )

        return {
            "pattern": pattern,
            "description": description,
            "transition_count": len(transitions),
            "transition_density": f"{transition_density:.2f}",
        }

    def _identify_meta_patterns(self, ternary_digits: List[int]) -> Dict[str, str]:
        """
        Identify higher-order patterns across the entire number.

        Args:
            ternary_digits: The ternary digits to analyze

        Returns:
            Dictionary with meta-pattern information
        """
        # Check for various meta-patterns
        symmetry_score = self._calculate_symmetry_score(ternary_digits)

        # Check for repeating sub-patterns
        has_repeating_pattern = False
        repeating_pattern_length = 0

        # Check for patterns of length 2-4 (if the number is long enough)
        max_pattern_length = min(4, len(ternary_digits) // 2)
        for pattern_length in range(2, max_pattern_length + 1):
            for start in range(len(ternary_digits) - 2 * pattern_length + 1):
                pattern = ternary_digits[start : start + pattern_length]
                next_segment = ternary_digits[
                    start + pattern_length : start + 2 * pattern_length
                ]
                if pattern == next_segment:
                    has_repeating_pattern = True
                    repeating_pattern_length = pattern_length
                    break
            if has_repeating_pattern:
                break

        # Check for wave-like structure (alternating elements)
        has_wave_structure = False
        if len(ternary_digits) >= 4:
            alternating_count = 0
            for i in range(len(ternary_digits) - 2):
                if ternary_digits[i] == ternary_digits[i + 2]:
                    alternating_count += 1
            if alternating_count >= (len(ternary_digits) - 2) * 0.7:
                has_wave_structure = True

        # Determine the primary meta-pattern
        if symmetry_score > 0.8:
            pattern = "Reflective"
            description = (
                "The system mirrors itself, suggesting balance and self-reference."
            )
        elif has_repeating_pattern:
            pattern = "Fractal"
            description = f"The system shows self-similarity with a repeating pattern of length {repeating_pattern_length}."
        elif has_wave_structure:
            pattern = "Wave"
            description = "The system oscillates in a rhythmic manner, suggesting cyclical processes."
        else:
            pattern = "Unique"
            description = "The system follows a distinctive path without obvious meta-structural qualities."

        return {
            "pattern": pattern,
            "description": description,
            "symmetry_score": f"{symmetry_score:.2f}",
            "has_repeating_pattern": has_repeating_pattern,
            "has_wave_structure": has_wave_structure,
        }

    def _analyze_triad_integration(
        self,
        _ternary_digits: List[int],  # Not used directly but kept for API compatibility
        triad_analysis: Dict,
    ) -> Dict[str, str]:
        """
        Analyze how the three triads integrate with each other.

        Args:
            ternary_digits: The ternary digits to analyze
            triad_analysis: Analysis of the triads in the pattern

        Returns:
            Dictionary with triad integration information
        """
        # Extract triad information from the triad_analysis dictionary
        potential_triad = []
        process_triad = []
        emergence_triad = []

        # Extract the potential triad digits
        if triad_analysis.get("potential", {}).get("positions"):
            potential_positions = triad_analysis["potential"]["positions"]
            potential_triad = [pos.get("digit", 0) for pos in potential_positions]

        # Extract the process triad digits
        if triad_analysis.get("process", {}).get("positions"):
            process_positions = triad_analysis["process"]["positions"]
            process_triad = [pos.get("digit", 0) for pos in process_positions]

        # Extract the emergence triad digits
        if triad_analysis.get("emergence", {}).get("positions"):
            emergence_positions = triad_analysis["emergence"]["positions"]
            emergence_triad = [pos.get("digit", 0) for pos in emergence_positions]

        # Calculate similarity between triads
        potential_process_similarity = 0.0
        process_emergence_similarity = 0.0

        if potential_triad and process_triad:
            # Compare the triads element by element
            min_length = min(len(potential_triad), len(process_triad))
            matches = 0
            for i in range(min_length):
                if (
                    potential_triad[len(potential_triad) - 1 - i]
                    == process_triad[len(process_triad) - 1 - i]
                ):
                    matches += 1
            potential_process_similarity = matches / min_length

        if process_triad and emergence_triad:
            # Compare the triads element by element
            min_length = min(len(process_triad), len(emergence_triad))
            matches = 0
            for i in range(min_length):
                if (
                    process_triad[len(process_triad) - 1 - i]
                    == emergence_triad[len(emergence_triad) - 1 - i]
                ):
                    matches += 1
            process_emergence_similarity = matches / min_length

        # Determine integration patterns
        foundation_development = ""
        development_culmination = ""

        if potential_process_similarity > 0.66:
            foundation_development = "Coherent Development"
            foundation_description = "The process naturally extends from the foundation, maintaining core principles."
        elif potential_process_similarity > 0.33:
            foundation_development = "Evolving Development"
            foundation_description = (
                "The process builds upon the foundation while introducing new elements."
            )
        else:
            foundation_development = "Transformative Development"
            foundation_description = "The process represents a significant shift from the foundation, introducing new dynamics."

        if process_emergence_similarity > 0.66:
            development_culmination = "Consistent Culmination"
            culmination_description = "The emergence follows naturally from the developmental process, fulfilling its trajectory."
        elif process_emergence_similarity > 0.33:
            development_culmination = "Integrative Culmination"
            culmination_description = "The emergence builds upon the developmental process while transcending some of its limitations."
        else:
            development_culmination = "Transcendent Culmination"
            culmination_description = "The emergence represents a breakthrough beyond the developmental process, introducing novel qualities."

        # Create overall integration description
        if emergence_triad:
            overall_pattern = self._determine_overall_integration_pattern(
                potential_triad, process_triad, emergence_triad
            )
        else:
            overall_pattern = self._determine_partial_integration_pattern(
                potential_triad, process_triad
            )

        return {
            "foundation_development": {
                "pattern": foundation_development,
                "description": foundation_description,
                "similarity_score": f"{potential_process_similarity:.2f}",
            },
            "development_culmination": {
                "pattern": development_culmination,
                "description": culmination_description,
                "similarity_score": f"{process_emergence_similarity:.2f}",
            },
            "overall_pattern": overall_pattern,
        }

    def _determine_overall_integration_pattern(
        self,
        potential_triad: List[int],
        process_triad: List[int],
        emergence_triad: List[int],
    ) -> str:
        """
        Determine the overall integration pattern across all three triads.

        Args:
            potential_triad: The Potential triad digits
            process_triad: The Process triad digits
            emergence_triad: The Emergence triad digits

        Returns:
            Description of the overall integration pattern
        """
        # Count elements in each triad
        potential_counts = [potential_triad.count(i) for i in range(3)]
        process_counts = [process_triad.count(i) for i in range(3)]
        emergence_counts = [emergence_triad.count(i) for i in range(3)]

        # Determine dominant element in each triad
        potential_dominant = potential_counts.index(max(potential_counts))
        process_dominant = process_counts.index(max(process_counts))
        emergence_dominant = emergence_counts.index(max(emergence_counts))

        # Check for various patterns
        if potential_dominant == process_dominant == emergence_dominant:
            return f"Unified Pattern: The {self.ELEMENT_NAMES[potential_dominant]} element provides a consistent theme throughout all levels of manifestation."

        if (
            potential_dominant == 0
            and process_dominant == 1
            and emergence_dominant == 2
        ):
            return "Evolutionary Progression: The pattern shows a classic evolution from potential (Aperture) through transformation (Surge) to structure (Lattice)."

        if (
            potential_dominant == 2
            and process_dominant == 1
            and emergence_dominant == 0
        ):
            return "Dissolution Progression: The pattern shows a dissolution from structure (Lattice) through transformation (Surge) to potential (Aperture)."

        if (
            potential_dominant == process_dominant
            and process_dominant != emergence_dominant
        ):
            return f"Breakthrough Pattern: The {self.ELEMENT_NAMES[potential_dominant]} element dominates the foundation and development before giving way to {self.ELEMENT_NAMES[emergence_dominant]} energy at the culmination."

        if (
            potential_dominant != process_dominant
            and process_dominant == emergence_dominant
        ):
            return f"Transformative Foundation: The pattern begins with {self.ELEMENT_NAMES[potential_dominant]} energy before shifting to a consistent {self.ELEMENT_NAMES[process_dominant]} theme in its development and culmination."

        # Default case
        return f"Complex Integration: The pattern shows distinct qualities at each level - {self.ELEMENT_NAMES[potential_dominant]} foundation, {self.ELEMENT_NAMES[process_dominant]} development, and {self.ELEMENT_NAMES[emergence_dominant]} culmination."

    def _determine_partial_integration_pattern(
        self, potential_triad: List[int], process_triad: List[int]
    ) -> str:
        """
        Determine the integration pattern for a pattern with only Potential and Process triads.

        Args:
            potential_triad: The Potential triad digits
            process_triad: The Process triad digits

        Returns:
            Description of the integration pattern
        """
        # Count elements in each triad
        potential_counts = [potential_triad.count(i) for i in range(3)]
        process_counts = [process_triad.count(i) for i in range(3)]

        # Determine dominant element in each triad
        potential_dominant = potential_counts.index(max(potential_counts))
        process_dominant = process_counts.index(max(process_counts))

        # Check for various patterns
        if potential_dominant == process_dominant:
            return f"Consistent Development: The {self.ELEMENT_NAMES[potential_dominant]} element provides a unified theme across both foundation and development."

        if potential_dominant == 0 and process_dominant == 1:
            return "Activating Pattern: The pattern shows potential (Aperture) becoming activated through transformation (Surge)."

        if potential_dominant == 0 and process_dominant == 2:
            return "Structuring Pattern: The pattern shows potential (Aperture) becoming organized into structure (Lattice)."

        if potential_dominant == 1 and process_dominant == 2:
            return "Stabilizing Pattern: The pattern shows transformation (Surge) becoming consolidated into structure (Lattice)."

        if potential_dominant == 1 and process_dominant == 0:
            return "Opening Pattern: The pattern shows transformation (Surge) creating new potential (Aperture)."

        if potential_dominant == 2 and process_dominant == 0:
            return "Dissolving Pattern: The pattern shows structure (Lattice) opening into potential (Aperture)."

        if potential_dominant == 2 and process_dominant == 1:
            return "Mobilizing Pattern: The pattern shows structure (Lattice) becoming energized through transformation (Surge)."

        # Default case
        return f"Transitional Pattern: The pattern shifts from {self.ELEMENT_NAMES[potential_dominant]} foundation to {self.ELEMENT_NAMES[process_dominant]} development."

    def _synthesize_overall_interpretation(
        self,
        ternary_digits: List[int],
        pattern_identity: Dict[str, str],
        flow_analysis: Dict[str, str],
        triad_integration: Optional[Dict[str, Dict[str, str]]],
        meta_patterns: Dict[str, str],
    ) -> str:
        """
        Synthesize an overall interpretation that ties together all the analyses.

        Args:
            ternary_digits: The ternary digits to analyze
            pattern_identity: The pattern identity analysis
            flow_analysis: The dimensional flow analysis
            triad_integration: The triad integration analysis (if available)
            meta_patterns: The meta-pattern analysis

        Returns:
            A comprehensive synthesis paragraph
        """
        num_digits = len(ternary_digits)

        # Count elements
        element_counts = {0: 0, 1: 0, 2: 0}
        for digit in ternary_digits:
            element_counts[digit] += 1

        # No need to determine dominant element here as it's handled in _get_key_elements

        # Create synthesis based on pattern characteristics
        synthesis = f"This {num_digits}-digit ternary pattern represents a {pattern_identity['title'].lower()} "
        synthesis += f"with a {flow_analysis['pattern'].lower()} flow dynamic. At its core, it embodies "
        synthesis += f"the principle of {self._get_core_principle(pattern_identity, flow_analysis)}, "
        synthesis += f"which manifests through the interplay of {self._get_key_elements(element_counts, num_digits)}. "

        # Add dimensional progression insights
        synthesis += self._analyze_dimensional_progression(ternary_digits) + " "

        # Add triad context if available
        if num_digits >= 4 and triad_integration:
            if num_digits >= 7:
                synthesis += f"Spanning all three levels of manifestation, it reveals a {triad_integration['overall_pattern'].split(':')[0].lower()} "
                synthesis += "from foundation through development to culmination. "
                synthesis += (
                    self._analyze_complete_triad_journey(triad_integration) + " "
                )
            else:
                synthesis += f"Encompassing both foundation and development, it exhibits a {triad_integration['foundation_development']['pattern'].lower()} pattern "
                synthesis += (
                    f"where {self._analyze_partial_triad_journey(triad_integration)}. "
                )

        # Add meta-pattern information with deeper insight
        synthesis += f"The {meta_patterns['pattern'].lower()} meta-structure creates a system where "
        synthesis += (
            self._elaborate_meta_pattern_implications(meta_patterns, pattern_identity)
            + " "
        )

        # Add element balance information with deeper implications
        synthesis += (
            self._analyze_element_balance_implications(
                element_counts, num_digits, pattern_identity
            )
            + " "
        )

        # Add transformational potential
        synthesis += (
            self._analyze_transformational_potential(
                ternary_digits, pattern_identity, flow_analysis
            )
            + " "
        )

        # Add archetypal resonance
        synthesis += (
            self._identify_archetypal_resonance(
                ternary_digits, pattern_identity, flow_analysis, meta_patterns
            )
            + " "
        )

        # Add final insight based on primary trait with practical applications
        synthesis += self._provide_practical_applications(
            pattern_identity, flow_analysis, element_counts
        )

        return synthesis

    def _get_core_principle(
        self, pattern_identity: Dict[str, str], flow_analysis: Dict[str, str]
    ) -> str:
        """Identify the core principle embodied by the pattern."""
        if pattern_identity["primary_trait"] == "Stable" and flow_analysis[
            "pattern"
        ] in ["Uniform", "Balanced"]:
            return "structured harmony"
        elif pattern_identity["primary_trait"] == "Stable" and flow_analysis[
            "pattern"
        ] in ["Oscillating", "Transformative"]:
            return "dynamic equilibrium"
        elif pattern_identity["primary_trait"] == "Dynamic" and flow_analysis[
            "pattern"
        ] in ["Ascending", "Initiating"]:
            return "progressive evolution"
        elif pattern_identity["primary_trait"] == "Dynamic" and flow_analysis[
            "pattern"
        ] in ["Descending", "Culminating"]:
            return "transformative dissolution"
        elif (
            pattern_identity["primary_trait"] == "Dynamic"
            and flow_analysis["pattern"] == "Oscillating"
        ):
            return "rhythmic transformation"
        elif (
            pattern_identity["primary_trait"] == "Complex"
            and flow_analysis["pattern"] == "Reflective"
        ):
            return "self-referential integration"
        elif (
            pattern_identity["primary_trait"] == "Complex"
            and flow_analysis["pattern"] == "Fractal"
        ):
            return "recursive complexity"
        else:
            return "multidimensional coherence"

    def _get_key_elements(self, element_counts: Dict[int, int], num_digits: int) -> str:
        """Identify the key elements and their relationship."""
        elements = []
        threshold = num_digits * 0.25  # Elements that appear at least 25% of the time

        for digit, count in element_counts.items():
            if count >= threshold:
                elements.append(
                    f"{self.ELEMENT_QUALITIES[digit]['energy'].lower()} {self.ELEMENT_NAMES[digit].lower()}"
                )

        if len(elements) == 1:
            return elements[0]
        elif len(elements) == 2:
            return f"{elements[0]} and {elements[1]}"
        elif len(elements) == 3:
            return f"{elements[0]}, {elements[1]}, and {elements[2]}"
        else:
            return "balanced elemental forces"

    def _analyze_dimensional_progression(self, ternary_digits: List[int]) -> str:
        """Analyze how the pattern progresses through dimensions."""
        if len(ternary_digits) <= 3:
            return "The pattern operates primarily at the foundational level, establishing core qualities without extending into process or emergence."

        # Check for progression from 0→1→2
        ascending = True
        for i in range(len(ternary_digits) - 2):
            if not (
                ternary_digits[i] <= ternary_digits[i + 1] <= ternary_digits[i + 2]
            ):
                ascending = False
                break

        # Check for progression from 2→1→0
        descending = True
        for i in range(len(ternary_digits) - 2):
            if not (
                ternary_digits[i] >= ternary_digits[i + 1] >= ternary_digits[i + 2]
            ):
                descending = False
                break

        # Check for alternating pattern
        alternating = True
        for i in range(len(ternary_digits) - 2):
            if not (ternary_digits[i] == ternary_digits[i + 2]):
                alternating = False
                break

        if ascending and len(ternary_digits) >= 5:
            return "The dimensional progression reveals a clear evolutionary trajectory, moving from potential through activation to structured manifestation."
        elif descending and len(ternary_digits) >= 5:
            return "The dimensional progression shows a dissolution pattern, transitioning from structure through transformation to renewed potential."
        elif alternating and len(ternary_digits) >= 5:
            return "The dimensional progression creates a rhythmic oscillation between states, establishing a pulsating flow through the system."
        else:
            # Analyze first and last digits
            first = ternary_digits[0]
            last = ternary_digits[-1]

            if first == 0 and last == 2:
                return "The pattern begins with open potential and culminates in structured form, suggesting a manifestation process."
            elif first == 2 and last == 0:
                return "The pattern begins with established structure and opens into new potential, suggesting a release or renewal process."
            elif first == 1 and last == 1:
                return "The pattern begins and ends with transformative energy, creating a dynamic cycle that continuously renews itself."
            elif first == last:
                return f"The pattern begins and ends with {self.ELEMENT_NAMES[first].lower()} energy, creating a coherent frame that contains the internal dynamics."
            else:
                return "The dimensional progression weaves a complex tapestry of interactions that defies simple linear interpretation."

    def _analyze_complete_triad_journey(self, triad_integration: Dict) -> str:
        """Analyze the complete journey through all three triads."""
        foundation_dev = triad_integration["foundation_development"]["pattern"]
        dev_culmination = triad_integration["development_culmination"]["pattern"]

        if (
            foundation_dev == "Coherent Development"
            and dev_culmination == "Consistent Culmination"
        ):
            return "This creates a harmonious progression where each level builds naturally upon the previous, resulting in a seamless evolution from seed to full manifestation."
        elif (
            foundation_dev == "Coherent Development"
            and dev_culmination == "Transcendent Culmination"
        ):
            return "While the process develops naturally from the foundation, the emergence represents a quantum leap that transcends the established patterns, creating breakthrough potential."
        elif (
            foundation_dev == "Transformative Development"
            and dev_culmination == "Consistent Culmination"
        ):
            return "The dramatic shift between foundation and process eventually stabilizes into a coherent culmination, suggesting initial disruption that ultimately finds resolution."
        elif (
            foundation_dev == "Transformative Development"
            and dev_culmination == "Transcendent Culmination"
        ):
            return "Each transition represents a significant transformation, creating a pattern of continuous reinvention that culminates in radical emergence."
        else:
            return "The journey through the triads reveals a nuanced interplay of continuity and transformation, creating a rich developmental narrative."

    def _analyze_partial_triad_journey(self, triad_integration: Dict) -> str:
        """Analyze the journey through the Potential and Process triads."""
        pattern = triad_integration["foundation_development"]["pattern"]

        if pattern == "Coherent Development":
            return "the process dimensions naturally extend and elaborate the foundational qualities"
        elif pattern == "Evolving Development":
            return "the process dimensions introduce new dynamics while maintaining connection to the foundation"
        elif pattern == "Transformative Development":
            return "the process dimensions represent a significant shift from the foundational pattern, introducing novel dynamics"
        else:
            return "the relationship between foundation and process creates a dynamic interplay of continuity and change"

    def _elaborate_meta_pattern_implications(
        self, meta_patterns: Dict[str, str], pattern_identity: Dict[str, str]
    ) -> str:
        """Elaborate on the implications of the meta-pattern."""
        pattern = meta_patterns["pattern"]
        primary_trait = pattern_identity["primary_trait"]

        if pattern == "Reflective":
            if primary_trait == "Stable":
                return "inner and outer aspects mirror each other, creating a self-reinforcing structure that maintains integrity through symmetrical balance."
            elif primary_trait == "Dynamic":
                return "transformations occur in complementary pairs, creating a dynamic equilibrium where changes in one area are balanced by corresponding shifts elsewhere."
            else:
                return "complexity is organized through self-similar relationships, creating a coherent whole despite intricate internal dynamics."
        elif pattern == "Fractal":
            if primary_trait == "Stable":
                return "stability is achieved through nested patterns that maintain consistent principles across different scales of organization."
            elif primary_trait == "Dynamic":
                return "transformation follows recurring patterns that manifest at multiple levels, creating coherent change across the system."
            else:
                return "complexity emerges from simple recursive principles, generating rich diversity within a unified framework."
        elif pattern == "Wave":
            if primary_trait == "Stable":
                return "stability is maintained through rhythmic oscillations that balance opposing forces in a dynamic equilibrium."
            elif primary_trait == "Dynamic":
                return "transformation occurs in cyclical phases, creating a pulsating evolution that continuously renews the system."
            else:
                return "complexity is orchestrated through interwoven rhythms that create harmonious relationships between diverse elements."
        else:  # Unique
            if primary_trait == "Stable":
                return "stability emerges from a distinctive configuration that creates its own internal logic and coherence."
            elif primary_trait == "Dynamic":
                return "transformation follows a unique trajectory that defies conventional patterns, creating novel possibilities."
            else:
                return "complexity manifests through an original synthesis that integrates diverse elements in unprecedented ways."

    def _analyze_element_balance_implications(
        self,
        element_counts: Dict[int, int],
        num_digits: int,
        pattern_identity: Dict[str, str],
    ) -> str:
        """Analyze the implications of the element balance."""
        max_count = max(element_counts.values())
        dominant_element = max(element_counts.items(), key=lambda x: x[1])[0]

        if max_count > num_digits * 0.6:  # Strong dominance
            if dominant_element == 0:  # Aperture dominant
                return "The pronounced emphasis on Aperture creates a system rich in potential and receptivity, capable of accommodating diverse possibilities but potentially lacking the structure or dynamism to fully actualize them."
            elif dominant_element == 1:  # Surge dominant
                return "The strong presence of Surge creates a highly transformative system characterized by continuous change and adaptation, though it may struggle to maintain stability or establish enduring patterns."
            else:  # Lattice dominant
                return "The predominance of Lattice creates a highly structured system with clear organization and stability, though it may resist necessary change or lack the flexibility to adapt to new conditions."
        elif max_count > num_digits * 0.4:  # Moderate dominance
            secondary_element = sorted(
                element_counts.items(), key=lambda x: x[1], reverse=True
            )[1][0]

            if dominant_element == 0 and secondary_element == 1:
                return "The balance between Aperture and Surge creates a system that maintains openness while engaging in dynamic transformation, capable of continuous renewal without losing its essential flexibility."
            elif dominant_element == 0 and secondary_element == 2:
                return "The interplay between Aperture and Lattice creates a system where structure emerges from potential, establishing patterns that remain open to further development and refinement."
            elif dominant_element == 1 and secondary_element == 0:
                return "The combination of Surge and Aperture creates a system where transformation continuously opens new possibilities, maintaining dynamism through cycles of release and renewal."
            elif dominant_element == 1 and secondary_element == 2:
                return "The balance between Surge and Lattice creates a system where dynamic change occurs within structured parameters, allowing for evolution that maintains coherence and continuity."
            elif dominant_element == 2 and secondary_element == 0:
                return "The interplay between Lattice and Aperture creates a system where structure contains openings for new potential, balancing stability with the capacity for renewal and adaptation."
            elif dominant_element == 2 and secondary_element == 1:
                return "The combination of Lattice and Surge creates a system where established structures undergo controlled transformation, enabling evolution without compromising essential organization."
        else:  # Balanced
            return "The balanced distribution of elements creates a highly integrated system that harmonizes stability, transformation, and potential, capable of maintaining integrity while evolving and remaining open to new possibilities."

    def _analyze_transformational_potential(
        self,
        ternary_digits: List[int],
        pattern_identity: Dict[str, str],
        flow_analysis: Dict[str, str],
    ) -> str:
        """Analyze the transformational potential of the pattern."""
        # Check for specific transformational indicators
        has_aperture_surge_sequence = False
        has_surge_lattice_sequence = False
        has_lattice_aperture_sequence = False

        for i in range(len(ternary_digits) - 1):
            if ternary_digits[i] == 0 and ternary_digits[i + 1] == 1:
                has_aperture_surge_sequence = True
            elif ternary_digits[i] == 1 and ternary_digits[i + 1] == 2:
                has_surge_lattice_sequence = True
            elif ternary_digits[i] == 2 and ternary_digits[i + 1] == 0:
                has_lattice_aperture_sequence = True

        # Analyze based on transformational indicators and pattern characteristics
        if pattern_identity["primary_trait"] == "Dynamic" or flow_analysis[
            "pattern"
        ] in ["Transformative", "Oscillating", "Ascending", "Descending"]:
            if has_aperture_surge_sequence and has_surge_lattice_sequence:
                return "The pattern shows strong evolutionary potential, capable of activating latent possibilities and developing them into coherent structures."
            elif has_lattice_aperture_sequence and has_aperture_surge_sequence:
                return "The pattern demonstrates regenerative potential, able to dissolve existing structures into new possibilities that can then be dynamically developed."
            elif has_surge_lattice_sequence and has_lattice_aperture_sequence:
                return "The pattern exhibits cyclical transformation potential, moving through phases of consolidation and release that continuously renew the system."
            else:
                return "The pattern contains significant transformational potential that manifests through its distinctive flow dynamics and elemental interactions."
        elif pattern_identity["primary_trait"] == "Stable":
            if (
                has_aperture_surge_sequence
                or has_surge_lattice_sequence
                or has_lattice_aperture_sequence
            ):
                return "Despite its overall stability, the pattern contains specific transition points that offer potential for controlled, strategic transformation when activated."
            else:
                return "The pattern's transformational potential lies in its capacity to maintain integrity through changing conditions, adapting through subtle reconfiguration rather than dramatic change."
        else:  # Complex
            return "The pattern's transformational potential emerges from its intricate interrelationships, which can generate emergent properties and novel configurations through non-linear interactions."

    def _identify_archetypal_resonance(
        self,
        ternary_digits: List[int],
        pattern_identity: Dict[str, str],
        flow_analysis: Dict[str, str],
        meta_patterns: Dict[str, str],
    ) -> str:
        """Identify archetypal patterns that resonate with this ternary configuration."""
        # Identify key characteristics for archetypal matching
        is_cyclical = flow_analysis["pattern"] in ["Oscillating", "Cyclical"]
        is_progressive = flow_analysis["pattern"] in ["Ascending", "Initiating"]
        is_dissolving = flow_analysis["pattern"] in ["Descending", "Culminating"]
        is_reflective = meta_patterns["pattern"] == "Reflective"
        is_fractal = meta_patterns["pattern"] == "Fractal"

        # Count elements for additional context
        aperture_count = ternary_digits.count(0)
        surge_count = ternary_digits.count(1)
        lattice_count = ternary_digits.count(2)

        # Match to archetypal patterns
        if is_cyclical and is_reflective:
            return "This pattern resonates with the archetypal cycle of renewal, embodying the principle of death and rebirth that maintains continuity through transformation."
        elif is_progressive and lattice_count > surge_count > aperture_count:
            return "This pattern resonates with the archetypal journey of manifestation, embodying the principle of potential becoming form through progressive development."
        elif is_dissolving and aperture_count > surge_count > lattice_count:
            return "This pattern resonates with the archetypal process of dissolution, embodying the principle of release that allows fixed forms to return to a state of renewed potential."
        elif is_reflective and aperture_count == lattice_count:
            return "This pattern resonates with the archetypal principle of polarity, embodying the complementary relationship between form and emptiness, structure and potential."
        elif is_fractal and surge_count > (aperture_count + lattice_count):
            return "This pattern resonates with the archetypal principle of organic growth, embodying the self-similar patterns of development seen throughout natural systems."
        elif pattern_identity["primary_trait"] == "Stable" and lattice_count > (
            aperture_count + surge_count
        ):
            return "This pattern resonates with the archetypal principle of cosmic order, embodying the fundamental structures that provide coherence and meaning to experience."
        elif pattern_identity["primary_trait"] == "Dynamic" and surge_count > (
            aperture_count + lattice_count
        ):
            return "This pattern resonates with the archetypal principle of creative transformation, embodying the dynamic forces that drive evolution and innovation."
        elif (
            pattern_identity["primary_trait"] == "Complex"
            and min(aperture_count, surge_count, lattice_count)
            >= len(ternary_digits) * 0.2
        ):
            return "This pattern resonates with the archetypal principle of integration, embodying the harmonious relationship between diverse elements within a coherent whole."
        else:
            return "This pattern resonates with multiple archetypal principles, creating a unique synthesis that defies simple categorization."

    def _provide_practical_applications(
        self,
        pattern_identity: Dict[str, str],
        flow_analysis: Dict[str, str],
        element_counts: Dict[int, int],
    ) -> str:
        """Provide practical applications based on the pattern's characteristics."""
        applications = []

        # Applications based on primary trait
        if pattern_identity["primary_trait"] == "Stable":
            applications.append("establishing enduring frameworks")
            applications.append("maintaining consistency through changing conditions")
            applications.append("creating reliable systems")
        elif pattern_identity["primary_trait"] == "Dynamic":
            applications.append("facilitating transformation processes")
            applications.append("navigating periods of significant change")
            applications.append("catalyzing innovation and evolution")
        else:  # Complex
            applications.append("integrating diverse elements into coherent wholes")
            applications.append("addressing multifaceted challenges")
            applications.append("developing nuanced understanding of complex systems")

        # Applications based on flow pattern
        if flow_analysis["pattern"] in ["Oscillating", "Cyclical"]:
            applications.append("managing cyclical processes")
            applications.append("working with natural rhythms")
        elif flow_analysis["pattern"] in ["Ascending", "Initiating"]:
            applications.append("supporting developmental processes")
            applications.append("building progressive momentum")
        elif flow_analysis["pattern"] in ["Descending", "Culminating"]:
            applications.append("facilitating release and completion")
            applications.append("managing transitions to new states")

        # Applications based on element balance
        dominant_element = max(element_counts.items(), key=lambda x: x[1])[0]
        if (
            dominant_element == 0
            and element_counts[0] > sum(element_counts.values()) * 0.4
        ):
            applications.append("creating space for new possibilities")
            applications.append("maintaining receptivity to emerging potentials")
        elif (
            dominant_element == 1
            and element_counts[1] > sum(element_counts.values()) * 0.4
        ):
            applications.append("driving active change processes")
            applications.append("energizing stagnant situations")
        elif (
            dominant_element == 2
            and element_counts[2] > sum(element_counts.values()) * 0.4
        ):
            applications.append("establishing clear structures and boundaries")
            applications.append("crystallizing vague concepts into defined forms")

        # Select and format applications
        selected_applications = applications[:4]  # Limit to 4 applications

        if len(selected_applications) == 1:
            return f"This pattern would be particularly effective for {selected_applications[0]}."
        else:
            formatted_apps = (
                ", ".join(selected_applications[:-1])
                + ", and "
                + selected_applications[-1]
            )
            return f"This pattern would be particularly effective for {formatted_apps}."
