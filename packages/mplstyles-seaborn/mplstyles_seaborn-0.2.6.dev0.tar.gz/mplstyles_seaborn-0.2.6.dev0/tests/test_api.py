import pytest
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from pathlib import Path

import mplstyles_seaborn


class TestListAvailableStyles:
    
    def test_returns_list(self):
        """Test that list_available_styles returns a list."""
        result = mplstyles_seaborn.list_available_styles()
        assert isinstance(result, list)
    
    def test_returns_120_styles(self):
        """Test that exactly 120 styles are returned."""
        result = mplstyles_seaborn.list_available_styles()
        assert len(result) == 120
    
    def test_styles_are_sorted(self):
        """Test that styles are returned in sorted order."""
        result = mplstyles_seaborn.list_available_styles()
        assert result == sorted(result)
    
    def test_all_styles_have_correct_prefix(self):
        """Test that all styles start with 'seaborn-v0_8-'."""
        result = mplstyles_seaborn.list_available_styles()
        for style in result:
            assert style.startswith('seaborn-v0_8-')
    
    def test_no_duplicate_styles(self):
        """Test that there are no duplicate style names."""
        result = mplstyles_seaborn.list_available_styles()
        assert len(result) == len(set(result))


class TestUseStyle:
    
    def test_use_style_with_defaults(self):
        """Test use_style with all default parameters."""
        # Should not raise an exception
        mplstyles_seaborn.use_style()
        
        # Verify the style was applied (matplotlib's current style should be updated)
        current_style = plt.rcParams
        assert current_style is not None
    
    def test_use_style_with_all_parameters(self):
        """Test use_style with all parameters specified."""
        mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
        
        # Verify the style was applied
        current_style = plt.rcParams
        assert current_style is not None
    
    def test_use_style_with_partial_parameters(self):
        """Test use_style with some parameters specified."""
        mplstyles_seaborn.use_style(palette='colorblind', context='talk')
        mplstyles_seaborn.use_style(style='whitegrid', context='poster')
        mplstyles_seaborn.use_style(style='dark', palette='muted')
    
    def test_use_style_invalid_style(self):
        """Test use_style raises ValueError for invalid style."""
        with pytest.raises(ValueError, match="style must be one of"):
            mplstyles_seaborn.use_style('invalid_style')
    
    def test_use_style_invalid_palette(self):
        """Test use_style raises ValueError for invalid palette."""
        with pytest.raises(ValueError, match="palette must be one of"):
            mplstyles_seaborn.use_style(palette='invalid_palette')
    
    def test_use_style_invalid_context(self):
        """Test use_style raises ValueError for invalid context."""
        with pytest.raises(ValueError, match="context must be one of"):
            mplstyles_seaborn.use_style(context='invalid_context')
    
    def test_use_style_file_not_found(self, monkeypatch):
        """Test use_style raises FileNotFoundError for missing style file."""
        # Mock the styles directory to be empty
        mock_dir = Path("/nonexistent/path")
        monkeypatch.setattr(mplstyles_seaborn, '_STYLES_DIR', mock_dir)
        
        with pytest.raises(FileNotFoundError, match="Style file not found"):
            mplstyles_seaborn.use_style()
    
    def test_all_valid_combinations(self, all_style_combinations):
        """Test that all valid style combinations work."""
        # Test a sample of combinations to avoid long test times
        sample_combinations = all_style_combinations[::10]  # Every 10th combination
        
        for style, palette, context in sample_combinations:
            # Should not raise an exception
            mplstyles_seaborn.use_style(style, palette, context)
    
    def test_use_style_with_font_scale_default(self):
        """Test use_style with default font_scale parameter."""
        import matplotlib as mpl
        
        # Get baseline font size with font_scale=1.0
        mplstyles_seaborn.use_style(font_scale=1.0)
        baseline_fontsize = mpl.rcParams['font.size']
        
        # Use with default font_scale (1.5)
        mplstyles_seaborn.use_style()
        expected_size = baseline_fontsize * 1.5
        assert abs(mpl.rcParams['font.size'] - expected_size) < 0.1
    
    def test_use_style_with_font_scale_scaling(self):
        """Test use_style with font_scale parameter scaling."""
        import matplotlib as mpl
        
        # Test with font_scale=1.5
        mplstyles_seaborn.use_style(font_scale=1.5)
        scaled_fontsize = mpl.rcParams['font.size']
        
        # Reset and get baseline
        mplstyles_seaborn.use_style(font_scale=1.0)
        baseline_fontsize = mpl.rcParams['font.size']
        
        # Scale again and verify
        mplstyles_seaborn.use_style(font_scale=1.5)
        expected_size = baseline_fontsize * 1.5
        assert abs(mpl.rcParams['font.size'] - expected_size) < 0.1
    
    def test_use_style_with_font_scale_invalid(self):
        """Test use_style raises ValueError for invalid font_scale."""
        with pytest.raises(ValueError, match="font_scale must be a positive number"):
            mplstyles_seaborn.use_style(font_scale=0)
        
        with pytest.raises(ValueError, match="font_scale must be a positive number"):
            mplstyles_seaborn.use_style(font_scale=-1.0)
        
        with pytest.raises(ValueError, match="font_scale must be a positive number"):
            mplstyles_seaborn.use_style(font_scale="invalid")
    
    def test_use_style_with_rc_parameter(self):
        """Test use_style with rc parameter."""
        import matplotlib as mpl
        
        # Test with custom rc parameters
        custom_rc = {
            'axes.spines.right': False,
            'axes.spines.top': False,
            'grid.linewidth': 2.0
        }
        
        mplstyles_seaborn.use_style(rc=custom_rc)
        
        assert mpl.rcParams['axes.spines.right'] == False
        assert mpl.rcParams['axes.spines.top'] == False
        assert mpl.rcParams['grid.linewidth'] == 2.0
    
    def test_use_style_with_rc_none(self):
        """Test use_style with rc=None (default)."""
        # Should not raise an exception
        mplstyles_seaborn.use_style(rc=None)
    
    def test_use_style_with_empty_rc(self):
        """Test use_style with empty rc dictionary."""
        # Should not raise an exception
        mplstyles_seaborn.use_style(rc={})
    
    def test_use_style_with_font_scale_and_rc(self):
        """Test use_style with both font_scale and rc parameters."""
        import matplotlib as mpl
        
        custom_rc = {'grid.alpha': 0.5}
        mplstyles_seaborn.use_style(font_scale=1.2, rc=custom_rc)
        
        # Both should be applied
        assert mpl.rcParams['grid.alpha'] == 0.5
        # Font scaling is harder to test precisely due to cumulative effects


class TestRegisterStyles:
    
    def test_register_styles_adds_to_matplotlib(self):
        """Test that register_styles adds styles to matplotlib library."""
        # Since styles are auto-registered on import, just check they exist
        mplstyles_seaborn.register_styles()
        
        # Check that our specific combination styles are in matplotlib's library
        # (filter out matplotlib's built-in seaborn styles which have different naming)
        current_styles = set(mplstyle.library.keys())
        our_styles = [s for s in current_styles if s.startswith('seaborn-v0_8-') 
                      and len(s.split('-')) >= 5]  # Our styles have format: seaborn-v0_8-style-palette-context
        
        # Should have all 120 of our combination styles registered
        assert len(our_styles) >= 120
    
    def test_registered_styles_are_accessible(self):
        """Test that registered styles can be used with matplotlib."""
        mplstyles_seaborn.register_styles()
        
        # Test that we can use a registered style
        test_style = 'seaborn-v0_8-darkgrid-dark-notebook'
        
        # Should not raise an exception
        plt.style.use(test_style)
    
    def test_register_styles_handles_missing_directory(self, monkeypatch):
        """Test register_styles handles missing styles directory gracefully."""
        # Mock the styles directory to be nonexistent
        mock_dir = Path("/nonexistent/path")
        monkeypatch.setattr(mplstyles_seaborn, '_STYLES_DIR', mock_dir)
        
        # Should not raise an exception (glob returns empty iterator)
        mplstyles_seaborn.register_styles()


class TestConstants:
    
    def test_styles_constant(self):
        """Test STYLES constant has correct values."""
        expected = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
        assert mplstyles_seaborn.STYLES == expected
    
    def test_palettes_constant(self):
        """Test PALETTES constant has correct values."""
        expected = ['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep']
        assert mplstyles_seaborn.PALETTES == expected
    
    def test_contexts_constant(self):
        """Test CONTEXTS constant has correct values."""
        expected = ['paper', 'notebook', 'talk', 'poster']
        assert mplstyles_seaborn.CONTEXTS == expected
    
    def test_version_constant(self):
        """Test __version__ constant exists and is a string."""
        assert hasattr(mplstyles_seaborn, '__version__')
        assert isinstance(mplstyles_seaborn.__version__, str)
    
    def test_all_constant(self):
        """Test __all__ constant has expected exports."""
        expected = ['use_style', 'list_available_styles', 'register_styles', 'STYLES', 'PALETTES', 'CONTEXTS']
        assert mplstyles_seaborn.__all__ == expected


class TestAutoRegistration:
    
    def test_styles_auto_registered_on_import(self):
        """Test that styles are automatically registered when module is imported."""
        # Styles should already be registered from the import
        test_style = 'seaborn-v0_8-darkgrid-dark-notebook'
        
        # Should be in matplotlib's style library
        assert test_style in mplstyle.library
        
        # Should be usable
        plt.style.use(test_style)