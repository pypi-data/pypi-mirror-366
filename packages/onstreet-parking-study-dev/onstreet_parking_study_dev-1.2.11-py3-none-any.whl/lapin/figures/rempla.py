# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:27 2021

@author: alaurent
@author: lgauthier
"""
import os
import itertools

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.transforms as transforms
import matplotlib.patches as mpatches
import seaborn as sns
import scipy
from statsmodels.stats.weightstats import DescrStatsW
from deprecated import deprecated


from lapin.figures import base
from lapin.figures import colors
from lapin.figures import config
from lapin.tools.utils import xform_list_entre_to_dict
from lapin import constants
from lapin.models.rempla import categorize_parking_usage
from lapin.tools.utils import IncompleteDataError


def remplacement_map(
    park_time_street,
    cols,
    delims,
    savepath="cache/",
    fig_name_base="",
    add_cat_prc=False,
    build_leg=True,
    rotation=None,
    fig_buffer=None,
    map_dpi=config.MAP_DPI,
    leg_dpi=config.LEG_DPI,
):
    """Plot all park_timeupancy wanted and save it.

    Parameters
    ----------
    park_time : geopandas.GeoDataFrame
        The compiled park_timeupancy with geobase double road segment.
    cols : str
        Name of all the columns to use for plotting. Each columns will be a different figure.
    delim : dict
        Of the form {name:geometry} with geometry a shapely.geometry.Multipolygon
        or shapely.geometry.Polygon. These geometry are delimitations of the
        different plots to be produced, each delim will generate a figure name
        using the key's value.
    savepath : str
        Where to save the images. In total there will be n_cols x n_delims figs.
    """

    park_time_street = park_time_street.copy()
    rotation = xform_list_entre_to_dict(
        rotation, list(delims.keys()), default=0, valueVarName="rotation"
    )
    fig_buffer = xform_list_entre_to_dict(
        fig_buffer, list(delims.keys()), default=100, valueVarName="fig_buffer"
    )

    for zone, delim in delims.items():
        for col in cols:
            path = os.path.join(
                savepath, f"{fig_name_base}_taux_park_time_{zone}_colonne_{col}.png"
            )
            park_time_street[col] = park_time_street[col].apply(
                lambda x: x / 3600 if pd.api.types.is_number(x) else x
            )

            park_time, n_cuts, n_colors, base_colors = base.set_color(
                data=park_time_street,
                col=col,
                numeric_cuts=config.REMPLA_NUM_CUTS,
                num_colors=config.REMPLA_COLORS,
                base_cat_colors=config.RELATIV_CAT_COLORS,
                add_cat_prc=add_cat_prc,
            )
            base._generic_plot_map(
                park_time,
                col,
                delim,
                path,
                anotate=False,
                dpi=map_dpi,
                rotation=rotation[zone],
                fig_buffer=fig_buffer[zone],
                compass_rose=True,
            )
            # legend
            os.makedirs(os.path.join(savepath, "legends"), exist_ok=True)
            leg_path = os.path.join(
                savepath,
                f"legends/{fig_name_base}_taux_park_time_{zone}_colonne_{col}.png",
            )
            base._plot_leg(
                n_cuts, n_colors, leg_path, base_cat_colors=base_colors, dpi=leg_dpi
            )


def plot_rempl_leg(save_path, leg_dpi=config.LEG_DPI):
    """
    Plot the legend of the _plot_remplacement_map func.

    Arguments
    ---------
    save_path : string
        Where to save the figure.
    """
    base._plot_leg(
        config.REMPLA_NUM_CUTS,
        config.REMPLA_COLORS,
        save_path,
        base_cat_colors=config.BASIC_CAT_COLORS,
        dpi=leg_dpi,
    )


def plot_cat_park_distrib(
    park_time, savepath, fig_base_name="", fig_dpi=config.FIG_DPI
):
    """
    Plot the distribution of the parking time as an horizontal histogram.

    Arguments
    ---------
    park_time : pandas.DataFrame
        Output of analyse.rempla._park_time_distribution
    save_path : string
        Where to save the figure
    fig_base_name : string. Default is ''.
        String to further describe the picture in the savename.

    TODO :
    1. Make more generic ? Or melt analyse.rempla.park_time_distribution
    with this func ?
    """
    park_time = park_time.copy()
    park_time.rename(
        columns={"nb_lap": "Pourcentage", "category": "Type d'utilisation"},
        inplace=True,
    )

    # make figure
    f, ax = plt.subplots(figsize=(10, 10))
    sns.barplot(
        data=park_time,
        x="Pourcentage",
        y="Type d'utilisation",
        orientation="horizontal",
        order=["Très court", "Court", "Moyen", "Long"],
        palette=colors.LAPIN_PALETTES["OCC_BLUES"](),
        ax=ax,
    )

    # Annotate
    for p in ax.patches:
        ax.annotate(
            format(p.get_width(), ".0f"),
            (p.get_width(), p.get_y() + p.get_height() / 2.0),
            ha="center",
            va="center",
            xytext=(10, 12),
            textcoords="offset points",
        )

    f.savefig(
        os.path.join(savepath, f"{fig_base_name}_distribution_parking_time.png"),
        bbox_inches="tight",
        dpi=fig_dpi,
    )
    plt.close()


def park_cat_weighted_average(
    df, data_col, weight_col, by_col, res_col="mean", confidence=0.95
):

    df["_data_times_weight"] = df[data_col] * df[weight_col]
    df["_weight_where_notnull"] = df[weight_col] * pd.notnull(df[data_col])
    g = df.groupby(by_col)
    result = pd.DataFrame(index=df[by_col].unique())
    result.index.names = [by_col]

    for idx, data in g:
        weighted_stats = DescrStatsW(data[data_col], weights=data[weight_col], ddof=0)
        result.loc[idx, res_col] = weighted_stats.mean
        result.loc[idx, "ci"] = weighted_stats.std_mean * scipy.stats.t.ppf(
            (1 + confidence) / 2.0, data.shape[0] - 1
        )
        result.loc[idx, "std"] = weighted_stats.std

    del df["_data_times_weight"], df["_weight_where_notnull"]

    return result


def do_a_barrel_roll(cat_park_time):
    """_summary_

    Parameters
    ----------
    cat_park_time : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    cat_cols = [
        col
        for col in cat_park_time.columns
        if col not in [constants.SEGMENT, constants.SIDE_OF_STREET, "weight"]
    ]
    # transform data to fit usage
    park_time_dist = cat_park_time.melt(
        [constants.SEGMENT, constants.SIDE_OF_STREET, "weight"],
        value_vars=cat_cols,
        var_name="Type d'occupation",
        value_name="Pourcentage",
    )

    return park_time_dist


def prepare_data_buterfly_plot(
    park_time: pd.DataFrame,
    occ_ts: pd.DataFrame,
    numeric_cuts_rempla: dict = None,
    handle_undetermined: dict[str, list[str]] = None,
) -> tuple[list[str], list[float], list[float], list[float]]:
    """Prepare all necessary data array for the buterfly plot.

    Parameters
    ----------
    park_time : pd.DataFrame
        Parktime dataframe for the studied time window.
    occ_ts : pd.DataFrame
        Mean occupancy for the studied time window.
    numeric_cuts_rempla : dict, optional
        Specify the length of a parking event, by default None. If None,
        default configuration is used.
    handle_undetermined : dict[str, list[str]], optional
        How to handle the undtermined parking event, by default None. If None
        then config.REMPLA_UNDETERMINED_HANDLE is used.

    Returns
    -------
    tuple[list[str], list[float], list[float], list[float]]
        Buterfly Index, Determined perc., undetermined perc., total perc.
    """

    park_time = park_time.copy()
    occ_ts = occ_ts.copy()

    if "weight" not in occ_ts.columns:
        raise IncompleteDataError(occ_ts, "weight", "prepare_data_buterfly_plot")

    if park_time.empty:
        return None, None, None, None

    # 1-categorize parking replacement
    cat_rempla = categorize_parking_usage(
        park_time=park_time, occ_ts=occ_ts, numeric_cuts=numeric_cuts_rempla
    )

    # 2-compute KPI on determined and undetermined duration separetly
    # recover columns for each dataframe
    cols_det = [c for c in cat_rempla.columns if not c.startswith("Indéterminé")]
    cols_indet = [
        c
        for c in cat_rempla.columns
        if c.startswith("Indéterminé")
        or c in ["segment", "side_of_street", "weight", constants.REMPL_CAT_NO_PARK]
    ]
    cols = [constants.SEGMENT, constants.SIDE_OF_STREET, "weight"] + list(
        numeric_cuts_rempla.keys()
    )

    # set columns to be the same
    cat_rempla_det = cat_rempla[cols_det].copy()
    cat_rempla_indet = cat_rempla[cols_indet].copy()
    cat_rempla_indet = cat_rempla_indet.rename(
        columns=lambda x: x.replace("Indéterminé ", "")
    )
    cat_rempla_indet[list(set(cols).difference(set(cat_rempla_indet.columns)))] = 0
    cat_rempla_det[list(set(cols).difference(set(cat_rempla_det.columns)))] = 0

    # pivot dataframes
    determine = park_cat_weighted_average(
        do_a_barrel_roll(cat_rempla_det),
        "Pourcentage",
        "weight",
        "Type d'occupation",
        "Déterminée",
    )
    indetermine = park_cat_weighted_average(
        do_a_barrel_roll(cat_rempla_indet),
        "Pourcentage",
        "weight",
        "Type d'occupation",
        "Indéterminée",
    )
    indetermine.loc[constants.REMPL_CAT_NO_PARK] = 0

    rr = determine.join(indetermine, rsuffix="_indetermine")

    # set undertimined short stay as undertemined duration.
    # keep long stay as if it's determined and keep distinction
    # between medium stay determined and undtermined (as default)
    if not handle_undetermined:
        handle_undetermined = config.REMPLA_UNDETERMINED_HANDLE

    labels = list(numeric_cuts_rempla.keys())

    # insert a new row by copy
    rr.loc["Indéterminé"] = rr.loc[labels[0]]

    # undetermined
    rr.loc["Indéterminé", "Déterminée"] = 0
    for cat in handle_undetermined["undetermined"]:
        try:
            rr.loc["Indéterminé", "Déterminée"] += rr.loc[cat, "Indéterminée"]
            rr.loc[cat, "Indéterminée"] = 0
        except KeyError:
            continue
    rr.loc["Indéterminé", "Indéterminée"] = 0

    # merged
    for cat in handle_undetermined["merged"]:
        try:
            rr.loc[cat, "Déterminée"] += rr.loc[cat, "Indéterminée"]
            rr.loc[cat, "Indéterminée"] = 0
        except KeyError:
            continue

    rr = rr.reindex(labels + ["Indéterminé", constants.REMPL_CAT_NO_PARK])

    idx = rr.index[::-1].to_list()
    y1 = rr["Déterminée"][::-1].to_list()
    y2 = rr["Indéterminée"][::-1].to_list()

    perc_veh_tot = []
    for label, value in numeric_cuts_rempla.items():
        mask = np.ones(park_time.shape[0])

        if label in handle_undetermined["undetermined"]:
            mask = mask & ~park_time.first_or_last

        previous_label = np.argwhere(np.array(labels) == label)[0][0] - 1
        previous_label = labels[previous_label] if previous_label >= 0 else ""
        mask = (
            mask
            & (park_time.park_time <= value * 3600)
            & (park_time.park_time > numeric_cuts_rempla.get(previous_label, 0) * 3600)
        )

        perc_veh_tot.append(park_time[mask].shape[0] / park_time.shape[0])

    max_hour_label = 0
    for ll in handle_undetermined["undetermined"]:
        if numeric_cuts_rempla[ll] > max_hour_label:
            max_hour_label = numeric_cuts_rempla[ll]

    perc_veh_tot.append(
        park_time[
            park_time.first_or_last & (park_time.park_time < max_hour_label * 3600)
        ].shape[0]
        / park_time.shape[0]
    )
    perc_veh_tot.append(0)

    perc_veh_tot = perc_veh_tot[::-1]

    return idx, y1, y2, perc_veh_tot


def buterfly_parking_time_plot(
    label: list[str],
    indetermine: list[float],
    determine: list[float],
    veh_per_label: list[float],
    title: str = "Intensité de l'utilisation de l'espace de stationnement"
    + " selon la durée",
    legend: bool = True,
    right_xlim: float = None,
    left_xlim: float = None,
) -> mpl.axes.Axes:
    """Plot the parking time and use of the space on a butterfly plot.

    Parameters
    ----------
    label : list[str]
        Label to use for the plot (in the middle, y axis).
    indetermine : list[float]
        Percentage of space used by parking event of undetermined duration.
    determine : list[float]
        Percentage of space used by parking event of determined duration.
    veh_per_label : list[float]
        Percentage of vehicule by time (label)
    title : str, optional
        Title of the plot, by default 'Intensité de l\'utilisationde l\'espace
        de stationnement selon la durée'.
    legend : bool, optional
        Create a legend, by default True
    right_xlim : float, optional
        Specify the x limit of the plot, by default None
    left_xlim : float, optional
        Specify the y limit of the plot, by default None

    Returns
    -------
    matplotlib.axes.Axes
        Figure
    """

    fig = plt.figure(figsize=(20, 9))

    # there is no data
    if not (label and indetermine and determine and veh_per_label):
        return fig

    axs = fig.subplot_mosaic(
        [["bar", "bar1"]],
        subplot_kw={"yticks": []},
        gridspec_kw={"wspace": 0.3},
    )

    plt.rcParams.update(
        {
            # general
            "figure.facecolor": "w",
            # font sizes
            "font.size": 12,
            "axes.titlesize": 16,
            "ytick.labelsize": 10,
            # force black border
            "patch.force_edgecolor": True,
            "patch.facecolor": "black",
            # remove spines
            "axes.spines.bottom": False,
            "axes.spines.left": False,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "ytick.left": False,
            "ytick.right": False,
            "xtick.major.pad": 8,
            "axes.titlepad": 10,
            # grid
            "axes.grid": True,
            "grid.color": "k",
            "grid.linestyle": ":",
            "grid.linewidth": 0.5,
            "lines.dotted_pattern": [1, 3],
            "lines.scale_dashes": False,
            # hatch
            "hatch.color": "k",
            "hatch.linewidth": 0.5,
        }
    )

    # Fill data
    axs["bar1"].barh(
        label,
        determine,
        edgecolor="black",
        linewidth=0.5,
        color=["#221F1F", "#c2c9c9"]
        + list(itertools.repeat("#2070b4", len(determine) - 2)),
    )
    axs["bar1"].barh(
        label,
        indetermine,
        left=determine,
        edgecolor="black",
        linewidth=0.5,
        color=sns.palettes.color_palette("Blues_r", len(indetermine)),
        hatch="///",
    )

    axs["bar"].barh(
        label,
        veh_per_label,
        edgecolor="black",
        linewidth=0.5,
        color=["#c2c9c9", "#c2c9c9"]
        + list(itertools.repeat("#2070b4", len(veh_per_label) - 2)),
    )
    axs["bar"].invert_xaxis()

    # Legend
    if legend:
        hatch_leg = mpatches.Patch(
            facecolor="white",
            edgecolor="black",
            linewidth=0.5,
            hatch="////",
            label="Pourrait se retrouver\n dans la classe sup.",
        )
        axs["bar1"].legend(handles=[hatch_leg], prop={"size": 14})

    # Annotate
    anotations = {}
    for p in axs["bar1"].patches:
        y = p.get_y() + p.get_height() / 2.0
        x = p.get_width()
        anotations[y] = anotations.get(y, 0) + x

    for y, x in anotations.items():
        axs["bar1"].annotate(
            format(x, ".0%"),
            (x, y),
            ha="center",
            va="center",
            xytext=(15, 5),
            textcoords="offset points",
        )

    for p in axs["bar"].patches:
        y = p.get_y() + p.get_height() / 2.0
        x = p.get_width()
        if x == 0:
            continue
        axs["bar"].annotate(
            format(x, ".0%"),
            (x, y),
            ha="center",
            va="center",
            xytext=(-15, 5),
            textcoords="offset points",
        )

    # format axes
    xfmt = mtick.PercentFormatter(xmax=1, decimals=0)
    axs["bar"].xaxis.set_major_formatter(xfmt)
    axs["bar1"].xaxis.set_major_formatter(xfmt)

    # turn on axes spines on the inside y-axis
    axs["bar"].spines["right"].set_visible(True)
    axs["bar1"].spines["left"].set_visible(True)

    # place center labels
    middle_label_offset = 0.015
    transform = transforms.blended_transform_factory(
        fig.transFigure, axs["bar1"].transData
    )
    for i, label in enumerate(label):
        axs["bar1"].text(
            0.5 + middle_label_offset,
            i,
            label,
            ha="center",
            va="center",
            transform=transform,
        )

    # labels
    fig.text(
        0.5 + middle_label_offset,
        0.875,
        "Durée du \nstationnement",
        fontsize=14,
        ha="center",
    )
    axs["bar1"].set_title("Distribution de l'occupation de l'espace")
    axs["bar"].set_title("Distribution des véhicules observés")

    # ylimits
    if left_xlim:
        axs["bar"].set_xlim(left_xlim)
    if right_xlim:
        axs["bar1"].set_xlim(right=right_xlim)

    plt.suptitle(title, fontsize="xx-large")

    return fig


@deprecated
def plot_cat_park_time(
    cat_park_time, savepath, fig_base_name="", fig_dpi=config.FIG_DPI
):
    """
    Plot the type usage of parking slot as an horizontal histogram. Display
    innoccupied slot percentage too.

    Arguments
    ---------
    cat_park_time : pandas.DataFrame
        Output of analyse.rempla.categorize_parking_usage
    save_path : string
        Where to save the figure
    fig_base_name : string. Default is ''.
        String to further describe the picture in the savename.

    TODO :
    1. Make more generic ? Or melt analyse.rempla.park_time_distribution
    with this func ?
    """

    cat_park_time = cat_park_time.copy()

    cat_cols = [
        col
        for col in cat_park_time.columns
        if col not in [constants.SEGMENT, constants.SIDE_OF_STREET, "weight"]
    ]

    # transform data to fit usage
    park_time_dist = cat_park_time.melt(
        [constants.SEGMENT, constants.SIDE_OF_STREET, "weight"],
        value_vars=cat_cols,
        var_name="Type d'occupation",
        value_name="Pourcentage",
    )
    park_time_dist["Pourcentage"] *= 100

    def weighted_average(
        df, data_col, weight_col, by_col, res_col="mean", confidence=0.95
    ) -> pd.DataFrame:
        g = df.groupby(by_col)
        result = pd.DataFrame(index=df[by_col].unique())
        result.index.names = [by_col]
        for idx, data in g:
            weighted_stats = DescrStatsW(
                data[data_col], weights=data[weight_col], ddof=0
            )
            result.loc[idx, res_col] = weighted_stats.mean
            result.loc[idx, "ci"] = weighted_stats.std_mean * scipy.stats.t.ppf(
                (1 + confidence) / 2.0, data.shape[0] - 1
            )
            result.loc[idx, "std"] = weighted_stats.std
        return result

    park_time_dist = weighted_average(
        park_time_dist, "Pourcentage", "weight", "Type d'occupation", "Pourcentage"
    )
    park_time_dist = park_time_dist.reset_index()

    error = park_time_dist["ci"].values

    # create figure
    f, ax = plt.subplots(figsize=(10, 10))

    g = sns.barplot(
        data=park_time_dist,
        x="Pourcentage",
        y="Type d'occupation",
        # hue="Type d'occupation",
        order=cat_cols,  # ['Places inocupées','Places très courte durée',
        # 'Places courte durée', 'Places moyenne durée',
        #'Places longue durée'],
        orient="h",
        palette="Blues",
        dodge=False,
        xerr=error,
        ax=ax,
    )
    if g.legend_:
        g.legend.remove()
    # Annotate
    for p in ax.patches:
        ax.annotate(
            format(p.get_width(), ".0f"),
            (p.get_width(), p.get_y() + p.get_height() / 2.0),
            ha="center",
            va="center",
            xytext=(10, 12),
            textcoords="offset points",
        )

    f.savefig(
        os.path.join(savepath, f"{fig_base_name}categorisation_parking_time.png"),
        bbox_inches="tight",
        dpi=fig_dpi,
    )
    plt.close()


def park_time_provenance(
    park_time_dist, savepath, fig_base_name, fig_dpi=config.FIG_DPI
):
    """
    Plot the parking time by provenance as an horizontal histogram. Display
    innoccupied slot percentage too.

    Arguments
    ---------
    cat_park_time : pandas.DataFrame
        Output of analyse.rempla.parking_time_by_provenance
    save_path : string
        Where to save the figure
    fig_base_name : string. Default is ''.
        String to further describe the picture in the savename.

    TODO :
    1. Make more generic ? Or melt analyse.rempla.park_time_distribution
    with this func ?
    """
    park_time_dist = park_time_dist.copy()
    park_time_dist.rename(
        columns={"dist_class": "Distance", "category": "Type de stationnement"},
        inplace=True,
    )

    # Figures
    g = sns.FacetGrid(
        park_time_dist,
        col="Distance",
        hue="Type de stationnement",
        aspect=1,
        height=3,
        palette=colors.LAPIN_PALETTES["OCC_BLUES"](),
        col_wrap=3,
        legend_out=True,
    )

    g.map(
        sns.barplot,
        "Pourcentage d'immobilisation totale",
        "Type de stationnement",
        alpha=1,
        ci=95,
        capsize=0.2,
        order=["Très court", "Court", "Moyen", "Long"],
        orient="h",
    )
    # Annotate
    for ax in g.axes.ravel():
        ax.set_xlabel("")
        ax.set_ylabel("")
        for p in ax.patches:
            ax.annotate(
                format(p.get_width(), ".0f"),
                (p.get_width(), p.get_y() + p.get_height() / 2.0),
                ha="center",
                va="center",
                xytext=(10, 12),
                textcoords="offset points",
            )

    # plt.xlabel("Pourcentage d'immobilisation totale")
    # plt.ylabel("Type de stationnement")

    g.savefig(
        os.path.join(savepath, f"{fig_base_name}distance_parking_time.png"), dpi=fig_dpi
    )
    plt.close()


def park_time_hist_plot(data, savepath, fig_base_name, fig_dpi=config.FIG_DPI):
    """plot the histogram of parking duration."""

    data = data.copy()
    data = data[~data.first_or_last]
    # seconds to hours
    data.park_time /= 3600
    # add columns of info
    data.datetime = pd.to_datetime(data.datetime)
    data["Période"] = [
        "Fin de semaine" if x in [5, 6] else "Semaine" for x in data.datetime.dt.weekday
    ]

    bins = [
        0,
        0.5,
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        4.5,
        5,
        5.5,
        6,
        6.5,
        max(data.park_time.max(), 24),
    ]
    with sns.axes_style("whitegrid"):
        f, ax = plt.subplots()
        sns.histplot(
            data=data,
            x="park_time",
            bins=bins,
            hue="Période",
            multiple="dodge",
            shrink=0.8,
            palette="Blues_r",
            alpha=1,
            ax=ax,
        )
        ax.set_xlabel("Temps de stationnement")
        ax.set_ylabel("Nombre d'immobilisation")

        ax.set_xticks(bins[:-1])
        ax.set_xticklabels([f"{int(t*60)} min" for t in bins[:-1]], rotation=45)

        ax.tick_params(bottom=False)
        ax.grid(axis="x")

        f = plt.gcf()
        f.savefig(
            os.path.join(savepath, f"{fig_base_name}parking_time_distribution.png"),
            dpi=fig_dpi,
        )
        plt.close()
