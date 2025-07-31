import pytest
import pandas as pd
import tempfile
import os
from omixvizpy import plot_pca
import pytest

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
class TestPCAPlotting:
    """Test cases for PCA plotting functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.eigenvalues = [10, 8, 6, 4, 2]
        # Create sample eigenvec data
        self.sample_eigenvec_data = {
            'eid': [f"eid_{x}" for x in range(1, 6)],
            'PC1': [0.1, 0.2, 0.3, 0.4, 0.5],
            'PC2': [0.15, 0.25, 0.35, 0.45, 0.55],
            'PC3': [0.11, 0.21, 0.31, 0.41, 0.51],
            'PC4': [0.12, 0.22, 0.32, 0.42, 0.52],
            'PC5': [0.13, 0.23, 0.33, 0.43, 0.53],
            'bt_trait': [0, 1, 0, 1, 0]
        }
        
        # Create sample country data
        self.sample_country_data = {
            'eid': [self.sample_eigenvec_data['eid'][i] for i in range(5)],
            'Country_of_birth': [1, 2, 3, 4, 1],
            'Ethnic_background': [1, 2, 3, 4, 5]
        }
        
        # Create temporary files
        self.temp_dir = tempfile.mkdtemp()
        self.eigenvec_file = os.path.join(self.temp_dir, 'test_eigenvec.txt')
        self.covar_file = os.path.join(self.temp_dir, 'test_country.csv')
        
        # Write eigenvec file with correct format
        with open(self.eigenvec_file, 'w') as f:
            f.write('#eigvals: ' + ' '.join(f"{x}" for x in self.eigenvalues) + '\n')
            df = pd.DataFrame(self.sample_eigenvec_data)
            for col in df.columns:
                if col.startswith('PC'):
                    df[col] = df[col].map(lambda x: f"{x:5.3f}")
            for idx, row in df.iterrows():
                line = f"{row['eid']:>11} " + " ".join(row[f'PC{i+1}'] for i in range(5)) + f" {row['bt_trait']}\n"
                f.write(line)
        
        pd.DataFrame(self.sample_country_data).to_csv(
                self.covar_file,
                sep=',',
                header=True,
                index=False
        )
    
    def test_plot_pca_basic(self):
        """Test basic functionality of plot_pca."""
        # This test checks if the function runs without errors
        # In a real test environment, you might want to check plot outputs
        try:
            plot_pca(
                eigenvec_file=self.eigenvec_file,
                covar_file=self.covar_file,
                cov1='Country_of_birth',
                cov2='Ethnic_background',
                legend_title_cov1='Country of Birth',
                legend_title_cov2='Ethnicity',
                cov1_levels=['England', 'Wales', 'Scotland', 'Others'],
                cov2_levels=['White', 'Mixed', 'Asian', 'Black', 'Chinese'],
                save_figs=False  # Don't save during testing
            )
            assert True  # If no exception, test passes
        except Exception as e:
            pytest.fail(f"plot_pca raised an exception: {e}")
    
    def test_file_loading(self):
        """Test if files are loaded correctly."""

        # Test eigenvec file loading
        eigenvec_df = pd.read_table(self.eigenvec_file, sep='\\s+', header=0)
        assert len(eigenvec_df) == 5
        
        # Test country file loading
        country_df = pd.read_table(self.covar_file, sep='\\s+', header=0)
        assert len(country_df) == 5
    
    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def test_import():
    """Test if the package can be imported successfully."""
    import omixvizpy
    assert hasattr(omixvizpy, 'plot_pca')
    assert omixvizpy.__version__


def test_version():
    """Test if version is defined."""
    import omixvizpy
    assert omixvizpy.__version__ == "0.1.2"
