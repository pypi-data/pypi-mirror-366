#!/usr/bin/env python3
"""Research script to extract seaborn style components."""

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from pprint import pprint

# Available seaborn contexts and palettes
print("=== Seaborn Contexts ===")
print(sns.plotting_context.__doc__)
contexts = ['paper', 'notebook', 'talk', 'poster']
print(f"Available contexts: {contexts}")

print("\n=== Seaborn Palettes ===")
palettes = ['deep', 'muted', 'bright', 'pastel', 'dark', 'colorblind']
print(f"Available palettes: {palettes}")

print("\n=== Seaborn Styles ===")
styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
print(f"Available styles: {styles}")

# Set seaborn-v0_8-dark theme and examine rcParams
print("\n=== Setting seaborn-v0_8-dark theme ===")
sns.set_theme(style='darkgrid', palette='dark', context='notebook')

# Get current rcParams that differ from matplotlib defaults
default_rcparams = mpl.rcParamsDefault.copy()
current_rcparams = mpl.rcParams.copy()

seaborn_changes = {}
for key, value in current_rcparams.items():
    if key in default_rcparams and default_rcparams[key] != value:
        seaborn_changes[key] = value

print(f"\nFound {len(seaborn_changes)} changed rcParams:")
pprint(seaborn_changes)

# Test different combinations
print("\n=== Testing combinations ===")
combinations = [
    {'style': 'darkgrid', 'palette': 'dark', 'context': 'notebook'},
    {'style': 'darkgrid', 'palette': 'colorblind', 'context': 'notebook'},
    {'style': 'darkgrid', 'palette': 'dark', 'context': 'talk'},
    {'style': 'darkgrid', 'palette': 'colorblind', 'context': 'talk'},
]

for combo in combinations:
    print(f"\nCombination: {combo}")
    sns.set_theme(**combo)
    
    # Get the specific changes for this combination
    combo_rcparams = mpl.rcParams.copy()
    combo_changes = {}
    for key, value in combo_rcparams.items():
        if key in default_rcparams and default_rcparams[key] != value:
            combo_changes[key] = value
    
    print(f"  Changed rcParams: {len(combo_changes)} parameters")
    
    # Save this combination's style to a file
    style_name = f"seaborn-v0_8-{combo['style']}-{combo['palette']}-{combo['context']}"
    print(f"  Style name: {style_name}")