from __future__ import annotations
import base64, io, logging, numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
from matplotlib.collections import PatchCollection
import folium
from folium.features import CustomIcon
from obspy.imaging.beachball import beach

logger = logging.getLogger(__name__)


DEFAULT_REGIME_COLORS = {
    "Normal": "#3182bd",
    "Reverse": "#de2d26",
    "Strike-slip": "#238b45",
    "Normal-Strike-slip": "#6baed6",
    "Reverse-Strike-slip": "#fc9272",
    "Oblique": "#ff8c00",
    "Undetermined": "#636363",
}


class BeachballLayer:
    """
    Focal‑mechanism icons.

    • Diameter look‑up → *size_map* (label → px) **or**
      fallback to   base_size + scaling_factor·(Mw - vmin)
    • Colour look‑up   → regime_colors (dict)
    """

    _CACHE: dict[str, str] = {}
    _warned = 0

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        size_map: dict[str, int] | None = None,
        mag_bins: list[float] | None = None,
        regime_colors: dict[str, str] | None = None,
        base_size: int = 12,
        scaling_factor: float = 2.0,
        vmin: float | None = None,
        show: bool = True,
        legend_map: dict[str, str] | None = None,
    ):
        cols = ["mrr", "mtt", "mpp", "mrt", "mrp", "mtp"]
        self.df = (
            df.dropna(subset=cols)
            .loc[df[cols].apply(lambda r: np.isfinite(r.values).all(), axis=1)]
            .copy()
        )
        self.show = show
        self.size_map = size_map or {}
        self.bins = mag_bins or []
        self.base = base_size
        self.scaling = scaling_factor
        self.vmin = vmin if vmin is not None else self.df["mag"].min()
        self.legend_map = legend_map or {}
        self.colors = (regime_colors or DEFAULT_REGIME_COLORS).copy()

    # ---------------------------------------------------------------- helpers
    def _label(self, mag: float) -> str | None:
        for i in range(len(self.bins) - 1):
            lo, hi = self.bins[i], self.bins[i + 1]
            if lo <= mag < hi:
                return f"{lo:.1f}-{hi:.1f}"
        if self.bins:
            return f">={self.bins[-1]:.1f}"
        return None

    def _size(self, mag: float) -> int:
        lbl = self._label(mag)
        if lbl and lbl in self.size_map:
            return self.size_map[lbl]
        return int(self.base + self.scaling * max(0, mag - self.vmin))

    def _icon_uri(self, r) -> str | None:
        eid = r["event_id"]
        if eid in self._CACHE:
            return self._CACHE[eid]

        mt = [r.mrr, r.mtt, r.mpp, r.mrt, r.mrp, r.mtp]
        size_px = self._size(r.mag)
        facecolor = self.colors.get(
            r.fault_style, DEFAULT_REGIME_COLORS["Undetermined"]
        )

        try:
            fig_or_patch = beach(
                mt, size=size_px, linewidth=0.6, facecolor=facecolor, edgecolor="black"
            )
            if isinstance(fig_or_patch, PatchCollection):
                fig = plt.figure(figsize=(size_px / 72, size_px / 72), dpi=72)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_axis_off()
                ax.add_collection(fig_or_patch)
                ax.set_aspect("equal")
                ax.autoscale_view()
            else:
                fig = fig_or_patch

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=72, transparent=True)
            plt.close(fig)

        except Exception as e:
            if self._warned < 10:
                logger.warning("Skip beachball for %s: %s", eid, e)
                self._warned += 1
            return None

        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        self._CACHE[eid] = uri
        return uri

    def _popup(self, r) -> folium.Popup:
        lg = self.legend_map
        lines = [
            f"<b>{lg.get('mag','Magnitude')}:</b> {r.mag:.2f}",
            f"<b>{lg.get('fault_style','Fault Style')}:</b> {r.fault_style}",
        ]
        if "Repi" in r and np.isfinite(r.Repi):
            lines.append(f"<b>Epicentral Distance:</b> {r.Repi:.1f}&nbsp;km")
        return folium.Popup("<br>".join(lines), max_width=300)

    # ---------------------------------------------------------------- builder
    def to_feature_group(self) -> folium.FeatureGroup:
        grp = folium.FeatureGroup(name="Beachballs", show=self.show)
        for _, r in self.df.iterrows():
            uri = self._icon_uri(r)
            if not uri:
                continue
            sz = self._size(r.mag)
            folium.Marker(
                location=[r.latitude, r.longitude],
                icon=CustomIcon(
                    uri, icon_size=(sz, sz), icon_anchor=(sz // 2, sz // 2)
                ),
                tooltip=f"Mw {r.mag:.1f}",
                popup=self._popup(r),
            ).add_to(grp)
        logger.info("Beachball layer: %d icons drawn.", len(grp._children))
        return grp
