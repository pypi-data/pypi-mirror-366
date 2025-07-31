#!/usr/bin/env python3
"""
Basic usage examples for mplstyles-seaborn package.

This script demonstrates the basic ways to use the mplstyles-seaborn package
to apply seaborn-style matplotlib themes without requiring seaborn as a dependency.
"""

import matplotlib.pyplot as plt
import numpy as np
import mplstyles_seaborn

# Set random seed for reproducibility
np.random.seed(19680801)

def create_sample_data():
    """Generate sample data for plotting examples."""
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x + np.pi / 4)
    return x, y1, y2, y3

def example_convenience_function():
    """Example 1: Using the convenience function."""
    import os
    
    output_dir = "examples/basic_usage_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Example 1: Using convenience function ===")
    
    # Use the convenience function to apply style, palette, and context
    mplstyles_seaborn.use_style("whitegrid", "colorblind", "talk")
    
    x, y1, y2, y3 = create_sample_data()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y1, label=r"$\sin(x)$", linewidth=2)
    ax.plot(x, y2, label=r"$\cos(x)$", linewidth=2)
    ax.plot(x, y3, label=r"$\sin(x + \pi/4)$", linewidth=2)
    ax.set_title("Trigonometric Functions")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend()
    
    filename = f"{output_dir}/basic_convenience_function.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filename}")

def example_direct_style_use():
    """Example 2: Using plt.style.use directly."""
    import os
    
    output_dir = "examples/basic_usage_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n=== Example 2: Using plt.style.use directly ===")
    
    # Use matplotlib's style.use with the registered style name
    plt.style.use("seaborn-v0_8-dark-muted-notebook")
    
    x, y1, y2, y3 = create_sample_data()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y1, label=r"$\sin(x)$", linewidth=2)
    ax.plot(x, y2, label=r"$\cos(x)$", linewidth=2)
    ax.plot(x, y3, label=r"$\sin(x + \pi/4)$", linewidth=2)
    ax.set_title("Trigonometric Functions")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend()
    
    filename = f"{output_dir}/basic_direct_style.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filename}")

def example_scatter_plot():
    """Example 3: Scatter plot demonstration."""
    import os
    
    output_dir = "examples/basic_usage_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n=== Example 3: Scatter plot ===")
    
    mplstyles_seaborn.use_style("ticks", "bright", "poster")
    
    # Generate random scatter data
    prng = np.random.RandomState(42)
    x_scatter = prng.randn(200)
    y_scatter = prng.randn(200)
    colors = prng.randint(0, 6, size=200)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(x_scatter, y_scatter, c=colors, alpha=0.7, s=60)
    ax.set_title("Random Scatter Plot")
    ax.set_xlabel(r"$X$ values")
    ax.set_ylabel(r"$Y$ values")
    
    plt.colorbar(scatter, label="Color category")
    filename = f"{output_dir}/basic_scatter_plot.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filename}")

def example_font_scale_and_rc():
    """Example 4: Demonstrating font_scale and rc parameters (like seaborn.set_theme)."""
    import os
    
    output_dir = "examples/basic_usage_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n=== Example 4: font_scale and rc parameters ===")
    
    # Custom rc parameters to remove top and right spines (like seaborn)
    custom_rc = {
        'axes.spines.right': False,
        'axes.spines.top': False,
        'grid.alpha': 0.3
    }
    
    # Use style with larger font scale and custom rcParams
    mplstyles_seaborn.use_style("darkgrid", "colorblind", "talk", 
                               font_scale=1.3, rc=custom_rc)
    
    x, y1, y2, y3 = create_sample_data()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left plot: Line plot
    ax1.plot(x, y1, label=r"$\sin(x)$", linewidth=2.5)
    ax1.plot(x, y2, label=r"$\cos(x)$", linewidth=2.5)
    ax1.set_title("With Large Fonts & Custom RC")
    ax1.set_xlabel(r"$x$")
    ax1.set_ylabel(r"$y$")
    ax1.legend()
    
    # Right plot: Bar plot
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    ax2.bar(categories, values)
    ax2.set_title("Bar Chart Example")
    ax2.set_xlabel("Categories")
    ax2.set_ylabel("Values")
    
    plt.tight_layout()
    filename = f"{output_dir}/basic_font_scale_rc.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filename}")

def show_available_styles():
    """Display information about available styles."""
    print("\n=== Available Style Information ===")
    print(f"Total available styles: {len(mplstyles_seaborn.list_available_styles())}")
    print(f"Available styles: {mplstyles_seaborn.STYLES}")
    print(f"Available palettes: {mplstyles_seaborn.PALETTES}")
    print(f"Available contexts: {mplstyles_seaborn.CONTEXTS}")
    
    print("\nFirst 10 registered style names:")
    for i, style in enumerate(mplstyles_seaborn.list_available_styles()[:10]):
        print(f"  {i+1:2d}. {style}")
    print("  ...")

if __name__ == "__main__":
    print("mplstyles-seaborn Basic Usage Examples")
    print("=" * 40)
    
    show_available_styles()
    example_convenience_function()
    example_direct_style_use()
    example_scatter_plot()
    example_font_scale_and_rc()
    
    print("\n✓ All basic examples completed successfully!")