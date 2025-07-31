# mplstyles-seaborn

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/github/license/monodera/mplstyles-seaborn)](LICENSE)
[![Matplotlib](https://img.shields.io/badge/matplotlib-3.8%2B-orange.svg)](https://matplotlib.org)
[![Tests](https://github.com/monodera/mplstyles-seaborn/workflows/Tests/badge.svg)](https://github.com/monodera/mplstyles-seaborn/actions)
[![codecov](https://codecov.io/gh/monodera/mplstyles-seaborn/branch/main/graph/badge.svg)](https://codecov.io/gh/monodera/mplstyles-seaborn)
[![GitHub last commit](https://img.shields.io/github/last-commit/monodera/mplstyles-seaborn)](https://github.com/monodera/mplstyles-seaborn/commits)
[![GitHub issues](https://img.shields.io/github/issues/monodera/mplstyles-seaborn)](https://github.com/monodera/mplstyles-seaborn/issues)
[![Type hints](https://img.shields.io/badge/type%20hints-included-brightgreen.svg)](#api-reference)
[![Styles](https://img.shields.io/badge/styles-120-blue.svg)](#available-options)

Matplotlib style sheets based on seaborn v0.8 themes with combinable palettes and contexts.

## Overview

While matplotlib includes built-in seaborn v0.8 style sheets, they offer only a limited set of predefined combinations. This package extends matplotlib's seaborn styling without requiring seaborn as a dependency, providing all 120 possible combinations of seaborn's styles, color palettes, and contexts.

## Features

- **Zero seaborn dependency**: Use seaborn-style plots with pure matplotlib
- **Complete coverage**: All 120 combinations of seaborn v0.8 styles, palettes, and contexts
- **Easy integration**: Styles automatically registered with matplotlib on import
- **Multiple usage methods**: Convenience functions or direct matplotlib integration
- **Type hints**: Full type annotation support

![Comprehensive Plot Demonstration](examples/comprehensive_demo_output/comprehensive_demo.png)

## Example Galleries

For comprehensive visual examples, see our **[📸 Example Galleries](examples/)**:

- **[Basic Usage Gallery](examples/basic_usage_gallery.md)** - Fundamental usage patterns and plot types
- **[Style Comparison Gallery](examples/style_comparison_gallery.md)** - All 120 style combinations visualized  
- **[Comprehensive Demo Gallery](examples/comprehensive_demo_gallery.md)** - Advanced plot types and publication-ready figures

## Installation

Install from PyPI:

```bash
pip install mplstyles-seaborn
```

Or with uv:

```bash
uv add mplstyles-seaborn
```

### Development Installation

For development, install directly from GitHub:

```bash
pip install git+https://github.com/monodera/mplstyles-seaborn.git
```

Or with uv:

```bash
uv add git+https://github.com/monodera/mplstyles-seaborn.git
```

## Quick Start

```python
import matplotlib.pyplot as plt
import mplstyles_seaborn
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Method 1: Use convenience function
mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')

plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)')
plt.title('Example Plot')
plt.legend()
plt.show()
```

## Available Options

### Styles (5 options)
- `darkgrid` - Dark grid background
- `whitegrid` - White grid background  
- `dark` - Dark background, no grid
- `white` - White background, no grid
- `ticks` - White background with ticks

### Palettes (6 options)
- `dark` - Deep, saturated colors
- `colorblind` - Colorblind-friendly palette
- `muted` - Muted, subdued colors
- `bright` - Bright, vibrant colors
- `pastel` - Light, pastel colors
- `deep` - Dark, deep colors

### Contexts (4 options)
- `paper` - Smallest elements, for papers/publications
- `notebook` - Default size, for notebooks
- `talk` - Larger elements, for presentations
- `poster` - Largest elements, for posters

## Usage Methods

### 1. Convenience Function

```python
import mplstyles_seaborn

# Use all three parameters
mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')

# Use defaults for some parameters (defaults: darkgrid, dark, notebook)
mplstyles_seaborn.use_style(palette='colorblind', context='talk')
```

### 2. Direct Matplotlib

```python
import matplotlib.pyplot as plt

# Styles are automatically registered on import
plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')
```

### 3. List Available Styles

```python
import mplstyles_seaborn

# See all 120 available style combinations
styles = mplstyles_seaborn.list_available_styles()
print(f"Available styles: {len(styles)}")

# Print first few styles
for style in styles[:5]:
    print(style)
```

Run the examples with:

```bash
# Basic usage examples
uv run python examples/basic_usage.py

# Generate all 120 style combination comparisons  
uv run python examples/style_comparison.py

# Comprehensive demonstration with 7 different plot types
uv run python examples/comprehensive_demo.py
```

### Basic Line Plot

```python
import matplotlib.pyplot as plt
import numpy as np
import mplstyles_seaborn

# Apply style
mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')

# Create plot
x = np.linspace(0, 10, 100)
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(x, np.sin(x), label='sin(x)', linewidth=2)
ax.plot(x, np.cos(x), label='cos(x)', linewidth=2)
ax.plot(x, np.sin(x + np.pi/4), label='sin(x + pi/4)', linewidth=2)

ax.set_title('Trigonometric Functions')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()

plt.tight_layout()
plt.show()
```

### Scatter Plot

```python
import matplotlib.pyplot as plt
import numpy as np
import mplstyles_seaborn

# Apply dark theme with muted palette
mplstyles_seaborn.use_style('dark', 'muted', 'notebook')

# Generate data
np.random.seed(42)
x = np.random.randn(200)
y = np.random.randn(200)

# Create scatter plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(x, y, alpha=0.7, s=60)
ax.set_title('Random Scatter Plot')
ax.set_xlabel('X values')
ax.set_ylabel('Y values')

plt.tight_layout()
plt.show()
```

## Font Configuration

The package includes optimized font settings:

1. **Source Sans 3** (if available)
2. **Arial** (fallback)
3. **DejaVu Sans** (further fallback)
4. System fonts

Font family is automatically set to `sans-serif` for consistent appearance.

## API Reference

### Functions

#### `use_style(style='darkgrid', palette='dark', context='notebook')`

Apply a seaborn-v0.8 style with specified parameters.

**Parameters:**
- `style` (str): Style type - 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks'
- `palette` (str): Color palette - 'dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep'  
- `context` (str): Context scaling - 'paper', 'notebook', 'talk', 'poster'

#### `list_available_styles()`

Returns a sorted list of all 120 available style names.

**Returns:**
- `list[str]`: List of style names

#### `register_styles()`

Register all styles with matplotlib (called automatically on import).

### Constants

- `STYLES`: List of available style types
- `PALETTES`: List of available color palettes  
- `CONTEXTS`: List of available contexts

## Development

### Requirements

- Python >=3.11
- matplotlib >=3.5
- seaborn >=0.11 (for development/generation only)

### Setup

```bash
git clone https://github.com/monodera/mplstyles-seaborn.git
cd mplstyles-seaborn
uv sync
```

### Testing

This project includes comprehensive tests covering:
- Unit tests for all API functions
- Integration tests with matplotlib
- Validation tests for all 120 style files
- Error handling and edge cases
- Performance benchmarks

#### Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/mplstyles_seaborn --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_api.py          # API function tests
uv run pytest tests/test_integration.py # Matplotlib integration tests
uv run pytest tests/test_styles.py      # Style file validation tests
uv run pytest tests/test_errors.py      # Error handling tests

# Run performance tests (marked as slow)
uv run pytest tests/test_performance.py -m "not slow"  # Fast performance tests
uv run pytest tests/test_performance.py                # All performance tests

# Run with verbose output
uv run pytest -v
```

#### Manual Testing

```bash
# Test package import and basic functionality
uv run python -c "import mplstyles_seaborn; print(len(mplstyles_seaborn.list_available_styles()))"

# Test specific style application
uv run python -c "import matplotlib.pyplot as plt; plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')"

# Run example scripts
uv run python examples/basic_usage.py
uv run python examples/style_comparison.py
uv run python examples/comprehensive_demo.py
```

### Regenerating Styles

```bash
# Generate and fix all 120 style files in one command (recommended)
uv run python scripts/build_styles.py

# Alternative: Generate only (for development/testing)
uv run python scripts/build_styles.py --generate-only

# Alternative: Fix existing files only
uv run python scripts/build_styles.py --fix-only
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Development Support

This project was primarily developed using [Claude Code](https://claude.ai/code), Anthropic's AI-powered coding assistant.

## Related Projects

- [seaborn](https://seaborn.pydata.org/) - Statistical data visualization library
- [matplotlib](https://matplotlib.org/) - Python plotting library