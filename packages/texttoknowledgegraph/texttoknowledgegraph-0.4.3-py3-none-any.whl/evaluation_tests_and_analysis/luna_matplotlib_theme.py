import matplotlib.pyplot as plt
import numpy as np

# Define global visual style
base_font_size = 48
custom_theme = {
    'font.size': base_font_size,
    'axes.titlesize': base_font_size,
    'axes.labelsize': base_font_size,
    'legend.fontsize': base_font_size,
    'legend.edgecolor': 'black',
    'legend.frameon': False,
    'lines.linewidth': 0.5,
    'font.family': ['Arial', 'sans-serif'],
    'svg.fonttype': 'none',
    'pdf.fonttype': 'truetype',
    'axes.spines.top': True,
    'axes.spines.right': True,
    'axes.spines.left': True,
    'axes.spines.bottom': True,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.labelsize': base_font_size,
    'ytick.labelsize': base_font_size
}


# Apply the theme to matplotlib globally
def apply_luna_theme():
    for key, value in custom_theme.items():
        plt.rcParams[key] = value
