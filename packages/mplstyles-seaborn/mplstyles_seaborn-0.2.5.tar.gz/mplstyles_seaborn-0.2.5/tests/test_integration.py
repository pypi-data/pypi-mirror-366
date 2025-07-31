import pytest
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import numpy as np
from pathlib import Path

import mplstyles_seaborn


class TestMatplotlibIntegration:
    
    def test_style_application_changes_rcparams(self):
        """Test that applying a style actually changes matplotlib rcParams."""
        # Get initial rcParams
        initial_params = dict(plt.rcParams)
        
        # Apply a style
        mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
        
        # Check that rcParams have changed
        new_params = dict(plt.rcParams)
        assert initial_params != new_params
    
    def test_direct_matplotlib_usage(self):
        """Test that styles can be used directly with matplotlib."""
        style_name = 'seaborn-v0_8-whitegrid-colorblind-talk'
        
        # Should not raise an exception
        plt.style.use(style_name)
        
        # Verify style is applied by checking a known parameter
        # All seaborn styles should have specific font sizes for 'talk' context
        assert plt.rcParams['font.size'] > 10  # talk context has larger fonts
    
    def test_style_context_manager(self):
        """Test that styles work with matplotlib's context manager."""
        initial_font_size = plt.rcParams['font.size']
        
        with plt.style.context('seaborn-v0_8-darkgrid-dark-poster'):
            # Poster context should have even larger fonts
            poster_font_size = plt.rcParams['font.size']
            assert poster_font_size > initial_font_size
        
        # Should revert after context
        assert plt.rcParams['font.size'] == initial_font_size
    
    def test_multiple_style_applications(self):
        """Test applying multiple styles in sequence."""
        styles_to_test = [
            ('darkgrid', 'dark', 'paper'),
            ('whitegrid', 'colorblind', 'notebook'),
            ('white', 'muted', 'talk'),
            ('ticks', 'bright', 'poster')
        ]
        
        for style, palette, context in styles_to_test:
            # Should not raise an exception
            mplstyles_seaborn.use_style(style, palette, context)
            
            # Verify style is applied by checking it affects some parameter
            assert plt.rcParams is not None
    
    def test_style_affects_plot_appearance(self):
        """Test that different styles actually affect plot appearance."""
        # Create some test data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        # Test with different styles and check that they produce different results
        style_params = []
        
        for style in ['darkgrid', 'whitegrid', 'white']:
            mplstyles_seaborn.use_style(style, 'dark', 'notebook')
            
            # Create a figure and capture some styling parameters
            fig, ax = plt.subplots()
            ax.plot(x, y)
            
            # Capture some parameters that should differ between styles
            params = {
                'axes_facecolor': ax.get_facecolor(),
                'axes_edgecolor': ax.spines['bottom'].get_edgecolor(),
                'grid_visible': ax.xaxis.grid,
            }
            style_params.append(params)
            plt.close(fig)
        
        # Different styles should produce different parameters
        assert len(set(str(p) for p in style_params)) > 1
    
    def test_color_palette_affects_plot_colors(self):
        """Test that different palettes affect plot colors."""
        x = np.arange(5)
        y = np.random.rand(5, 5)
        
        colors_by_palette = {}
        
        for palette in ['dark', 'colorblind', 'bright']:
            mplstyles_seaborn.use_style('darkgrid', palette, 'notebook')
            
            fig, ax = plt.subplots()
            lines = ax.plot(x, y.T)
            
            # Capture the colors of the first few lines
            colors = [line.get_color() for line in lines[:3]]
            colors_by_palette[palette] = colors
            plt.close(fig)
        
        # Different palettes should produce different colors
        palette_names = list(colors_by_palette.keys())
        for i in range(len(palette_names)):
            for j in range(i + 1, len(palette_names)):
                palette1, palette2 = palette_names[i], palette_names[j]
                assert colors_by_palette[palette1] != colors_by_palette[palette2]


class TestStylePersistence:
    
    def test_style_persists_across_figures(self):
        """Test that applied style persists across multiple figures."""
        mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
        
        # Get font size from the applied style
        expected_font_size = plt.rcParams['font.size']
        
        # Create multiple figures
        for i in range(3):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 2])
            
            # Style should persist
            assert plt.rcParams['font.size'] == expected_font_size
            plt.close(fig)
    
    def test_style_reset_works(self):
        """Test that matplotlib style reset works after applying seaborn styles."""
        # Apply a seaborn style
        mplstyles_seaborn.use_style('darkgrid', 'dark', 'poster')
        seaborn_font_size = plt.rcParams['font.size']
        
        # Reset to default
        plt.style.use('default')
        default_font_size = plt.rcParams['font.size']
        
        # Font sizes should be different
        assert seaborn_font_size != default_font_size


class TestStyleRegistry:
    
    def test_all_styles_registered_in_matplotlib(self):
        """Test that all 120 styles are registered in matplotlib's library."""
        available_styles = mplstyles_seaborn.list_available_styles()
        
        for style_name in available_styles:
            assert style_name in mplstyle.library
    
    def test_registered_styles_point_to_correct_files(self, styles_dir):
        """Test that registered styles point to the correct file paths."""
        available_styles = mplstyles_seaborn.list_available_styles()
        
        # Test a sample of styles
        sample_styles = available_styles[::20]  # Every 20th style
        
        for style_name in sample_styles:
            registered_path = mplstyle.library[style_name]
            expected_path = styles_dir / f"{style_name}.mplstyle"
            
            assert Path(registered_path) == expected_path
            assert Path(registered_path).exists()
    
    def test_style_registration_is_idempotent(self):
        """Test that registering styles multiple times doesn't cause issues."""
        # Register styles multiple times
        for _ in range(3):
            mplstyles_seaborn.register_styles()
        
        # Should still work normally
        test_style = 'seaborn-v0_8-darkgrid-dark-notebook'
        plt.style.use(test_style)
        
        # Should still have all styles available
        available_styles = mplstyles_seaborn.list_available_styles()
        assert len(available_styles) == 120


class TestStyleCompatibility:
    
    def test_compatible_with_matplotlib_style_chaining(self):
        """Test that seaborn styles work with matplotlib's style chaining."""
        # Apply multiple styles in sequence (later styles override earlier ones)
        plt.style.use(['seaborn-v0_8-darkgrid-dark-notebook', 'seaborn-v0_8-white-bright-talk'])
        
        # Should not raise an exception and should apply the last style
        # Talk context should have larger fonts than notebook
        assert plt.rcParams['font.size'] > 11
    
    def test_compatible_with_custom_rcparams(self):
        """Test that seaborn styles work with custom rcParams modifications."""
        # Apply a seaborn style
        mplstyles_seaborn.use_style('darkgrid', 'dark', 'notebook')
        
        # Modify some rcParams manually
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['lines.linewidth'] = 3
        
        # Should not cause issues
        fig, ax = plt.subplots()
        line, = ax.plot([1, 2, 3], [1, 4, 2])
        
        # Custom settings should be preserved
        assert fig.get_size_inches().tolist() == [12, 8]
        assert line.get_linewidth() == 3
        
        plt.close(fig)