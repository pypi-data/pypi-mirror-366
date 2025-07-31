#!/usr/bin/env python3
"""
Style comparison demonstration for mplstyles-seaborn package.

This script is based on matplotlib's style_sheets_reference.py and demonstrates
different mplstyles-seaborn styles using a common set of example plots.
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import mplstyles_seaborn

# Set random seed for reproducibility
np.random.seed(19680801)

def plot_scatter(ax, prng, nb_samples=100):
    """Create a scatter plot."""
    for mu, sigma, marker in [(-.5, 0.75, 'o'), (0.75, 1., 's')]:
        x, y = prng.normal(loc=mu, scale=sigma, size=(2, nb_samples))
        ax.plot(x, y, ls='none', marker=marker)
    ax.set_xlabel(r'$X$-label')
    ax.set_title('Scatter Plot')
    return ax

def plot_colored_lines(ax):
    """Plot lines with colors following the style color cycle."""
    t = np.linspace(-10, 10, 100)
    
    def sigmoid(t, t0):
        return 1 / (1 + np.exp(-(t - t0)))
    
    nb_colors = len(plt.rcParams['axes.prop_cycle'])
    shifts = np.linspace(-5, 5, nb_colors)
    amplitudes = np.linspace(1, 1.5, nb_colors)
    for t0, a in zip(shifts, amplitudes):
        ax.plot(t, a * sigmoid(t, t0), '-')
    ax.set_xlim(-10, 10)
    ax.set_title('Line Plot')
    return ax

def plot_bar_graphs(ax, prng, min_value=5, max_value=25, nb_samples=5):
    """Plot two bar graphs side by side."""
    x = np.arange(nb_samples)
    ya, yb = prng.randint(min_value, max_value, size=(2, nb_samples))
    width = 0.35
    ax.bar(x, ya, width, label='Series A')
    ax.bar(x + width, yb, width, label='Series B')
    ax.set_xticks(x + width/2, labels=['A', 'B', 'C', 'D', 'E'])
    ax.set_title('Bar Chart')
    ax.legend()
    return ax

def plot_histograms(ax, prng, nb_samples=10000):
    """Plot overlapping histograms."""
    params = ((10, 10), (4, 12), (50, 12), (6, 55))
    for a, b in params:
        values = prng.beta(a, b, size=nb_samples)
        ax.hist(values, histtype="stepfilled", bins=30,
                alpha=0.8, density=True)
    ax.set_title('Histograms')
    return ax

def plot_figure(style_name, style_config):
    """Create a demonstration figure with the given style."""
    # Apply the style
    if len(style_config) == 3:
        mplstyles_seaborn.use_style(style_config[0], style_config[1], style_config[2])
    else:
        plt.style.use(style_config[0])
    
    # Use consistent random state
    prng = np.random.RandomState(96917002)
    
    fig, axs = plt.subplots(ncols=4, nrows=1, figsize=(16, 4), 
                           layout='constrained')
    
    # Determine title color based on background
    background_color = mcolors.rgb_to_hsv(
        mcolors.to_rgb(plt.rcParams['figure.facecolor']))[2]
    if background_color < 0.5:
        title_color = [0.8, 0.8, 1]
    else:
        title_color = np.array([19, 6, 84]) / 256
    
    fig.suptitle(style_name, x=0.02, ha='left', color=title_color,
                 fontsize=16, fontweight='bold')
    
    # Create plots
    plot_scatter(axs[0], prng)
    plot_colored_lines(axs[1])
    plot_bar_graphs(axs[2], prng)
    plot_histograms(axs[3], prng)
    
    return fig

def demonstrate_all_combinations():
    """Generate comparison plots for all 120 style combinations."""
    import os
    
    # Create output directory
    output_dir = "examples/style_comparison_output"
    os.makedirs(output_dir, exist_ok=True)
    
    styles = mplstyles_seaborn.STYLES
    palettes = mplstyles_seaborn.PALETTES  
    contexts = mplstyles_seaborn.CONTEXTS
    
    total_combinations = len(styles) * len(palettes) * len(contexts)
    print(f"Creating {total_combinations} style comparison plots...")
    
    count = 0
    for style in styles:
        for palette in palettes:
            for context in contexts:
                count += 1
                style_name = f"{style} + {palette} + {context}"
                style_config = (style, palette, context)
                
                fig = plot_figure(style_name, style_config)
                
                # Save the figure
                filename = f"{output_dir}/comparison_{style}_{palette}_{context}.png"
                fig.savefig(filename, dpi=150, bbox_inches='tight')
                plt.close(fig)
                
                if count % 10 == 0:
                    print(f"Progress: {count}/{total_combinations} plots completed")
    
    print(f"✓ All {total_combinations} comparison plots saved to {output_dir}/")

def demonstrate_context_comparison():
    """Compare the same style with different contexts."""
    import os
    
    output_dir = "examples/style_comparison_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nCreating context comparison...")
    
    base_style = ("whitegrid", "colorblind")
    contexts = ["paper", "notebook", "talk", "poster"]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    prng = np.random.RandomState(96917002)
    
    for i, context in enumerate(contexts):
        # Apply style with current context
        mplstyles_seaborn.use_style(base_style[0], base_style[1], context)
        
        ax = axes[i]
        
        # Create a simple line plot to show context differences
        x = np.linspace(0, 10, 100)
        for j in range(3):
            y = np.sin(x + j * np.pi/3)
            ax.plot(x, y, label=f'Line {j+1}', linewidth=2)
        
        ax.set_title(f'Context: {context}', fontsize=plt.rcParams['axes.titlesize'])
        ax.set_xlabel(r'$X$ values')
        ax.set_ylabel(r'$Y$ values')
        ax.legend()
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/context_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_dir}/context_comparison.png")

if __name__ == "__main__":
    print("mplstyles-seaborn Style Comparison Demo")
    print("=" * 42)
    
    demonstrate_all_combinations()
    demonstrate_context_comparison()
    
    print("\n✓ All style comparison examples completed successfully!")