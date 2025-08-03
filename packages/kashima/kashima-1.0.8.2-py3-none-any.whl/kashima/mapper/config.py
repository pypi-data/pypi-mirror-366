# file: config.py

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0  # Earth's radius in kilometers

# ----------------------------------------------------------------
# Extended TILE_LAYERS dict to include OpenStreetMap, Stamen, etc.
# ----------------------------------------------------------------


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


# ----------------------------------------------------------------
# Each key -> a dict with 'tiles' (the actual Folium identifier or URL)
# and 'attr' for attribution
# ----------------------------------------------------------------
# mapper/config.py  ── basemap options used by EventMap
TILE_LAYER_CONFIGS = {
    # ── Esri portfolio ───────────────────────────────────────────────
    TILE_LAYERS["ESRI_SATELLITE"]: {
        "tiles": "Esri.WorldImagery",
        "attr": "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, etc.",
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
    # ── OpenStreetMap & derivatives ─────────────────────────────────
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
    # ── Carto styles ────────────────────────────────────────────────
    TILE_LAYERS["CARTO_POSITRON"]: {
        "tiles": "CartoDB positron",
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
    TILE_LAYERS["CARTO_DARK"]: {
        "tiles": "CartoDB dark_matter",
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
    TILE_LAYERS["CARTO_VOYAGER"]: {
        "tiles": "CartoDB voyager",  # built-in provider shortcut
        "attr": "© CartoDB © OpenStreetMap contributors",
    },
}


# kashima/mapper/config.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MapConfig:
    project_name: str
    client: str
    latitude: float
    longitude: float
    radius_km: float

    # map controls
    base_zoom_level: int = 8
    min_zoom_level: int = 4
    max_zoom_level: int = 18
    default_tile_layer: str = "OpenStreetMap"

    # epicentral circles
    epicentral_circles_title: str = "Epicentral Distance"
    epicentral_circles: int = 5
    MIN_EPICENTRAL_CIRCLES: int = 3
    MAX_EPICENTRAL_CIRCLES: int = 25

    # NEW – let the caller decide whether to auto‑fit after drawing
    auto_fit_bounds: bool = True
    lock_pan: bool = False  # freeze panning when True


# … (rest of config.py unchanged) …


# … previous imports / TILE_LAYER_CONFIGS unchanged …


# kashima/mapper/config.py   –  EventConfig only
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class EventConfig:
    """
    Style + filtering knobs for EventMap.

    New in v‑2025‑06‑30
    -------------------
    • mag_bins            list[float]   manual magnitude breaks (ascending)
    • dot_palette         dict[str,str] fixed colors for the magnitude bins
    • beachball_palette   dict[str,str] colors per faulting regime
    • dot_sizes           dict[str,int] fixed diameters per magnitude bin
    • beachball_sizes     dict[str,int] fixed diameters per magnitude bin
    """

    # ------------------------------------------------------------------
    # 1) marker / heat‑map colour map (kept for backward‑compat)
    # ------------------------------------------------------------------
    color_palette: str = "magma"
    color_reversed: bool = False

    # ------------------------------------------------------------------
    # 2) fixed discrete scale  (preferred – leave at None to ignore)
    # ------------------------------------------------------------------
    mag_bins: List[float] | None = None  # [4.0, 4.5, …, 9.0]
    dot_palette: dict[str, str] | None = None  # bin‑label -> hex
    beachball_palette: dict[str, str] | None = None  # regime  -> hex
    dot_sizes: dict[str, int] | None = None  # bin‑label -> px
    beachball_sizes: dict[str, int] | None = None  # bin‑label -> px

    # ------------------------------------------------------------------
    # 3) radii & filters
    # ------------------------------------------------------------------
    scaling_factor: float = 2.0  # still used if mag_bins is None
    event_radius_multiplier: float = 1.0
    vmin: Optional[float] = None
    vmax: Optional[float] = None

    # ------------------------------------------------------------------
    # 4) heat‑map visuals
    # ------------------------------------------------------------------
    heatmap_radius: int = 20
    heatmap_blur: int = 15
    heatmap_min_opacity: float = 0.5

    # ------------------------------------------------------------------
    # 5) legend & visibility defaults
    # ------------------------------------------------------------------
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


__version__ = "1.0.1.7"
