"""
mplstyles-seaborn: Matplotlib style sheets based on seaborn-v0_8-dark theme

This package provides matplotlib style sheets that replicate the seaborn-v0.8-dark
theme with various combinations of palettes and contexts, allowing you to use 
seaborn-like styling without requiring seaborn as a dependency.

Available styles:
- seaborn-v0_8-darkgrid-dark-notebook (default)
- seaborn-v0_8-whitegrid-colorblind-talk
- seaborn-v0_8-dark-muted-poster
- And many more combinations across 5 styles, 6 palettes, and 4 contexts...

Usage:
    import matplotlib.pyplot as plt
    import mplstyles_seaborn
    
    # Use a specific style by name
    plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')
    
    # Or use the convenience function with defaults (ticks, colorblind, talk, font_scale=1.5)
    mplstyles_seaborn.use_style()
    
    # Or use the convenience function with all parameters
    mplstyles_seaborn.use_style('whitegrid', 'deep', 'notebook')
    
    # Or use defaults for some parameters
    mplstyles_seaborn.use_style(style='darkgrid')  # uses colorblind palette, talk context
    
    # Scale fonts independently (like seaborn.set_theme)
    mplstyles_seaborn.use_style('darkgrid', 'deep', 'notebook', font_scale=1.2)
    
    # Override specific rcParams (like seaborn.set_theme)
    custom_rc = {'axes.spines.right': False, 'axes.spines.top': False}
    mplstyles_seaborn.use_style(rc=custom_rc)  # uses all defaults with custom rc
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Literal, Optional, Dict, Any

try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover
    # Fallback for development or if setuptools-scm is not available
    __version__ = "0.0.0+unknown"

# Get the styles directory
_STYLES_DIR = Path(__file__).parent / "styles"

# Available options
STYLES = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
PALETTES = ['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep']
CONTEXTS = ['paper', 'notebook', 'talk', 'poster']

def list_available_styles():
    """List all available style combinations."""
    styles = []
    for style_file in _STYLES_DIR.glob("*.mplstyle"):
        styles.append(style_file.stem)
    return sorted(styles)

def use_style(
    style: Literal['darkgrid', 'whitegrid', 'dark', 'white', 'ticks'] = 'ticks',
    palette: Literal['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep'] = 'colorblind',
    context: Literal['paper', 'notebook', 'talk', 'poster'] = 'talk',
    font_scale: float = 1.5,
    rc: Optional[Dict[str, Any]] = None
):
    """
    Apply a seaborn-v0_8 style with specified style, palette and context.
    
    Parameters
    ----------
    style : str, default 'ticks'
        Style type to use. Options: 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks'
    palette : str, default 'colorblind'
        Color palette to use. Options: 'dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep'
    context : str, default 'talk' 
        Context scaling for elements. Options: 'paper', 'notebook', 'talk', 'poster'
    font_scale : float, default 1.5
        Separate scaling factor to independently scale the size of the font elements.
    rc : dict or None, optional
        Dictionary of rc parameter mappings to override the style settings.
        
    Examples
    --------
    >>> import mplstyles_seaborn
    >>> mplstyles_seaborn.use_style()  # uses defaults: ticks, colorblind, talk, font_scale=1.5
    >>> mplstyles_seaborn.use_style('whitegrid', 'deep', 'notebook')
    >>> mplstyles_seaborn.use_style(style='darkgrid')  # uses colorblind palette, talk context
    >>> mplstyles_seaborn.use_style('darkgrid', 'deep', 'notebook', font_scale=1.2)
    >>> custom_rc = {'axes.spines.right': False, 'axes.spines.top': False}
    >>> mplstyles_seaborn.use_style(rc=custom_rc)  # uses all defaults with custom rc
    """
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}")
    if palette not in PALETTES:
        raise ValueError(f"palette must be one of {PALETTES}")
    if context not in CONTEXTS:
        raise ValueError(f"context must be one of {CONTEXTS}")
    if not isinstance(font_scale, (int, float)) or font_scale <= 0:
        raise ValueError("font_scale must be a positive number")
        
    style_name = f"seaborn-v0_8-{style}-{palette}-{context}"
    style_path = _STYLES_DIR / f"{style_name}.mplstyle"
    
    if not style_path.exists():
        raise FileNotFoundError(f"Style file not found: {style_path}")
        
    # Apply the base style
    plt.style.use(str(style_path))
    
    # Apply font scaling if different from default
    if font_scale != 1.0:
        import matplotlib as mpl
        # Get current font sizes and scale them
        font_keys = [
            'font.size', 'axes.titlesize', 'axes.labelsize', 'xtick.labelsize',
            'ytick.labelsize', 'legend.fontsize', 'figure.titlesize'
        ]
        for key in font_keys:
            current_size = mpl.rcParams[key]
            if isinstance(current_size, (int, float)):
                mpl.rcParams[key] = current_size * font_scale
    
    # Apply custom rc parameters if provided
    if rc is not None:
        import matplotlib as mpl
        mpl.rcParams.update(rc)

def register_styles():
    """Register all styles with matplotlib so they can be used by name."""
    import matplotlib.style as mplstyle
    
    for style_file in _STYLES_DIR.glob("*.mplstyle"):
        # Register with both full path and just the name
        mplstyle.library[style_file.stem] = str(style_file)

# Auto-register styles when the module is imported
register_styles()

__all__ = ['use_style', 'list_available_styles', 'register_styles', 'STYLES', 'PALETTES', 'CONTEXTS']
