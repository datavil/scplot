from __future__ import annotations

from typing import Literal

# Core scverse libraries
import polars as pl
from cellestial.decorators.util import interactive, theme_dimension
# Data retrieval
import scanpy as sc
from lets_plot import *
from lets_plot import (
    LetsPlot,
    aes,
    element_blank,
    element_line,
    element_text,
    geom_point,
    ggplot,
    ggsize,
    ggtb,
    labs,
    layer_tooltips,
    scale_color_continuous,
    scale_color_hue,
    theme,
    theme_classic,
)

LetsPlot.setup_html()


@interactive
@theme_dimension
def dimension(
    data,
    key: Literal["leiden", "louvain"] | str = "leiden",
    *,
    dimensions: Literal["umap", "pca", "tsne"] = "umap",
    size: float = 0.8,
    interactive: bool = False,
    color_low: str = "#ffffff",
    color_high: str = "#377eb8",
    arrow_axis: bool = True,
    arrow_size: float= 0.25,
    arrow_color: str = "#3f3f3f",
) -> PlotSpec:
    # Handling Data tpyes
    if not isinstance(data, sc.AnnData):
        raise ValueError("data must be an AnnData object")
    
    key_col = key

    # get the coordinates of the cells in the dimension reduced space
    frame = pl.from_numpy(
        data.obsm[f"X_{dimensions}"], schema=[f"{dimensions}1", f"{dimensions}2"]
    ).with_columns(pl.Series("ID", data.obs_names))

    # -------------------------- IF IT IS A CLUSTER --------------------------
    if key in ["leiden", "louvain"]:  # if it is a clustering
        key_col = "Cluster" # update the key column name if it is a cluster
        frame = frame.with_columns(
            pl.Series("ID", data.obs_names), pl.Series(key_col, data.obs[key])
        )
        # cluster scatter
        scttr = (
            ggplot(data=frame)
            + geom_point(
                aes(x=f"{dimensions}2", y=f"{dimensions}1", color=key_col),
                size=size,
                tooltips=layer_tooltips(["ID", key_col]),
            )
            + scale_color_hue()
            + labs(
                x=f"{dimensions}2".upper(), y=f"{dimensions}1".upper()
            )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
            + scale_shape(
                guide = guide_legend(nrow=3)
            )
        )
    # -------------------------- IF IT IS A GENE --------------------------
    elif key in data.var_names:  # if it is a gene
        # adata.X is a matrix , axis0 is cells, axis1 is genes
        # find the index of the gene
        index = data.var_names.get_indexer(
            data.var_names[data.var_names.str.startswith(key)]
        )  # get the index of the gene
        frame = frame.with_columns(
            pl.Series("ID", data.obs_names),
            pl.Series(key, data.X[:, index].flatten().astype("float64")),
        )
        scttr = (
            ggplot(data=frame)
            + geom_point(
                aes(x=f"{dimensions}2", y=f"{dimensions}1", color=key),
                size=size,
                tooltips=layer_tooltips(["ID", key]),
            )
            + scale_color_continuous(low=color_low, high=color_high)
            + labs(
                x=f"{dimensions}2".upper(), y=f"{dimensions}1".upper()
            )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
        )
    # -------------------------- GEOM SEGMENT --------------------------
    if arrow_axis:
        x_max = frame.select(f"{dimensions}2").max().item()
        x_min = frame.select(f"{dimensions}2").min().item()
        y_max = frame.select(f"{dimensions}1").max().item()
        y_min = frame.select(f"{dimensions}1").min().item()

        # find total difference between the max and min for both axis
        x_diff = x_max - x_min
        y_diff = y_max - y_min        

        # find the ends of the arrows
        xend = x_min + arrow_size * x_diff
        yend = y_min + arrow_size * y_diff

        # adjust bottom ends of arrows
        x_adjusted = x_min - x_diff * 0.005
        y_adjusted = y_min - y_diff * 0.005

        # X axis
        scttr += geom_segment(
            x=x_adjusted, y=y_min, xend=xend, yend=y_min,
            color=arrow_color,
            size=3,
            arrow=arrow(20),
        )
        # Y axis
        scttr += geom_segment(
            x=x_min, y=y_adjusted, xend=x_min, yend=yend,
            color=arrow_color,
            size=3,
            arrow=arrow(20),
        )



    # -------------------------- NOT A GENE OR CLUSTER --------------------------
    else:
        msg = f"'{key}' is not present in cluster names nor gene names"
        raise msg

    return scttr


def test_dimension():
    import os
    import scanpy as sc
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent.parent) # to project root
    data = sc.read("data/pbmc3k_pped.h5ad")

    umap_plot = dimension(data, key="leiden", dimensions="umap", interactive=True)
    umap_plot.to_html("plots/test_dim_umap.html")

if __name__ == "__main__":
    test_dimension()