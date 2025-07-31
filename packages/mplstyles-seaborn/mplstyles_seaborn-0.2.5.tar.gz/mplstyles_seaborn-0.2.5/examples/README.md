# Examples

This directory contains comprehensive examples demonstrating the usage of the `mplstyles-seaborn` package.

## 📸 Visual Galleries

- **[Basic Usage Gallery](basic_usage_gallery.md)** - Fundamental usage patterns and plot types
- **[Style Comparison Gallery](style_comparison_gallery.md)** - All 120 style combinations visualized
- **[Comprehensive Demo Gallery](comprehensive_demo_gallery.md)** - Advanced plot types and publication-ready figures

## Example Files

### 1. `basic_usage.py`
Demonstrates the fundamental ways to use the package:
- Using the convenience function `mplstyles_seaborn.use_style()`
- Using `plt.style.use()` with registered style names
- Basic plot types: line plots, scatter plots
- Listing available styles, palettes, and contexts

**Run with:**
```bash
uv run python examples/basic_usage.py
```

### 2. `style_comparison.py`
Compares different styles using matplotlib's reference approach:
- Side-by-side comparison of different style combinations
- Demonstrates the visual differences between styles, palettes, and contexts
- Uses multiple plot types: scatter, line, bar, histogram
- Context comparison showing size and spacing differences

**Run with:**
```bash
uv run python examples/style_comparison.py
```

### 3. `comprehensive_demo.py`
Advanced demonstration showcasing the full capabilities:
- Complex subplot layouts with multiple plot types
- Palette comparison across all 6 available palettes
- Style comparison across all 5 base styles
- Publication-ready figure example
- Advanced plot types: polar plots, contour plots, box plots

**Run with:**
```bash
uv run python examples/comprehensive_demo.py
```

## Generated Output

Each script generates organized output in dedicated directories:

### `basic_usage_output/`

- `basic_convenience_function.png` - Basic convenience function usage
- `basic_direct_style.png` - Direct style usage  
- `basic_scatter_plot.png` - Scatter plot example

### `style_comparison_output/`

- `comparison_*.png` - **All 120 style combination plots** (style_palette_context.png)
- `context_comparison.png` - Context size comparison

### `comprehensive_demo_output/`

- `comprehensive_demo.png` - Advanced subplot demonstration
- `palette_comparison.png` - All palettes side-by-side
- `style_comparison.png` - All base styles comparison  
- `publication_ready.png/.pdf` - Publication-quality figures

## Style Combinations Available

The package provides **120 total combinations** from:

- **5 Styles**: darkgrid, whitegrid, dark, white, ticks
- **6 Palettes**: dark, colorblind, muted, bright, pastel, deep  
- **4 Contexts**: paper, notebook, talk, poster

## Usage Patterns

### Method 1: Convenience Function

```python
import mplstyles_seaborn
mplstyles_seaborn.use_style("whitegrid", "colorblind", "talk")
```

### Method 2: Direct matplotlib

```python
import matplotlib.pyplot as plt
plt.style.use("seaborn-v0_8-whitegrid-colorblind-talk")
```

### Method 3: List Available Styles

```python
styles = mplstyles_seaborn.list_available_styles()
print(f"Available: {len(styles)} styles")
```

## Dependencies

All examples require:

- `matplotlib >= 3.5`
- `numpy`
- `mplstyles_seaborn` (this package)

No seaborn dependency required!