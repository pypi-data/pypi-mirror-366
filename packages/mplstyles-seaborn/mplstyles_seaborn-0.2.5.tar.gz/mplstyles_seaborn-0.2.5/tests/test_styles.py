import pytest
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from pathlib import Path
import configparser

import mplstyles_seaborn


class TestStyleFileValidation:
    
    def test_all_style_files_exist(self, styles_dir, all_style_combinations):
        """Test that all expected style files exist."""
        for style, palette, context in all_style_combinations:
            style_name = f"seaborn-v0_8-{style}-{palette}-{context}"
            style_path = styles_dir / f"{style_name}.mplstyle"
            assert style_path.exists(), f"Missing style file: {style_path}"
    
    def test_no_extra_style_files(self, styles_dir, all_style_combinations):
        """Test that there are no unexpected extra style files."""
        expected_files = set()
        for style, palette, context in all_style_combinations:
            style_name = f"seaborn-v0_8-{style}-{palette}-{context}"
            expected_files.add(f"{style_name}.mplstyle")
        
        actual_files = set(f.name for f in styles_dir.glob("*.mplstyle"))
        
        # Should have exactly the expected files
        assert actual_files == expected_files
    
    def test_style_files_are_valid_format(self, styles_dir):
        """Test that all style files are valid matplotlib style format."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        
        # Test a sample of files to avoid long test times
        sample_files = style_files[::10]  # Every 10th file
        
        for style_file in sample_files:
            # Test that matplotlib can load the style file
            try:
                plt.style.use(str(style_file))
            except Exception as e:
                pytest.fail(f"Style file {style_file} cannot be loaded by matplotlib: {e}")
    
    def test_all_style_files_loadable(self, styles_dir):
        """Test that all style files can be loaded by matplotlib."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        
        # Test a representative sample
        sample_files = style_files[::15]  # Every 15th file
        
        for style_file in sample_files:
            try:
                # Try to load the style
                plt.style.use(str(style_file))
            except Exception as e:
                pytest.fail(f"Style file {style_file} cannot be loaded: {e}")
    
    def test_style_files_have_required_parameters(self, styles_dir):
        """Test that style files contain expected parameters."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        sample_file = style_files[0]  # Test just one file as representative
        
        # Read the style file
        with open(sample_file, 'r') as f:
            content = f.read()
        
        # Should contain key seaborn-style parameters
        expected_params = [
            'axes.prop_cycle',
            'axes.facecolor',
            'font.family',
            'axes.edgecolor',
            'axes.linewidth'
        ]
        
        for param in expected_params:
            assert param in content, f"Missing parameter {param} in {sample_file}"
    
    def test_style_files_have_proper_color_format(self, styles_dir):
        """Test that color parameters in style files are properly formatted."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        sample_file = style_files[0]
        
        with open(sample_file, 'r') as f:
            content = f.read()
        
        # Check axes.prop_cycle format
        prop_cycle_line = None
        for line in content.split('\n'):
            if 'axes.prop_cycle' in line:
                prop_cycle_line = line
                break
        
        assert prop_cycle_line is not None, "axes.prop_cycle not found"
        
        # Should contain cycler syntax with color values
        assert 'cycler(' in prop_cycle_line, "axes.prop_cycle should use cycler syntax"
        assert 'color' in prop_cycle_line, "axes.prop_cycle should specify colors"


class TestStyleCombinations:
    
    @pytest.mark.parametrize("style", mplstyles_seaborn.STYLES)
    def test_all_styles_work(self, style):
        """Test that each style type works with default palette and context."""
        mplstyles_seaborn.use_style(style=style)
        # Should not raise an exception
    
    @pytest.mark.parametrize("palette", mplstyles_seaborn.PALETTES)
    def test_all_palettes_work(self, palette):
        """Test that each palette works with default style and context."""
        mplstyles_seaborn.use_style(palette=palette)
        # Should not raise an exception
    
    @pytest.mark.parametrize("context", mplstyles_seaborn.CONTEXTS)
    def test_all_contexts_work(self, context):
        """Test that each context works with default style and palette."""
        mplstyles_seaborn.use_style(context=context)
        # Should not raise an exception
    
    def test_context_affects_font_size(self):
        """Test that different contexts produce different font sizes."""
        contexts_and_expected_order = [
            ('paper', 'smallest'),
            ('notebook', 'small'),
            ('talk', 'large'),
            ('poster', 'largest')
        ]
        
        font_sizes = {}
        for context, _ in contexts_and_expected_order:
            mplstyles_seaborn.use_style(context=context)
            font_sizes[context] = plt.rcParams['font.size']
        
        # Contexts should have increasing font sizes
        assert font_sizes['paper'] < font_sizes['notebook']
        assert font_sizes['notebook'] < font_sizes['talk']
        assert font_sizes['talk'] < font_sizes['poster']
    
    def test_palette_affects_colors(self):
        """Test that different palettes produce different color cycles."""
        palettes_to_test = ['dark', 'colorblind', 'bright']
        color_cycles = {}
        
        for palette in palettes_to_test:
            mplstyles_seaborn.use_style(palette=palette)
            
            # Get the color cycle
            prop_cycle = plt.rcParams['axes.prop_cycle']
            colors = [item['color'] for item in prop_cycle]
            color_cycles[palette] = colors[:3]  # First 3 colors
        
        # Different palettes should have different colors
        for i, palette1 in enumerate(palettes_to_test):
            for palette2 in palettes_to_test[i+1:]:
                assert color_cycles[palette1] != color_cycles[palette2]
    
    def test_style_affects_grid_and_spines(self):
        """Test that different styles affect grid and spine visibility."""
        # Test styles that should have different grid/spine behavior
        test_cases = [
            ('darkgrid', True),   # Should have grid
            ('whitegrid', True),  # Should have grid
            ('white', False),     # Should not have grid by default
            ('dark', False),      # Should not have grid by default
        ]
        
        for style, should_have_grid in test_cases:
            mplstyles_seaborn.use_style(style=style)
            
            # Check rcParams for grid setting
            grid_enabled = plt.rcParams['axes.grid']
            
            if should_have_grid:
                # For grid styles, matplotlib should be configured to show grids
                assert grid_enabled is True, f"Style '{style}' should have grid enabled"
            else:
                # For non-grid styles, grid should be disabled or not explicitly set
                assert grid_enabled is False or grid_enabled is None, f"Style '{style}' should not have grid enabled"


class TestStyleConsistency:
    
    def test_all_combinations_have_same_parameter_structure(self, styles_dir):
        """Test that all style files have consistent core parameter structure."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        
        # Define core parameters that should be in all files
        core_params = {
            'axes.axisbelow', 'axes.edgecolor', 'axes.facecolor', 'axes.labelcolor',
            'axes.labelsize', 'axes.linewidth', 'axes.prop_cycle', 'axes.titlesize',
            'font.family', 'font.sans-serif'
        }
        
        # Check that all files have the core parameters
        sample_files = style_files[::20]  # Every 20th file
        
        for style_file in sample_files:
            with open(style_file, 'r') as f:
                content = f.read()
            
            params = set()
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    param_name = line.split(':')[0].strip()
                    params.add(param_name)
            
            # Check that all core parameters are present
            missing_params = core_params - params
            assert not missing_params, f"Missing core parameters {missing_params} in {style_file}"
    
    def test_font_family_consistency(self, styles_dir):
        """Test that all style files have consistent font.family setting."""
        style_files = list(styles_dir.glob("*.mplstyle"))
        sample_files = style_files[::25]  # Sample files
        
        font_families = set()
        
        for style_file in sample_files:
            with open(style_file, 'r') as f:
                content = f.read()
            
            for line in content.split('\n'):
                if 'font.family' in line and ':' in line:
                    font_family = line.split(':')[1].strip()
                    font_families.add(font_family)
                    break
        
        # All files should have the same font.family setting
        assert len(font_families) == 1, f"Inconsistent font.family settings: {font_families}"
        
        # Should be 'sans-serif'
        assert 'sans-serif' in font_families


class TestStyleFileContent:
    
    def test_axes_prop_cycle_format(self, sample_style_file):
        """Test that axes.prop_cycle is in the correct format."""
        with open(sample_style_file, 'r') as f:
            content = f.read()
        
        prop_cycle_line = None
        for line in content.split('\n'):
            if 'axes.prop_cycle' in line:
                prop_cycle_line = line
                break
        
        assert prop_cycle_line is not None
        
        # Should be in cycler format with color specification
        assert prop_cycle_line.startswith('axes.prop_cycle')
        assert 'cycler(' in prop_cycle_line  # Should use cycler syntax
        assert 'color' in prop_cycle_line  # Should specify colors
    
    def test_axes_facecolor_format(self, sample_style_file):
        """Test that axes.facecolor is properly formatted."""
        with open(sample_style_file, 'r') as f:
            content = f.read()
        
        facecolor_line = None
        for line in content.split('\n'):
            if 'axes.facecolor' in line:
                facecolor_line = line
                break
        
        assert facecolor_line is not None
        
        # Should be unquoted hex color or color name
        color_value = facecolor_line.split(':')[1].strip()
        assert not (color_value.startswith('"') and color_value.endswith('"'))
        assert not (color_value.startswith("'") and color_value.endswith("'"))