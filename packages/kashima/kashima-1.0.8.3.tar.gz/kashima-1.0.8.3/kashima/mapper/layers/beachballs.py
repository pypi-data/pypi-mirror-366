from __future__ import annotations
import base64, io, logging, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import folium
from folium.features import CustomIcon
from obspy.imaging.beachball import beach

logger = logging.getLogger(__name__)


class BeachballLayer:
    """
    Focal‑mechanism icons driven by a key→(label,color) dictionary.
    """

    _CACHE: dict[str, str] = {}
    _warned = 0

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        fault_style_meta: dict[str, dict[str, str]],
        mag_bins: list[float] | None,
        size_map: dict[str, int] | None = None,
        base_size: int = 12,
        scaling_factor: float = 2.0,
        vmin: float | None = None,
        show: bool = True,
    ):
        cols = ["mrr", "mtt", "mpp", "mrt", "mrp", "mtp"]
        self.df = (
            df.dropna(subset=cols)
            .loc[df[cols].apply(lambda r: np.isfinite(r.values).all(), axis=1)]
            .copy()
        )
        self.meta = fault_style_meta
        self.bins = mag_bins or []
        self.size_map = size_map or {}
        self.base = base_size
        self.scaling = scaling_factor
        self.vmin = vmin if vmin is not None else self.df["mag"].min()
        self.show = show

    # ----------------------------------------------------------- helpers
    def _label(self, mag: float) -> str | None:
        for i in range(len(self.bins) - 1):
            lo, hi = self.bins[i], self.bins[i + 1]
            if lo <= mag < hi:
                return f"{lo:.1f}-{hi:.1f}"
        return f">={self.bins[-1]:.1f}" if self.bins else None

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
        facecolor = self.meta.get(r.fault_style, {}).get("color", "#636363")

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

    # ----------------------------------------------------------- popup
    def _popup(self, r) -> folium.Popup:
        meta = self.meta.get(r.fault_style, {})
        label = meta.get("label", r.fault_style)
        html = (
            f"<b>Magnitude:</b> {r.mag:.2f}<br>"
            f"<b>Fault Style:</b> {label}"
        )
        return folium.Popup(html, max_width=300)

    # ----------------------------------------------------------- builder
    def to_feature_group(self) -> folium.FeatureGroup:
        grp = folium.FeatureGroup(name="Beachballs", show=self.show)
        for _, r in self.df.iterrows():
            uri = self._icon_uri(r)
            if not uri:
                continue
            sz = self._size(r.mag)
            folium.Marker(
                location=[r.latitude, r.longitude],
                icon=CustomIcon(uri, icon_size=(sz, sz), icon_anchor=(sz // 2, sz // 2)),
                tooltip=f"Mw {r.mag:.1f}",
                popup=self._popup(r),
            ).add_to(grp)
        return grp
