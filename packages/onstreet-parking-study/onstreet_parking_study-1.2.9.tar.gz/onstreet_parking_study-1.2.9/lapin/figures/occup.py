# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:56 2021

@author: lgauthier
@author: alaurent
"""
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

from lapin.figures import base
from lapin.figures import colors
from lapin.figures import config
from lapin.figures import STUDY_CRS
from lapin import constants
from lapin.tools import utils
from lapin.tools.utils import xform_list_entre_to_dict


def hour_occupancy_barplot(data:pd.DataFrame, savepath:str, hr_col:str='hour',
                           occ_col:str='mean', ci_col:str='',  **kwargs):
    data = data.copy()
    #TODO : si la représentativité est trop faible (peu de segment parcourus) ne pas calculer l'occupation horraire moyenne
    if (data[occ_col].fillna(0) <= 2).all():
        data[occ_col] *= 100
        if ci_col:
            data[ci_col] *= 100

    f, ax = plt.subplots()

    data = data.reset_index()
    ax_order = data[hr_col].sort_values().unique()

    sns.barplot(
        data=data,
        x=hr_col,
        y=occ_col,
        alpha=1,
        errorbar=None,
        order=ax_order,
        color='#c6dbef',
        ax=ax
    )


    if ci_col:
        ax.errorbar(
            x=ax_order,
            y=data.set_index(hr_col).loc[ax_order, occ_col].fillna(0),
            yerr=data.set_index(hr_col).loc[ax_order, ci_col].fillna(0),
            fmt='none',
            c='black',
            capsize=2
        )

    ax.tick_params(axis='x', labelrotation=90)

    ax.axhline(y=100, color='r', linestyle='--', linewidth=1)
    ax.axhline(y=90, color='#36454F', linestyle='--', linewidth=1)
    ax.axhline(y=80, color='#36454F', linestyle='--', linewidth=1)

    ax.set_ylabel("Taux d'occupation")
    ax.set_xlabel("Heure")

    #g.set(ylim=(0,1.4))
    f.savefig(savepath+f'taux_occ_horraire_region.png', dpi=150, bbox_inches='tight')

def occupancy_map(occ_df, cols, delims, savepath='cache/', basename='',
                  add_cat_prc=False, anotate=False, rotation=None,
                  fig_buffer=None, compass_rose=False,
                  map_dpi=config.MAP_DPI, leg_dpi=config.LEG_DPI,
                  capacity_df=None):
    """ Plot all occupancy wanted and save it.

    Parameters
    ----------
    occ_df : geopandas.GeoDataFrame
        The compiled occupancy with geobase double road segment.
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
    occ_df = occ_df.copy()
    rotation = xform_list_entre_to_dict(
        rotation,
        list(delims.keys()),
        default=0,
        valueVarName='rotation'
    )
    fig_buffer = xform_list_entre_to_dict(
        fig_buffer,
        list(delims.keys()),
        default=100,
        valueVarName='fig_buffer'
    )

    for zone, delim in delims.items():
        for col in cols:
            path = os.path.join(savepath, f"{basename}taux_occupation_{zone}_colonne_{col}.png")
            # remove no data
            occ_col, n_cuts, n_colors, base_colors = base.set_color(
                data=occ_df,
                col=col,
                numeric_cuts=config.OCC_NUM_CUTS,
                num_colors=config.OCC_COLORS,
                base_cat_colors=config.BASIC_CAT_COLORS,
                add_cat_prc=add_cat_prc,
            )
            base._generic_plot_map(
                occ_col,
                col,
                delim,
                path,
                anotate=anotate,
                dpi=map_dpi,
                rotation=rotation[zone],
                fig_buffer=fig_buffer[zone],
                compass_rose=compass_rose,
                other_anotation=capacity_df[col] if capacity_df is not None else None,
                anot_percent=True,
            )
            # legend
            os.makedirs(os.path.join(savepath, 'legends'), exist_ok=True)
            leg_path = os.path.join(os.path.join(savepath, "legends"), f"{basename}taux_occupation_{zone}_colonne_{col}.png")
            base._plot_leg(n_cuts, n_colors, leg_path, base_cat_colors=base_colors, dpi=leg_dpi)


def compared_occupancy_map(occ1, occ2, cols, seg_gis, delims, savepath='cache/',
                           basename='', desc='', rotation=None, fig_buffer=None,
                           map_dpi=config.MAP_DPI, leg_dpi=config.LEG_DPI, **kwargs):
    """ Plot all occupancy comparison between two occupancy results on columns
    cols. Compared columns need to have the same name on both dataframe.

    Parameters
    ----------
    occ1 : pd.DataFrame
        The first compiled occupancy on cols.
    occ2 : geopandas.GeoDataFrame
        The second compiled occupancy on cols.
    cols : str
        Name of all the columns to use for plotting. Each columns will be a different figure.
    delim : dict
        Of the form {name:geometry} with geometry a shapely.geometry.Multipolygon
        or shapely.geometry.Polygon. These geometry are delimitations of the
        different plots to be produced, each delim will generate a figure name
        using the key's value.
    savepath : str (Default 'cache/')
        Where to save the images. In total there will be n_cols x n_delims figs.
    """
    occ1 = occ1.copy()
    occ2 = occ2.copy()

    rotation = xform_list_entre_to_dict(rotation, list(delims.keys()), default=0, valueVarName='rotation')
    fig_buffer = xform_list_entre_to_dict(fig_buffer, list(delims.keys()), default=100, valueVarName='fig_buffer')

    for zone, delim in delims.items():
        basemap, b_ext = base.get_tile(config.CURRENT_TILE, *delim.bounds)
        for col in cols:
            path = os.path.join(savepath, f"{basename}comparaison_taux_occupation_{desc}_zone_{zone}_colonne_{col}.png")

            # get compared result for occ1 and occ2
            occ1_, occ2_, compared = utils.compare_two_lapi_results(occ1, occ2, seg_gis, metric_name=col)
            # as value are normalized and pd.cut does not allow negative value, we transform to positiv only values
            occ1_['compared'] = np.clip(compared +1, 0, 2)
            if occ1_.empty:
                continue

            occ_col, n_cuts, n_colors, base_colors = base.set_color(
                data=occ1_,
                col='compared',
                numeric_cuts=config.OCC_NUM_CUTS,
                num_colors=config.OCC_COLORS,
                base_cat_colors=config.BASIC_CAT_COLORS,
                add_cat_prc=False,
            )
            base._generic_plot_map(
                occ_col,
                'compared',
                delim,
                path,
                anotate=True,
                dpi=map_dpi,
                rotation=rotation[zone],
                fig_buffer=fig_buffer[zone],
                compass_rose=True,
            )
            #n_cuts, n_colors, base_colors = base._generic_plot_map(
                #occ1_, 'compared', delim, path,
                #numeric_cuts=config.OCC_RELATIV_CUTS,
                #num_colors=config.OCC_RELATIV_COLORS,
                #base_cat_colors=config.RELATIV_CAT_COLORS,
                #basemap=basemap, b_ext=b_ext,
                #add_cat_prc=False, build_leg=build_leg,
                #rotation=rotation[zone],
                #fig_buffer=fig_buffer[zone],
                #dpi=map_dpi, **kwargs
            #)
            # legend
            os.makedirs(os.path.join(savepath, 'legends'), exist_ok=True)
            leg_path = os.path.join(savepath, f'legends/{basename}comparaison_taux_occupation_{desc}_zone_{zone}_colonne_{col}.png')
            base._plot_leg(n_cuts, n_colors, leg_path, base_cat_colors=base_colors, dpi=leg_dpi)


def occupancy_relative_map(occ_h, occ_ts, cols, delims, savepath='cache/', basename='', build_leg=True,
                           rotation=None, fig_buffer=None, compass_rose=False, map_dpi=config.MAP_DPI, leg_dpi=config.LEG_DPI, **kwargs):
    """ Plot all relative hour occupancy compared to timeslot occupancy.

    Parameters
    ----------
    occ_h : geopandas.GeoDataFrame
        The compiled occupancy by hour with geobase double road segment.
    occ_ts : geopandas.GeoDataFrame
        The compiled occupancy by timeslot geobase double road segment.
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

    occ_h = occ_h.copy()
    occ_ts = occ_ts.copy()

    rotation = xform_list_entre_to_dict(rotation, list(delims.keys()), default=0, valueVarName='rotation')
    fig_buffer = xform_list_entre_to_dict(fig_buffer, list(delims.keys()), default=100, valueVarName='fig_buffer')

    for zone, delim in delims.items():
        basemap, b_ext = base.get_tile(config.CURRENT_TILE, *delim.bounds)
        for col in cols:
            path = os.path.join(savepath, f"{basename}taux_occupation_relative_{zone}_colonne_{col}.png")

            def compare_occ(val1, val2):
                if pd.isna(val1) and pd.isna(val2):
                    return np.nan
                if not pd.api.types.is_number(val1) and val1 == val2:
                    return val1
                if not pd.api.types.is_number(val1) or pd.isna(val1):
                    val1 = 0
                if not pd.api.types.is_number(val2) or pd.isna(val2):
                    val2 = 0
                return np.clip((val1 - val2) +1, 0, 2)

            occ_mean = occ_ts.merge(occ_h, on=['segment', 'side_of_street'], how='right').mean_occ.copy()
            # occ_h[col] = np.vectorize(compare_occ)(occ_h[col].values, occ_mean.values)
            occ_h[col] = list(map(compare_occ, occ_h[col].values, occ_mean.values))

            n_cuts, n_colors, base_colors = base._generic_plot_map(
                occ_h, col, delim, path,
                numeric_cuts=config.OCC_RELATIV_CUTS,
                num_colors=config.OCC_RELATIV_COLORS,
                base_cat_colors=config.RELATIV_CAT_COLORS,
                basemap=basemap, b_ext=b_ext,
                add_cat_prc=False, build_leg=build_leg,
                rotation=rotation[zone],
                fig_buffer=fig_buffer[zone],
                compass_rose=compass_rose,
                dpi=map_dpi, **kwargs
            )
            # legend
            os.makedirs(os.path.join(savepath, 'legends'), exist_ok=True)
            leg_path = os.path.join(savepath, f'legends/{basename}taux_occupation_relative_{zone}_colonne_{col}.png')
            base._plot_leg(n_cuts, n_colors, leg_path, base_cat_colors=base_colors, dpi=leg_dpi)


def segment_capacity_map(
    seg_info,
    delims,
    save_path,
    basename='',
    restrictions=False,
    normalized=False,
    rotation=None,
    fig_buffer=None,
    map_dpi=config.MAP_DPI,
    leg_dpi=config.LEG_DPI,
    anotate=False,
    save_geojson=False,
    **kwargs
):
    """ Plot parking capacity of segment and save it.

    Parameters
    ----------
    seg_info : geopandas.GeoDataFrame
        The information capacity about segements.
    seg_gis : geopandas.GeoDataFrame
        The geographic information about segments.
    delim : dict
        Of the form {name:geometry} with geometry a shapely.geometry.Multipolygon
        or shapely.geometry.Polygon. These geometry are delimitations of the
        different plots to be produced, each delim will generate a figure name
        using the key's value.
    savepath : str
        Where to save the images. In total there will be n_cols x n_delims figs.
    """
    seg_info = seg_info.copy()

    # 1 - get parameters for map
    rotation = xform_list_entre_to_dict(rotation,
                                        list(delims.keys()),
                                        default=0,
                                        valueVarName='rotation')
    fig_buffer = xform_list_entre_to_dict(fig_buffer,
                                          list(delims.keys()),
                                          default=100,
                                          valueVarName='fig_buffer')

    # 3 - retrieve number of parking spot on each segment
    long_troncon = seg_info.to_crs(STUDY_CRS).geometry.length.values
    mask = ~seg_info[constants.CAP_N_VEH].isna()
    seg_info.loc[mask, 'places'] = (
        (seg_info.loc[mask, constants.CAP_DELIM_SPACE] +
         seg_info.loc[mask, constants.CAP_N_VEH]) * constants.VEH_SIZE / long_troncon
        if normalized else seg_info.loc[mask, constants.CAP_N_VEH]
    )
    seg_info.loc[seg_info[constants.CAP_N_VEH].isna(), 'places'] = np.nan

    # 5 - Plot
    for zone, delim in delims.items():
        path = os.path.join(save_path, f"{basename}segments_capacity_secteur_{zone}.png")
        if normalized:
            path = os.path.join(save_path,
                                f"{basename}segments_capacity_secteur_{zone}_normalized.png")


        occ_col, n_cuts, n_colors, base_colors = base.set_color(
            data=seg_info,
            col='places',
            numeric_cuts=config.CAPA_NORM_NUM_CUTS if normalized else config.CAPA_NUM_CUTS, #None,
            num_colors=config.CAPA_NORM_COLORS if normalized else None,#config.CAPA_COLORS,#None,
            num_cmap=colors.LAPIN_PALETTES['CAPA'](as_cmap=True),
            mc_k=4, # TODO shoot in config
            base_cat_colors=config.BASIC_CAT_COLORS,
            add_cat_prc=False,
        )
        base._generic_plot_map(
            occ_col,
            'places',
            delim,
            path,
            anotate=anotate,
            dpi=map_dpi,
            rotation=rotation[zone],
            fig_buffer=fig_buffer[zone],
            normalized_val=normalized,
            anot_percent=False,
            compass_rose=kwargs.get('compass_rose', False)
        )

        # legend
        os.makedirs(os.path.join(save_path, 'legends'), exist_ok=True)
        leg_path = os.path.join(
            save_path,
            f'legends/{basename}segments_capacity_secteur_{zone}.png'
        )
        if normalized:
            leg_path = os.path.join(
                save_path,
                f'legends/{basename}segments_capacity_secteur_{zone}_normalized.png'
            )

        base._plot_leg(
            n_cuts,
            n_colors,
            leg_path,
            base_cat_colors=base_colors,
            dpi=leg_dpi
        )

    if save_geojson:
        os.makedirs(os.path.join(save_path, 'data'), exist_ok=True)
        seg_info.to_file(
            os.path.join(save_path, f'data/{basename}segments_capacity.geojson'.replace(':', '-')),
            index=False,
            driver='GeoJSON'
        )

def plot_capacity_leg(save_path, leg_dpi=config.LEG_DPI):
    base._plot_leg(config.CAPA_NUM_CUTS, config.CAPA_COLORS, save_path,
                   base_cat_colors=config.BASIC_CAT_COLORS, dpi=leg_dpi)

def plot_occ_leg(save_path, leg_dpi=config.LEG_DPI):
    base._plot_leg(config.OCC_NUM_CUTS, config.OCC_COLORS, save_path,
                   base_cat_colors=config.BASIC_CAT_COLORS, dpi=leg_dpi)

def plot_occ_relativ_leg(save_path, leg_dpi=config.LEG_DPI):
    base._plot_leg(config.OCC_RELATIV_CUTS, config.OCC_RELATIV_COLORS, save_path,
                   base_cat_colors=config.RELATIV_CAT_COLORS, dpi=leg_dpi)
