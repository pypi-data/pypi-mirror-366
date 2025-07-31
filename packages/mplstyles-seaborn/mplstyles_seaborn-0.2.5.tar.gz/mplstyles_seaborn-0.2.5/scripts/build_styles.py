#!/usr/bin/env python3
"""Build matplotlib style sheets from seaborn themes with integrated fixing."""

import argparse
import os
import re
from pathlib import Path

import matplotlib as mpl
import seaborn as sns


def format_rcparam_value(key, value):
    """Format rcParam values for mplstyle files with proper matplotlib formatting."""
    if isinstance(value, str):
        return value
    elif hasattr(value, "name"):  # For enums like CapStyle
        # Handle specific enum cases
        if "capstyle" in key.lower():
            return value.name.lower()  # matplotlib expects lowercase for capstyle
        return value.name
    elif hasattr(value, "_keys"):  # It's a cycler
        # Extract color values from cycler and format properly for matplotlib
        colors = [item["color"] for item in value]
        color_strs = []
        for color in colors:
            if isinstance(color, tuple):
                # Convert RGB tuple to hex without # prefix
                hex_color = "{:02x}{:02x}{:02x}".format(
                    int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
                )
                color_strs.append(hex_color)
            else:
                # Remove # prefix from hex colors for matplotlib style files
                color_str = str(color).lstrip('#')
                color_strs.append(color_str)
        # Format as proper cycler syntax for matplotlib
        colors_str = "', '".join(color_strs)
        return f"cycler('color', ['{colors_str}'])"
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    else:
        return str(value)


def generate_style_file(style_config, output_path):
    """Generate a matplotlib style file from seaborn configuration."""
    # Reset to defaults first
    mpl.rcParams.update(mpl.rcParamsDefault)

    # Apply seaborn theme
    sns.set_theme(**style_config)

    # Get changes from defaults
    default_rcparams = mpl.rcParamsDefault
    current_rcparams = mpl.rcParams

    changes = {}
    for key, value in current_rcparams.items():
        if key in default_rcparams and default_rcparams[key] != value:
            # Skip problematic parameters
            if key == "image.cmap" and value == "rocket":
                continue  # rocket colormap doesn't exist in matplotlib
            changes[key] = value
    
    # Force include essential style parameters even if they match defaults
    essential_params = [
        'axes.facecolor',
        'axes.grid', 
        'xtick.bottom',
        'ytick.left'
    ]
    for param in essential_params:
        if param in current_rcparams and param not in changes:
            changes[param] = current_rcparams[param]

    # Add custom font settings
    changes["mathtext.default"] = "regular"
    changes["mathtext.fallback"] = "stixsans"
    changes["pdf.fonttype"] = 42  # Use Type 42 (TrueType) fonts in PDF
    changes["font.family"] = "sans-serif"  # Ensure font.family is set

    # Update font.sans-serif to include Source Sans 3 at the beginning
    if "font.sans-serif" in changes:
        current_fonts = changes["font.sans-serif"]
        if isinstance(current_fonts, str):
            font_list = [f.strip() for f in current_fonts.split(",")]
        else:
            font_list = current_fonts
        # Add Source Sans 3 at the beginning if not already there
        if "Source Sans 3" not in font_list:
            font_list.insert(0, "Source Sans 3")
        changes["font.sans-serif"] = ", ".join(font_list)
    else:
        # If font.sans-serif wasn't changed by seaborn, add our custom setting
        changes["font.sans-serif"] = "Source Sans 3, DejaVu Sans, sans-serif"

    # Write style file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("# Matplotlib style sheet\n")
        f.write(f"# Generated from seaborn configuration: {style_config}\n")
        f.write(f"# Total parameters changed: {len(changes)}\n\n")

        for key, value in sorted(changes.items()):
            formatted_value = format_rcparam_value(key, value)
            # Additional formatting fixes for specific parameters
            if key == "axes.facecolor" and isinstance(formatted_value, str):
                # Ensure facecolor is unquoted and without # prefix
                formatted_value = formatted_value.strip("'\"").lstrip('#')
            f.write(f"{key}: {formatted_value}\n")

    print(f"Generated style file: {output_path} ({len(changes)} parameters)")


def fix_existing_styles(styles_dir):
    """Fix formatting issues in existing style files."""
    print("Fixing existing style files...")
    
    for style_file in styles_dir.glob("*.mplstyle"):
        content = style_file.read_text()
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Fix axes.prop_cycle - use proper cycler syntax
            if line.startswith("axes.prop_cycle:"):
                colors_part = line.split(":", 1)[1].strip()
                # Handle existing cycler syntax by extracting colors
                if "cycler(" in colors_part:
                    # Extract colors from cycler syntax
                    color_match = re.search(r"cycler\('color', \[(.*?)\]\)", colors_part)
                    if color_match:
                        colors_str = color_match.group(1)
                        # Remove quotes from individual colors
                        colors = [
                            color.strip().strip("'\"") for color in colors_str.split(",")
                        ]
                    else:
                        colors = [color.strip() for color in colors_part.split(",")]
                else:
                    colors = [color.strip() for color in colors_part.split(",")]

                # Use proper cycler syntax that matplotlib requires
                # Remove # prefix from hex colors for matplotlib style files
                colors_clean = [color.lstrip('#') for color in colors]
                colors_str = "', '".join(colors_clean)
                fixed_line = f"axes.prop_cycle: cycler('color', ['{colors_str}'])"
                fixed_lines.append(fixed_line)

            # Fix facecolor - ensure hex colors are unquoted and without # prefix for matplotlib
            elif line.startswith("axes.facecolor:"):
                color_part = line.split(":", 1)[1].strip()
                # Don't modify colors that are already correct (like 'white' or hex without #)
                # Only remove quotes and # prefix if present
                if color_part.startswith("'") or color_part.startswith('"'):
                    color_part = color_part.strip("'\"")
                if color_part.startswith('#'):
                    color_part = color_part.lstrip('#')
                fixed_line = f"axes.facecolor: {color_part}"
                fixed_lines.append(fixed_line)

            # Fix capstyle
            elif "lines.solid_capstyle: CapStyle.round" in line:
                fixed_lines.append(line.replace("CapStyle.round", "round"))

            else:
                fixed_lines.append(line)

        # Add font.family setting if not present
        has_font_family = any(line.startswith("font.family:") for line in fixed_lines)
        if not has_font_family:
            # Find where to insert font.family (after font.sans-serif if present)
            insert_idx = len(fixed_lines)
            for i, line in enumerate(fixed_lines):
                if line.startswith("font.sans-serif:"):
                    insert_idx = i + 1
                    break
            fixed_lines.insert(insert_idx, "font.family: sans-serif")

        style_file.write_text("\n".join(fixed_lines))
        print(f"Fixed {style_file.name}")


def main():
    """Build all style combinations with optional modes."""
    parser = argparse.ArgumentParser(description="Build matplotlib style sheets from seaborn themes")
    parser.add_argument("--fix-only", action="store_true", 
                       help="Only fix existing style files without regenerating")
    parser.add_argument("--generate-only", action="store_true",
                       help="Only generate new style files without fixing")
    
    args = parser.parse_args()
    
    styles_dir = Path("../src/mplstyles_seaborn/styles")

    if args.fix_only:
        fix_existing_styles(styles_dir)
        return

    # Define all available options
    styles = ["darkgrid", "whitegrid", "dark", "white", "ticks"]
    palettes = ["dark", "colorblind", "muted", "bright", "pastel", "deep"]
    contexts = ["paper", "notebook", "talk", "poster"]

    combinations = []

    # Generate comprehensive combinations
    for style in styles:
        for palette in palettes:
            for context in contexts:
                combinations.append(
                    {"style": style, "palette": palette, "context": context}
                )

    print(f"Generating {len(combinations)} style combinations...")

    for config in combinations:
        # Create filename
        filename = f"seaborn-v0_8-{config['style']}-{config['palette']}-{config['context']}.mplstyle"
        output_path = styles_dir / filename

        generate_style_file(config, output_path)

    # Apply fixes unless --generate-only is specified
    if not args.generate_only:
        print("\nApplying final formatting fixes...")
        fix_existing_styles(styles_dir)

    print(f"\n✅ Successfully built {len(combinations)} style files!")


if __name__ == "__main__":
    main()