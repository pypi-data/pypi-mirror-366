import pytest
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path


@pytest.fixture(autouse=True)
def reset_matplotlib():
    """Reset matplotlib to default state before each test."""
    # Use non-interactive backend for testing
    matplotlib.use('Agg')
    
    # Reset to default style before each test
    plt.style.use('default')
    
    # Clear any existing figures
    plt.close('all')
    
    yield
    
    # Clean up after test
    plt.close('all')


@pytest.fixture
def styles_dir():
    """Path to the styles directory."""
    return Path(__file__).parent.parent / "src" / "mplstyles_seaborn" / "styles"


@pytest.fixture
def sample_style_file(styles_dir):
    """Path to a sample style file for testing."""
    return styles_dir / "seaborn-v0_8-darkgrid-dark-notebook.mplstyle"


@pytest.fixture
def all_style_combinations():
    """All valid style combinations."""
    styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
    palettes = ['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep']
    contexts = ['paper', 'notebook', 'talk', 'poster']
    
    combinations = []
    for style in styles:
        for palette in palettes:
            for context in contexts:
                combinations.append((style, palette, context))
    
    return combinations