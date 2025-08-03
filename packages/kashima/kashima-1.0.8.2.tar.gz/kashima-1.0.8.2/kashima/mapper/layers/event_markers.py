from __future__ import annotations
import html, numpy as np, pandas as pd, folium
from folium.plugins import MarkerCluster
from ..config import EventConfig
from ._layer_base import MapLayer


class EventMarkerLayer(MapLayer):
    """
    Circle markers whose colour and radius follow a discrete Mw scheme.

    • Colour look‑up     → EventConfig.dot_palette   (label → hex)
    • Radius look‑up     → EventConfig.dot_sizes     (label → px)
    Labels are generated as ASCII strings, e.g. "4.5-5.0", ">=8.5".
    """

    # ------------------------------------------------------------------ init
    def __init__(
        self,
        events_df: pd.DataFrame,
        event_cfg: EventConfig,
        legend_map: dict[str, str],
        tooltip_fields: list[str] | None = None,
        clustered: bool = False,
        show: bool = True,
    ):
        self.df = events_df
        self.cfg = event_cfg
        self.legend = legend_map
        self.tooltip_fields = tooltip_fields or ["place"]
        self.clustered = clustered
        self.show = show

        # fallback continuous scale for when no discrete palette is supplied
        self._cmap = None
        if not self.cfg.dot_palette:
            import matplotlib.pyplot as plt, branca

            cmap = plt.get_cmap(self.cfg.color_palette)
            if self.cfg.color_reversed:
                cmap = cmap.reversed()
            colours = [cmap(i / cmap.N) for i in range(cmap.N)]
            vmin = self.cfg.vmin or self.df["mag"].min()
            vmax = self.cfg.vmax or self.df["mag"].max()
            self._cmap = branca.colormap.LinearColormap(colours, vmin=vmin, vmax=vmax)

    # ---------------------------------------------------------------- helpers
    def _label(self, mag: float) -> str | None:
        """Return the magnitude‑bin label for *mag* (ASCII)."""
        bins = self.cfg.mag_bins or []
        if not bins:
            return None
        for i in range(len(bins) - 1):
            lo, hi = bins[i], bins[i + 1]
            if lo <= mag < hi:
                return f"{lo:.1f}-{hi:.1f}"
        return f">={bins[-1]:.1f}"

    def _colour(self, mag: float) -> str:
        lbl = self._label(mag)
        if lbl and self.cfg.dot_palette:
            return self.cfg.dot_palette.get(lbl, "#636363")
        return self._cmap(mag) if self._cmap else "blue"

    def _radius(self, mag: float) -> int:
        lbl = self._label(mag)
        if lbl and self.cfg.dot_sizes:
            return self.cfg.dot_sizes.get(lbl, 4)
        base = 2
        scale = self.cfg.scaling_factor
        vmin = self.cfg.vmin or self.df["mag"].min()
        return int(base + scale * max(0, mag - vmin))

    @staticmethod
    def _fmt(val):
        if isinstance(val, (float, np.floating)):
            return f"{val:.3f}" if 1e-3 < abs(val) < 1e4 else f"{val:.2e}"
        if isinstance(val, pd.Timestamp):
            return val.strftime("%Y-%m-%d %H:%M:%S")
        return str(val)

    # ---------------------------------------------------------------- builder
    def to_feature_group(self) -> folium.FeatureGroup:
        grp = (
            MarkerCluster(name="Events", show=self.show)
            if self.clustered
            else folium.FeatureGroup(name="Events", show=self.show)
        )

        esc = (
            lambda s: (s or "")
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("\n", "\\n")
        )

        for _, r in self.df.iterrows():
            colour = self._colour(r.mag)
            radius = self._radius(r.mag)

            tooltip = " | ".join(
                esc(str(r.get(f, ""))).strip()
                for f in self.tooltip_fields
                if pd.notnull(r.get(f, ""))
            )

            lines = [
                f"<b>{html.escape(self.legend.get(c, c))}:</b> {html.escape(self._fmt(r[c]))}"
                for c in self.legend
                if c in r and pd.notnull(r[c])
            ]
            if "Repi" in r and np.isfinite(r.Repi):
                lines.append(f"<b>Epicentral Distance:</b> {r.Repi:.1f}&nbsp;km")
            popup = folium.Popup("<br>".join(lines), max_width=300)

            folium.CircleMarker(
                location=[r.latitude, r.longitude],
                radius=radius,
                color=colour,
                fill=True,
                fill_opacity=0.7,
                tooltip=tooltip or None,
                popup=popup,
            ).add_to(grp)

        return grp
