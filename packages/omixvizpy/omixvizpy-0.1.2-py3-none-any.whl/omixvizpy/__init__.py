"""
omixvizpy: A Python package for omics data visualization

This package provides tools for visualizing omics data, particularly PCA plots.
"""

__version__ = "0.1.2"
__author__ = "Zhen Lu"
__email__ = "luzh29@mail2.sysu.edu.cn"

from .pca_plotting import plot_pca

__all__ = ["plot_pca"]
