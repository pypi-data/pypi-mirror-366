"""
kashima.mapper.config
=====================

• All global constants used across the package
• Dataclass containers for map, event, fault, station, blast configuration
• Default fault‑style metadata (key → {label, colour})

This file is a **drop‑in replacement** – copy it verbatim.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List

# ----------------------------------------------------------------------
#  0. Basic constants
# ----------------------------------------------------------------------
EARTH_RADIUS_KM = 6371.0          # average Earth radius

# ----------------------------------------------------------------------
#  1. Tile‑layer catalogue (unchanged from original package)
# ----------------------------------------------------------------------
TILE_LAYERS = {
    "OPENSTREETMAP": "OpenStreetMap",
    "OPENSTREETMAP_HOT": "OpenStreetMap.HOT",
    "OPEN_TOPO": "OpenTopoMap",
    "CYCL_OSM": "CyclOSM",
    "CARTO_POSITRON": "CartoDB positron",
    "CARTO_DARK": "CartoDB dark_matter",
    "CARTO_VOYAGER": "CartoDB voyager",
    "ESRI_SATELLITE": "Esri.WorldImagery",
    "ESRI_STREETS": "Esri.WorldStreetMap",
    "ESRI_TERRAIN": "Esri.WorldTerrain",
    "ESRI_RELIEF": "Esri.WorldShadedRelief",
    "ESRI_NATGEO": "Esri.NatGeoWorldMap",
}

TILE_LAYER_CONFIGS = {
    TILE_LAYERS["ESRI_SATELLITE"]: {
        "tiles": "Esri.WorldImagery",
        "attr": "Tiles © Esri — Source: Esri, i‑cubed, USDA, USGS, AEX, GeoEye, etc.",
    },
    TILE_LAYERS["ESRI_STREETS"]: {
        "tiles": "Esri.WorldStreetMap",
        "attr": "Tiles © Esri — Source: Esri, DeLorme, NAVTEQ, etc.",
    },
    TILE_LAYERS["ESRI_TERRAIN"]: {
        "tiles": "Esri.WorldTerrain",
        "attr": "Tiles © Esri — Source: USGS, Esri, TANA, DeLorme, etc.",
    },
    TILE_LAYERS["ESRI_RELIEF"]: {
        "tiles": "Esri.WorldShadedRelief",
        "attr": "Tiles © Esri — Source: Esri",
    },
    TILE_LAYERS["ESRI_NATGEO"]: {
        "tiles": "Esri.NatGeoWorldMap",
        "attr": "Tiles © Esri — National Geographic, Esri, DeLorme, NAVTEQ, etc.",
    },
    TILE_LAYERS["OPENSTREETMAP"]: {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors",
    },
    TILE_LAYERS["OPENSTREETMAP_HOT"]: {
        "tiles": "OpenStreetMap.HOT",
        "attr": "© OpenStreetMap contributors — Humanitarian style",
    },
    TILE_LAYERS["OPEN_TOPO"]: {
        "tiles": "OpenTopoMap",
        "attr": "Map data © OpenStreetMap contributors, SRTM — Map style © OpenTopoMap",
    },
    TILE_LAYERS["CYCL_OSM"]: {
        "tiles": "CyclOSM",
        "attr": "© CyclOSM, OpenStreetMap contributors",
    },
    TILE_LAYERS["CARTO_POSITRON"]: {
        "tiles": "CartoDB positron",
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
    TILE_LAYERS["CARTO_DARK"]: {
        "tiles": "CartoDB dark_matter",
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
    TILE_LAYERS["CARTO_VOYAGER"]: {
        "tiles": "CartoDB voyager",
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
}

# ----------------------------------------------------------------------
#  2. Fault‑style keys and default metadata  (ASCII only – stable keys)
# ----------------------------------------------------------------------
DEFAULT_FAULT_STYLE_META: dict[str, dict[str, str]] = {
    "N":   {"label": "Normal",                 "color": "#3182bd"},
    "R":   {"label": "Reverse",                "color": "#de2d26"},
    "SS":  {"label": "Strike-slip",            "color": "#31a354"},
    "NSS": {"label": "Normal-Strike-slip",     "color": "#6baed6"},
    "RSS": {"label": "Reverse-Strike-slip",    "color": "#fc9272"},
    "O":   {"label": "Oblique",                "color": "#bdbdbd"},
    "U":   {"label": "Undetermined",           "color": "#969696"},
}

# ----------------------------------------------------------------------
#  3. Dataclass containers
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MapConfig:
    project_name: str
    client: str
    latitude: float
    longitude: float
    radius_km: float

    base_zoom_level: int = 8
    min_zoom_level: int = 4
    max_zoom_level: int = 18
    default_tile_layer: str = TILE_LAYERS["OPENSTREETMAP"]

    epicentral_circles: int = 5
    auto_fit_bounds: bool = True
    lock_pan: bool = False


@dataclass
class EventConfig:
    # 1) continuous colour map fallback
    color_palette: str = "magma"
    color_reversed: bool = False

    # 2) discrete Mw bins & styles
    mag_bins: List[float] | None = None
    dot_palette: dict[str, str] | None = None
    dot_sizes: dict[str, int] | None = None
    beachball_sizes: dict[str, int] | None = None

    # 3) fault‑style meta: key → {label, color}
    fault_style_meta: dict[str, dict[str, str]] = field(
        default_factory=lambda: DEFAULT_FAULT_STYLE_META.copy()
    )

    # 4) magnitude & distance filters
    scaling_factor: float = 2.0
    event_radius_multiplier: float = 1.0
    vmin: Optional[float] = None
    vmax: Optional[float] = None

    # 5) heat‑map parameters
    heatmap_radius: int = 20
    heatmap_blur: int = 15
    heatmap_min_opacity: float = 0.5

    # 6) legend & layer visibility
    legend_position: str = "bottomright"
    legend_title: str = "Magnitude (Mw)"

    show_events_default: bool = True
    show_heatmap_default: bool = False
    show_cluster_default: bool = False
    show_epicentral_circles_default: bool = False
    show_beachballs_default: bool = False
    beachball_min_magnitude: float | None = None


@dataclass
class FaultConfig:
    include_faults: bool = False
    faults_gem_file_path: str = ""
    regional_faults_color: str = "darkblue"
    regional_faults_weight: int = 3
    coordinate_system: str = "EPSG:4326"


@dataclass
class StationConfig:
    station_file_path: str = ""
    coordinate_system: str = "EPSG:4326"
    layer_title: str = "Seismic Stations"


@dataclass
class BlastConfig:
    blast_file_path: str = ""
    coordinate_system: str = "EPSG:32722"
    f_TNT: float = 0.90
    a_ML: float = 0.75
    b_ML: float = -1.0

# ----------------------------------------------------------------------
__version__ = "2.0.0"
