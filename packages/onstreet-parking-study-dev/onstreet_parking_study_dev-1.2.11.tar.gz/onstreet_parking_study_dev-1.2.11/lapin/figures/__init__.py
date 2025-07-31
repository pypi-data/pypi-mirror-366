from lapin.constants import MONTREAL_CRS as STUDY_CRS
import matplotlib.pyplot as plt

plt.rcParams.update({
    # general
    'figure.facecolor': 'w',
    # font sizes
    'font.size': 12,
    'axes.titlesize': 16,
    'ytick.labelsize': 10,
    # force black border
    'patch.force_edgecolor': True,
    'patch.facecolor': 'black',
    # remove spines
    'axes.spines.bottom': False,
    'axes.spines.left': False,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'ytick.left': False,
    'ytick.right': False,
    'xtick.major.pad': 8,
    'axes.titlepad': 10,
    # grid
    'axes.grid': True,
    'grid.color': 'k',
    'grid.linestyle': ':',
    'grid.linewidth': 0.5,
    'lines.dotted_pattern': [1, 3],
    'lines.scale_dashes': False,
    # hatch
    'hatch.color': 'k',
    'hatch.linewidth': 0.5
})
