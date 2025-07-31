# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:27 2021

@author: lgauthier
"""
import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
from adjustText import adjust_text

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

from lapin import constants
from lapin.figures import config
from lapin.figures import base
from lapin.figures import colors
from lapin.figures import STUDY_CRS

from lapin.tools.ctime import Ctime


def plot_distribution(
    lapi, save_path, basename="", x="dist_ori_m", dpi=config.FIG_DPI, stat="percent"
):
    lapi = lapi.copy()
    lapi[x] /= 1000

    # get unique plaque per day
    # lapi['day'] = lapi.datetime.dt.day
    lapi = lapi.copy()

    ### distribution
    # set a grey background (use sns.set_theme() if seaborn version 0.11.0 or above)
    with sns.axes_style("darkgrid"):
        # creating a figure composed of two matplotlib.Axes objects (ax_box and ax_hist)
        f, (ax_box, ax_hist) = plt.subplots(
            2, sharex=True, gridspec_kw={"height_ratios": (0.15, 0.85)}, dpi=100
        )

        # assigning a graph to each ax
        sns.boxplot(data=lapi, x=x, showfliers=False, ax=ax_box)
        sns.histplot(data=lapi[lapi[x] <= 45], x=x, binwidth=1, ax=ax_hist, stat=stat)

        # Remove x axis name for the boxplot
        ax_box.set(xlabel="")

        # set labels
        ylabel = "Nombre d'immobilisations"
        if stat == "percent":
            ylabel += " (%)"
        ax_hist.set_ylabel(ylabel)
        ax_hist.set_xlabel("Distance (km)")

        # save fig
        f.savefig(f"{save_path}/{basename}distribution_distances", dpi=dpi)
        plt.close()


def _choropleth_map(
    data,
    save_path,
    bar_title,
    bounds=gpd.GeoDataFrame(),
    x_col="count",
    numeric_cuts=None,
    mc_k=5,
    add_cat_num=True,
    anotate=False,
    regs_zoom=None,
    hydro_order=1,
    road_order=2,
    data_order=3,
    data_edge_color="k",
    cmap="Blues",
    hydro_path=config.HYDRO_SHAPE,
    road_path=config.ROAD_SHAPE,
    map_dpi=config.MAP_DPI,
):

    data = data.copy().to_crs(STUDY_CRS)
    # bounding box delim
    if bounds.empty:
        bounds = data.copy()
    elif bounds.crs is None:
        raise ValueError("`bounds` is missing a crs, cannot proceed")
    else:
        bounds = bounds.to_crs(STUDY_CRS)

    df2, _ = base.create_bounds_gdf(bounds)

    f, ax = base.basemap_from_shapefile(
        bounds=bounds,
        hydro_order=hydro_order,
        road_order=road_order,
        hydro_path=hydro_path,
        road_path=road_path,
    )

    data = gpd.clip(data, df2)

    # Categorize
    if not numeric_cuts:
        numeric_cuts = base._numerical_cuts(data[x_col], k=mc_k, base=1)

    if add_cat_num:
        numeric_cuts = {k + " ({:d})": v for k, v in numeric_cuts.items()}

    labels = list(numeric_cuts.keys())
    data["category"] = pd.cut(
        data[x_col],
        [0] + list(numeric_cuts.values()),
        labels=labels,
        include_lowest=True,
    )

    # complete the labels
    if add_cat_num:
        replace = {
            labels[i]: labels[i].format(data[(data["category"] == labels[i])].shape[0])
            for i in range(len(labels))
        }
        data["category"] = data["category"].map(replace)
        labels = list(replace.values())

    num_colors = base._numeric_color(labels, cmap)

    data["category"] = data["category"].astype(str)
    data["color_cat"] = data["category"].map(num_colors)

    data.plot(
        ax=ax,
        alpha=0.8,
        legend=False,
        color=data["color_cat"],
        # column=x_col,
        # cmap=cmap,
        edgecolor=data_edge_color,
        zorder=data_order,
    )

    if anotate:
        texts = []
        data_num = data.copy()
        for _, row in data_num.iterrows():
            if not row["geometry"]:
                continue
            texts.append(
                ax.text(
                    *row["geometry"].representative_point().coords[0],
                    s=f"{int(np.round(row[x_col],0))}%",
                    alpha=0.7,
                    fontsize=8,
                )
            )

        # adjust_text(texts)

    if regs_zoom:
        # create an index of regions bounds
        statesbounds = data.bounds
        statesbounds = statesbounds.merge(
            data["reg"], how="left", left_on=statesbounds.index, right_on=data.index
        )
        statesbounds = statesbounds.set_index("reg")
        statesbounds.drop("key_0", axis=1, inplace=True)

        # create a zoom window
        axins = zoomed_inset_axes(ax, 3, loc="lower right")

        minx, miny, _, _ = statesbounds.loc[regs_zoom].min()
        _, _, maxx, maxy = statesbounds.loc[regs_zoom].max()
        axins.set_xlim(minx, maxx)
        axins.set_ylim(miny, maxy)

        mark_inset(
            ax, axins, loc1=1, loc2=3, fc="none", ec="0.5", zorder=data_order + 1
        )

        # Plot zoom window
        data_zoom = data.loc[data["reg"].isin(regs_zoom)].copy()
        data_zoom.plot(
            ax=axins,
            alpha=0.8,
            legend=False,
            color=data_zoom["color_cat"],
            edgecolor=data_edge_color,
            zorder=data_order,
        )
        data_zoom["coords"] = data_zoom["geometry"].apply(
            lambda x: x.representative_point().coords[:]
        )
        data_zoom["coords"] = [coords[0] for coords in data_zoom["coords"]]
        for _, row in data_zoom.iterrows():
            plt.annotate(
                text=f"{int(np.round(row[x_col],0))}%",
                xy=row["coords"],
                horizontalalignment="center",
            )

        # X AXIS -BORDER
        axins.axes.get_xaxis().set_visible(False)

        # Y AXIS -BORDER
        axins.axes.get_yaxis().set_visible(False)

    # Now adding the colorbar
    base._build_legend(
        ax,
        title="Légende",
        title_color=colors.LAPIN_COLORS.LEG_TXT,
        bbox_to_anchor=(0.5, -0.01),
        loc="upper center",
        kdes_kwords=[{"label": str(k), "color": v} for k, v in num_colors.items()],
        align_title="left",
        ncol=(len(num_colors) // 4 + int(len(num_colors) % 4 > 0)),
        facecolor=colors.LAPIN_COLORS.LEGEND_BG,
        labelcolor=colors.LAPIN_COLORS.LEG_TXT,
    )

    f.savefig(save_path, dpi=map_dpi)
    plt.close()


def choropleth_prov_in_mtl(
    prov_by_reg,
    save_path,
    numeric_cuts=config.PROV_NUM_CUTS,
    mc_k=5,
    add_cat_num=True,
    anotate=False,
    basename="",
    col="prc_reg",
    map_dpi=config.MAP_DPI,
):

    prov_by_reg = prov_by_reg.copy()

    prov_by_reg = prov_by_reg[
        ~prov_by_reg["reg"].isin(
            ["Couronne Nord", "Couronne Sud", "Hors ARTM", "Laval", "Rive-Sud"]
        )
    ]
    cmap = colors.LAPIN_PALETTES["PROV_REDS"](as_cmap=True)

    _choropleth_map(
        prov_by_reg,
        x_col=col,
        numeric_cuts=numeric_cuts,
        mc_k=mc_k,
        add_cat_num=add_cat_num,
        anotate=anotate,
        regs_zoom=[],
        cmap=cmap,
        bar_title="Pourcentage d'immobilisations partant d'un port d'attache",
        save_path=f"{save_path}/{basename}Distribution_des_origines_centré_sur_Montréal",
        map_dpi=map_dpi,
    )


def choropleth_prov_in_artm(
    prov_by_reg,
    save_path,
    numeric_cuts=config.PROV_NUM_CUTS,
    mc_k=5,
    add_cat_num=True,
    anotate=False,
    regs_zoom=None,
    basename="",
    col="prc_reg",
    map_dpi=config.MAP_DPI,
):

    prov_by_reg = prov_by_reg.copy()

    prov_by_reg = prov_by_reg[~prov_by_reg["reg"].isin(["Hors ARTM"])]
    cmap = colors.LAPIN_PALETTES["PROV_REDS"](as_cmap=True)

    _choropleth_map(
        prov_by_reg,
        x_col=col,
        numeric_cuts=numeric_cuts,
        mc_k=mc_k,
        add_cat_num=add_cat_num,
        anotate=anotate,
        regs_zoom=regs_zoom,
        cmap=cmap,
        bar_title="Pourcentage d'immobilisations partant d'un port d'attache",
        save_path=f"{save_path}/{basename}Distribution_des_origines_centré_sur_ARTM",
        map_dpi=map_dpi,
    )


def kde_plot_in_artm(
    trips,
    reg,
    save_path,
    basename="",
    classe_dist=[0, 1, 3, 7, 15, np.inf],
    map_dpi=config.MAP_DPI,
):

    trips = trips.copy().to_crs(STUDY_CRS)
    reg = reg.copy().to_crs(STUDY_CRS)
    reg = reg[~reg["reg"].isin(["Hors ARTM"])]

    # define classe_str and colors
    classe_str = [f"<{i} km" for i in classe_dist[1:-1]] + [f"{classe_dist[-2]}+ km"]
    colors_list = list(
        colors.LAPIN_PALETTES["PROV_BLUES"](reverse=True, n_colors=len(classe_str) + 1)
    )
    cmap = colors.LAPIN_PALETTES["PROV_BLUES"](
        as_cmap=True, reverse=True, n_colors=len(classe_str) + 1
    )

    # make legend dict
    kdes_kwords = []
    for c, l in zip(colors_list[::-1], classe_str):
        kdes_kwords.append({"color": c, "label": l, "alpha": 1})

    # kde_levels
    levels = [
        0.08259587020648967,
        0.20501474926253688,
        0.38200589970501475,
        0.6887905604719764,
        0.9144542772861357,
        1.0,
    ]
    # levels= len(classe_str) + 1

    f, ax = base.basemap_from_shapefile(bounds=reg, hydro_order=2, road_order=3)
    t = gpd.clip(trips, reg).copy()
    t["x"] = t.geometry.x
    t["y"] = t.geometry.y

    sns.kdeplot(
        data=t,
        x="x",
        y="y",
        ax=ax,
        fill=True,
        alpha=1,
        zorder=1,
        levels=levels,
        cmap=cmap,
    )
    sns.kdeplot(
        data=t,
        x="x",
        y="y",
        ax=ax,
        fill=False,
        alpha=1,
        zorder=1,
        levels=levels,
        color="white",
        linewidths=0.5,
    )
    base._build_legend(ax=ax, bbox_to_anchor=(0, 1), kdes_kwords=kdes_kwords)

    f.savefig(f"{save_path}/{basename}KDE_des_origines_centré_sur_la_CMM", dpi=map_dpi)
    plt.close()


def trace_dist(
    lapi,
    artm,
    which_days="fin de semaine",
    how="stacked",
    classe_dist=[0, 0.3, 0.5, 1, 3, 7, 15, np.inf],
    # class_str=['<300 m', '<500 m', '<1 km', ],
    save_path="./",
    x_order=None,
    basename="",
    fig_dpi=config.FIG_DPI,
):
    """
    This assumes that lapi contains the following columns:
        - IsCom
        - InArtm
        - Immat
        - DistClass

        where immat is the shapely.geometry.Point object reflecting the UDL
        associated with this vehicule

    Parameters
    ----------
    lapi : TYPE
        DESCRIPTION.
    troncons : TYPE
        DESCRIPTION.
    artm : TYPE
        DESCRIPTION.
    code_postaux : TYPE
        DESCRIPTION.
    type_plaques : TYPE
        DESCRIPTION.
    which_days : TYPE, optional
        DESCRIPTION. The default is 'fin de semaine'.
    classe_dist : TYPE, optional
        DESCRIPTION. The default is [0, 1, 3, 7, 15, np.inf].
    save_path : TYPE, optional
        DESCRIPTION. The default is './'.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    # set the weekday if it doesn't exists
    lapi = lapi.copy().to_crs(STUDY_CRS)
    lapi[constants.PLATE] = np.arange(0, lapi.shape[0], 1)
    # lapi.datetime = pd.to_datetime(lapi.datetime)
    # lapi['weekday'] = lapi.datetime.dt.dayofweek
    # lapi['is_week'] = lapi['weekday'] < 5

    #########

    classe_str = [
        f"<{int(i*1000)} m" if i < 1 else f"<{i} km" for i in classe_dist[1:-1]
    ] + [f"{classe_dist[-2]}+ km"]
    lapi["dist_class"] = pd.cut(
        lapi.dist_ori_m / 1000, bins=classe_dist, labels=classe_str
    )

    # rework the 20+ km class
    lapi = gpd.sjoin(
        lapi,
        artm[["reg", "geometry"]].to_crs(STUDY_CRS),
        predicate="within",
        how="left",
    )

    def to_Ctime(datetime):
        return (
            Ctime.from_datetime(datetime).round_time(round_min_base=30, how="ceil").time
            // 100
        )

    def change_in_artm(assigned_class, in_artm, class_text="20+ km"):
        if not assigned_class == class_text:
            return assigned_class

        if not in_artm:
            return "Hors ARTM"
        else:
            return assigned_class

    lapi["distClass"] = lapi.apply(
        lambda x: change_in_artm(
            x.dist_class, not np.isnan(x.index_right), class_text=classe_str[-1]
        ),
        axis=1,
    )
    # lapi['30min_hrs']  = lapi.apply(lambda x: to_Ctime(x.datetime), axis=1)

    # if which_days == 'semaine':
    # lapi = lapi.query('is_week == True')
    # elif which_days == 'fin de semaine':
    # lapi = lapi.query('is_week == False')
    # else:
    # lapi = lapi

    # if lapi.empty:
    #    return -1

    grouped = (
        lapi.groupby(["period", "distClass"])
        .agg({constants.PLATE: pd.Series.nunique})
        .reset_index()
    )
    pivoted = grouped.pivot_table(
        values=constants.PLATE, index="period", columns="distClass"
    ).fillna(0)
    if x_order:
        pivoted = pivoted.loc[x_order]
    normalized = pivoted.copy().apply(lambda x: x / x.sum() * 100, axis=1)

    if "Hors ARTM" in pivoted.columns:
        classe_str.append("Hors ARTM")

    if how == "normalized":
        counts = [
            normalized[col].tolist() for col in classe_str if col in normalized.columns
        ]
        ylabel = "Pourcentage d'immobilisations collectées"
    else:
        counts = [pivoted[col].tolist() for col in classe_str if col in pivoted.columns]
        ylabel = "Nombre d'immobilisations collectées"

    # fill gap > 30 min with 0
    # idx_hours_gap = pivoted.reset_index()['30min_hrs'].diff()[pivoted.reset_index()['30min_hrs'].diff() > 70]
    ticklabels = pivoted.index.values
    # for index, gap in idx_hours_gap.iteritems():

    #    # nb missing values
    #    nb_slices = int(np.divmod(gap, 100)[0]*2) if np.divmod(gap, 100)[1] > 0 else int(np.divmod(gap, 100)[0]*2 - 1)

    #    # missing ticks
    #    missing_ticks = [i*100 + j \
    #        for i in range(math.ceil(ticklabels[index-1]/100), math.ceil(ticklabels[index]/100)) \
    #        for j in range(0, 31, 30)]

    #    # duplicates data near frontiere special case
    #    added=0
    #    if np.remainder(ticklabels[index-1], 100) == 30:
    #        missing_ticks = [ticklabels[index-1]] + missing_ticks
    #        nb_slices += 1
    #        added+=1
    #    if np.remainder(ticklabels[index], 100) == 0:
    #        missing_ticks =  missing_ticks + [ticklabels[index]]
    #        nb_slices += 1
    #        added+=1

    #    counts = np.insert(counts, [index for _ in range(nb_slices+2-added)], 0, axis=1) # +2 because duplicating first and last break values
    #    ticklabels = np.insert(ticklabels, index, missing_ticks)

    ## make x axis
    # x = (np.diff(ticklabels, prepend=np.nan) != 0).cumsum() - 1
    ## remove duplicates ticks labels
    # ticklabels = np.unique(ticklabels)

    groupnames = classe_str

    # ticklabels =  [f'{(Ctime(i*100)-3000).hhmm // 100:2d}h{(Ctime(i*100)-3000).hhmm % 100:02d} à {i // 100:2d}h{i % 100:02d}' for i in ticklabels]

    fig, ax = base.plot_base_dist_graphs(
        counts,
        groupnames,
        x=None,
        # title="Nombre d'immobilisations en fonction de l'heure et de la distance du code postal d'immatriculation"+add,
        xlabel="Période",
        ylabel=ylabel,
        ticklabels=ticklabels,
        legend_kwargs={"loc": "upper left"},
        colormap=colors.LAPIN_PALETTES["PROV_BLUES"](n_colors=len(groupnames)),
        # seaborn.diverging_palette(150, 275, s=80, l=55, n=len(groupnames))
    )

    ax.set_ylim(bottom=0, top=(max(np.sum(counts, axis=0)) // 20 + 1) * 20)
    if how == "normalized":
        ax.set_ylim(bottom=0, top=100)
        ax.set_yticks(range(0, int(ax.get_ylim()[-1]) + 1, 20))

    fig.savefig(
        f"{save_path}/{basename}Distribution_horaires_distances_{how}.png",
        bbox_inches="tight",
        dpi=fig_dpi,
    )
    plt.close()
