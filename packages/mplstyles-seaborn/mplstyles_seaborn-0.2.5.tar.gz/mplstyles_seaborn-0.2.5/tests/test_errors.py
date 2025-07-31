import pytest
import matplotlib.pyplot as plt
from pathlib import Path
from unittest.mock import patch

import mplstyles_seaborn


class TestInputValidation:
    
    def test_invalid_style_values(self):
        """Test that invalid style values raise ValueError."""
        invalid_styles = [
            'invalid_style',
            'seaborn',  # Missing specificity
            'darkgrid_extra',  # Not in the list
            '',  # Empty string
            None,  # None value (if passed as kwarg)
            123,  # Wrong type
        ]
        
        for invalid_style in invalid_styles:
            if invalid_style is None:
                continue  # Skip None as it would be caught by type hints
            
            with pytest.raises(ValueError, match="style must be one of"):
                mplstyles_seaborn.use_style(style=invalid_style)
    
    def test_invalid_palette_values(self):
        """Test that invalid palette values raise ValueError."""
        invalid_palettes = [
            'invalid_palette',
            'color',  # Too generic
            'rainbow',  # Not a seaborn palette
            '',
            'dark_extra',
            123,
        ]
        
        for invalid_palette in invalid_palettes:
            with pytest.raises(ValueError, match="palette must be one of"):
                mplstyles_seaborn.use_style(palette=invalid_palette)
    
    def test_invalid_context_values(self):
        """Test that invalid context values raise ValueError."""
        invalid_contexts = [
            'invalid_context',
            'medium',  # Not a seaborn context
            'large',
            '',
            'paper_extra',
            123,
        ]
        
        for invalid_context in invalid_contexts:
            with pytest.raises(ValueError, match="context must be one of"):
                mplstyles_seaborn.use_style(context=invalid_context)
    
    def test_case_sensitivity(self):
        """Test that function is case-sensitive for inputs."""
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style='DARKGRID')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette='DARK')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context='NOTEBOOK')
    
    def test_whitespace_handling(self):
        """Test that whitespace in inputs is not automatically stripped."""
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style=' darkgrid ')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette=' dark ')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context=' notebook ')


class TestFileSystemErrors:
    
    def test_missing_style_file(self):
        """Test behavior when a style file is missing."""
        # Mock the styles directory to point to a non-existent location
        with patch.object(mplstyles_seaborn, '_STYLES_DIR', Path('/nonexistent/path')):
            with pytest.raises(FileNotFoundError, match="Style file not found"):
                mplstyles_seaborn.use_style()
    
    def test_corrupted_styles_directory(self):
        """Test behavior when styles directory exists but is empty."""
        # Create a temporary empty directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(mplstyles_seaborn, '_STYLES_DIR', Path(temp_dir)):
                with pytest.raises(FileNotFoundError, match="Style file not found"):
                    mplstyles_seaborn.use_style()
    
    def test_permission_denied_on_style_file(self):
        """Test behavior when style file exists but cannot be read."""
        # This test is tricky to implement reliably across platforms
        # We'll mock the file reading to raise a PermissionError
        with patch('matplotlib.pyplot.style.use') as mock_use:
            mock_use.side_effect = PermissionError("Permission denied")
            
            # The error should propagate up
            with pytest.raises(PermissionError):
                mplstyles_seaborn.use_style()
    
    def test_list_styles_with_missing_directory(self):
        """Test list_available_styles when styles directory is missing."""
        with patch.object(mplstyles_seaborn, '_STYLES_DIR', Path('/nonexistent/path')):
            result = mplstyles_seaborn.list_available_styles()
            # Should return empty list, not raise an error
            assert result == []
    
    def test_register_styles_with_missing_directory(self):
        """Test register_styles when styles directory is missing."""
        with patch.object(mplstyles_seaborn, '_STYLES_DIR', Path('/nonexistent/path')):
            # Should not raise an error, just do nothing
            mplstyles_seaborn.register_styles()


class TestEdgeCases:
    
    def test_multiple_rapid_style_changes(self):
        """Test applying many styles in rapid succession."""
        styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
        palettes = ['dark', 'colorblind', 'muted']
        contexts = ['paper', 'notebook', 'talk', 'poster']
        
        # Apply 50 different style combinations rapidly
        for i in range(50):
            style = styles[i % len(styles)]
            palette = palettes[i % len(palettes)]
            context = contexts[i % len(contexts)]
            
            # Should not raise any exceptions
            mplstyles_seaborn.use_style(style, palette, context)
    
    def test_style_application_with_existing_figures(self):
        """Test applying styles when figures already exist."""
        # Create some figures first
        figs = []
        for i in range(3):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 2])
            figs.append(fig)
        
        # Apply a style (should not affect existing figures)
        mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
        
        # Create a new figure (should use the new style)
        fig_new, ax_new = plt.subplots()
        ax_new.plot([1, 2, 3], [1, 4, 2])
        
        # Clean up
        for fig in figs + [fig_new]:
            plt.close(fig)
    
    def test_concurrent_style_registration(self):
        """Test that multiple registrations don't cause conflicts."""
        import threading
        
        def register_styles():
            mplstyles_seaborn.register_styles()
        
        # Run multiple registrations concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=register_styles)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should still work normally
        mplstyles_seaborn.use_style()
    
    def test_style_application_after_matplotlib_reset(self):
        """Test style application after matplotlib has been reset."""
        # Apply a style
        mplstyles_seaborn.use_style('darkgrid', 'dark', 'notebook')
        
        # Reset matplotlib completely
        import importlib
        importlib.reload(plt)
        
        # Should still be able to apply styles (they should be re-registered)
        mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')


class TestTypeErrors:
    
    def test_non_string_inputs(self):
        """Test that non-string inputs raise appropriate errors."""
        # These should raise ValueError due to not being in the valid lists
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style=123)
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette=['dark'])
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context={'context': 'notebook'})
    
    def test_none_values_with_kwargs(self):
        """Test behavior when None is explicitly passed for parameters."""
        # These should raise ValueError since None is not in the valid lists
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style=None)
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette=None)
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context=None)


class TestBoundaryConditions:
    
    def test_empty_string_inputs(self):
        """Test behavior with empty string inputs."""
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style='')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette='')
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context='')
    
    def test_very_long_invalid_inputs(self):
        """Test behavior with very long invalid inputs."""
        long_invalid = 'a' * 1000
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style=long_invalid)
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette=long_invalid)
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context=long_invalid)
    
    def test_unicode_inputs(self):
        """Test behavior with unicode inputs."""
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(style='dαrkgrid')  # Alpha instead of 'a'
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(palette='dårk')  # Non-ASCII character
        
        with pytest.raises(ValueError):
            mplstyles_seaborn.use_style(context='notebοοk')  # Greek omicron instead of 'o'


class TestErrorMessages:
    
    def test_error_message_content(self):
        """Test that error messages contain helpful information."""
        try:
            mplstyles_seaborn.use_style(style='invalid')
        except ValueError as e:
            error_msg = str(e)
            # Should mention what the valid options are
            assert 'darkgrid' in error_msg
            assert 'whitegrid' in error_msg
            assert 'must be one of' in error_msg
    
    def test_file_not_found_error_message(self):
        """Test that FileNotFoundError has helpful message."""
        with patch.object(mplstyles_seaborn, '_STYLES_DIR', Path('/nonexistent')):
            try:
                mplstyles_seaborn.use_style()
            except FileNotFoundError as e:
                error_msg = str(e)
                assert 'Style file not found' in error_msg
                assert 'seaborn-v0_8-ticks-colorblind-talk' in error_msg