from __future__ import annotations

from typing import Literal

# Core scverse libraries
import polars as pl

# Data retrieval
import scanpy as sc
from lets_plot import *
from lets_plot import (
    LetsPlot,
    aes,
    arrow,
    element_blank,
    element_line,
    element_rect,
    element_text,
    geom_blank,
    geom_jitter,
    geom_point,
    geom_segment,
    geom_violin,
    gggrid,
    ggplot,
    ggsize,
    ggtb,
    guide_colorbar,
    guide_legend,
    guides,
    labs,
    layer_tooltips,
    scale_color_brewer,
    scale_color_continuous,
    scale_color_gradient,
    scale_color_hue,
    scale_color_viridis,
    scale_shape,
    theme,
    theme_classic,
)
from lets_plot.plot.core import PlotSpec
from scanpy import AnnData

from cellestial.themes import _THEME_DIMENSION
from cellestial.util import _add_arrow_axis, interactive

LetsPlot.setup_html()


@interactive
def dimension(
    data: AnnData,
    key: Literal["leiden", "louvain"] | str = "leiden",
    *,
    dimensions: Literal["umap", "pca", "tsne"] = "umap",
    size: float = 0.8,
    interactive: bool = False,  # used by interactive decorator
    cluster_name: str = "Cluster",
    barcode_name: str = "Barcode",
    color_low: str = "#e6e6e6",
    color_high: str = "#377eb8",
    axis_type: Literal["axis", "arrow"] | None = "arrow",
    arrow_length: float = 0.25,
    arrow_size: float = 3,
    arrow_color: str = "#3f3f3f",
    arrow_angle: float = 20,
) -> PlotSpec:
    # Handling Data tpyes
    if not isinstance(data, AnnData):
        msg = "data must be an `AnnData` object"
        raise TypeError(msg)

    # get the coordinates of the cells in the dimension reduced space

    # only take the first two dimensions (pca comes with more dimensions)
    frame = pl.from_numpy(
        data.obsm[f"X_{dimensions}"][:, :2], schema=[f"{dimensions}1", f"{dimensions}2"]
    ).with_columns(pl.Series(barcode_name, data.obs_names))

    # -------------------------- IF IT IS A CLUSTER --------------------------
    if key in ["leiden", "louvain"]:  # if it is a clustering
        # update the key column name if it is a cluster
        frame = frame.with_columns(
            pl.Series(barcode_name, data.obs_names), pl.Series(cluster_name, data.obs[key])
        )
        # cluster scatter
        scttr = (
            (
                ggplot(data=frame)
                + geom_point(
                    aes(x=f"{dimensions}1", y=f"{dimensions}2", color=cluster_name),
                    size=size,
                    tooltips=layer_tooltips([barcode_name, cluster_name]),
                )
                + labs(
                    x=f"{dimensions}1".upper(), y=f"{dimensions}2".upper()
                )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
            )
            + _THEME_DIMENSION
            + scale_color_brewer(palette="Set2")
        )  #
    # -------------------------- IF IT IS A GENE --------------------------
    elif key in data.var_names:  # if it is a gene
        # adata.X is a sparse matrix , axis0 is cells, axis1 is genes
        # find the index of the gene
        index = data.var_names.get_indexer(
            data.var_names[data.var_names.str.startswith(key)]
        )  # get the index of the gene
        frame = frame.with_columns(
            pl.Series(barcode_name, data.obs_names),
            pl.Series(key, data.X[:, index].flatten().astype("float32")),
        )
        scttr = (
            ggplot(data=frame)
            + geom_point(
                aes(x=f"{dimensions}1", y=f"{dimensions}2", color=key),
                size=size,
                tooltips=layer_tooltips([barcode_name, key]),
            )
            + scale_color_continuous(low=color_low, high=color_high)
            + labs(
                x=f"{dimensions}1".upper(), y=f"{dimensions}2".upper()
            )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
        ) + _THEME_DIMENSION
    # -------------------------- NOT A GENE OR CLUSTER --------------------------
    else:
        msg = f"'{key}' is not present in `cluster names` nor `gene names`"
        raise msg

    # handle arrow axis
    scttr += _add_arrow_axis(
        frame=frame,
        axis_type=axis_type,
        arrow_size=arrow_size,
        arrow_color=arrow_color,
        arrow_angle=arrow_angle,
        arrow_length=arrow_length,
        dimensions=dimensions,
    )

    return scttr


@interactive
def expression(
    data: AnnData,
    gene: str,
    *,
    dimensions: Literal["umap", "pca", "tsne"] = "umap",
    size: float = 0.8,
    interactive: bool = False,  # used by interactive decorator
    cluster_name: str = "Cluster",
    cluster_type: Literal["leiden", "louvain"] | None = None,
    barcode_name: str = "Barcode",
    color_low: str = "#e6e6e6",
    color_high: str = "#377eb8",
    axis_type: Literal["axis", "arrow"] | None = "arrow",
    arrow_length: float = 0.25,
    arrow_size: float = 3,
    arrow_color: str = "#3f3f3f",
    arrow_angle: float = 20,
) -> PlotSpec:
    # Handling Data tpyes
    if not isinstance(data, AnnData):
        msg = "data must be an `AnnData` object"
        raise TypeError(msg)

    # get the coordinates of the cells in the dimension reduced space

    # only take the first two dimensions (pca comes with more dimensions)
    frame = pl.from_numpy(
        data.obsm[f"X_{dimensions}"][:, :2], schema=[f"{dimensions}1", f"{dimensions}2"]
    ).with_columns(pl.Series(barcode_name, data.obs_names))

    if cluster_type is not None:
        if cluster_type in ["leiden", "louvain"]:
            frame = frame.with_columns(pl.Series(cluster_name, data.obs[cluster_type]))
        else:
            msg = f"'{cluster_type}' is not a valid cluster type"
            raise ValueError(msg)

    # -------------------------- IF IT IS A GENE --------------------------
    if gene in data.var_names:  # if it is a gene
        # adata.X is a sparse matrix, axis0 is cells, axis1 is genes
        # find the index of the gene
        index = data.var_names.get_indexer(
            data.var_names[data.var_names.str.startswith(gene)]
        )  # get the index of the gene
        frame = frame.with_columns(
            pl.Series(barcode_name, data.obs_names),
            pl.Series(gene, data.X[:, index].flatten().astype("float32")),
        )
        if cluster_type is not None:
            tooltips = [barcode_name, gene, cluster_name]
        else:
            tooltips = [barcode_name, gene]
        scttr = (
            ggplot(data=frame)
            + geom_point(
                aes(x=f"{dimensions}1", y=f"{dimensions}2", color=gene),
                size=size,
                tooltips=layer_tooltips(tooltips),
            )
            + scale_color_continuous(low=color_low, high=color_high)
            + labs(
                x=f"{dimensions}1".upper(), y=f"{dimensions}2".upper()
            )  # UMAP1 and UMAP2 rather than umap1 and umap2 etc.,
        ) + _THEME_DIMENSION
    # -------------------------- NOT A GENE OR CLUSTER --------------------------
    else:
        msg = f"'{gene}' is not present in `gene names`"
        raise Exception(msg)

    # handle arrow axis
    scttr += _add_arrow_axis(
        frame=frame,
        axis_type=axis_type,
        arrow_size=arrow_size,
        arrow_color=arrow_color,
        arrow_angle=arrow_angle,
        arrow_length=arrow_length,
        dimensions=dimensions,
    )

    return scttr


def test_dimension():
    import os
    from pathlib import Path

    import scanpy as sc

    os.chdir(Path(__file__).parent.parent.parent.parent)  # to project root
    data = sc.read("data/pbmc3k_pped.h5ad")

    dimension(data, key="leiden", dimensions="umap", interactive=True, axis_type=None).to_html(
        "plots/test_dim_umap_none.html"
    )
    dimension(data, key="leiden", dimensions="umap", interactive=True, axis_type="arrow").to_html(
        "plots/test_dim_umap_arrow.html"
    )
    dimension(data, key="leiden", dimensions="umap", interactive=True, axis_type="axis").to_html(
        "plots/test_dim_umap_axis.html"
    )

    return


def test_expression():
    import os
    from pathlib import Path

    import scanpy as sc

    os.chdir(Path(__file__).parent.parent.parent.parent)  # to project root
    data = sc.read("data/pbmc3k_pped.h5ad")
    expression(data, gene="MT-ND2", interactive=True).to_html("plots/test_expression.html")


if __name__ == "__main__":
    test_expression()
