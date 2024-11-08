from __future__ import annotations

from typing import Literal
# Core scverse libraries
import polars as pl

# Data retrieval
import scanpy as sc
from lets_plot import (
    LetsPlot,
    aes,
    element_blank,
    element_line,
    element_text,
    geom_blank,
    geom_jitter,
    geom_point,
    geom_violin,
    gggrid,
    ggplot,
    ggsize,
    ggtb,
    guide_colorbar,
    guides,
    labs,
    layer_tooltips,
    scale_color_continuous,
    scale_color_gradient,
    scale_color_hue,
    scale_color_viridis,
    theme,
    theme_classic,
)

LetsPlot.setup_html()



def scatter(
    data,
    key: str = "leiden",
    *,
    dimensions: Literal["umap", "pca", "tsne"] = "umap",
    size=0.8,
    interactive: bool = False,
    color_low: str = "#ffffff",
    color_high: str = "#377eb8",
):
    if not isinstance(data, sc.AnnData):
        raise ValueError("data must be an AnnData object")
    # get the coordinates of the cells in the dimension reduced space
    frame = pl.from_numpy(
        data.obsm[f"X_{dimensions}"], schema=[f"{dimensions}1", f"{dimensions}2"]
    ).with_columns(pl.Series("ID", data.obs_names))

    # deterministic names
    if key in ["leiden", "louvain"]:  # if it is a clustering
        frame = frame.with_columns(
            pl.Series("ID", data.obs_names), pl.Series("Cluster", data.obs[key])
        )
        # cluster scatter
        scttr = (
            ggplot(data=frame)
            + geom_point(
                aes(x=f"{dimensions}2", y=f"{dimensions}1", color="Cluster"),
                size=size,
                tooltips=layer_tooltips(["ID", "Cluster"]),
            )
            + scale_color_hue()
        )
    else:  # if it is a gene
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
            + theme_classic()
        )

    # add common layers
    scttr += (
        ggsize(700, 500)
        + theme_classic()
        + theme(
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            #   axis_ticks_y=element_blank(),
            #   axis_ticks_x=element_blank(),
            text=element_text(color="#1f1f1f", family="Arial", size=12, face="bold"),
            title=element_text(color="#1f1f1f", family="Arial"),
            axis_title_x=element_text(
                color="#3f3f3f",
                family="Arial",
                size=16,
            ),
            axis_title_y=element_text(color="#3f3f3f", family="Arial", size=16),
            legend_text=element_text(color="#1f1f1f", size=10, face="plain"),
            axis_line=element_line(color="#3f3f3f", size=0.2),
        )
        + labs(
            x=f"{dimensions}2".upper(), y=f"{dimensions}1".upper()
        )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
    )

    if interactive:
        return scttr + ggtb()
    else:
        return scttr
