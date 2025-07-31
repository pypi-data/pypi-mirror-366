"""
OmixVizPy - PCA Plotting Module

This module provides functionality for visualizing PCA (Principal Component Analysis) results
with customizable covariate-based coloring and styling options.

Author: Zhen Lu
License: MIT
Version: 0.1.2
"""

from typing import Optional, List, Dict, Any
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns

# Set default plotting style for publication quality figures
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],
    "legend.fontsize": 12.5,
    "legend.title_fontsize": 13
})

def _get_covariate_settings(
    df: pd.DataFrame,
    cov_name: Optional[str],
    cov_levels: List[str],
    _DEFAULT_MARKERS: List[str],
    _DEFAULT_COLORS: List[str]
) -> Dict[str, Any]:
    """
    Internal function to process covariate settings for PCA visualization.
    
    Args:
        df: DataFrame containing the covariate data
        cov_name: Name of the covariate column
        cov_levels: List of expected covariate levels
        _DEFAULT_MARKERS: List of available markers
        _DEFAULT_COLORS: List of available colors
        
    Returns:
        Dictionary containing processed covariate settings
    """
    if cov_name is None:
        return {
            "uniq_count": 0,
            "legend_label": {},
            "sorted_hue_order": [],
            "new_hue_order": [],
            "markers_to_use": [],
            "palette_to_use": []
        }
    
    uniq_count = df[cov_name].nunique()
    if uniq_count != len(cov_levels):
        raise ValueError(f"Number of unique values in {cov_name} ({uniq_count}) does not match the expected number of levels ({len(cov_levels)}).")
    level_count = df[cov_name].value_counts()
    code_to_name = {code: cov_levels[idx] for idx, code in enumerate(sorted(level_count.index))}
    legend_label = {
        code: f"{code_to_name[code]} (N={level_count[code]:,})"
        for code in sorted(level_count.index)
    }
    sorted_hue_order = sorted(legend_label.keys())
    new_hue_order = list(legend_label.values())
    markers_to_use = _DEFAULT_MARKERS[:uniq_count]
    palette_to_use = _DEFAULT_COLORS[:uniq_count]
    return {
        "uniq_count": uniq_count,
        "legend_label": legend_label,
        "sorted_hue_order": sorted_hue_order,
        "new_hue_order": new_hue_order,
        "markers_to_use": markers_to_use,
        "palette_to_use": palette_to_use
    }

def plot_pca(
    eigenvec_file: str,
    covar_file: str,
    cov1: str = 'Country_of_birth',
    cov2: Optional[str] = None,
    legend_title_cov1: str = 'Country of Birth',
    legend_title_cov2: Optional[str] = None,
    cov1_levels: List[str] = ['England', 'Wales', 'Scotland', 'Others'],
    cov2_levels: Optional[List[str]] = None,
    fig_path: Optional[str] = None,
    fig1_name: str = 'variance_explained',
    fig2_name: str = 'Scatter_plot_of_PC1_vs_PC2_colored_and_shaped_by_covariates',
    fig3_name: str = 'Scatter_plot_of_PC1-5_colored_and_shaped_by_covariate1',
    fig4_name: str = 'Scatter_plot_of_PC1-5_colored_and_shaped_by_covariate2',
    fig1_size: tuple = (11, 9),
    fig2_size: tuple = (12, 12),
    save_figs: bool = False
) -> None:
    """
    Generate publication-quality PCA visualization plots with covariate-based styling.

    This function creates four types of plots:
    1. Variance explained by each PC (horizontal bar plot)
    2. PC1 vs PC2 scatter plot with covariate-based coloring and shapes
    3. Pairplot of first 5 PCs colored by covariate 1
    4. Pairplot of first 5 PCs colored by covariate 2 (if different from covariate 1)

    Args:
        eigenvec_file: Path to the eigenvector file from PCA analysis
        covar_file: Path to the CSV file containing covariate information
        cov1: Name of the first covariate column for coloring
        cov2: Name of the second covariate column for shapes (optional)
        legend_title_cov1: Title for the first covariate's legend
        legend_title_cov2: Title for the second covariate's legend
        cov1_levels: List of expected levels for the first covariate
        cov2_levels: List of expected levels for the second covariate
        fig_path: Directory to save the figures (if save_figs is True)
        fig1_name: Filename for the variance explained plot
        fig2_name: Filename for the PC1 vs PC2 scatter plot
        fig3_name: Filename for the covariate 1 pairplot
        fig4_name: Filename for the covariate 2 pairplot
        fig1_size: Size of the variance explained plot
        fig2_size: Size of the PC1 vs PC2 scatter plot
        save_figs: Whether to save the figures to disk

    Returns:
        None. Displays or saves the plots based on save_figs parameter.

    Raises:
        ValueError: If number of PCs is less than 5 or if covariate levels don't match the data
    """
    # ---1. read eigenvec and covar files ---
    with open(eigenvec_file, 'r') as f:
        first_line = f.readline().strip()
        eigvals= [str(x) for x in re.split(r'\s+', first_line) if x]
        eigvals = np.array(eigvals[1:]).astype(float)

    num_of_pcs= eigvals.__len__()
    if num_of_pcs < 5:
        raise ValueError(f"Number of PCs in {eigenvec_file} is less than 5, found {num_of_pcs} PCs.")
    
    pca_df = pd.read_table(eigenvec_file, sep='\\s+', header= None, skiprows=1)
    pca_df.columns = ['eid'] + [f'PC{i+1}' for i in range(num_of_pcs)] + ['bt_trait']
    pca_df['eid'] = pca_df['eid'].str.split(':').str[0]
    covar_df = pd.read_table(covar_file, sep=',', header=0)
    covar_df['eid'] = covar_df['eid'].astype(str)
    pca_covar_df = pd.merge(pca_df, covar_df, on='eid', how='left')
    
    # ---2. Calculate the variance explained by each PC ---
    variance_explained = eigvals / np.sum(eigvals) * 100
    variance_explained_str1= [f'PC{i+1} ({var:.2f}% of Top {num_of_pcs} PCs)' for i, var in enumerate(variance_explained)]
    variance_explained_str2= [f'PC{i+1} ({var:.2f}%)' for i, var in enumerate(variance_explained)]
    ## fig1: bar plot of variance explained by each PC
    plt.figure(figsize= fig1_size)
    ax = plt.gca()
    fig1 = sns.barplot(
        y=list(range(0, num_of_pcs)),
        x=variance_explained,
        color='#4A9871',
        orient="h"
    )
    plt.yticks(
        ticks=list(range(0, num_of_pcs)),
        labels=variance_explained_str2,
        fontsize=12, rotation=10
    )
    plt.xticks(fontsize=12)
    plt.xlabel(f'Variance Explained (%) for Top {num_of_pcs} Principal Components (PCs)', fontsize=16, labelpad=10)
    fig1.spines['bottom'].set_visible(False)
    fig1.spines['right'].set_visible(False)
    fig1.spines['top'].set_linewidth(1.5)
    fig1.spines['left'].set_linewidth(1.5)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    if save_figs and fig_path:
        os.makedirs(fig_path, exist_ok=True)
        plt.savefig(os.path.join(fig_path, fig1_name + ".png"), dpi=600, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

    # ---3. Plot PCA results ---
    _DEFAULT_MARKERS = ["P", "X", "D", "s", "*", "o", "^", "v", "<", ">", "h", "H", "+", "x", "d", "|", "_"]
    _DEFAULT_COLORS = ['#1f77b4', '#ff7f0e', '#9467bd', '#d62728', '#17becf', '#8c564b', '#2ca02c',
                '#e377c2', '#7f7f7f', '#bcbd22', '#aec7e8', '#ffbb78', '#c5b0d5', '#ff9896',
                '#98df8a', '#c49c94', '#f7b6d2']
    if cov1 is not None and (cov1_levels is None or legend_title_cov1 is None):
        raise ValueError(f"Covariate levels and legend title for {cov1} must be provided.")
    if cov2 is not None and (cov2_levels is None or legend_title_cov2 is None):
        raise ValueError(f"Covariate levels and legend title for {cov2} must be provided.")

    cov_settings = {}
    for cov, levels in zip([cov1, cov2], [cov1_levels, cov2_levels]):
        cov_settings[cov] = _get_covariate_settings(pca_covar_df, cov, levels, _DEFAULT_MARKERS, _DEFAULT_COLORS)
    max_cat= max([cov_settings[cov]['uniq_count'] for cov in [cov1, cov2]])
    markers_to_use = _DEFAULT_MARKERS[:max_cat]
    palette_to_use = _DEFAULT_COLORS[:max_cat]

    ## Fig2: Scatter plot of PC1 vs PC2 colored and shaped by provided covariates
    # Create pairplot
    if cov2 is None:
        cov2 = cov1
        cov_settings[cov2] = cov_settings[cov1]
    plt.figure(figsize=fig2_size)
    ax = plt.gca()
    fig2 = sns.scatterplot(data=pca_covar_df,
                           x="PC1",
                           y="PC2",
                           hue=cov1,
                           hue_order=cov_settings[cov1]['sorted_hue_order'],
                           palette=cov_settings[cov1]['palette_to_use'],
                           style=cov2,
                           style_order=cov_settings[cov2]['sorted_hue_order'],
                           markers=cov_settings[cov2]['markers_to_use'],
                           edgecolor=None,
                           alpha=0.8,
                           s=20,
                           ax=ax)
    fig2.spines['top'].set_visible(False)
    fig2.spines['right'].set_visible(False)
    fig2.spines['bottom'].set_linewidth(1.5)
    fig2.spines['left'].set_linewidth(1.5)
    plt.xlabel(variance_explained_str1[0], fontsize=16, labelpad=10)
    plt.ylabel(variance_explained_str1[1], fontsize=16, labelpad=10)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    if cov2 == cov1:
        handles, labels = ax.get_legend_handles_labels()
        for handle in handles:
            handle.set_markersize(10)
        new_legend_label = [cov_settings[cov1]['legend_label'].get(label, label) for label in cov_settings[cov1]['sorted_hue_order']]
        legend = ax.legend(
            handles=handles, labels=new_legend_label,
            title=legend_title_cov1, bbox_to_anchor=(.975, 1),
            frameon=False, borderaxespad=0.1,
            loc='upper left',
            alignment='left'
        )
    else:
        handles_hue, labels_hue = ax.get_legend_handles_labels()
        n_hue= len(cov_settings[cov1]['sorted_hue_order'])
        handles_hue = handles_hue[1:n_hue+1]
        for handle in handles_hue:
            handle.set_markersize(10)
            handle.set_marker('o')
        labels_hue = [cov_settings[cov1]['legend_label'].get(label, label) for label in cov_settings[cov1]['sorted_hue_order']]
        legend_cov1 = ax.legend(
            handles_hue, labels_hue,
            title= legend_title_cov1,
            bbox_to_anchor=(.975, 1),
            frameon=False, borderaxespad=0.1,
            loc='upper left',
            alignment='left'
        )
        ax.add_artist(legend_cov1)

        style_labels = cov_settings[cov2]['sorted_hue_order']
        style_markers = cov_settings[cov2]['markers_to_use']
        handles_style = [
            mlines.Line2D([], [], marker=style_markers[i], linestyle='None', color='black', markersize=10)
            for i in range(len(style_labels))
        ]
        labels_style = [cov_settings[cov2]['legend_label'].get(label, label) for label in style_labels]
        legend_cov2 = ax.legend(
            handles=handles_style, labels=labels_style,
            title=legend_title_cov2,
            bbox_to_anchor=(.975, .6),
            frameon=False, borderaxespad=0.1,
            loc='upper left',
            alignment='left'
        )

    if save_figs and fig_path:
        os.makedirs(fig_path, exist_ok=True)
        plt.savefig(os.path.join(fig_path, fig2_name + ".png"), dpi=600, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

    # Fig3: Scatter plot of PC1-5 colored and shaped by provided covariate1
    fig3 = sns.pairplot(data=pca_covar_df,
                        vars=["PC1", "PC2", "PC3", "PC4", "PC5"],
                        hue=cov1,
                        hue_order=cov_settings[cov1]['sorted_hue_order'],
                        markers=cov_settings[cov1]['markers_to_use'],
                        palette=cov_settings[cov1]['palette_to_use'],
                        height=2,
                        dropna=True,
                        corner=False,
                        plot_kws={"s":20, "alpha": 0.8},
                        diag_kind="auto")
    for i in range(5):
        for j in range(5):
            ax = fig3.axes[i, j]
            ax.spines['bottom'].set_linewidth(1.5)
            ax.spines['left'].set_linewidth(1.5)
            ax.tick_params(axis='both', labelsize=12)
    for i in range(5):
        fig3.axes[4, i].set_xlabel(variance_explained_str2[i], fontsize=16, labelpad=10)
        fig3.axes[i, 0].set_ylabel(variance_explained_str2[i], fontsize=16, labelpad=10)
    try:
        legend = getattr(fig3, '_legend', None)
        try:
            legend.set_alignment('left') 
        except AttributeError:
            legend._legend_box.align = "left"
        if legend is not None:
            new_legend_label = [cov_settings[cov1]['legend_label'].get(label, label) for label in cov_settings[cov1]['sorted_hue_order']]
            for t, l in zip(legend.texts, new_legend_label):
                t.set_text(l)
            for handle in legend.legend_handles:
                handle.set_markersize(10)
            legend.set_title(legend_title_cov1)
            legend.set_bbox_to_anchor((1.08, .95))
            legend.set_frame_on(False)
            legend.set_borderaxespad(0.1)
            legend.set_loc('upper left')
    except AttributeError:
        pass

    if save_figs and fig_path:
        os.makedirs(fig_path, exist_ok=True)
        plt.savefig(os.path.join(fig_path, fig3_name + ".png"), dpi=600, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

    # Fig4: Scatter plot of PC1-5 colored and shaped by provided covariate2
    if cov2 != cov1:
        fig4 = sns.pairplot(data=pca_covar_df,
                            vars=["PC1", "PC2", "PC3", "PC4", "PC5"],
                            hue=cov2,
                            hue_order=cov_settings[cov2]['sorted_hue_order'],
                            markers=cov_settings[cov2]['markers_to_use'],
                            palette=cov_settings[cov2]['palette_to_use'],
                            height=2,
                            dropna=True,
                            corner=False,
                            plot_kws={"s":20, "alpha": 0.8},
                            diag_kind="auto")
        for i in range(5):
            for j in range(5):
                ax = fig4.axes[i, j]
                ax.spines['bottom'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)
                ax.tick_params(axis='both', labelsize=12)
        for i in range(5):
            fig4.axes[4, i].set_xlabel(variance_explained_str2[i], fontsize=16, labelpad=10)
            fig4.axes[i, 0].set_ylabel(variance_explained_str2[i], fontsize=16, labelpad=10)
        try:
            legend = getattr(fig4, '_legend', None)
            if legend is not None:
                try:
                    legend.set_alignment('left') 
                except AttributeError:
                    legend._legend_box.align = "left"
                new_legend_label = [cov_settings[cov2]['legend_label'].get(label, label) for label in cov_settings[cov2]['sorted_hue_order']]
                for t, l in zip(legend.texts, new_legend_label):
                    t.set_text(l)
                for handle in legend.legend_handles:
                    handle.set_markersize(10)
                legend.set_title(legend_title_cov2)
                legend.set_bbox_to_anchor((1.08, .95))
                legend.set_frame_on(False)
                legend.set_borderaxespad(0.1)
                legend.set_loc('upper left')
        except AttributeError:
            pass

        if save_figs and fig_path:
            os.makedirs(fig_path, exist_ok=True)
            plt.savefig(os.path.join(fig_path, fig4_name + ".png"), dpi=600, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

    print("Done.")


