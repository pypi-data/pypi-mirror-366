# ScanPy / AnnData Interactive ROI Selector

This package implements a simple region of interest (ROI) selection plugin to Jupyter Lab.

## Installation

```bash
pip install scanpy-jupyter-roi
```

## Usage

In a Jupyter Notebook, 

```python

%matplotlib widget

from scanpy_jupyter_roi import ScanpyInteractivePolygonApp
import scanpy as sc

# Load your Scanpy data
adata = sc.datasets.visium_sge()  # Or load your own spatial data.

# Run the app
app = ScanpyInteractivePolygonApp(adata, spot_size=5, color=None, subsample=False)
```

You will end up with something like this:

![polygon](figures/polygon.png)

You can press "Filter ROI" to generate an `AnnData` object that is stored in `app.selected_spots` containing the filtered `AnnData` object with spots inside the boundary (TODO: allow removal of spots inside boundary, i.e. keep everything outside of that boundary for, say, artifact removal.)

The `app.selected_spots` is now your resultant `AnnData` object that you can utilize for downstream analysis.

You can view a full sample use case in `scanpy_jupyter_roi/tests/test_visium.ipynb`.

### Parameters

* You can set `spot_size` to control the radius of the plotted spots.

* You can set `color` if you have, say, a clustering stored in your `adata` with
key `"leiden"`, or if you want to color the plot by gene expression, etc.

* If you have a lot of spots (e.g. 1 million), you may experience latency in 
drawing the polygons. You can set `subsample` to `True` to decrease latency, 
at the expense of spot density (usually worth it; the subsample currently
takes 50,000 random spots on the slide.)

## Validation

Tested on:

* Visium

* Slide-Seq

Will test on other spatial sequencing platforms as they become avaialble,
and modify the app to accomodate any metadata they have.
