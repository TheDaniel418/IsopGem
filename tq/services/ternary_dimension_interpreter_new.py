"""
Purpose: Provides interpretation services for 6-digit ternary hexagrams using the new structured model.

This file is the source of truth for the new Kamea hexagram interpretive system.

Key features:
- Only accepts 6-digit ternary numbers (hexagrams)
- Outputs a structured interpretation with all required fields
- Implements bigram, dimensional, pattern, and relationship analysis
- Synthesizes a divinatory meaning from all elements

Dependencies:
- typing: For type annotations
- tq.utils.ternary_converter: For ternary/decimal conversions
- tq.utils.potential_triad_definitions: For triad meanings (if needed)

"""
from typing import Dict, List, Tuple

from tq.utils.ternary_converter import ternary_to_decimal

# Placeholder for DIMENSIONAL_INTERPRETATIONS (should be imported or defined elsewhere)
DIMENSIONAL_INTERPRETATIONS = {
    1: {0: "Seed: Openness", 1: "Seed: Surge", 2: "Seed: Structure"},
    2: {0: "Resonance: Openness", 1: "Resonance: Surge", 2: "Resonance: Structure"},
    3: {0: "Echo: Openness", 1: "Echo: Surge", 2: "Echo: Structure"},
    4: {0: "Weave: Openness", 1: "Weave: Surge", 2: "Weave: Structure"},
    5: {0: "Pulse: Openness", 1: "Pulse: Surge", 2: "Pulse: Structure"},
    6: {0: "Flow: Openness", 1: "Flow: Surge", 2: "Flow: Structure"},
}

FIRST_BIGRAM_MEANINGS = {
    0: {
        "name": "Void Gateway",
        "interpretation": "Openness at both beginning and end creates a channel of pure potential. There is no fixed start or destination, allowing for infinite adaptability and possibility. Represents journeys that remain undefined, explorative processes, and the freedom of unmapped territories.",
        "greek": "Κενή Πύλη",
        "transliteration": "Kení Pýli",
    },
    1: {
        "name": "Emergent Direction",
        "interpretation": "Beginnings rooted in openness develop into defined movement. Represents spontaneous inspiration that finds purpose, undefined potential that discovers direction, or the crystallization of wandering into purposeful journey.",
        "greek": "Αναδυόμενη Κατεύθυνση",
        "transliteration": "Anadyómeni Kateýthynsi",
    },
    2: {
        "name": "Emergent Structure",
        "interpretation": "Open beginnings that evolve into defined form. Represents natural organization that arises from chaos, intuitive processes that create lasting patterns, or the way potential congeals into tangible frameworks without forced intervention.",
        "greek": "Αναδυόμενη Δομή",
        "transliteration": "Anadyómeni Domí",
    },
    3: {
        "name": "Active Opening",
        "interpretation": "Directed beginnings that lead to open-ended results. Represents initiated journeys with unpredictable outcomes, purposeful action that creates space, or the way decisive starts can lead to expansive possibilities.",
        "greek": "Ενεργό Άνοιγμα",
        "transliteration": "Energó Ánoigma",
    },
    4: {
        "name": "Dynamic Channel",
        "interpretation": "Active force at both beginning and end creates a direct pipeline of transformation. Represents purposeful journeys with clear direction, processes that maintain momentum throughout, or situations where initiative directly creates change.",
        "greek": "Δυναμικό Κανάλι",
        "transliteration": "Dynamikó Kanáli",
    },
    5: {
        "name": "Crystallizing Force",
        "interpretation": "Active beginnings that coalesce into stable form. Represents creative impulses that build lasting structures, pioneers who establish traditions, or the journey from exploration to establishment.",
        "greek": "Κρυσταλλωτική Δύναμη",
        "transliteration": "Krystallotikí Dýnami",
    },
    6: {
        "name": "Dissolving Structure",
        "interpretation": "Structured beginnings that open into possibility. Represents systems that evolve toward greater freedom, the relaxing of rigid frameworks, or how boundaries can become permeable portals.",
        "greek": "Διαλυόμενη Δομή",
        "transliteration": "Dialyómeni Domí",
    },
    7: {
        "name": "Activating Structure",
        "interpretation": "Structured beginnings that generate dynamic movement. Represents foundations that enable action, traditions that inspire innovation, or the way stability can become a platform for change.",
        "greek": "Ενεργοποιητική Δομή",
        "transliteration": "Energopoiitikí Domí",
    },
    8: {
        "name": "Formed Pathway",
        "interpretation": "Structure at both beginning and end creates a stable, defined channel. Represents established processes with predictable outcomes, traditional paths with clear protocols, or situations where order maintains itself through consistent patterns.",
        "greek": "Διαμορφωμένο Μονοπάτι",
        "transliteration": "Diamorfomeno Monopáti",
    },
}

SECOND_BIGRAM_MEANINGS = {
    0: {
        "name": "Open Resonance Chamber",
        "interpretation": "Openness in both internal state and timing creates a field of pure potential. Represents heightened receptivity to synchronicity, the ability to adapt to any rhythm, or a complete lack of attachment to predetermined patterns.",
        "greek": "Θάλαμος Ανοιχτού Συντονισμού",
        "transliteration": "Thálamos Anoichtoú Syntonismoú",
    },
    1: {
        "name": "Receptive Impulse",
        "interpretation": "Inner openness that manifests through decisive timing. Represents intuitive alignment with the right moment, the capacity to sense when to act without preconception, or internal stillness that knows precisely when to move.",
        "greek": "Δεκτική Παρόρμιση",
        "transliteration": "Dektikí Parórmisi",
    },
    2: {
        "name": "Receptive Rhythm",
        "interpretation": "Inner openness contained within structured timing. Represents meditation within routine, the way stillness can find expression through regular patterns, or adaptive inner states within consistent frameworks.",
        "greek": "Δεκτικός Ρυθμός",
        "transliteration": "Dektikós Rythmós",
    },
    3: {
        "name": "Dynamic Receptivity",
        "interpretation": "Inner activity coupled with open timing. Represents passionate exploration without deadlines, enthusiastic energy that remains flexible in its expression, or transformative states that unfold according to their own natural timing.",
        "greek": "Δυναμική Δεκτικότητα",
        "transliteration": "Dynamikí Dektikótita",
    },
    4: {
        "name": "Amplifying Resonance",
        "interpretation": "Dynamic energy in both internal state and timing creates self-reinforcing momentum. Represents accelerating processes, snowball effects, or situations where energy builds upon itself through synchronized action.",
        "greek": "Ενισχυτικός Συντονισμός",
        "transliteration": "Enischytikós Syntonismós",
    },
    5: {
        "name": "Contained Dynamism",
        "interpretation": "Inner activity expressed through structured timing. Represents creativity within constraints, passionate expression channeled through discipline, or transformative energy released at strategic intervals.",
        "greek": "Περιορισμένος Δυναμισμός",
        "transliteration": "Periorisménos Dynamismós",
    },
    6: {
        "name": "Structured Openness",
        "interpretation": "Inner structure paired with receptive timing. Represents stable systems that remain adaptable in their expression, clear internal frameworks with flexible application, or traditions that accommodate spontaneity.",
        "greek": "Δομημένη Ανοιχτότητα",
        "transliteration": "Domiméni Anoichtótita",
    },
    7: {
        "name": "Structured Impulse",
        "interpretation": "Inner structure that expresses through decisive timing. Represents calculated action at precise moments, the way expertise enables perfect timing, or how established knowledge can inform when to make critical moves.",
        "greek": "Δομημένη Παρόρμηση",
        "transliteration": "Domiméni Parórmisi",
    },
    8: {
        "name": "Reinforced Pattern",
        "interpretation": "Structure in both internal state and timing creates self-reinforcing stability. Represents traditions that preserve themselves through regular practice, deeply established rhythms that resist disruption, or situations where order maintains itself at multiple levels.",
        "greek": "Ενισχυμένο Μοτίβο",
        "transliteration": "Enischyméno Motívo",
    },
}

THIRD_BIGRAM_MEANINGS = {
    0: {
        "name": "Boundless Field",
        "interpretation": "Openness in both expression and connection creates a field of unlimited possibility. Represents environments where anything can emerge and connect in any way, undefined spaces where new patterns can spontaneously form, or the primordial void from which all networks may arise.",
        "greek": "Απεριόριστο Πεδίο",
        "transliteration": "Aperiórito Pedío",
    },
    1: {
        "name": "Formless Weaving",
        "interpretation": "Open expression that creates dynamic connections. Represents influence that spreads organically through active engagement, potential that manifests through relationship, or the way undefined ideas can catalyze vibrant networks.",
        "greek": "Άμορφη Πλέξη",
        "transliteration": "Ámorfi Pléxi",
    },
    2: {
        "name": "Emerging Pattern",
        "interpretation": "Open expression that generates structured networks. Represents spontaneous order emerging from chaos, the way undefined potential can self-organize into coherent systems, or natural evolution from formlessness to pattern.",
        "greek": "Αναδυόμενο Μοτίβο",
        "transliteration": "Anadyómeno Motívo",
    },
    3: {
        "name": "Dynamic Expansion",
        "interpretation": "Active expression within open networks. Represents energetic broadcast into undefined territories, transformative influence spreading without boundaries, or the way directed energy can explore unlimited connection possibilities.",
        "greek": "Δυναμική Επέκταση",
        "transliteration": "Dynamikí Epéktasi",
    },
    4: {
        "name": "Propagating Wave",
        "interpretation": "Dynamic energy in both expression and connection creates amplifying influence. Represents viral spread, catalytic effects in actively receptive environments, or transformative messages that gain momentum as they travel.",
        "greek": "Διαδιδόμενο Κύμα",
        "transliteration": "Diadidómeno Kýma",
    },
    5: {
        "name": "Channeled Influence",
        "interpretation": "Active expression flowing through structured networks. Represents revolutionary ideas spreading through established channels, transformative energy directed along defined pathways, or how change can be efficiently distributed through existing systems.",
        "greek": "Διοχετευμένη Επιρροή",
        "transliteration": "Diocheteumeni Epirroí",
    },
    6: {
        "name": "Structured Emergence",
        "interpretation": "Defined expression opening into unlimited connection. Represents clear messages that invite unpredictable responses, established patterns generating new possibilities, or the way order can create space for spontaneity.",
        "greek": "Δομημένη Ανάδυση",
        "transliteration": "Domiméni Anádysi",
    },
    7: {
        "name": "Patterned Activation",
        "interpretation": "Structured expression creating dynamic networks. Represents established traditions catalyzing new movements, the way clear forms can stimulate active engagement, or how defined boundaries can generate energetic response.",
        "greek": "Μοτιβική Ενεργοποίηση",
        "transliteration": "Motivikí Energopoíisi",
    },
    8: {
        "name": "Crystallized Network",
        "interpretation": "Structure in both expression and connection creates self-reinforcing patterns. Represents established systems that replicate themselves, tightly integrated networks that maintain coherence, or situations where order propagates order through consistent relationship.",
        "greek": "Κρυσταλλωμένο Δίκτυο",
        "transliteration": "Krystallomeno Díktyo",
    },
}

# Hellenic Ternary Oracle: Hierophants (The Nine Primes)
# Maps each prime ditrune to its Pattern Archetype name, Greek name, and description
HIEROPHANTS = {
    "000000": {
        "name": "The Void",
        "greek": "Κενόν (Kenon)",
        "ternary": "000000",
        "description": "The absolute emptiness that contains all possibility. The unmanifest source; pure potential before differentiation.",
    },
    "010101": {
        "name": "The Oscillator",
        "greek": "Παλμός (Palmos)",
        "ternary": "010101",
        "description": "Rhythmic movement between potential and manifestation. The power of transition; regular alternation between states.",
    },
    "020202": {
        "name": "The Enclosure",
        "greek": "Περίβολος (Peribolos)",
        "ternary": "020202",
        "description": "Structured openness, container for potential. Sacred boundaries; the creation of defined space for possibility.",
    },
    "101010": {
        "name": "The Liberator",
        "greek": "Ἐλευθερωτής (Eleutherotes)",
        "ternary": "101010",
        "description": "Dynamic liberation, transformative unbinding. Action that creates new openings; the breaking of limitations.",
    },
    "111111": {
        "name": "The Dynamo",
        "greek": "Δύναμις (Dynamis)",
        "ternary": "111111",
        "description": "Unbroken dynamic force, continuous transformation. The power of pure action; perpetual movement and change.",
    },
    "121212": {
        "name": "The Weaver",
        "greek": "Ὑφαντής (Hyphantes)",
        "ternary": "121212",
        "description": "Perfect alternation between expression and form. The cosmic dance of becoming; integration of different patterns.",
    },
    "202020": {
        "name": "The Foundation",
        "greek": "Θεμέλιον (Themelion)",
        "ternary": "202020",
        "description": "Formed potential, structured matrix of emergence. Generative container; the stable ground from which forms arise.",
    },
    "212121": {
        "name": "The Harmonizer",
        "greek": "Ἁρμοστής (Harmostes)",
        "ternary": "212121",
        "description": "Structured dynamism, contained transformation. Perfection through limitation; balanced expression of change.",
    },
    "222222": {
        "name": "The Matrix",
        "greek": "Πλέγμα (Plegma)",
        "ternary": "222222",
        "description": "Ultimate structure, perfect pattern. The absolute crystallization of order; complete structural integrity.",
    },
}

# Hellenic Ternary Oracle: Acolytes (Eight Channels Per Family)
# List of Acolyte titles, Greek spellings, and their functions/natures
ACOLYTE_TITLES = [
    {
        "position": 1,
        "title": "Mystagogos",
        "greek": "Μυσταγωγός",
        "function": "The Initiator",
        "nature": "Introduces seekers to the mysteries of the Hierophant",
    },
    {
        "position": 2,
        "title": "Daidouchos",
        "greek": "Δᾳδοῦχος",
        "function": "The Torch-Bearer",
        "nature": "Illuminates the path toward the Hierophant's wisdom",
    },
    {
        "position": 3,
        "title": "Hydranos",
        "greek": "Ὑδρανός",
        "function": "The Purifier",
        "nature": "Prepares vessels to receive the Hierophant's essence",
    },
    {
        "position": 4,
        "title": "Hierophylax",
        "greek": "Ἱεροφύλαξ",
        "function": "The Guardian",
        "nature": "Protects and preserves the Hierophant's teachings",
    },
    {
        "position": 5,
        "title": "Prophetes",
        "greek": "Προφήτης",
        "function": "The Prophet",
        "nature": "Speaks the Hierophant's truth in the world",
    },
    {
        "position": 6,
        "title": "Thyrsoforis",
        "greek": "Θυρσοφόρις",
        "function": "The Wand-Bearer",
        "nature": "Channels and directs the Hierophant's power",
    },
    {
        "position": 7,
        "title": "Hierodoulos",
        "greek": "Ἱερόδουλος",
        "function": "The Sacred Servant",
        "nature": "Embodies the Hierophant's work in practical service",
    },
    {
        "position": 8,
        "title": "Telesphoros",
        "greek": "Τελεσφόρος",
        "function": "The Completer",
        "nature": "Brings the Hierophant's influence to fulfillment",
    },
]

# Define the ACOLYTES dictionary with sample data
# In a real implementation, this would contain all 72 Acolytes (8 per family × 9 families)
ACOLYTES = {
    # Family 0 (The Void) Acolytes
    "0_1": {
        "ternary": "000001",
        "title": "Mystagogos of the Void",
        "greek": "Μυσταγωγός του Κενόν",
        "function": "The Initiator of Emptiness",
        "family": 0,
    },
    "0_2": {
        "ternary": "000010",
        "title": "Daidouchos of the Void",
        "greek": "Δᾳδοῦχος του Κενόν",
        "function": "The Torch-Bearer of Emptiness",
        "family": 0,
    },
    # Family 1 (The Dynamo) Acolytes
    "1_1": {
        "ternary": "111101",
        "title": "Mystagogos of the Dynamo",
        "greek": "Μυσταγωγός του Δύναμις",
        "function": "The Initiator of Transformation",
        "family": 1,
    },
    "1_2": {
        "ternary": "111110",
        "title": "Daidouchos of the Dynamo",
        "greek": "Δᾳδοῦχος του Δύναμις",
        "function": "The Torch-Bearer of Transformation",
        "family": 1,
    },
    # Family 2 (The Matrix) Acolytes
    "2_1": {
        "ternary": "222201",
        "title": "Mystagogos of the Matrix",
        "greek": "Μυσταγωγός του Πλέγμα",
        "function": "The Initiator of Structure",
        "family": 2,
    },
    "2_2": {
        "ternary": "222210",
        "title": "Daidouchos of the Matrix",
        "greek": "Δᾳδοῦχος του Πλέγμα",
        "function": "The Torch-Bearer of Structure",
        "family": 2,
    },
    # Add more Acolytes for each family as needed
    # This is just a minimal set for the Temple Position Analyzer to work
}

# Refined meanings for each line (position 1-6) and element (0,1,2)
REFINED_LINE_MEANINGS = {
    1: {
        0: {
            "name": "The Void Seed",
            "interpretation": "The beginning emerges from absolute potential, unmarked by preconception or definition. A foundation that offers infinite possibility rather than predetermined direction. Indicates journeys that begin with questioning, openness, and the courage to enter the unknown. The virtue of emptiness as starting point; the path begins with clearing and receptivity.",
            "greek": "Κενός Σπόρος",
            "transliteration": "Kenós Spóros",
        },
        1: {
            "name": "The Igniting Spark",
            "interpretation": "The beginning bursts forth with purposeful energy and catalytic force. A foundation built on initiative, impulse, and the will to manifest. Indicates journeys that begin with decisive action, clear direction, and the courage to break new ground. The virtue of purpose as starting point; the path begins with momentum and clarity of intent.",
            "greek": "Πυρώδης Σπινθήρας",
            "transliteration": "Pyródis Spinthíras",
        },
        2: {
            "name": "The Foundation Stone",
            "interpretation": "The beginning establishes itself through structure, order, and defined patterns. A foundation built on principles, frameworks, and careful delineation. Indicates journeys that begin with planning, preparation, and the wisdom to build upon established wisdom. The virtue of form as starting point; the path begins with boundaries and coherent design.",
            "greek": "Θεμέλιος Λίθος",
            "transliteration": "Themélios Líthos",
        },
    },
    2: {
        0: {
            "name": "The Inner Emptiness",
            "interpretation": "The core maintains a sacred void, a still point of pure potential at the center of being. An inner nature characterized by adaptability, non-attachment, and receptive awareness. Indicates a capacity for deep listening, intuitive knowing, and holding paradox. The power of letting internal space remain undefined; wisdom through inner silence.",
            "greek": "Εσωτερικό Κενό",
            "transliteration": "Esoterikó Kenó",
        },
        1: {
            "name": "The Inner Flame",
            "interpretation": "The core burns with transformative energy, a dynamic center that continually renews itself. An inner nature characterized by passion, creativity, and self-generating momentum. Indicates a capacity for enthusiasm, inspiration, and generating new possibilities from within. The power of perpetual becoming; wisdom through inner movement.",
            "greek": "Εσωτερική Φλόγα",
            "transliteration": "Esoterikí Flóga",
        },
        2: {
            "name": "The Inner Crystal",
            "interpretation": "The core maintains a coherent structure, a stable pattern that organizes experience. An inner nature characterized by consistency, integrity, and principled order. Indicates a capacity for discernment, maintaining boundaries, and creating reliable inner frameworks. The power of inner coherence; wisdom through structured awareness.",
            "greek": "Εσωτερικός Κρύσταλλος",
            "transliteration": "Esoterikós Krýstallos",
        },
    },
    3: {
        0: {
            "name": "The Boundless Voice",
            "interpretation": "Expression that transcends definition, creating space rather than content. Projects outward through receptivity, allowing others to find their own meaning. Indicates influence through openness, the art of creating possibilities without imposing form. Communication that invites rather than asserts; touching others through question rather than answer.",
            "greek": "Απέραντη Φωνή",
            "transliteration": "Apéranti Foní",
        },
        1: {
            "name": "The Catalytic Voice",
            "interpretation": "Expression that transforms and energizes, sending ripples of change through its environment. Projects outward through active engagement, stimulating response and evolution. Indicates influence through inspiration, the art of kindling new fire in others. Communication that activates and motivates; touching others through spark and movement.",
            "greek": "Καταλυτική Φωνή",
            "transliteration": "Katalytikí Foní",
        },
        2: {
            "name": "The Crystalline Voice",
            "interpretation": "Expression that gives form to principle, articulating clear patterns and structures. Projects outward through coherent communication, offering definition and boundary. Indicates influence through clarity, the art of making the implicit explicit. Communication that organizes and defines; touching others through pattern and precision.",
            "greek": "Κρυστάλλινη Φωνή",
            "transliteration": "Krystállini Foní",
        },
    },
    4: {
        0: {
            "name": "The Permeable Boundary",
            "interpretation": "Connections characterized by openness and fluid exchange. Relates to others through receptive space, allowing authentic interplay without predetermined rules. Indicates relationships based on presence rather than agenda, networks defined by possibility rather than purpose. The art of connection through open boundaries; relationships as shared exploration.",
            "greek": "Διαπερατό Όριο",
            "transliteration": "Diaperató Ório",
        },
        1: {
            "name": "The Vital Exchange",
            "interpretation": "Connections characterized by energy transfer and dynamic interaction. Relates to others through active engagement, catalyzing transformation through relationship. Indicates networks defined by movement, purpose, and mutual stimulation. The art of connection through synergistic activity; relationships as transformative encounters.",
            "greek": "Ζωτική Ανταλλαγή",
            "transliteration": "Zotikí Antallagí",
        },
        2: {
            "name": "The Structured Alliance",
            "interpretation": "Connections characterized by clear agreements and defined parameters. Relates to others through coherent frameworks, establishing reliable patterns of exchange. Indicates relationships based on mutual understanding of roles, responsibilities, and boundaries. The art of connection through articulated structure; relationships as coherent systems.",
            "greek": "Δομημένη Συμμαχία",
            "transliteration": "Domiméni Symmachía",
        },
    },
    5: {
        0: {
            "name": "The Pregnant Pause",
            "interpretation": "Timing characterized by receptive awareness of the moment's potential. Relates to time through spaciousness, allowing events to unfold at their natural pace. Indicates the wisdom of non-action, strategic waiting, and attunement to the rhythm beneath events. The art of perfect timing through listening; success through alignment with what wants to emerge.",
            "greek": "Έγκυος Παύση",
            "transliteration": "Éngyos Pávsi",
        },
        1: {
            "name": "The Critical Moment",
            "interpretation": "Timing characterized by recognition and seizure of opportunity. Relates to time through active intervention, creating momentum at precise junctures. Indicates the wisdom of decisive action, acceleration, and the courage to create one's own timing. The art of perfect timing through initiative; success through bold response to unfolding conditions.",
            "greek": "Κρίσιμη Στιγμή",
            "transliteration": "Krísimi Stigmí",
        },
        2: {
            "name": "The Measured Cadence",
            "interpretation": "Timing characterized by rhythmic consistency and structured progression. Relates to time through ordered cycles, establishing reliable patterns of development. Indicates the wisdom of patience, persistence, and attunement to larger temporal frameworks. The art of perfect timing through disciplined rhythm; success through aligned participation in established cycles.",
            "greek": "Μετρημένος Ρυθμός",
            "transliteration": "Metriménos Rythmós",
        },
    },
    6: {
        0: {
            "name": "The Open Horizon",
            "interpretation": "Culmination that remains undefined, preserving potentiality rather than fixing a result. Outcomes characterized by openness to continued evolution and transformation. Indicates processes that conclude by opening new possibilities rather than reaching definitive endpoints. The wisdom of completion through release; fulfillment found in what remains possible.",
            "greek": "Ανοιχτός Ορίζοντας",
            "transliteration": "Anichtós Orízontas",
        },
        1: {
            "name": "The Breakthrough Point",
            "interpretation": "Culmination that catalyzes new beginnings, an ending that contains the seed of its own renewal. Outcomes characterized by momentum carrying forward into new cycles. Indicates processes that conclude with dynamic resolution and immediate impulse toward what comes next. The wisdom of completion through transformation; fulfillment found in evolutionary leaps.",
            "greek": "Σημείο Ανατροπής",
            "transliteration": "Símeio Anatropís",
        },
        2: {
            "name": "The Perfected Form",
            "interpretation": "Culmination that establishes lasting structure, an ending that crystallizes into definitive pattern. Outcomes characterized by stability, definition, and coherent completion. Indicates processes that conclude with clear resolution and establishment of new order. The wisdom of completion through manifestation; fulfillment found in what has been definitively created.",
            "greek": "Τελειοποιημένη Μορφή",
            "transliteration": "Teleiopoiiméni Morphí",
        },
    },
}

# Hebrew names and transliterations for upper trigrams (000-022 as examples)
UPPER_TRIGRAM_MEANINGS = {
    "000": {
        "english_name": "The Celestial Void",
        "name": "החלל השמימי",
        "transliteration": "HaChalal HaShamaymi",
        "interpretation": "As an upper trigram, the Void represents transcendence, unlimited potential, and connection to higher dimensions. It suggests outcomes that remain undefined but full of possibility, spiritual openness, and receptivity to cosmic influences.",
    },
    "001": {
        "english_name": "The Divine Spark",
        "name": "הניצוץ האלוהי",
        "transliteration": "HaNitzotz HaElohi",
        "interpretation": "As an upper trigram, the Spark represents sudden inspiration from above, divine insight, and breakthrough awareness. It suggests transformative ideas that arrive unexpectedly, illumination from higher sources, and catalytic vision.",
    },
    "002": {
        "english_name": "The Sacred Peak",
        "name": "הפסגה הקדושה",
        "transliteration": "HaPisga HaKedosha",
        "interpretation": "As an upper trigram, the Mountain represents elevated perspective, spiritual authority, and enduring wisdom. It suggests outcomes that stand firm against time, principles that remain unwavering, and connection to eternal truths.",
    },
    "010": {
        "english_name": "The Celestial Breath",
        "name": "הנשימה השמימית",
        "transliteration": "HaNeshima HaShmaymit",
        "interpretation": "As an upper trigram, the Wind represents subtle influence, invisible guidance, and the power of gentle persistence. It suggests situations where softness overcomes hardness, where ideas penetrate without force, and where change comes through adaptation.",
    },
    "011": {
        "english_name": "The Ascending Flame",
        "name": "הלהבה העולה",
        "transliteration": "HaLehava HaOlah",
        "interpretation": "As an upper trigram, the Flame represents illumination, purification, and transformative awareness. It suggests situations where clarity emerges through transformation, where vision becomes radiant, and where passion leads to insight.",
    },
    "012": {
        "english_name": "The Reflecting Pool",
        "name": "האגם המשתקף",
        "transliteration": "HaAgam HaMishtakef",
        "interpretation": "As an upper trigram, the Lake represents clarity through stillness, the mirror of truth, and contained wisdom. It suggests outcomes where boundaries create depth, where reflection leads to insight, and where beauty emerges through form.",
    },
    "020": {
        "english_name": "The Veil",
        "name": "הענן",
        "transliteration": "HaAnan",
        "interpretation": "As an upper trigram, the Cloud represents mystery, the boundary between worlds, and divine concealment. It suggests situations where truth is partly hidden, where revelation comes gradually, and where obscurity serves a higher purpose.",
    },
    "021": {
        "english_name": "The Descending Grace",
        "name": "החסד היורד",
        "transliteration": "HaChesed HaYored",
        "interpretation": "As an upper trigram, the Stream represents flowing wisdom, guidance that finds its way, and nourishment from above. It suggests outcomes where higher principles manifest in practical ways, where inspiration becomes tangible.",
    },
    "022": {
        "english_name": "The Crown",
        "name": "הכתר",
        "transliteration": "HaKeter",
        "interpretation": "As an upper trigram, the Crystal represents perfected awareness, absolute clarity, and divine order. It suggests situations where the highest truth crystallizes into perfect understanding, where spiritual principles become fully actualized.",
    },
    # ...add more as needed...
}
LOWER_TRIGRAM_MEANINGS = {
    "000": {
        "english_name": "The Primal Void",
        "name": "החלל הראשוני",
        "transliteration": "HaChalal HaRishoni",
        "interpretation": "As a lower trigram, the Void represents pure potential at the foundation, the uncarved block, and original innocence. It suggests situations arising from complete openness, beginnings without preconception, and foundations built on receptivity.",
    },
    "001": {
        "english_name": "The Quickening",
        "name": "ההתעוררות",
        "transliteration": "HaHit'orerut",
        "interpretation": "As a lower trigram, the Spark represents initial impulse, the first movement from stillness, and awakening energy. It suggests situations arising from sudden insight, initiatives born from inspiration, and foundations built on mo000tary clarity.",
    },
    "002": {
        "english_name": "The Bedrock",
        "name": "הסלע היסודי",
        "transliteration": "HaSela HaYesodi",
        "interpretation": "As a lower trigram, the Mountain represents solid foundation, fundamental principles, and immovable ground. It suggests situations arising from stability, beginnings rooted in established wisdom, and foundations built to endure.",
    },
    "010": {
        "english_name": "The First Breath",
        "name": "הנשימה הראשונה",
        "transliteration": "HaNeshima HaRishona",
        "interpretation": "As a lower trigram, the Wind represents gentle beginnings, subtle foundations, and persistent softness. It suggests situations arising from indirect approaches, initiatives that work through adaptation, and foundations built through flexibility.",
    },
    "011": {
        "english_name": "The Hearth Fire",
        "name": "אש האח",
        "transliteration": "Esh HaAch",
        "interpretation": "As a lower trigram, the Flame represents passionate foundation, energetic core, and transformative beginning. It suggests situations arising from enthusiasm, initiatives fueled by conviction, and foundations built through dynamic action.",
    },
    "012": {
        "english_name": "The Well",
        "name": "הבאר",
        "transliteration": "HaBe'er",
        "interpretation": "As a lower trigram, the Lake represents contained depths, accessible wisdom, and foundations with clear boundaries. It suggests situations arising from defined limits, beginnings with clear parameters, and foundations built through inner depth.",
    },
    "020": {
        "english_name": "The Mist",
        "name": "הערפל",
        "transliteration": "HaArafel",
        "interpretation": "As a lower trigram, the Cloud represents emergent form, foundations in transition, and the cusp of manifestation. It suggests situations arising from ambiguity, beginnings that are still taking shape, and foundations built during times of change.",
    },
    "021": {
        "english_name": "The Underground Current",
        "name": "הזרם התת-קרקעי",
        "transliteration": "HaZerem HaTat-Karka'i",
        "interpretation": "As a lower trigram, the Stream represents hidden momentum, foundations in movement, and strength that flows beneath the surface. It suggests situations arising from unseen influences, beginnings with inherent direction, and foundations built on continuous flow.",
    },
    "022": {
        "english_name": "The Foundation Stone",
        "name": "אבן היסוד",
        "transliteration": "Even HaYesod",
        "interpretation": "As a lower trigram, the Crystal represents perfect pattern at the core, fundamental structure, and essential order. It suggests situations arising from clear design, beginnings with precise intention, and foundations built with meticulous attention.",
    },
    # ...add more as needed...
}

UPPER_TRIGRAM_MEANINGS.update(
    {
        "100": {
            "english_name": "The Sky Thunder",
            "name": "הרעם השמים",
            "transliteration": "Ha-Ra'am Ha-Shamayim",
            "interpretation": "Represents divine announcement, awakening from above, and sudden revelation. Indicates situations where higher awareness breaks through resistance, where transformation comes suddenly, and where spiritual truth arrives with unmistakable power.",
        },
        "101": {
            "english_name": "The Heavenly Messenger",
            "name": "מלאך שמים",
            "transliteration": "Mal'akh Shamayim",
            "interpretation": "Represents divine timing, celestial alignment, and messages from beyond. Indicates situations developing toward momentous revelation, outcomes that arrive at precise cosmic moments, and guidance from higher dimensions.",
        },
        "102": {
            "english_name": "The Reaching Canopy",
            "name": "חופת העצים",
            "transliteration": "Chofat Ha-Etzim",
            "interpretation": "Represents diversification of expression, spreading influence, and the strength of interconnected growth. Indicates situations developing toward greater complexity, outcomes with rich variation, and aspirations toward community.",
        },
        "110": {
            "english_name": "The Cosmic Tide",
            "name": "הגאות הקוסמית",
            "transliteration": "Ha-Ge'ut Ha-Kosmit",
            "interpretation": "Represents rhythmic influence, emotional intelligence, and the power of cyclical change. Indicates situations developing toward harmonious flow, outcomes that arrive in waves, and aspirations that follow natural emotional patterns.",
        },
        "111": {
            "english_name": "The Radiant Crown",
            "name": "הכתר הזוהר",
            "transliteration": "Ha-Keter Ha-Zoher",
            "interpretation": "Represents complete illumination, perfected activity, and solar consciousness. Indicates situations developing toward full expression, outcomes that shine with undimmed power, and aspirations that radiate from a centered source.",
        },
        "112": {
            "english_name": "The Sacred Eruption",
            "name": "ההתפרצות הקדושה",
            "transliteration": "Ha-Hitpartzut Ha-Kedoshah",
            "interpretation": "Represents breakthrough power, emergence of hidden forces, and transformative culmination. Indicates situations developing toward dramatic revelation, outcomes where long-contained energy finds expression, and aspirations that challenge boundaries.",
        },
        "120": {
            "english_name": "The Dissolving Veil",
            "name": "המסך המתמוסס",
            "transliteration": "Ha-Masakh Ha-Mitmoseh",
            "interpretation": "Represents boundaries becoming permeable, transition between states, and the beautiful uncertainty of becoming. Indicates situations developing toward elegant dissolution, outcomes where clarity and mystery intertwine, and aspirations that transcend definition.",
        },
        "121": {
            "english_name": "The Guiding Star",
            "name": "כוכב המנחה",
            "transliteration": "Kokhav Ha-Mancheh",
            "interpretation": "Represents distant guidance, cosmic purpose, and illuminated destiny. Indicates situations developing toward aligned purpose, outcomes that fulfill distant callings, and aspirations that connect immediate action with eternal principles.",
        },
        "122": {
            "english_name": "The Living Monument",
            "name": "המצבה החיה",
            "transliteration": "Ha-Matzevah Ha-Chayah",
            "interpretation": "Represents evolutionary structure, legacy in formation, and collaborative creation. Indicates situations developing toward enduring works, outcomes that grow more significant with time, and aspirations that unite many into lasting achievement.",
        },
    }
)
LOWER_TRIGRAM_MEANINGS.update(
    {
        "100": {
            "english_name": "The First Thunder",
            "name": "הרעם הראשון",
            "transliteration": "Ha-Ra'am Ha-Rishon",
            "interpretation": "Represents awakening energy, initial breakthrough, and primal arousal. Indicates situations arising from sudden activation, beginnings that shake foundations, and initiatives born from powerful realization.",
        },
        "101": {
            "english_name": "The Ancient Signal",
            "name": "האות הקדמון",
            "transliteration": "Ha-Ot Ha-Kadmon",
            "interpretation": "Represents prophetic foundation, cyclical return, and destined beginning. Indicates situations arising from cosmic timing, initiatives marked by significance beyond their appearance, and foundations built on alignment with greater cycles.",
        },
        "102": {
            "english_name": "The Sacred Grove",
            "name": "האשרה הקדושה",
            "transliteration": "Ha-Asherah Ha-Kedoshah",
            "interpretation": "Represents integrated wisdom, living tradition, and roots that connect. Indicates situations arising from organic knowledge, beginnings that honor interconnection, and foundations built through balanced relationship.",
        },
        "110": {
            "english_name": "The Primal Ocean",
            "name": "הים הקדמון",
            "transliteration": "Ha-Yam Ha-Kadmon",
            "interpretation": "Represents emotional depth, the collective unconscious, and foundations in flow. Indicates situations arising from deep feeling, beginnings born from intuitive knowing, and foundations built on responsiveness to unseen currents.",
        },
        "111": {
            "english_name": "The Eternal Flame",
            "name": "האש הנצחית",
            "transliteration": "Ha-Esh Ha-Nitzchit",
            "interpretation": "Represents pure dynamic foundation, self-generating energy, and unbroken initiative. Indicates situations arising from passionate commitment, beginnings that contain their own momentum, and foundations built on continuous renewal.",
        },
        "112": {
            "english_name": "The Dormant Power",
            "name": "הכח הרדום",
            "transliteration": "Ha-Koach Ha-Radum",
            "interpretation": "Represents potential strength, contained passion, and disciplined power. Indicates situations arising from controlled energy, beginnings that hold tremendous potential, and foundations built on the balance between restraint and force.",
        },
        "120": {
            "english_name": "The Rising Mist",
            "name": "הערפל העולה",
            "transliteration": "Ha-Arafel Ha-Oleh",
            "interpretation": "Represents emergent potential, foundations in transition, and the mystery of beginning. Indicates situations arising from the interplay of structure and formlessness, beginnings that hover between states, and foundations built during liminal times.",
        },
        "121": {
            "english_name": "The Inner Light",
            "name": "האור הפנימי",
            "transliteration": "Ha-Or Ha-Pnimi",
            "interpretation": "Represents illuminated intuition, directed passion, and purposeful energy. Indicates situations arising from inner knowing, beginnings guided by clear vision, and foundations built on the marriage of enthusiasm and direction.",
        },
        "122": {
            "english_name": "The Growing Foundation",
            "name": "היסוד הצומח",
            "transliteration": "Ha-Yesod Ha-Tzomeach",
            "interpretation": "Represents organic structure, principles in development, and living tradition. Indicates situations arising from collaborative wisdom, beginnings that honor both structure and growth, and foundations built through communal effort.",
        },
    }
)

UPPER_TRIGRAM_MEANINGS.update(
    {
        "200": {
            "english_name": "The Celestial Cavern",
            "name": "המערה השמימית",
            "transliteration": "Ha-Me'arah Ha-Shmeimit",
            "interpretation": "Represents sacred enclosure, protected wisdom, and the sanctuary of higher truth. Indicates situations developing toward inner revelation, outcomes that require going within, and aspirations that find fulfillment in contemplative depth.",
        },
        "201": {
            "english_name": "The Beacon Light",
            "name": "אור המגדלור",
            "transliteration": "Or Ha-Migdalor",
            "interpretation": "Represents guiding illumination, directed wisdom, and light that shows the way. Indicates situations developing toward clarity of purpose, outcomes that illuminate paths for others, and aspirations that combine tradition with vision.",
        },
        "202": {
            "english_name": "The Heavenly Garden",
            "name": "הגן השמימי",
            "transliteration": "Ha-Gan Ha-Shmeimi",
            "interpretation": "Represents cultivated perfection, cosmic order in manifestation, and the harvest of higher principles. Indicates situations developing toward harmonious abundance, outcomes that unify diversity in perfect arrangement, and aspirations toward sustainable order.",
        },
        "210": {
            "english_name": "The Rainbow Bridge",
            "name": "גשר הקשת",
            "transliteration": "Gesher Ha-Keshet",
            "interpretation": "Represents connection between realms, ordered transition, and structured pathway to the beyond. Indicates situations developing toward meaningful passage, outcomes that link different dimensions of experience, and aspirations that build connections across differences.",
        },
        "211": {
            "english_name": "The Sacred Workshop",
            "name": "בית המלאכה הקדוש",
            "transliteration": "Beit Ha-Melakha Ha-Kadosh",
            "interpretation": "Represents divine craftsmanship, transformation within order, and the art of sacred change. Indicates situations developing toward mastery, outcomes where transformation serves higher purpose, and aspirations that transform through disciplined attention.",
        },
        "212": {
            "english_name": "The Heavenly Stairway",
            "name": "המדרגות השמימיות",
            "transliteration": "Ha-Madregot Ha-Shmeimiyot",
            "interpretation": "Represents graduated ascension, hierarchical wisdom, and sequential revelation. Indicates situations developing through distinct stages, outcomes that arrive through ordered progression, and aspirations that honor the wisdom of levels.",
        },
        "220": {
            "english_name": "The Sacred Chalice",
            "name": "הגביע הקדוש",
            "transliteration": "Ha-Gavia Ha-Kadosh",
            "interpretation": "Represents structured receptivity, perfected container, and the vessel of higher purpose. Indicates situations developing toward sacred holding, outcomes that contain without confining, and aspirations that create space for the divine.",
        },
        "221": {
            "english_name": "The King's Highway",
            "name": "דרך המלך",
            "transliteration": "Derekh Ha-Melekh",
            "interpretation": "Represents established progress, authoritative direction, and the path of dignified achievement. Indicates situations developing along structured routes, outcomes that arrive through persistence on proven paths, and aspirations guided by enduring principles.",
        },
        "222": {
            "english_name": "The Celestial Temple",
            "name": "היכל השמים",
            "transliteration": "Heikhal Ha-Shamayim",
            "interpretation": "Represents ultimate sacred order, perfected structure, and the architecture of divine principles. Indicates situations developing toward consummate harmony, outcomes that embody perfect proportion, and aspirations that unite heaven and earth through sacred design.",
        },
    }
)
LOWER_TRIGRAM_MEANINGS.update(
    {
        "200": {
            "english_name": "The Ancient Hollow",
            "name": "החלל הקדמון",
            "transliteration": "Ha-Chalal Ha-Kadmon",
            "interpretation": "Represents foundational emptiness, protected potential, and womb-like beginning. Indicates situations arising from sheltered development, beginnings that require protection, and foundations built through creating sacred space.",
        },
        "201": {
            "english_name": "The Ancient Flame",
            "name": "הלהבה הקדמונית",
            "transliteration": "Ha-Lehava Ha-Kadmonit",
            "interpretation": "Represents inherited wisdom, foundational knowledge, and illumination from tradition. Indicates situations arising from established teachings, beginnings guided by received knowledge, and foundations built on proven methods.",
        },
        "202": {
            "english_name": "The Sacred Ground",
            "name": "האדמה הקדושה",
            "transliteration": "Ha-Adamah Ha-Kedoshah",
            "interpretation": "Represents fertile foundation, generative stability, and nurturing structure. Indicates situations arising from established earth, beginnings rooted in practical wisdom, and foundations built through patient cultivation.",
        },
        "210": {
            "english_name": "The Ancient Pathway",
            "name": "הנתיב הקדמון",
            "transliteration": "Ha-Nativ Ha-Kadmon",
            "interpretation": "Represents established route, tested passage, and foundation in movement. Indicates situations arising from travels between states, beginnings that follow time-honored routes, and foundations built through creating connections.",
        },
        "211": {
            "english_name": "The Primal Kiln",
            "name": "הכבשן הקדמון",
            "transliteration": "Ha-Kivshan Ha-Kadmon",
            "interpretation": "Represents formative heat, structured transformation, and containment of power. Indicates situations arising from intentional transformation, beginnings forged through challenge, and foundations built through alchemical process.",
        },
        "212": {
            "english_name": "The Terraced Foundation",
            "name": "היסוד המדורג",
            "transliteration": "Ha-Yesod Ha-Medurag",
            "interpretation": "Represents layered beginning, developmental structure, and organized progression. Indicates situations arising from careful staging, beginnings that acknowledge different levels, and foundations built through systematic approach.",
        },
        "220": {
            "english_name": "The Ancient Vessel",
            "name": "הכלי הקדמון",
            "transliteration": "Ha-Kli Ha-Kadmon",
            "interpretation": "Represents container of beginning, structured potential, and bounded possibility. Indicates situations arising from defined limits, beginnings that require containment, and foundations built through establishing boundaries.",
        },
        "221": {
            "english_name": "The Foundation Path",
            "name": "נתיב היסוד",
            "transliteration": "Netiv Ha-Yesod",
            "interpretation": "Represents directed structure, purposeful order, and movement within form. Indicates situations arising from clear intention within boundaries, beginnings that follow established routes, and foundations built through disciplined progression.",
        },
        "222": {
            "english_name": "The Eternal Foundation",
            "name": "היסוד הנצחי",
            "transliteration": "Ha-Yesod Ha-Nitzchi",
            "interpretation": "Represents perfect order at beginning, absolute structure, and complete pattern as origin. Indicates situations arising from established perfection, beginnings built on complete systems, and foundations that embody harmony in all dimensions.",
        },
    }
)


class TernaryDimensionInterpreter:
    """
    Interprets ternary values and provides information about their position in the Kamea system.
    """

    def __init__(self):
        pass

    def determine_family(self, ternary_value: str) -> int:
        """Determine which family a ternary value belongs to.

        Args:
            ternary_value: The ternary value to check

        Returns:
            Family ID (0-8)
        """
        # Check if it's a Hierophant (Prime Ditrune)
        for family_id, hierophant in HIEROPHANTS.items():
            if ternary_value == hierophant["ternary"]:
                return family_id

        # For non-Hierophants, use a pattern matching approach
        # This is a simplified implementation
        # In a real implementation, this would use a more sophisticated algorithm

        # For now, use the first digit as a simple heuristic
        first_digit = int(ternary_value[0]) if ternary_value else 0
        if first_digit == 0:
            return 0  # The Void family
        elif first_digit == 1:
            return 1  # The Dynamo family
        elif first_digit == 2:
            return 2  # The Matrix family

        # Default to family 0 if we can't determine
        return 0


class HexagramInterpreter:
    """
    Interprets 6-digit ternary hexagrams using the new structured model.
    """

    def __init__(self):
        pass

    def get_hierophant_info(self, ditrune: str) -> dict:
        """
        Returns the Hierophant info if ditrune is a prime, else None.
        """
        return HIEROPHANTS.get(ditrune)

    def get_acolyte_info(self, ditrune: str) -> dict:
        """
        Returns the Acolyte info for a non-prime ditrune, or None if ditrune is a prime.
        Uses family (prime) and position (1–8) within the family.
        Adds an 'influence' field describing how the Acolyte channels the Hierophant's core essence.
        """
        # Determine family
        family, _ = self.get_family_and_level(ditrune)
        # If prime, return None
        if ditrune in HIEROPHANTS:
            return None
        # Find all possible family members (same first two digits, 6 digits total)
        # Exclude the prime itself
        family_prefix = family
        family_members = [
            f"{family_prefix}{a}{b}{c}{d}"
            for a in "012"
            for b in "012"
            for c in "012"
            for d in "012"
        ]
        family_members = [
            d for d in family_members if d != family_prefix * 3 and len(d) == 6
        ]
        # Remove the prime from the list if present
        if family_prefix * 3 in family_members:
            family_members.remove(family_prefix * 3)
        # Sort family members for consistent ordering
        family_members_sorted = sorted(family_members)
        # Find the position (1-based index) of this ditrune in the family (excluding the prime)
        try:
            acolyte_index = family_members_sorted.index(ditrune) % 8  # 0-7
        except ValueError:
            acolyte_index = 0  # fallback
        acolyte = ACOLYTE_TITLES[acolyte_index]
        # Get the Hierophant info for this family
        hierophant = HIEROPHANTS.get(
            family_prefix * 3, {"name": family_prefix * 3, "core_essence": ""}
        )
        # Synthesize the influence statement
        influence = (
            f"As {acolyte['title']} of {hierophant['name']}, this channel {acolyte['function'].lower()} "
            f"by {acolyte['nature'].lower()} and expressing: {hierophant.get('core_essence', '')}"
        )
        return {
            "title": acolyte["title"],
            "greek": acolyte["greek"],
            "function": acolyte["function"],
            "nature": acolyte["nature"],
            "serves": hierophant["name"],
            "serves_greek": hierophant.get("greek", ""),
            "influence": influence,
        }

    def classify_ditrune_type(self, ditrune: str) -> str:
        """
        Classifies a ditrune as 'prime' (Hierophant), 'acolyte' (Composite), or 'temple' (Concurrent).
        - Prime: In HIEROPHANTS
        - Acolyte: In the 8 composites per family (not prime, but matches acolyte position)
        - Temple: All others (concurrents)
        """
        if ditrune in HIEROPHANTS:
            return "prime"
        # Determine family
        family, _ = self.get_family_and_level(ditrune)
        family_prefix = family
        # Generate all possible acolyte numbers for this family (excluding the prime)
        acolyte_candidates = [
            f"{family_prefix}{a}{b}{c}{d}"
            for a in "012"
            for b in "012"
            for c in "012"
            for d in "012"
        ]
        acolyte_candidates = [
            d for d in acolyte_candidates if d != family_prefix * 3 and len(d) == 6
        ]
        # Remove the prime from the list if present
        if family_prefix * 3 in acolyte_candidates:
            acolyte_candidates.remove(family_prefix * 3)
        # There are 8 acolytes per family, so get the first 8 in sorted order
        acolyte_numbers = sorted(acolyte_candidates)[:8]
        if ditrune in acolyte_numbers:
            return "acolyte"
        return "temple"

    def interpret(self, ditrune: str) -> dict:
        """
        Main entry: Interpret a 6-digit ternary hexagram.
        Returns a dict with explicit layer info: ditrune_type, bigram meanings, and the appropriate mythic overlay.
        """
        if not (
            isinstance(ditrune, str)
            and len(ditrune) == 6
            and all(c in "012" for c in ditrune)
        ):
            raise ValueError("Input must be a 6-digit ternary string.")
        digits = [int(c) for c in ditrune]
        decimal_value = ternary_to_decimal(ditrune)
        kamea_locator = self.get_kamea_locator(ditrune)
        family, level = self.get_family_and_level(ditrune)
        core_essence = self.get_core_essence(digits, family)
        # Esoteric bigram meanings for all
        bigram_defs = [
            (FIRST_BIGRAM_MEANINGS, (0, 5), "First Bigram"),
            (SECOND_BIGRAM_MEANINGS, (1, 4), "Second Bigram"),
            (THIRD_BIGRAM_MEANINGS, (2, 3), "Third Bigram"),
        ]
        bigrams = []
        for meaning_dict, (a_idx, b_idx), label in bigram_defs:
            a, b = digits[a_idx], digits[b_idx]
            val = a * 3 + b

            try:
                info = meaning_dict[val]
                # Create bigram info with available keys
                bigram_info = {
                    "label": label,
                    "positions": f"{a_idx+1} & {b_idx+1}",
                    "bigram": f"{a}{b}",
                    "decimal": val,
                    "name": info.get("name", f"Bigram {a}{b}"),
                }

                # Add interpretation if available
                if "interpretation" in info:
                    bigram_info["interpretation"] = info["interpretation"]
                else:
                    bigram_info[
                        "interpretation"
                    ] = f"Combination of {['Aperture', 'Surge', 'Lattice'][a]} and {['Aperture', 'Surge', 'Lattice'][b]}"
            except KeyError:
                # Handle missing bigram definitions
                bigram_info = {
                    "label": label,
                    "positions": f"{a_idx+1} & {b_idx+1}",
                    "bigram": f"{a}{b}",
                    "decimal": val,
                    "name": f"Bigram {a}{b}",
                    "interpretation": f"Combination of {['Aperture', 'Surge', 'Lattice'][a]} and {['Aperture', 'Surge', 'Lattice'][b]}",
                }

            bigrams.append(bigram_info)
        # Classify ditrune type
        ditrune_type = self.classify_ditrune_type(ditrune)
        result = {
            "Ditrune": ditrune,
            "Decimal Value": decimal_value,
            "Kamea Locator": kamea_locator,
            "Family": family,
            "Level": level,
            "CORE ESSENCE": core_essence,
            "Bigrams": bigrams,
            "ditrune_type": ditrune_type,
            "Dimensional Analysis": self.get_line_meanings(ditrune),
        }
        # Add the appropriate mythic overlay
        if ditrune_type == "prime":
            result["Hierophant"] = self.get_hierophant_info(ditrune)
            result["Interpretation Layer"] = "Hierophant (Prime) only"
        elif ditrune_type == "acolyte":
            acolyte = self.get_acolyte_info(ditrune)
            result["Acolyte"] = acolyte
            # Also include the Hierophant for context
            if acolyte:
                result["Hierophant"] = self.get_hierophant_info(acolyte["serves"])
            result["Interpretation Layer"] = "Acolyte (Composite) + Hierophant"
        else:  # temple
            temple = self.get_temple_info(ditrune)
            result["Temple"] = temple
            # Also include Acolyte and Hierophant for context
            acolyte = self.get_acolyte_info(ditrune)
            if acolyte:
                result["Acolyte"] = acolyte
                result["Hierophant"] = self.get_hierophant_info(acolyte["serves"])
            result[
                "Interpretation Layer"
            ] = "Temple (Concurrent) + Acolyte + Hierophant"
        # Add Trigram Analysis
        result["Trigram Analysis"] = self.get_trigram_meanings(ditrune)
        return result

    def get_kamea_locator(self, ditrune: str) -> str:
        # Placeholder: implement actual locator logic
        # Example: Family-Column-Row (first, middle, last two digits)
        return f"{ditrune[0]}-{ditrune[2]}-{ditrune[5]}"

    def get_family_and_level(self, ditrune: str) -> Tuple[str, str]:
        # Placeholder: implement actual family/level logic
        # Example: Family is first two digits, level is 'Prime' if all digits same
        family = ditrune[:2]
        level = "Prime" if len(set(ditrune)) == 1 else "Composite/Concurrent"
        return family, level

    def get_core_essence(self, digits: List[int], family: str) -> str:
        # Placeholder: simple essence based on digit pattern and family
        if len(set(digits)) == 1:
            return f"Pure {['Aperture','Surge','Lattice'][digits[0]]} essence of family {family}."
        if digits.count(1) > digits.count(0) and digits.count(1) > digits.count(2):
            return f"Transformative pattern with dynamic energy in family {family}."
        if digits.count(2) > digits.count(0) and digits.count(2) > digits.count(1):
            return f"Stable, structural pattern in family {family}."
        return f"Mixed pattern, adaptive essence in family {family}."

    def get_structure(self, digits: List[int]) -> List[dict]:
        """
        Returns a list of dicts for each bigram, including positions, bigram, decimal, name, and core_meaning.
        """
        bigram_defs = [
            (FIRST_BIGRAM_MEANINGS, (0, 5), "Seed & Flow"),
            (SECOND_BIGRAM_MEANINGS, (1, 4), "Resonance & Pulse"),
            (THIRD_BIGRAM_MEANINGS, (2, 3), "Echo & Weave"),
        ]
        structure = []
        for i, (meaning_dict, (a_idx, b_idx), label) in enumerate(bigram_defs):
            a, b = digits[a_idx], digits[b_idx]
            val = a * 3 + b
            info = meaning_dict[val]
            structure.append(
                {
                    "positions": f"{a_idx+1} & {b_idx+1} ({label})",
                    "bigram": f"{a}{b}",
                    "decimal": val,
                    "name": info["name"],
                    "interpretation": info["interpretation"],
                }
            )
        return structure

    def get_dimensional_analysis(self, digits: List[int]) -> List[str]:
        return [
            f"Position {i+1}: {DIMENSIONAL_INTERPRETATIONS[i+1][d]}"
            for i, d in enumerate(digits)
        ]

    def get_pattern_insights(self, digits: List[int]) -> str:
        # Simple pattern analysis: repetition, symmetry, sequence
        if digits == digits[::-1]:
            return "Perfectly palindromic pattern."
        if len(set(digits)) == 1:
            return "All digits identical: pure archetype."
        if digits[:3] == digits[3:][::-1]:
            return "First triad mirrors second triad."
        return "Complex or mixed pattern."

    def get_relationships(self, ditrune: str) -> Dict[str, str]:
        # Placeholder: implement actual conrune, reversal, mutation logic
        conrune = ditrune.translate(str.maketrans("012", "021"))
        reversal = ditrune[::-1]
        nuclear = self.nuclear_mutation_path(ditrune)
        return {
            "Conrune Pair": f"{conrune} (conrune transformation)",
            "Reversal": f"{reversal} (reversed)",
            "Nuclear Mutation": f"{nuclear} (mutation path)",
        }

    def nuclear_mutation_path(self, ditrune: str) -> str:
        # Placeholder: simple mutation (repeat for demonstration)
        # Real logic should implement actual nuclear mutation
        return ditrune  # TODO: implement mutation path

    def synthesize_divinatory(
        self, core, structure, dimensional, pattern, relationships
    ) -> str:
        # Synthesize a divinatory meaning from all elements
        return (
            f"Essence: {core}\n"
            f"Structure: {'; '.join(str(info['name']) for info in structure)}\n"
            f"Dimensional: {'; '.join(dimensional)}\n"
            f"Pattern: {pattern}\n"
            f"Relationships: {relationships['Conrune Pair']}, {relationships['Reversal']}, {relationships['Nuclear Mutation']}\n"
            f"Divinatory: This hexagram invites you to contemplate its core essence and structure, and to act in harmony with its pattern and relationships."
        )

    TEMPLE_TYPES = [
        {"name": "Prothyron", "greek": "Πρόθυρον"},
        {"name": "Temenos", "greek": "Τέμενος"},
        {"name": "Eschara", "greek": "Ἐσχάρα"},
        {"name": "Thesauros", "greek": "Θησαυρός"},
        {"name": "Adyton", "greek": "Ἄδυτον"},
        {"name": "Stoa", "greek": "Στοά"},
        {"name": "Bibliotheke", "greek": "Βιβλιοθήκη"},
        {"name": "Theatron", "greek": "Θέατρον"},
        {"name": "Telesterion", "greek": "Τελεστήριον"},
    ]

    def get_temple_info(self, ditrune: str) -> dict:
        """
        Returns the Temple info for a given ditrune, including type, element descriptor, acolyte, hierophant, and full mythic name.
        Naming follows: 'The [Temple Type] [Element Descriptor] under [Acolyte Title] of [Hierophant Name]'.
        """
        # 1. Temple Type: First Bigram (positions 1 & 6)
        first_bigram_decimal = int(ditrune[0]) * 3 + int(ditrune[5])
        temple_type = self.TEMPLE_TYPES[first_bigram_decimal]

        # 2. Element Descriptor: Analyze digit counts and pattern
        digits = [int(c) for c in ditrune]
        counts = {0: digits.count(0), 1: digits.count(1), 2: digits.count(2)}
        max_count = max(counts.values())
        dominant = [k for k, v in counts.items() if v == max_count]
        if len(dominant) == 1:
            if dominant[0] == 0:
                element_desc = "of Open Mystery"
            elif dominant[0] == 1:
                element_desc = "of Flowing Energy"
            else:
                element_desc = "of Formed Pattern"
        else:
            element_desc = "of Harmonic Balance"
        # Special pattern descriptors
        if digits == digits[::-1]:
            element_desc = "of Perfect Reflection"
        elif digits == sorted(digits):
            element_desc = "of Rising Power"
        elif digits == sorted(digits, reverse=True):
            element_desc = "of Deepening Wisdom"
        elif all(digits[i] != digits[i + 1] for i in range(len(digits) - 1)):
            element_desc = "of Rhythmic Exchange"
        elif any(digits.count(d) >= 3 for d in set(digits)):
            element_desc = "of Concentrated Force"

        # 3. Acolyte: Use get_acolyte_info
        acolyte = self.get_acolyte_info(ditrune)
        family, _ = self.get_family_and_level(ditrune)  # Ensure 'family' is defined
        hierophant = self.get_hierophant_info(family * 3) if family else None
        acolyte_title = acolyte.get("title", "") if acolyte else ""
        hierophant_name = hierophant.get("name", "") if hierophant else ""

        # 5. Assemble full name
        full_name = f"{acolyte_title} of {hierophant_name}"
        return {
            "temple_type": temple_type["name"]
            if isinstance(temple_type, dict)
            else temple_type,
            "temple_type_greek": temple_type.get("greek", "")
            if isinstance(temple_type, dict)
            else "",
            "element_descriptor": element_desc,
            "acolyte_title": acolyte_title,
            "acolyte_greek": acolyte.get("greek", "") if acolyte else "",
            "hierophant_name": hierophant_name,
            "hierophant_greek": hierophant.get("greek", "") if hierophant else "",
            "full_name": full_name,
        }

    def get_line_meanings(self, ditrune: str) -> list:
        """
        Returns a list of refined meanings for each line (position) in the ditrune.
        Each entry includes: position (1-based), element, name, interpretation, greek, and transliteration.
        """
        # Access the module-level dictionary
        from tq.services.ternary_dimension_interpreter_new import REFINED_LINE_MEANINGS

        meanings = []
        for i, c in enumerate(ditrune):
            pos = i + 1
            if pos > 6:
                break  # Only positions 1-6 are defined
            element = int(c)

            try:
                line_info = REFINED_LINE_MEANINGS[pos][element]
                meanings.append(
                    {
                        "position": pos,
                        "element": element,
                        "name": line_info["name"],
                        "interpretation": line_info["interpretation"],
                        "greek": line_info["greek"],
                        "transliteration": line_info["transliteration"],
                    }
                )
            except (KeyError, IndexError):
                # Handle missing line definitions
                element_names = ["Aperture", "Surge", "Lattice"]
                meanings.append(
                    {
                        "position": pos,
                        "element": element,
                        "name": f"The {element_names[element]} at Position {pos}",
                        "interpretation": f"Represents the qualities of {element_names[element]} at position {pos}.",
                        "greek": "",
                        "transliteration": "",
                    }
                )
        return meanings

    def get_trigram_meanings(self, ditrune: str) -> dict:
        """
        Returns the upper and lower trigram meanings for a given ditrune, including English name, Hebrew name, transliteration, and interpretation.
        """
        # Upper: positions 6-5-4
        upper_trigram = (
            f"{ditrune[5]}{ditrune[4]}{ditrune[3]}" if len(ditrune) >= 6 else ""
        )
        # Lower: positions 3-2-1
        lower_trigram = (
            f"{ditrune[2]}{ditrune[1]}{ditrune[0]}" if len(ditrune) >= 3 else ""
        )

        # Access the module-level dictionaries, not instance attributes
        from tq.services.ternary_dimension_interpreter_new import (
            LOWER_TRIGRAM_MEANINGS,
            UPPER_TRIGRAM_MEANINGS,
        )

        upper = UPPER_TRIGRAM_MEANINGS.get(
            upper_trigram,
            {
                "english_name": "(Not Defined)",
                "name": "(לא מוגדר)",
                "transliteration": "(Lo Mugdar)",
                "interpretation": "No interpretation defined yet.",
            },
        )
        lower = LOWER_TRIGRAM_MEANINGS.get(
            lower_trigram,
            {
                "english_name": "(Not Defined)",
                "name": "(לא מוגדר)",
                "transliteration": "(Lo Mugdar)",
                "interpretation": "No interpretation defined yet.",
            },
        )
        return {
            "Upper Trigram": {
                "trigram": upper_trigram,
                "english_name": upper["english_name"],
                "name": upper["name"],
                "transliteration": upper["transliteration"],
                "interpretation": upper["interpretation"],
            },
            "Lower Trigram": {
                "trigram": lower_trigram,
                "english_name": lower["english_name"],
                "name": lower["name"],
                "transliteration": lower["transliteration"],
                "interpretation": lower["interpretation"],
            },
        }

    def interpret_digit(self, digit: int, index: int) -> dict:
        """
        Interprets a single digit at a specific position (index).

        Args:
            digit: The ternary digit (0, 1, or 2)
            index: The position index (0-based, right-to-left)

        Returns:
            A dictionary with the interpretation of the digit at the given position
        """
        # Define position names and triad names
        position_names = [
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
        triad_names = ["Potential", "Process", "Emergence"]

        # Element names and qualities
        element_names = ["Aperture", "Surge", "Lattice"]
        element_energies = ["Receptive", "Dynamic", "Structural"]
        element_qualities = ["Openness", "Transformation", "Pattern"]

        # Get position name and triad
        position_name = (
            position_names[index]
            if index < len(position_names)
            else f"Position {index+1}"
        )
        triad_index = index // 3
        triad_name = (
            triad_names[triad_index]
            if triad_index < len(triad_names)
            else f"Triad {triad_index+1}"
        )

        # Calculate position value
        position_value = 3**index

        # Get element information
        element_name = element_names[digit]
        element_energy = element_energies[digit]
        element_quality = element_qualities[digit]

        # Generate descriptions based on digit and position
        descriptions = {
            0: [
                "Foundation of pure potential, undefined and receptive to all possibilities.",
                "Inner resonance characterized by adaptability and non-attachment.",
                "Expression that creates space rather than content, allowing others to find meaning.",
                "Connections characterized by openness and fluid exchange without predetermined rules.",
                "Timing characterized by receptive awareness, allowing events to unfold naturally.",
                "Culmination that remains undefined, preserving potentiality rather than fixing results.",
                "Convergence point that remains open to multiple influences and directions.",
                "Boundary that remains permeable, allowing free exchange between realms.",
                "Transformation that dissolves existing patterns into pure potential.",
            ],
            1: [
                "Foundation built on initiative, impulse, and the will to manifest.",
                "Inner nature characterized by passion, creativity, and self-generating momentum.",
                "Expression that transforms and energizes, sending ripples of change outward.",
                "Connections characterized by energy transfer and dynamic interaction.",
                "Timing characterized by recognition and seizure of opportunity.",
                "Culmination that catalyzes new beginnings, an ending containing seeds of renewal.",
                "Convergence point where energies intensify and transform into new patterns.",
                "Boundary that actively mediates between different states or realms.",
                "Transformation that accelerates and amplifies existing patterns into new forms.",
            ],
            2: [
                "Foundation built on principles, frameworks, and careful delineation.",
                "Inner nature characterized by consistency, integrity, and principled order.",
                "Expression that gives form to principle, articulating clear patterns.",
                "Connections characterized by clear agreements and defined parameters.",
                "Timing characterized by rhythmic consistency and structured progression.",
                "Culmination that establishes lasting structure, crystallizing into definitive pattern.",
                "Convergence point where patterns align into more complex ordered structures.",
                "Boundary that clearly delineates and organizes different domains.",
                "Transformation that perfects and completes existing patterns into ideal forms.",
            ],
        }

        # Get description based on digit and position
        description = (
            descriptions[digit][index]
            if index < len(descriptions[digit])
            else f"{element_name} at position {index+1}"
        )

        # Generate dimensional meaning based on position and digit
        dimensional_meanings = {
            0: [
                "The beginning emerges from absolute potential, unmarked by preconception.",
                "The core maintains a sacred void, a still point of pure potential at the center.",
                "Projects outward through receptivity, allowing others to find their own meaning.",
                "Relates to others through receptive space, allowing authentic interplay.",
                "Relates to time through spaciousness, allowing events to unfold naturally.",
                "Outcomes characterized by openness to continued evolution and transformation.",
                "A nexus that remains undefined, allowing multiple influences to converge.",
                "A horizon that remains open, inviting exploration beyond known boundaries.",
                "A transformation that dissolves structure back into pure potential.",
            ],
            1: [
                "The beginning bursts forth with purposeful energy and catalytic force.",
                "The core burns with transformative energy, a dynamic center of renewal.",
                "Projects outward through active engagement, stimulating response and evolution.",
                "Relates to others through active engagement, catalyzing transformation.",
                "Relates to time through active intervention, creating momentum at key moments.",
                "Outcomes characterized by momentum carrying forward into new cycles.",
                "A nexus where energies intensify and transform into breakthrough moments.",
                "A horizon that actively reveals new possibilities and directions.",
                "A transformation that accelerates evolution into entirely new patterns.",
            ],
            2: [
                "The beginning establishes itself through structure, order, and defined patterns.",
                "The core maintains a coherent structure, a stable pattern organizing experience.",
                "Projects outward through coherent communication, offering definition and boundary.",
                "Relates to others through coherent frameworks, establishing reliable patterns.",
                "Relates to time through ordered cycles, establishing reliable patterns.",
                "Outcomes characterized by stability, definition, and coherent completion.",
                "A nexus where patterns align into more complex ordered structures.",
                "A horizon that clearly delineates the boundaries of what is and can be.",
                "A transformation that perfects existing patterns into their ideal form.",
            ],
        }

        dimensional_meaning = (
            dimensional_meanings[digit][index]
            if index < len(dimensional_meanings[digit])
            else ""
        )

        return {
            "position": index + 1,  # 1-based position
            "position_name": position_name,
            "position_value": position_value,
            "triad_name": triad_name,
            "name": element_name,
            "energy": element_energy,
            "quality": element_quality,
            "description": description,
            "dimensional_meaning": dimensional_meaning,
        }

    def analyze_ternary(self, ternary_digits: list) -> dict:
        """
        Analyzes a list of ternary digits to provide a comprehensive interpretation.

        Args:
            ternary_digits: A list of integers (0, 1, 2) representing the ternary number

        Returns:
            A dictionary with the analysis results
        """
        if not ternary_digits:
            return {"error": "No digits provided for analysis."}

        # Ensure all digits are valid ternary digits
        if not all(d in [0, 1, 2] for d in ternary_digits):
            return {"error": "Invalid ternary digits. Only 0, 1, and 2 are allowed."}

        # We don't need to convert to string for our operations
        # But we'll keep this commented out in case we need it later
        # ternary_str = ''.join(str(d) for d in ternary_digits)

        # 1. Distribution analysis
        counts = [
            ternary_digits.count(0),
            ternary_digits.count(1),
            ternary_digits.count(2),
        ]
        element_names = ["Aperture", "Surge", "Lattice"]
        max_count = max(counts)
        dominant_indices = [i for i, count in enumerate(counts) if count == max_count]

        if len(dominant_indices) == 1:
            dominant_element = (
                f"{element_names[dominant_indices[0]]} ({dominant_indices[0]})"
            )
        else:
            dominant_elements = [f"{element_names[i]} ({i})" for i in dominant_indices]
            dominant_element = "Mixed: " + ", ".join(dominant_elements)

        # Determine balance
        if len(set(counts)) == 1:  # All counts equal
            balance = "Perfect balance between all elements"
        elif counts.count(0) > 0:  # At least one element has zero count
            balance = "Imbalanced - missing one or more elements"
        elif max(counts) > len(ternary_digits) // 2:  # One element dominates
            balance = "Strongly dominated by one element"
        else:
            balance = "Moderately balanced with some variation"

        distribution = {
            "counts": counts,
            "dominant_element": dominant_element,
            "balance": balance,
        }

        # 2. Pattern recognition
        patterns = {
            "repetitions": [],
            "sequences": [],
            "symmetry": {"score": 0.0, "description": "No symmetry detected"},
            "cross_triad_resonance": [],
        }

        # Check for repetitions or absences
        for i, count in enumerate(counts):
            if count == 0:
                patterns["repetitions"].append(
                    {"element": element_names[i], "absence": True}
                )
            elif count >= 3 and count >= len(ternary_digits) // 2:
                patterns["repetitions"].append(
                    {"element": element_names[i], "count": count}
                )

        # Check for sequences (3+ consecutive same digit)
        current_digit = None
        current_length = 0
        current_start = 0

        for i, digit in enumerate(ternary_digits):
            if digit == current_digit:
                current_length += 1
            else:
                if current_length >= 3:
                    patterns["sequences"].append(
                        {
                            "element": element_names[current_digit],
                            "length": current_length,
                            "position": current_start + 1,  # 1-based position
                        }
                    )
                current_digit = digit
                current_length = 1
                current_start = i

        # Check final sequence
        if current_length >= 3:
            patterns["sequences"].append(
                {
                    "element": element_names[current_digit],
                    "length": current_length,
                    "position": current_start + 1,  # 1-based position
                }
            )

        # Check for symmetry
        reversed_digits = ternary_digits[::-1]
        matches = sum(1 for a, b in zip(ternary_digits, reversed_digits) if a == b)
        symmetry_score = matches / len(ternary_digits) if ternary_digits else 0

        if symmetry_score == 1.0:
            patterns["symmetry"] = {
                "score": 1.0,
                "description": "Perfect palindromic symmetry",
            }
        elif symmetry_score >= 0.75:
            patterns["symmetry"] = {
                "score": symmetry_score,
                "description": "Strong symmetrical pattern",
            }
        elif symmetry_score >= 0.5:
            patterns["symmetry"] = {
                "score": symmetry_score,
                "description": "Moderate symmetrical elements",
            }

        # Check for cross-triad resonance (same digit in same position across triads)
        if len(ternary_digits) >= 6:
            triad1 = ternary_digits[:3]
            triad2 = ternary_digits[3:6]
            resonances = []

            for i in range(min(len(triad1), len(triad2))):
                if triad1[i] == triad2[i]:
                    resonances.append(
                        f"{element_names[triad1[i]]} resonance between positions {i+1} and {i+4}"
                    )

            patterns["cross_triad_resonance"] = resonances

        # 3. Generate narrative
        narrative = "## Core Narrative\n\n"

        # Add distribution insights
        narrative += "**Element Distribution:** "
        if counts.count(0) > 0:  # Missing elements
            missing = [element_names[i] for i, count in enumerate(counts) if count == 0]
            narrative += f"This pattern lacks {', '.join(missing)}, creating a focused expression "
            narrative += "through the remaining elements. "
        elif len(set(counts)) == 1:  # Perfect balance
            narrative += (
                "This pattern shows perfect balance between all three elements, "
            )
            narrative += "suggesting a comprehensive and integrated approach. "
        else:  # Some dominance
            dominant_idx = counts.index(max(counts))
            narrative += f"This pattern emphasizes {element_names[dominant_idx]}, "
            narrative += "indicating a primary focus on "
            if dominant_idx == 0:
                narrative += "potential, receptivity, and openness to possibility. "
            elif dominant_idx == 1:
                narrative += "transformation, dynamic change, and active energy. "
            else:
                narrative += "structure, pattern, and defined organization. "

        # Add pattern insights
        if patterns["symmetry"]["score"] >= 0.75:
            narrative += (
                "\n\n**Symmetry:** The strong symmetrical arrangement suggests "
            )
            narrative += "balance, reflection, and a harmonious relationship between beginning and end. "

        if patterns["sequences"]:
            narrative += (
                "\n\n**Sequences:** The pattern contains significant sequences of "
            )
            seq_elements = set(seq["element"] for seq in patterns["sequences"])
            narrative += ", ".join(seq_elements) + ", "
            narrative += "indicating sustained focus or momentum in these qualities. "

        if patterns["cross_triad_resonance"]:
            narrative += "\n\n**Cross-Triad Resonance:** There are meaningful connections between "
            narrative += (
                "the Potential and Process triads, suggesting coherent development "
            )
            narrative += "from foundation to expression. "

        # Add holistic interpretation
        holistic = "\n\n## Holistic Interpretation\n\n"

        if len(ternary_digits) <= 3:
            holistic += "This pattern focuses primarily on foundational qualities and potential. "
            holistic += "It describes inner nature and core essence rather than outer expression. "
        elif len(ternary_digits) <= 6:
            holistic += "This pattern encompasses both foundational qualities and their development. "
            holistic += "It shows how inner potential manifests through process and interaction. "
        else:
            holistic += "This pattern represents a complete cycle from foundation through process to emergence. "
            holistic += "It reveals how core qualities ultimately transform and transcend their origins. "

        # Add specific element combinations
        if counts[0] > counts[1] and counts[0] > counts[2]:  # Aperture dominant
            holistic += "With Aperture as the dominant element, this pattern suggests "
            holistic += "a journey characterized by openness, receptivity, and unlimited potential. "
        elif counts[1] > counts[0] and counts[1] > counts[2]:  # Surge dominant
            holistic += "With Surge as the dominant element, this pattern suggests "
            holistic += "a journey characterized by transformation, dynamic change, and active evolution. "
        elif counts[2] > counts[0] and counts[2] > counts[1]:  # Lattice dominant
            holistic += "With Lattice as the dominant element, this pattern suggests "
            holistic += "a journey characterized by structure, organization, and coherent development. "
        else:  # Mixed or balanced
            holistic += (
                "With a balanced distribution of elements, this pattern suggests "
            )
            holistic += (
                "a journey that integrates openness, transformation, and structure "
            )
            holistic += "in a complementary and harmonious way. "

        # Return the complete analysis
        return {
            "distribution": distribution,
            "patterns": patterns,
            "narrative": narrative,
            "holistic": holistic,
        }
