# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:56 2021

This file contains generic functions used to create graphics and maps

@author: alaurent
@author: lgauthier
"""
import os
import copy
import numbers

from typing import Tuple, Union, TypeVar, Dict, Any, List
from numpy.typing import ArrayLike

from deprecated import deprecated
from importlib_resources import files
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas
import shapely
import contextily as ctx
import numpy as np
import pandas
import mapclassify
from adjustText import adjust_text
from rasterio.warp import transform_bounds

from lapin.figures import colors
from lapin.figures import config
from lapin.figures import STUDY_CRS

Img = TypeVar("Img", bound=ArrayLike)
Extent = Tuple[int, int, int, int]
Provider = Union[dict, dict]
Bounds = TypeVar("Bounds", bound=geopandas.GeoDataFrame)
Color = Union[str, Tuple[float]]
Colormap = TypeVar("Colormap", bound=plt.colormaps)
Numeric = Union[int, float, np.number, numbers.Number]
ColumnName = Any
ListNumeric = List[Numeric]
CountList = List[List[Numeric]]


def get_tile(
    source: Provider,
    west: float,
    sud: float,
    east: float,
    north: float,
    is_lat_lng: bool = True,
) -> Tuple[Img, Extent]:
    """Wrapper aroung ctx.bounds2img to the information input is more coherent
    with the rest of the codebase.

    Parameters
    ----------
    source : Provider
        A provider encoded in figures.config
    west : float
        Western edge of the tile.
    sud : float
        Southern edge of the tile.
    east : float
        Eastern edge of the tile.
    north : float
        Northern edge of the tile.
    is_lat_lng : bool, optional
        If True, west, south, east, north are assumed to be lon/lat (EPSG:4326)
        as opposed to Spherical Mercator (EPSG:3857). The default is True.

    Returns
    -------
    Img:
        The image as a 3d array and it's bounds.
    Extent:
        A tuple containing xmin, ymin, xmax, ymax.
    """
    ghent_img, ghent_ext = ctx.bounds2img(
        w=west, s=sud, e=east, n=north, ll=is_lat_lng, source=source
    )
    return ghent_img, ghent_ext


# Les tuiles mapbox obtenues à l'aide de contextily sont des static tiles, dont
# la résolution dépend du niveau de zoom. Le niveau de zoom contrôle aussi les
# bounds de la tuile.

# Pour régler ce problème, on pourrait investiguer l'utilisation des vector
# tiles de mapbox, qui ne peuvent être géré par contextily. La librairie
# suivante semble être en mesure de les gérer:
# https://github.com/mapbox/vector-tile-base


def rotate_fig_elements(
    ax: mpl.axes.Axes, angle: float, o_x: float, o_y: float
) -> mpl.transforms.Affine2D:
    """A wrapper around the call to mpl.transforms.Affine2D because to apply
    automatically the transformation to the elements of the fig.

    Parameters
    ----------
    ax : mpl.axes.Axes
        The ax object containing the elements to rotate.
    angle : float
        DESCRIPTION.
    o_x : float
        DESCRIPTION.
    o_y : float
        DESCRIPTION.

    Returns
    -------
    r : mpl.transforms.Affine2D
        The transform is returned so it can be chained with with more calls
        to rotate(), rotate_deg(), translate() and scale().

    """
    r = mpl.transforms.Affine2D().rotate_deg_around(o_x, o_y, angle)
    for x in ax.images + ax.lines + ax.collections:
        trans = x.get_transform()
        x.set_transform(r + trans)
        if isinstance(x, mpl.collections.PathCollection):
            transoff = x.get_offset_transform()
            x._transOffset = r + transoff
    return r


def get_transformed_extents(
    ax: mpl.axes.Axes, transform: mpl.transforms.Affine2DBase
) -> Extent:
    """A function that can retreive the bounding box of objects contained
    inside an axe after a transformation is applied. This can be used to
    size elements correctly before applying the transformation.

    Parameters
    ----------
    ax : mpl.axes.Axes
        The ax object for which the new extents must be retreived.
    transform : mpl.transforms.Affine2DBase
        The transformation that as been applied to the fig.

    Returns
    -------
    Extent:
        A tuple containing xmin, ymin, xmax, ymax.

    """
    xmin = None
    xmax = None
    ymin = None
    ymax = None
    for x in ax.collections:
        for path in x.get_paths():
            [p1x, p1y], [p2x, p2y] = (
                path.transformed(transform=transform).get_extents().get_points()
            )

            if xmin is None:
                xmin = p1x
            elif xmin > p1x:
                xmin = p1x

            if xmax is None:
                xmax = p2x
            elif xmax < p2x:
                xmax = p2x

            if ymin is None:
                ymin = p1y
            elif ymin > p1y:
                ymin = p1y

            if ymax is None:
                ymax = p2y
            elif ymax < p2y:
                ymax = p2y

    return xmin, ymin, xmax, ymax


@deprecated("Les méthodes de pandas sont plus simples et plus rapides " + "à utiliser")
def get_rotated_total_bounds(
    poly: shapely.Polygon, rot: float, buffer: float = 0
) -> Extent:
    """Rotate a polygon around it's centroid and get the resulting axis-aligned
    bounding box.

    Parameters
    ----------
    poly : shapely.Polygon
        The polygon to rotate.
    rot : float
        The rotation angle to apply.
    buffer : float, optional
        Add a distance around the actual bounds. The default is 0.

    Returns
    -------
    Extent :
        A tuple containing xmin, ymin, xmax, ymax.

    """
    _p = poly.centroid.x
    _q = poly.centroid.y
    if rot < 0:
        rot += 360
    xs = []
    ys = []
    for _x, _y in poly.convex_hull.exterior.coords:
        xs.append((_x - _p) * np.cos(rot) - (_y - _q) * np.sin(rot) + _p)
        ys.append((_x - _p) * np.sin(rot) + (_y - _q) * np.cos(rot) + _q)

    return min(xs) - buffer, min(ys) - buffer, max(xs) + buffer, max(ys) + buffer


def create_bounds_gdf(
    gdf: Bounds, add_side_buffers: float = 0
) -> Tuple[Bounds, Extent]:
    """Calculate a bounding polygon around data provided in a
    geopandas.GeoDataFrame.

    Parameters
    ----------
    gdf : Bounds
        A geopandas.GeoDataFrame containing geographic data that can be used to
        infer the extent of the map to generate.
    add_side_buffers : float, optional
        Add a distance around the actual bounds.. The default is 0.

    Returns
    -------
    bounds : Bounds
        A geopandas.GeoDataFrame containing the bounding polygon
    bbox : Extent
        A tuple containing xmin, ymin, xmax, ymax.
    """
    minx, miny, maxx, maxy = gdf.total_bounds

    p1 = shapely.geometry.Point(minx - add_side_buffers, maxy + add_side_buffers)
    p2 = shapely.geometry.Point(maxx + add_side_buffers, maxy + add_side_buffers)
    p3 = shapely.geometry.Point(maxx + add_side_buffers, miny - add_side_buffers)
    p4 = shapely.geometry.Point(minx - add_side_buffers, miny - add_side_buffers)

    bb_polygon = shapely.geometry.Polygon(
        [
            (p1.coords.xy[0][0], p1.coords.xy[1][0]),
            (p2.coords.xy[0][0], p2.coords.xy[1][0]),
            (p3.coords.xy[0][0], p3.coords.xy[1][0]),
            (p4.coords.xy[0][0], p4.coords.xy[1][0]),
        ]
    )

    bounds = geopandas.GeoDataFrame(
        geopandas.GeoSeries(bb_polygon), columns=["geometry"], crs=STUDY_CRS
    )

    bbox = bounds.total_bounds

    return bounds, bbox


def basemap_from_shapefile(
    bounds: Bounds,
    background_color: Color = "#ffffff",
    figsize: Tuple[float, float] = (10, 10),
    dpi: float = config.MAP_DPI,
    hydro_order: int = 1,
    road_order: int = 2,
    hydro_path: str = config.HYDRO_SHAPE,
    road_path: str = config.ROAD_SHAPE,
) -> Tuple[mpl.figure.Figure, mpl.axes.Axes]:
    """Create a matplotlib figure with a predefined background built around assets
    provided in the codebase with bounds large enough to cover the data provided
    in `bounds`.

    Parameters
    ----------
    bounds: Bounds
        A geopandas.GeoDataFrame containing geographic data that can be used to
        infer the extent of the map to generate.
    background_color: Color
        Color to apply to figure's background. The default is '#ffffff'.
    figsize: tuple(float, float)
        Size of the figure, in inches (width, height). The default is (10,10).
    dpi: float,
        The resolution of the figure in dots-per-inch. The default is contained
        in config.MAP_DPI.
    hydro_order: int
        The layer to put the hydrology at. The default is 1.
    road_order: int
        The layer to put the road network at. The default is 2.
    hydro_path: str
        The path to retreive the hydro shape. The default is contained in
        config.HYDRO_SHAPE.
    road_path: str
        The path to retreive the road network shape. The default is contained
        in config.ROAD_SHAPE.

    Returns
    -------
    f:
        The mpl.figure.Figure object of the created map
    ax:
        The mpl.axes.Axes object of the created map
    """
    df2, bbox = create_bounds_gdf(bounds)

    f, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # hydro
    geopandas.clip(geopandas.read_file(hydro_path).to_crs(STUDY_CRS), df2).plot(
        color=colors.LAPIN_COLORS["HYDRO"], ax=ax, zorder=hydro_order
    )
    # road
    geopandas.clip(geopandas.read_file(road_path).to_crs(STUDY_CRS), df2).plot(
        color=colors.LAPIN_COLORS["ROADS"], ax=ax, alpha=0.33, zorder=road_order
    )

    ax.set_xlim(xmin=bbox[0], xmax=bbox[2])
    ax.set_ylim(ymin=bbox[1], ymax=bbox[3])

    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_facecolor(background_color)

    return f, ax


################################
### DEFAULT MAP PLOTING FUNC ###
################################
def _numerical_cuts(
    y: ArrayLike, k: int = 5, base: float = 1.0, decimals: int = 0
) -> Dict[str, float]:
    """Transform an array of numeric data into an array of labels using a Natural
    Breaks algorithm and a specified number of breaks.

    Parameters
    ----------
    y : ArrayLike
        The data to break into classes.
    k : int, optional
        The number of classes to break the data into. The default is 5.
    base : float, optional
        The base number to round the naturel breaks around. The default is 1.0.
    decimals : int, optional
        The number of decimals after the rounding. The default is 0.

    Returns
    -------
    numerical_cuts : Dict[str, float]
        A dictionnary containing the cuts labels and their corresponding break.

    """
    mc = mapclassify.NaturalBreaks(y, k)

    # round
    bins = np.round(base * np.ceil(mc.bins / base), decimals=decimals)

    numerical_cuts = {}
    for i in range(len(mc.bins)):
        if i == 0:
            numerical_cuts[config.LEGEND_LABEL["first"].format(int(bins[i]))] = bins[i]
        elif i == len(mc.bins) - 1:
            numerical_cuts[config.LEGEND_LABEL["last"].format(int(bins[i - 1]))] = bins[
                -1
            ]
        else:
            numerical_cuts[
                config.LEGEND_LABEL["middle"].format(int(bins[i - 1]), int(bins[i]))
            ] = bins[i]
    return numerical_cuts


def _numeric_color(labels: List[str], cmap: Colormap) -> Dict[str, Color]:
    """Builds a dictionnary of colors (r,g,b,a quadruplet) using a list of labels
    and a colormap. Colors are assigned as a fraction of the colormap in the
    order they first appear in the labels list.

    Parameters
    ----------
    labels : list[str]
        A list of labels to which colors must be assigned.
    cmap : Colormap
        A matplotlib.colors.Colormap like object

    Returns
    -------
    Dict[str, Color]
        The dictionnary of rgba quadruplet corresponding to the labels.

    """
    numeric_colors = {}
    uniquelabels = list(dict.fromkeys(labels))
    labels_len = len(uniquelabels)

    for i in range(labels_len):
        numeric_colors[uniquelabels[i]] = cmap(1 / (labels_len - 1) * i)

    return numeric_colors


def set_color(
    data: pandas.DataFrame | geopandas.GeoDataFrame,
    col: ColumnName,
    numeric_cuts: Dict[str, float] | None = None,
    mc_k: int = 5,
    num_colors: Dict[str, Color] | None = None,
    num_cmap: Colormap | None = None,
    base_cat_colors: Dict[str, Color] | None = None,
    add_cat_prc: bool = False,
) -> Tuple:
    """Assign colors to a column on a data structure according to a
    categorisation of the data range based on the numerical values.

    Parameters
    ----------
    data : pandas.DataFrame | geopandas.GeoDataFrame
        The dataframe containing data to colorcode.
    col : ColumnName
        The column who's values must be colorcoded
    numeric_cuts : Dict[str, float] or None, optional
        A dictionnary containing the category labels (keys) and their
        corresponding breaks (values). If omitted, the breaks will be
        calculated using a Natural Breaks algorithm. The default is None.
    mc_k : int, optional
        If `numeric_cuts` is None, the number of classes to break the data
        into. The default is 5.
    num_colors : Colormap or None, optional
        A dictionnary of category labels (keys) and rgba quadruplet (values)
        used to assign colors to the numerical data, by default None.
    num_cmap : Colormap or None, optional
        A matplotlib.colors.Colormap like object. If `num_colors`, the colormap
        object used to pick colors to every labels. If None, defaults to
        `colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)`, by default None.
    base_cat_colors : Dict[str, Color], optional
        A dictionnary of category labels (keys) and rgba quadruplet (values)
        used to assign colors to different types of missing values. If None,
        defaults to `config.BASIC_CAT_COLORS`. The default is None.
    add_cat_prc : bool, optional
        Transform the categories to a percentile notation. The default is
        False.

    Returns
    -------
    data : pandas.DataFrame | geopandas.GeoDataFrame
        The initial DataFrame or GeoDataFrame is returned with the following
        new colums: category (contains the categories labels) and color_cat
        (contains the rgba quadruplets).
    numeric_cuts : Dict[str, float]
        In case the `numeric_cuts` was not initialy provided, the function
        returns the dictionnary used to assign the category. It's structure is
        the same as the keyword parameter.
    num_colors : Colormap
        In case the `num_colors` was not initialy provided, the function
        returns the Colormap used to calculate colors used. It's structure is
        the same as the keyword parameter.
    base_cat_colors : Dict[str, Color]
        In case the `base_cat_colors` was not initialy provided, the function
        returns the dictionnary used to assign colors to the missing values
        categories. It's structure is the same as the keyword parameter.
    """
    data = data.copy()
    if base_cat_colors is None:
        base_cat_colors = config.BASIC_CAT_COLORS
    base_cat_colors = copy.deepcopy(base_cat_colors)

    if data.empty:
        return None, numeric_cuts, num_colors, base_cat_colors

    # grab all numeric data
    data_num = data[
        [pandas.api.types.is_number(x) and not pandas.isna(x) for x in data[col]]
    ].copy()
    if pandas.api.types.is_numeric_dtype(data[col].dtype):
        data_num = data[[not pandas.isna(x) for x in data[col]]].copy()

    if not numeric_cuts:
        numeric_cuts = _numerical_cuts(data_num[col], k=mc_k)

    if add_cat_prc:
        numeric_cuts = {k + " ({:.2f}%)": v for k, v in numeric_cuts.items()}

    labels = list(numeric_cuts.keys())
    data_num["category"] = pandas.cut(
        data_num[col],
        [0] + list(numeric_cuts.values()),
        labels=labels,
        include_lowest=True,
    )
    data_num["category"] = data_num["category"].astype(str)

    # complete the labels
    if add_cat_prc:
        replace = {
            labels[i]: labels[i].format(
                (data_num["category"] == labels[i]).sum()
                / data_num["category"].shape[0]
                * 100
            )
            for i in range(len(labels))
        }
        data_num["category"] = data_num["category"].map(replace)
        labels = list(replace.values())

    # grab all categorical data
    data_cat = pandas.DataFrame(columns=data_num.columns)
    data_cat = data_cat.astype(data_num.dtypes)
    if not pandas.api.types.is_numeric_dtype(data[col].dtype):
        data_cat = data[
            [not (pandas.api.types.is_number(x) or pandas.isna(x)) for x in data[col]]
        ].copy()
        data_cat["category"] = data_cat[col].copy()

    # grab all nan
    data_na = data[[pandas.isna(x) for x in data[col]]].copy()
    data_na["category"] = ["Sans donnée" for _ in range(data_na[col].shape[0])]
    data_na["category"] = data_na["category"]
    data_na = data_na.astype(data_num.dtypes)

    # bin them
    data = pandas.concat([data_num, data_cat, data_na])

    if not num_colors:
        if num_cmap is None:
            num_cmap = colors.LAPIN_PALETTES["OCC_BLUES"](as_cmap=True)
        num_colors = _numeric_color(labels, num_cmap)

    data["category"] = data["category"].astype(str)
    base_cat_colors = {
        key: base_cat_colors[key]
        for key in data["category"].unique()
        if key in base_cat_colors.keys()
    }
    cat_colors = dict(base_cat_colors, **num_colors)
    data["color_cat"] = data["category"].map(cat_colors)

    # drop whites, we purposefully can't see them and it messes up the
    # rotation bounds
    data = data[~data.color_cat.isin(["white"])]
    data = data.iloc[::-1]

    return data, numeric_cuts, num_colors, base_cat_colors


def _generic_plot_map(
    data: geopandas.GeoDataFrame,
    col: ColumnName,
    delim: shapely.geometry.Polygon | shapely.geometry.MultiPolygon,
    savepath: str,
    dpi: int = config.MAP_DPI,
    anotate: bool = False,
    normalized_val: bool = True,
    fig_buffer: float = 100.0,
    rotation: float = 0.0,
    compass_rose: bool = False,
    gpd_kwd=None,
    other_anotation=None,
    anot_percent=True,
) -> None:
    """Plot data of column 'col' on a map.

    Parameters
    ----------
    data : geopandas.GeoDataFrame
        The compiled occupancy with geobase double road segment.
    col : ColumnName
        Name of the column to use for plotting.
    delim : shapely.geometry.Polygon or shapely.geometry.Multipolygon
        Delimitation of the plot.
    savepath : str
        Path with name where to save the picture.
    dpi : int
        The resolution of the output. The default is found in config.MAP_DPI.
    anotate : bool
        If True, adds marks with the values on each geometry item plotted. The
        default is False.
    normalized_val : bool
        If True, normalize as a percentile the data shown through the annotate
        keyword. Has no effect if `annotate=False`. The default is True.
    fig_buffer : float
        A distance in meters to add around the data. This is important so the
        lines don't clip on the side of the plot which makes them hard to see.
        The default is 100.0.
    rotation : float
        The angle of rotation (in degrees) to use to rotate the map. Usefull to
        reduce the page footprint of a map. On most N-S roads, an angle close
        to -53 should allow to create an horizontal map. The default is 0.0.
    compass_rose : bool
        If True, add the image of a compass rose on the map to indicate the
        rotation angle used. The default is False.
    gpd_kwd:
        Dictionnary to be passed to the geopandas.GeoDataFrame.plot method.
        The default is an empty dictionnary ({}).
    other_anotation: pandas.Dataframe, default: None
        Other dataframe containing anotation to be displayed with data.

    Returns
    -------
    None
    """
    if rotation.__class__ not in Numeric.__args__:
        raise ValueError(
            "`rotate` must be of type int or float," + f"received {rotation.__class__}"
        )

    if gpd_kwd is None:
        gpd_kwd = {}

    data = data.copy()

    delim_gdf = geopandas.GeoDataFrame(geometry=[delim], crs=STUDY_CRS)

    if delim_gdf.crs != data.crs:
        data = data.to_crs(STUDY_CRS)

    data = geopandas.sjoin(data, delim_gdf, predicate="within", how="inner")

    data = data.drop_duplicates()

    if data.empty:
        return

    delim_gdf = delim_gdf.buffer(2).to_frame("geometry")
    try:
        data = data.rename_geometry("geometry")
    except ValueError:
        pass

    # plot map
    #    +   +---+-----------+
    # A  |   |   |           |
    #    +   +---+-------+   |
    #    |   |   |       |   |
    #    |   |   |       |   |
    # B  |   |   |       |   |     B = dy
    #    |   |   |       |   |     E = dx
    #    |   |   |       |   |
    #    +   |   +-------+   |
    # C  |   |               |
    #    +   +---------------+
    #
    #        +---+-------+---+
    #          D     E     F

    A = 0.1
    B = 0.8
    C = 0.1
    D = 0.1
    E = 0.8
    F = 0.1

    compass_multiplier = 1
    if compass_rose:
        compass_multiplier = 2
        A *= compass_multiplier
        B -= 0.1

    fig, bg_ax = plt.subplots(figsize=(10, 10), dpi=dpi)
    data_ax = bg_ax.inset_axes([D, C, E, B], zorder=100, frameon=False)
    rose_ax = bg_ax.inset_axes([D, B + C, A, A], zorder=100, frameon=False)

    data.plot(
        color=data["color_cat"],
        figsize=(12, 10),
        linewidth=2 * 200 / dpi,
        zorder=2,
        ax=data_ax,
        **gpd_kwd,
    )

    if anotate:
        texts = []
        if other_anotation is not None:
            other_anotation = other_anotation.fillna("?")
        x, y = (delim_gdf.unary_union.centroid.x, delim_gdf.unary_union.centroid.y)

        data_num = data[
            [pandas.api.types.is_number(x) and not pandas.isna(x) for x in data[col]]
        ].copy()
        if pandas.api.types.is_numeric_dtype(data[col].dtype):
            data_num = data[[not pandas.isna(x) for x in data[col]]].copy()

        data_num = data_num.to_crs(data.crs)
        data_num.geometry = data_num.rotate(rotation, origin=(x, y))
        for i, row in data_num.iterrows():
            if not row["geometry"]:
                continue
            text = int(np.round(row[col] * 100, 0)) if normalized_val else int(row[col])
            text = str(text)
            text += "%" if anot_percent else ""
            if other_anotation is not None:
                text += " / "
                text += str(int(other_anotation.loc[i]))
            texts.append(
                data_ax.text(
                    *row["geometry"].centroid.coords[0], s=text, alpha=0.7, fontsize=8
                )
            )

        adjust_text(texts)

    # set the limits - the tile query uses ax.axis() so setting the limits let
    # us control "how much we see" on the plot
    # because we might want to rotate the fig, at this point we'll query twice
    # the  space we need
    minx, miny, maxx, maxy = delim_gdf.total_bounds
    ominx, ominy, omaxx, omaxy = minx, miny, maxx, maxy
    # if rotation, double the tiles querried
    if rotation != 0:
        dx = maxx - minx
        dy = maxy - miny
        minx -= dx
        miny -= dy
        maxx += dx
        maxy += dy
    dx = maxx - minx
    dy = maxy - miny
    data_ax.set_xlim(xmin=minx, xmax=maxx)
    data_ax.set_ylim(ymin=miny, ymax=maxy)

    # calculate the bg limits
    dx2 = dx / E * F
    dy2 = dy / B * C
    bg_ax.set_xlim(xmin=minx - dx2, xmax=maxx + dx2)
    bg_ax.set_ylim(ymin=miny - dy2, ymax=maxy + compass_multiplier * dy2)

    def _reproj_bb(left, right, bottom, top, s_crs, t_crs):
        n_l, n_b, n_r, n_t = transform_bounds(s_crs, t_crs, left, bottom, right, top)
        return n_l, n_r, n_b, n_t

    left, right, bottom, top = _reproj_bb(
        ominx, omaxx, ominy, omaxy, data.crs.to_string(), {"init": "epsg:4326"}
    )
    zoom = ctx.tile._calculate_zoom(left, bottom, right, top)

    # query the tile
    # Contextily already cache tile (see: https://bit.ly/contextily-cache)
    ctx.add_basemap(
        data_ax,
        crs=data.crs.to_string(),
        source=config.CURRENT_TILE,
        zoom=min(config.CURRENT_TILE["max_zoom"], zoom),
    )
    ctx.add_basemap(
        bg_ax,
        crs=data.crs.to_string(),
        source=config.CURRENT_TILE,
        zoom=min(config.CURRENT_TILE["max_zoom"], zoom),
    )

    # apply the rotation
    x, y = delim_gdf.unary_union.centroid.x, delim_gdf.unary_union.centroid.y
    rotate_fig_elements(data_ax, rotation, x, y)
    rotate_fig_elements(bg_ax, rotation, x, y)

    # add the rose des vents
    if compass_rose:
        roseVent = mpl.pyplot.imread(
            files("lapin.figures.assets").joinpath("gite-la-rose-des-vents.png")
        )
        rose_ax.imshow(roseVent)
        rose_ax.axis("off")

        # I don't know why but rotation is inversed for image. Else north will not be in the good place
        rotate_fig_elements(
            rose_ax,
            -rotation,
            np.asarray(rose_ax.get_xlim()).mean(),
            np.asarray(rose_ax.get_ylim()).mean(),
        )

    # reset the limits to default values (rotation)
    # if rotation we need to compute rotated limits.
    #       For example: -------            -----
    #                    |     | rot(90) -> |   |
    #                    -------            |   |
    #                                       -----
    if rotation != 0:
        ominx, ominy, omaxx, omaxy = (
            delim_gdf.buffer(fig_buffer)
            .rotate(rotation, origin=(x, y))
            .bounds.values[0]
        )  # get_rotated_total_bounds(delim_gdf.geometry.iloc[0], rotation, x, y, buffer=fig_buffer)
    odx = omaxx - ominx
    ody = omaxy - ominy
    odx2 = odx / E * F
    ody2 = ody / B * C

    data_ax.set_xlim(xmin=ominx, xmax=omaxx)
    data_ax.set_ylim(ymin=ominy, ymax=omaxy)
    bg_ax.set_xlim(xmin=ominx - odx2, xmax=omaxx + odx2)
    bg_ax.set_ylim(ymin=ominy - ody2, ymax=omaxy + compass_multiplier * ody2)

    # remove axes
    data_ax.axis("off")
    bg_ax.get_xaxis().set_visible(False)
    bg_ax.get_yaxis().set_visible(False)
    rose_ax.axis("off")

    # replace ":" except for Drive on windows
    savepath = os.path.normpath(savepath)
    save_path_parts = savepath.split(os.sep)
    save_path_parts = [save_path_parts[0]] + [
        parts.replace(":", "-") for parts in save_path_parts[1:]
    ]
    savepath = os.sep.join(save_path_parts)

    # savefig
    fig.savefig(savepath, bbox_inches="tight", format="PNG", dpi=dpi)

    plt.close()


def _plot_leg(
    numeric_cuts: Dict[str, Numeric],
    num_colors: Dict[str, Numeric],
    save_path: str,
    base_cat_colors: Dict[str, Color] = None,
    dpi: float = config.LEG_DPI,
) -> None:
    """Plot a legend in a separate figure then save it to disk.

    Parameters
    ----------
    numeric_cuts : dict.
        Dictionnary of numeric cuts to bin the data. Keys are labels
        and values are numeric cuts.
    num_colors : dict.
        Assignation colors to each label of the numeric_cuts. Keys must match
        those of `numeric_cuts`.
    savepath : str.
        Path where to save the legend.
    base_cat_colors : dict.
        Base colors for legend.
    dpi : float
        The resolution of the figure in dots-per-inch. The default is found in
        config.LEG_DPI

    Returns
    -------
    None

    Note
    ----
    This function uses the _build_legend function but does not presently support
    it's points and kdes functionalities.

    """

    # plot map
    fig, ax = plt.subplots(dpi=dpi)

    ax.scatter(x=[0, 1], y=[1, 0])

    # labels
    labels = list(numeric_cuts.keys())

    # assign colors
    if base_cat_colors is None:
        base_cat_colors = config.BASIC_CAT_COLORS
    cat_colors = dict(num_colors, **base_cat_colors)

    # add a legend
    leg = _build_legend(
        ax,
        title="Légende",
        title_color=colors.LAPIN_COLORS.LEG_TXT,
        bbox_to_anchor=(0.5, -0.01),
        loc="upper center",
        lignes_kwords=[{"label": str(k), "color": v} for k, v in cat_colors.items()],
        align_title="left",
        ncol=(len(cat_colors) // 4 + int(len(cat_colors) % 4 > 0)),
        facecolor=colors.LAPIN_COLORS.LEGEND_BG,
        labelcolor=colors.LAPIN_COLORS.LEG_TXT,
    )

    fig.canvas.draw()
    bbox = leg.get_window_extent()
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

    # remove axes
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # replace ":" except for Drive on windows
    save_path = os.path.normpath(save_path)
    save_path_parts = save_path.split(os.sep)
    save_path_parts = [save_path_parts[0]] + [
        parts.replace(":", "-") for parts in save_path_parts[1:]
    ]
    save_path = os.sep.join(save_path_parts)

    fig.savefig(save_path, bbox_inches=bbox, format="PNG", dpi=dpi)
    plt.close()


##############
### Legend Utils
##############
def _make_legend_line(ldict: dict) -> mlines.Line2D:
    """Build a solid line to represent a line type in a figure legend

    Parameters
    ----------
    pdict : dict
        A dictionnary containing attributes compatible with matplotlib.lines.Line2D.

    Returns
    -------
    patches : matplotlib.mlines.Line2D
    """
    # pop those so we don't conflict with the dict unpacking
    color = ldict.pop("color", None)
    label = ldict.pop("label", None)
    # create the patch
    return mlines.Line2D([], [], color=color, label=label, **ldict)


def _make_legend_point(pdict: dict) -> mlines.Line2D:
    """
    Build a line made of a couple dots to represent a point type in a figure legend

    Parameters
    ----------
    pdict : dict
        A dictionnary containing attributes compatible with matplotlib.lines.Line2D.

    Returns
    -------
    patches : matplotlib.mlines.Line2D
    """
    # pop those so we don't conflict with the dict unpacking
    markerfacecolor = pdict.pop("markerfacecolor", None)
    markeredgecolor = pdict.pop("markeredgecolor", None)
    color = pdict.pop("color", None)
    label = pdict.pop("label", None)
    marker = pdict.pop("marker", ".")
    # decide which color to use. If both are None then screw the user
    mcolor = markerfacecolor if markerfacecolor is not None else color
    ecolor = markeredgecolor if markeredgecolor is not None else color
    # create the patch
    return mlines.Line2D(
        [],
        [],
        color=None,
        markerfacecolor=mcolor,
        markeredgecolor=ecolor,
        linewidth=0,
        marker=marker,
        label=label,
        **pdict,
    )


def _make_legend_boxpatch(kdict: dict) -> mpatches.FancyBboxPatch:
    """
    Build a square box to represent a kde zone in a figure legend

    Parameters
    ----------
    pdict : dict
        A dictionnary containing attributes compatible with matplotlib.patche.FancyBboxPatch.

    Returns
    -------
    patches : mpatches.FancyBboxPatch

    """
    # pop those so we don't conflict with the dict unpacking
    color = kdict.pop("color", None)
    label = kdict.pop("label", None)
    boxstyle = kdict.pop("boxstyle", mpatches.BoxStyle("Round", pad=0.02))
    # create the patch
    return mpatches.FancyBboxPatch(
        [0, 0], 0.1, 0.1, color=color, label=label, boxstyle=boxstyle, **kdict
    )


def _handle_patch(patch_kwargs, patch_type="point", label_order=None, memory=None):
    if memory is None:
        memory = {}
    if label_order is None:
        label_order = []
    if patch_type == "point":
        _make_patch = _make_legend_point
    elif patch_type == "lines":
        _make_patch = _make_legend_line
    elif patch_type == "boxes":
        _make_patch = _make_legend_boxpatch

    sorted_handles = {}
    unsorted_handles = {}
    for pkwarg in patch_kwargs:
        if pkwarg.pop("multiple", False):
            label = pkwarg.pop("label", None)
            if not label in memory:
                memory[label] = []
            # create the patch with no label and save it to memory
            memory[label].append(_make_patch(pkwarg))

        else:
            # create the patch
            patch = _make_patch(pkwarg)
            # add it to the correct list
            label = patch.get_label()
            if label in label_order and label is not None:
                sorted_handles[label] = patch
            else:
                unsorted_handles[label] = patch

    return memory, sorted_handles, unsorted_handles


def _build_legend(
    ax: plt.Axes,
    title: str | None = "Légende",
    bbox_to_anchor: Tuple[float, float] = (1.05, 1),
    loc: str = "upper left",
    title_color: str = "black",
    lignes_kwords: List[dict] = None,
    points_kwords: List[dict] = None,
    kdes_kwords: List[dict] = None,
    label_order: List[str] = None,
    align_title: str = "left",
    **kwargs,
) -> mpl.legend.Legend:
    """Build a legend to be attached to a map figure.

    Parameters
    ----------
    ax : matplotlib.axes.Axe
        The axe to attach the legend to.
    title : str or None, optional
        The tile of the legend box. The default is 'Légende'.
    bbox_to_anchor : tuple[float, float], optional
        Box that is used to position the legend in conjunction with loc. See
        matplotlib.pyplot.legend for more informations. The default is (1.05, 1).
    loc : str, optional
        Location of the legend. See matplotlib.pyplot.legend for more informations.
        The default is 'upper left'.
    title_color : str, optional
        The color of the legend title. The default is 'black'.
    lignes_kwords : list of dicts, optional
        A list containing a dictionnary for every line entry to add to the legend.
        The dictionnary themselves must contain keywords compatible with
        matplotlib.lines.Line2D. Be sure to provide at least values for 'color'
        and 'label' otherwise the legend will feel really empty. The default is
        an empty list (`[]`).
    points_kwords : list of dicts, optional
        A list containing a dictionnary for every point entry to add to the legend.
        The dictionnary themselves must contain keywords compatible with
        matplotlib.lines.Line2D. Be sure to provide at least values for 'color'
        and 'label' otherwise the legend will feel really empty. The default is
        an empty list (`[]`).
    kdes_kwords : list of dicts, optional
        A list containing a dictionnary for every kde entry to add to the legend.
        The dictionnary themselves must contain keywords compatible with
        matplotlib.lines.Line2D. Be sure to provide at least values for 'color'
        and 'label' otherwise the legend will feel really empty. The default is
        an empty list (`[]`).
    label_order : list[str,...], optional
        List of labels that should be put on top of the legend. The oder of the
        list is respected. Labels not part of this list are added after those
        in the list, ordered as in their respective <ITEM>_kwords list, starting
        with lignes_kwords, then points_kwords and finally kdes_kwords. The default
        is an empty list (`[]`).
    align_title : str, optional
        Force the alignement of the legend's title. Accepted values are `left`,
        `center`, and `right`. the default is 'left'.
    kwargs : dict, optional
        These parameters are passed to matplotlib.pyplot.legend

    Returns
    -------
    leg: matplotlib.legend.Legend
        The legend's handle

    Notes
    -----
    To merge multiple objects in the same legend, the keyword "multiple" can be
    used in both dictionnaries. The label is then used to group them as a
    single entity when building the legend patches. These objects don't need to
    be of the same type, tought combining them may require a certain order to
    give interesting results.

    #TODO: add an exemple

    """
    if lignes_kwords is None:
        lignes_kwords = []
    if points_kwords is None:
        points_kwords = []
    if kdes_kwords is None:
        kdes_kwords = []
    if label_order is None:
        label_order = []

    memory = {}
    # handle kde like patches
    memory, sorted_boxes, unsorted_boxes = _handle_patch(
        kdes_kwords, patch_type="boxes", label_order=label_order, memory=memory
    )
    # handle lines
    memory, sorted_lines, unsorted_lines = _handle_patch(
        lignes_kwords, patch_type="lines", label_order=label_order, memory=memory
    )
    # handle points
    memory, sorted_point, unsorted_point = _handle_patch(
        points_kwords, patch_type="point", label_order=label_order, memory=memory
    )

    sorted_handles = {**sorted_boxes, **sorted_lines, **sorted_point}
    unsorted_handles = (
        list(unsorted_boxes.values())
        + list(unsorted_lines.values())
        + list(unsorted_point.values())
    )
    unsorted_handles_labels = (
        list(unsorted_boxes.keys())
        + list(unsorted_lines.keys())
        + list(unsorted_point.keys())
    )

    # handle memorized patches
    if len(memory.keys()) > 0:
        for key, value in memory.items():
            if key in label_order and key is not None:
                sorted_handles[key] = tuple(value)
            else:
                unsorted_handles.append(value)
                unsorted_handles_labels.append(key)

    # generate the legend
    leg = ax.legend(
        [sorted_handles[key] for key in label_order] + unsorted_handles,
        # labels
        label_order + unsorted_handles_labels,
        loc=loc,
        bbox_to_anchor=bbox_to_anchor,
        fancybox=True,
        title=title,
        handler_map={tuple: mpl.legend_handler.HandlerTuple(ndivide=None)},
        **kwargs,
    )

    leg._legend_box.align = align_title

    plt.setp(leg.get_title(), color=title_color)

    return leg


##############
### Generic figs
##############
def plot_base_dist_graphs(
    counts: CountList,
    groupnames: List[str],
    x: List[Numeric] | None = None,
    colormap: List[Colormap] | None = None,
    ticklabels: List[str] | None = None,
    title=None,
    xlabel=None,
    ylabel=None,
    legend_kwargs: dict | None = None,
    figsize=(12.65, 9.49),
):
    """This is a base canevas for plotting "provenance" load graphs.

    These graphs being in need of complicated legend objects, this function is
    only a frame and does not provide the full capabilities found in it's API
    equivalent functions.

    Parameters
    ----------
    counts : 2dlist
        Data to show in the distribution for evey item in `ticklabels`. The second
        dimension of the 2dlist should be consistent with the dimension of
        `groupnames`.
    groupnames : list[str, ...]
        The name of the different surfaces.
    figsize: tuple(float, float)
        Size of the figure, in inches (width, height). The default is (12.65, 9.49).
    x : list[Numeric] or None, optional
        Axes on top of which data is drawn. The default is None.
    colormap : list of matplotlib.pyplot.colormap or None, optional
        The colors to assign to the surfaces. This should be the same dimension
        as `groupnames`.  If None, uses matplotlib default colorcycle. The
        default is None.
    ticklabels : list[str, ...] or None, optional
        The stop labels to assign on the x-axis of the plot. If None, the default
        matplotlib ticklabels are left intact, which means ``range(len(counts[0]))``.
        The default is None.
    title : str or None, optional
        The graph title. The default is None.
    xlabel : str or None, optional
        The x axis title. The default is None.
    ylabel : str or None, optional
        The y axis  title. The default is None.
    legend_kwargs : dict or None, optional
        If a dict is provided, triggers the creation of a legend via matplotlib.pyplot.legend
        using the options provided. An empty dict will use the default matplotlib
        settings for a legend. The default is None.

    Returns
    -------
    fig : maplotlib.figure.Figure

    ax : maplotlib.pyplot.axes.Axes

    """
    # produce the fig
    with sns.axes_style("darkgrid"):
        fig, axe = plt.subplots(figsize=figsize)

        if x is not None:
            axe.stackplot(x, counts, labels=groupnames, colors=colormap)
        else:
            axe.stackplot(
                range(len(counts[0])), *counts, labels=groupnames, colors=colormap
            )

        if xlabel is not None:
            axe.set_xlabel(xlabel, size=14)

        if ylabel is not None:
            axe.set_ylabel(ylabel, size=14)

        if title is not None:
            axe.set_title(title, size=14)

        if ticklabels is not None:
            axe.set_xticks(range(len(ticklabels)))
            axe.set_xticklabels(ticklabels, rotation=90, ha="center")

        if legend_kwargs is not None:
            axe.legend(**legend_kwargs)

        axe.set_axisbelow(True)

    return fig, axe
