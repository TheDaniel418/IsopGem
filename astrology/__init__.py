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

from astrology.models.aspect import Aspect, AspectPattern, AspectType

# Expose key components
from astrology.models.celestial_body import CelestialBody, CelestialBodyType, Planet
from astrology.models.chart import (
    Chart,
    ChartType,
    CompositeChart,
    NatalChart,
    TransitChart,
)
from astrology.models.zodiac import (
    Element,
    House,
    HouseSystem,
    Modality,
    Polarity,
    ZodiacSign,
)
from astrology.services.chart_service import ChartService
from astrology.services.kerykeion_service import KerykeionService
from astrology.services.location_service import Location, LocationService
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
    "Location",
]
