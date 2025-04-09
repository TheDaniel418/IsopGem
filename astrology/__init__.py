"""Astrology pillar for IsopGem.

This pillar provides astrological calculation and chart visualization capabilities including:
- Birth chart creation and analysis
- Planetary position calculations
- House system calculations
- Aspect calculations and pattern recognition
- Chart visualization with interactive wheel display

Key components:
- Models: CelestialBody, ZodiacSign, House, Chart, Aspect
- Services: ChartService, PlanetaryPositionService, AspectService
- UI Components: BirthChartPanel, ChartWheelWidget, PlanetaryPositionsWidget
"""

# Version
__version__ = "0.1.0"

# Expose key components
from astrology.models.celestial_body import CelestialBodyType, CelestialBody, Planet
from astrology.models.zodiac import Element, Modality, Polarity, ZodiacSign, House, HouseSystem
from astrology.models.chart import ChartType, Chart, NatalChart, TransitChart, CompositeChart
from astrology.models.aspect import AspectType, Aspect, AspectPattern

from astrology.services.chart_service import ChartService
from astrology.services.location_service import LocationService, Location
from astrology.services.kerykeion_service import KerykeionService

from astrology.ui.astrology_tab import AstrologyTab
from astrology.ui.dialogs.birth_chart_window import BirthChartWindow
from astrology.ui.dialogs.location_search_window import LocationSearchWindow
from astrology.ui.widgets.birth_chart_widget import BirthChartWidget
from astrology.ui.widgets.location_search_widget import LocationSearchWidget

__all__ = [
    # Models
    "CelestialBodyType",
    "CelestialBody",
    "Planet",
    "Element",
    "Modality",
    "Polarity",
    "ZodiacSign",
    "House",
    "HouseSystem",
    "ChartType",
    "Chart",
    "NatalChart",
    "TransitChart",
    "CompositeChart",
    "AspectType",
    "Aspect",
    "AspectPattern",

    # Services
    "ChartService",
    "KerykeionService",

    # UI Components
    "AstrologyTab",
    "BirthChartWindow",
    "BirthChartWidget",
    "LocationSearchWindow",
    "LocationSearchWidget",

    # Services
    "LocationService",
    "Location"
]