import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import PolygonSelector
import ipywidgets as widgets
from matplotlib.path import Path
from IPython.display import display

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.widgets import PolygonSelector
import scanpy as sc
import ipywidgets as widgets
import numpy as np

class ScanpyInteractivePolygonApp:
    def __init__(
        self,
        adata,
        spot_size: int = 5,
        color=None,
        subsample: bool = False,
    ):
        self.adata = adata
        self.color = color

        # Do we have z information?
        if adata.obsm["spatial"].shape[1] < 3:
            raise ValueError("obsm['spatial'] must have 3 columns (x, y, z)")

        # Sub-sampling for faster plotting
        self.num_to_sample_for_plot = (
            max(1, len(adata) // 50_000) if subsample else 1
        )

        # Scale factor (same logic you already had)
        if "spatial" in adata.uns:
            lib = list(adata.uns["spatial"].keys())[0]
            self.scale_factor = adata.uns["spatial"][lib]["scalefactors"][
                "tissue_hires_scalef"
            ]
            self.has_native_spot_size = True
        else:
            self.scale_factor = 1.0
            self.has_native_spot_size = False
            self.spot_size = spot_size

        # Extract z-coordinate range
        self.z_values = np.unique(adata.obsm["spatial"][:, 2].astype(int))
        self.current_z = int(self.z_values[0])

        # ---------- widgets ----------
        self.z_slider = widgets.IntSlider(
            description="z-plane",
            min=int(self.z_values.min()),
            max=int(self.z_values.max()),
            step=1,
            value=self.current_z,
        )
        self.z_slider.observe(self.update_z_slice, names="value")

        self.dz_slider = widgets.IntSlider(
            description="± Δz",
            min=0,
            max=int(self.z_values.max() - self.z_values.min()),
            step=1,
            value=0,
            style={"description_width": "60px"},
        )

        # Buttons
        self.filter_button = widgets.Button(description="Filter ROI")
        self.filter_button.on_click(self.filter_spots)

        self.clear_button = widgets.Button(description="Clear ROI")
        self.clear_button.on_click(self.clear_selection)

        # Layout
        display(widgets.HBox([self.z_slider, self.dz_slider]))
        display(widgets.HBox([self.filter_button, self.clear_button]))

        # ---------- figure ----------
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.plot_slice()  # initial draw

        # Polygon selector
        self.polygon_selector = PolygonSelector(
            self.ax,
            self.on_select,
            useblit=True,
            props=dict(color="red", linewidth=2),
        )

        # state
        self.polygon_path = None
        self.selected_spots = None

    # ---------- plotting helpers ----------
    def plot_slice(self):
        """Plot XY positions for the current z plane."""
        self.ax.clear()
        mask = self.adata.obsm["spatial"][:, 2].astype(int) == self.current_z
        adata_z = self.adata[mask][:: self.num_to_sample_for_plot]

        kwargs = dict(color=self.color, ax=self.ax, show=False, title=f"z = {self.current_z}")
        if not self.has_native_spot_size:
            kwargs["spot_size"] = self.spot_size

        sc.pl.spatial(adata_z, **kwargs)
        self.ax.set_title("Draw Polygon ROI on Spots")
        self.fig.canvas.draw_idle()

    def update_z_slice(self, change):
        """Callback when z slider is moved."""
        self.current_z = int(change["new"])
        # Remove any existing polygon drawing when we change slices
        [patch.remove() for patch in list(self.ax.patches)]
        self.polygon_path = None
        self.plot_slice()

    # ---------- ROI handling ----------
    def on_select(self, verts):
        self.polygon_path = Path(verts)
        poly = plt.Polygon(verts, closed=True, fill=False, edgecolor="red", linewidth=2)
        self.ax.add_patch(poly)
        self.fig.canvas.draw_idle()

    def filter_spots(self, _):
        if self.polygon_path is None:
            print("Draw an ROI before filtering.")
            return

        coords = self.adata.obsm["spatial"] * self.scale_factor
        xy = coords[:, :2]
        z = coords[:, 2].astype(int)

        in_roi = self.polygon_path.contains_points(xy)
        in_z   = np.abs(z - self.current_z) <= self.dz_slider.value
        mask   = in_roi & in_z

        self.selected_spots = self.adata[mask].copy()
        print(f"{mask.sum()} spots within ROI, Δz = ±{self.dz_slider.value}")

        # Visualise the projection (flattened onto XY)
        if self.has_native_spot_size:
            sc.pl.spatial(
                self.selected_spots[:: self.num_to_sample_for_plot],
                color=None,
                show=True,
                title="Projected ROI Spots",
            )
        else:
            sc.pl.spatial(
                self.selected_spots[:: self.num_to_sample_for_plot],
                color=None,
                show=True,
                title="Projected ROI Spots",
                spot_size=self.spot_size,
            )

    def clear_selection(self, _):
        [patch.remove() for patch in list(self.ax.patches)]
        self.polygon_path = None
        self.selected_spots = None
        self.fig.canvas.draw_idle()
        print("Cleared the ROI selection.")
