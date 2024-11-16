from functools import partial

from cellestial.single.core.dimensional import dimension, expression

# alias
dim = dimension
# subsets (partials)
umap = partial(dimension, dimensions="umap")
pca = partial(dimension, dimensions="pca")
tsne = partial(dimension, dimensions="tsne")


__all__ = [
    "dim",
    "umap",
    "pca",
    "tsne",
    "expression",
]