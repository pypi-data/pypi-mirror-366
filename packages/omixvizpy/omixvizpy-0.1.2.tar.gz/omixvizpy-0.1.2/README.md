# omixvizpy

A Python package for omics data visualization, particularly focused on Principal Component Analysis (PCA) plotting.

## Features

- **PCA Visualization**: Create comprehensive PCA plots with multiple grouping options
- **Flexible Plotting**: Support for scatter plots and pair plots of principal components
- **Customizable**: Easy-to-use functions with extensive customization options
- **Publication Ready**: High-quality plots suitable for scientific publications

## Installation

### From PyPI (recommended)

```bash
pip install omixvizpy
```

### From Source

```bash
git clone https://github.com/Leslie-Lu/omixvizpy.git
cd omixvizpy
pip install -e .
```

## Quick Start

```python
import omixvizpy

# Plot PCA results with covariates
omixvizpy.plot_pca(
    eigenvec_file="path/to/your/eigenvec.txt",
    covar_file="path/to/your/covariates.csv",
    cov1="Country_of_birth",                    # First covariate
    cov2="Ethnic_background",                   # Second covariate (optional)
    legend_title_cov1="Country of Birth",       # Legend title for first covariate
    legend_title_cov2="Ethnicity",             # Legend title for second covariate
    cov1_levels=["England", "Wales", "Scotland", "Others"],  # Labels for first covariate
    cov2_levels=["White", "Asian", "Black", "Others"],      # Labels for second covariate
    fig_path="output/directory",                # Output directory
    fig1_name="variance_explained",             # Variance plot
    fig2_name="pc1_vs_pc2",                    # PC1 vs PC2 scatter plot
    fig3_name="pca_by_country",                # Pairplot by first covariate
    fig4_name="pca_by_ethnicity",              # Pairplot by second covariate
    fig1_size=(11, 9),                           # Size of variance explained plot
    fig2_size=(12, 12),                         # Size of PC1 vs PC2
    save_figs=True                             # Save figures instead of displaying
)
```

## Function Reference

### `plot_pca`

Create comprehensive PCA visualization plots.

**Parameters:**
- `eigenvec_file` (str): Path to the eigenvec file containing PCA results
- `covar_file` (str): Path to the CSV file containing covariate information
- `cov1` (str): Name of the first covariate column (default: 'Country_of_birth')
- `cov2` (Optional[str]): Name of the second covariate column
- `legend_title_cov1` (str): Title for the first covariate's legend
- `legend_title_cov2` (Optional[str]): Title for the second covariate's legend
- `cov1_levels` (List[str]): Labels for the first covariate's values
- `cov2_levels` (Optional[List[str]]): Labels for the second covariate's values
- `fig_path` (Optional[str]): Directory path where figures will be saved
- `fig1_name` (str): Name for the variance explained plot (default: 'variance_explained')
- `fig2_name` (str): Name for the PC1 vs PC2 scatter plot
- `fig3_name` (str): Name for the pairplot colored by first covariate
- `fig4_name` (str): Name for the pairplot colored by second covariate
- `fig1_size` (Tuple[int, int]): Size of the variance explained plot (default: (11, 9))
- `fig2_size` (Tuple[int, int]): Size of the PC1 vs PC2 scatter plot (default: (12, 12))
- `save_figs` (bool): Whether to save the figures (default: False)

**Returns:**
- Displays interactive plots and optionally saves them as PNG files

## Input Data Format

### Eigenvec File
The eigenvec file should be a tab-separated file with the following columns:
- `eid`: Sample identifier
- `PC1`, `PC2`, `PC3`, etc.: Principal component values

### Covariate File
The covariate file should be a comma-separated (CSV) file with the following structure:
- `eid`: Sample identifier (matching eigenvec file)
- Additional columns for covariates (e.g., `Country_of_birth`, `Ethnic_background`)
  - Values in these columns should correspond to the levels specified in `cov1_levels` and `cov2_levels`
  - The order of levels in `cov*_levels` determines the order in the plot legend

## Requirements

- Python >=3.8
- pandas >=1.3.0
- matplotlib >=3.3.0
- seaborn >=0.11.0
- numpy >=1.20.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use omixvizpy in your research, please cite:

```
@software{omixvizpy,
  title={omixvizpy: A Python package for omics data visualization},
  author={Zhen Lu},
  year={2025},
  url={https://github.com/Leslie-Lu/omixvizpy}
}
```
