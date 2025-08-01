# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 00:50:04 2021

@author: lgauthier
"""
import itertools
import warnings
import functools
from typing import Any, Iterable, TypeVar, ParamSpec, List
from collections.abc import Callable, Mapping
from copy import deepcopy

import pandas as pd
import numpy as np
import geopandas as gpd

from statsmodels.stats.weightstats import DescrStatsW

from lapin.tools.ctime import Ctime
from lapin import constants

DAYS_MAP = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}

DAYS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]


def parse_days(day: str) -> list[int]:
    """
    Parse a days interval express by string to a list of intergers representing
    the day of week value with 0 = monday (lundi) and 6 = sunday (dimanche).

    Parameters
    ----------
    day : str
        A string containing one or more 3-letters day notations and zero or more
        operators to create intervals. Intervals of a single day are accepted.

        Accepted values for day notations are 'lun', 'mar', 'mer', 'jeu', 'ven',
        'sam', and 'dim'.

        Accepted values for operators are '-' (from to) and '+' (and).

    Return
    ------
    list_of_days : list of int
        int representation of the day interval.

    Example
    -------
    1. Joint interval of several days :
        >>> parse_days('lun-mer') ---> return [0, 1, 2]

    2. Interval of disjoint days :
        >>> parse_days('lun+mer') ---> return [0, 3]

    3. Interval of only one day :
        >>> parse_days('lun') ----> return [0]
    """
    if day == "dim-sam":
        return list(range(0, 7))
    day = day.strip()
    if day in DAYS:
        return [DAYS.index(day)]

    if "-" in day:
        first = DAYS.index(day.split("-")[0].strip())
        last = DAYS.index(day.split("-")[-1].strip())

        return list(range(first, last + 1))

    if "+" in day:
        return [DAYS.index(d.strip()) for d in day.split("+")]


def if_nan_then(x, val=0):
    """_summary_

    Parameters
    ----------
    x : _type_
        _description_
    val : int, optional
        _description_, by default 0

    Returns
    -------
    _type_
        _description_
    """
    return x if not np.isnan(x) else val


def myround(x, prec=2, base=0.05):
    """_summary_

    Parameters
    ----------
    x : _type_
        _description_
    prec : int, optional
        _description_, by default 2
    base : float, optional
        _description_, by default .05

    Returns
    -------
    _type_
        _description_
    """
    return round(base * round(float(x) / base), prec)


def parse_tz_mixed_time_offsets(
    se: pd.Series, format: str = None, tz: str = None, **kwargs
) -> pd.Series:
    """Convert a non time-aware Serie into a time-aware Serie.

    If tz is not specified, it will infer the time-zone. But if it contains
    a mixed_time_offset, it will error. You'll need to pass a tz information
    to this function.

    See https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html#to-datetime-tz-examples

    Parameters
    ----------
    se : pd.Series
        Pandas series to convert to datetime.
    format : str, optional
        Format of the time values, by default None.
    tz : str, optional
        Valid time-zone, by default None.
    kwargs:
        Additionnal paramaters to pass to the pandas.to_datetime function.


    Returns
    -------
    pd.Series
        _description_
    """
    if not tz:
        return pd.to_datetime(se, format=format)

    return pd.to_datetime(se, format=format, utc=True, **kwargs).dt.tz_convert(tz)


def deep_dict_update(source, overrides):
    """
    Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            returned = deep_dict_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def expend_time_interval(t_beg, t_end, as_string=True, strformat="hhmm"):
    """Take a time period express by a hour interval and create a list of all
    the hour present in it.

    Parameters
    ----------
    t_beg: str
        Hour in format f"{HH}h{mm}".
    t_end: str
        Hour in format f"{HH}h{mm}".

    Returns
    -------
    h_list : list of Ctime
        list of expended interval.
    """
    t_beg = Ctime.from_string(t_beg)
    t_end = Ctime.from_string(t_end)
    h_list = [deepcopy(t_beg)]

    while t_beg < t_end:
        t_beg.add_time(10000)
        h_list.append(deepcopy(t_beg))

    if as_string:
        h_list = [t.as_string(string_format=strformat) for t in h_list]

    return h_list


def parse_hours_bound(hb_dict, **kwargs):
    """Return all hours of study in a hoursBounds config dictionary

    Parameters
    ----------
    hb_dict : dict
        Hours bounds dict format. Exemple : {'lun':['08:00', '18:00']}

    Returns
    -------
    h_list : list
        List of all studied hours.
    """
    total_hours = []
    for _, h_bounds in hb_dict.items():
        total_hours.append(expend_time_interval(*h_bounds, **kwargs))

    # we remove first hour
    return list(np.unique(total_hours)[1:])


def filter_hour_bounds(data, hour_bounds):
    data = data.copy()
    data["hour"] = [Ctime.from_datetime(t) for t in data.datetime]
    data[constants.HOUR_BOUNDS] = np.nan

    for days, hour_intervals in hour_bounds.items():
        for interval in hour_intervals:
            days_l = parse_days(days)
            ts_beg = Ctime.from_string(interval["from"])
            ts_end = Ctime.from_string(interval["to"])

            mask = np.logical_and(
                data.datetime.dt.dayofweek.isin(days_l),
                np.logical_and(data["hour"] <= ts_end, data["hour"] >= ts_beg),
            )
            data.loc[mask, constants.HOUR_BOUNDS] = np.repeat(
                f"{days} ; {ts_beg} - {ts_end}", data.loc[mask].shape[0]
            )

    data.drop(columns="hour", inplace=True)

    # filter data outside hour_bounds
    data = data[~data[constants.HOUR_BOUNDS].isna()]

    return data


def nan_weighted_agg(
    arr: np.array, weights: np.array, agg_func: str | list = "mean"
) -> float | list[float]:
    """compute nan weighted statitiscal aggregation

    Parameters
    ----------
    arr: np.array
        1D array.
    weights: np.array
        1D array of shape (arr.shape)
    agg_func: str|list, optional
        Aggregation function. Default mean. For supported values see :
        statsmodels.stats.weightstats.DescrStatsW

    Return
    -------
    res: float | list[float]
        Weighted ggregated values of arr.
    """

    indices = np.where(np.logical_not(np.isnan(arr)))[0]
    nan_weight = weights[indices]
    nan_weight = np.nan_to_num(nan_weight, nan=1)
    stats_desc = DescrStatsW(arr[indices], weights=nan_weight, ddof=0)

    if indices.size == 0:
        return np.nan

    if isinstance(agg_func, str):
        return getattr(stats_desc, agg_func)
    else:
        return [getattr(stats_desc, z) for z in agg_func]


def restriction_aggfunc(
    list_occ: list[float], stats_type: str = "mean", weight: list = None
) -> list[float]:
    """Compute the aggregate mean of all occupancy in list. The aggregation
    function behave as this :
        1 - If only a slice of the list is a string, remove all occurances.
        2 - If all elements are numeric, return np.mean(list_occ)
        3 - Else return the first string occurance.

    Parameters
    ----------
    list_occ : list
        The list of all occupancy value to aggregate

    Return
    ------
    occ : str or int
        The occupancy to be displayed.

    Example
    -------
    1. Multi-valuated list
        >>> print(list_occ)
            [0.32, nan, 'travaux']
        >>> occupancy_restriction_aggfun(list_occ) ---> return 0.32
    2. Only strings
        >>> print(list_occ)
            ['travaux', nan, 'travaux']
        >>> occupancy_restriction_aggfun(list_occ) ---> return travaux
    3. Only float
        >>> print(list_occ)
            [0.32, 0.32, 0.32]
        >>> occupancy_restriction_aggfun(list_occ) ---> return 0.32
    """

    # remove nan
    if weight:
        weight = [w for i, w in enumerate(weight) if not pd.isna(list_occ[i])]

    if isinstance(list_occ, pd.Series):
        list_occ = list_occ.to_list()
    if isinstance(list_occ, np.ndarray):
        list_occ = list(list_occ).to_list()

    # count string (i.e. restrictions)
    nb_str_valued_occ = np.count_nonzero([isinstance(occ, str) for occ in list_occ])

    # is occ part-string part-float ? then remove strings
    if nb_str_valued_occ < len(list_occ):
        if weight:
            weight = [
                w for i, w in enumerate(weight) if not isinstance(list_occ[i], str)
            ]
        list_occ = [x for x in list_occ if not pd.isna(x)]
        list_occ = [occ for occ in list_occ if not isinstance(occ, str)]

    # empty list
    if not list_occ:
        return np.nan

    # if all occ are restrictions
    elif nb_str_valued_occ == len(list_occ):
        return list_occ[0]

    if stats_type == "mean":
        if weight:
            if sum(weight) != 0:
                return np.average(list_occ, weights=weight)
            else:
                return np.nan
        return np.nanmean(list_occ)
    if stats_type == "sum":
        return np.nansum(list_occ)
    return np.nanmedian(list_occ)


def expand_network(data, geodbl):
    """
    Fuse the occupation dataframe with the geodbl dataframe to obtain a
    complete occupancy_h dataframe.

    Parameters
    ----------
    data : geopandas.GeoDataFrame
        A db describing each segment's side of street' occupancy by hour.
    geodbl : geopandas.GeoDataFrame
        The road network containing both sides of the road to clip data on. All
        of the roads contained in this geodataframe will be returned in the
        output.  Clipping this geodataframe to the analysis zone beforehand is
        recommanded to reduce calculation times.

    Returns
    -------
    complete_occ_h : geopandas.GeoDataFrame
        Occupancy rate compiled by segment and hours on each road contained in
        geodbl.

    """
    data = data.copy()
    geodbl = geodbl.copy()

    # remove duplicates
    geodbl = (
        geodbl.groupby([constants.SEGMENT, constants.SIDE_OF_STREET])
        .nth(0)
        .reset_index()
    )

    # find roads that are present in both df
    presents = pd.merge(
        data,
        geodbl,
        how="inner",
        on=[constants.SEGMENT, constants.SIDE_OF_STREET],
    ).COTE_RUE_ID.tolist()

    # get the missing roads by sorting out the presents ones
    missing = (geodbl[~geodbl.COTE_RUE_ID.isin(presents)])[
        [
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
        ]
    ]

    data = pd.concat([data, missing])
    return data


def compute_viz_side_of_street(
    df: pd.DataFrame,
    seg_geom: pd.DataFrame,
    cols_to_crunch=constants.DEFAULT_COLS_CRUNCH,
):
    """TODO"""
    # Assert that columns are present in data
    ## df
    # Assert that columns are present in data
    df = df.copy()

    cols_df_assert = [
        constants.SEGMENT,
        constants.SIDE_OF_STREET,
    ]
    if all([col in df.index.names for col in cols_df_assert]):
        df = df.reset_index().copy()
    assert all([col in df.columns for col in cols_df_assert])

    cols_seg_geom_assert = [
        constants.SEGMENT,
        constants.SIDE_OF_STREET,
    ]
    assert all([col in seg_geom.columns for col in cols_seg_geom_assert])

    cols = []
    if constants.SEG_DB_GIS in seg_geom.columns:
        cols = [constants.SEG_DB_GIS]

    # retrieve one way segments
    seg_plex = seg_geom.set_index(constants.SIDE_OF_STREET_VIZ)[constants.SEGMENT].get(
        0, pd.Series([np.nan])
    )
    if isinstance(seg_plex, pd.Series):
        seg_plex = seg_plex.values
    elif pd.api.types.is_numeric_dtype(seg_plex):
        seg_plex = [seg_plex]
    else:
        seg_plex = []

    df[constants.SIDE_OF_STREET_VIZ] = df[constants.SIDE_OF_STREET]
    df.loc[df[constants.SEGMENT].isin(seg_plex), constants.SIDE_OF_STREET_VIZ] = 0

    # merge both side of street into one
    if cols_to_crunch:
        for col, f in cols_to_crunch.items():
            df[col] = df.groupby([constants.SEGMENT, constants.SIDE_OF_STREET_VIZ])[
                col
            ].transform(f)

        df = (
            df.groupby([constants.SEGMENT, constants.SIDE_OF_STREET_VIZ])
            .nth(0)
            .reset_index()
        )

    # add geom if exist
    if cols:
        df = df.join(
            other=seg_geom.set_index([constants.SEGMENT, constants.SIDE_OF_STREET_VIZ])[
                cols
            ],
            on=[constants.SEGMENT, constants.SIDE_OF_STREET_VIZ],
            how="left",
        )

    return df


def enforce_restrictions(occ_h, resh, zero_observ=True, time_period="hour"):
    """


    Parameters
    ----------
     occ_h : geopandas.GeoDataFrame
        A db describing each segment's side of street' occupancy by hour.
    resh : Curbs
        The regulation data, containing the number of spaces in the network.

    Returns
    -------
    corrected_occ_h : TYPE
        DESCRIPTION.

    """
    occ_h = occ_h.copy()

    occ_h = occ_h.set_index([constants.SEGMENT, constants.SIDE_OF_STREET]).sort_index()

    # find relevant columns to parse
    cols = [
        c
        for c in occ_h.columns
        if c
        not in [
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            constants.SEG_DB_GIS,
            "park_type",
            constants.SECTEUR_NAME,
        ]
    ]

    # make sure the restrictions are correctly applied
    for col in cols:
        if time_period == "hour":
            seg_info = resh.get_capacity(hour=col, as_dataframe=True)
        if time_period == "day":
            seg_info = resh.get_capacity(day=col, as_dataframe=True)
        if time_period == "dh":
            seg_info = resh.get_capacity(day=col, as_dataframe=True)
        if time_period == "all":
            seg_info = resh.get_capacity(as_dataframe=True)
        seg_info = compute_viz_side_of_street(seg_info, occ_h.reset_index())

        with_restricts = pd.merge(
            left=occ_h,
            right=seg_info,
            how="inner",
            on=[constants.SEGMENT, constants.SIDE_OF_STREET],
        )
        with_restricts = with_restricts[
            [constants.SEGMENT, constants.SIDE_OF_STREET]
        ].to_dict(orient="split")["data"]

        if len(with_restricts) > 0:
            # prepare the dfs
            seg_info = seg_info.set_index(
                [constants.SEGMENT, constants.SIDE_OF_STREET]
            ).sort_index()

            for seg_id in with_restricts:
                seg_id = tuple(seg_id)
                # skip segId not in segInfo
                if seg_id not in seg_info.index.tolist():
                    continue

                row = seg_info.loc[[seg_id]].iloc[0]

                if row[constants.CAP_N_VEH] == 0:
                    # there is no parking, so occupation is 0
                    occ_h.loc[seg_id, col] = np.float64(0)

    # set back missing to interger indexing
    occ_h = occ_h.reset_index()

    return occ_h


def compare_two_lapi_results(res1, res2, seg_gis, metric_name="mean_occ"):
    """Function to compare two already computed lapi metric results in
    the same space. In the function res2 is compared to res1. Hence the
    output will show res2 - res1. Also, only the data present on common
    road will be process in the comparison.

    Parameters
    ----------
    res1: pd.DataFrame
        First result.
    res2: pd.DataFrame
        Second result to compare to the first one.
    seg_gis: gpd.GeoDataFrame
        Roads geography for the study zone
    metric_name: str
        Columns name of the metric to compare.
    """
    # 1-Read rempla past and new
    res1 = res1.copy()
    res2 = res2.copy()

    if constants.SEG_DB_GIS in res1.columns:
        res1.drop(columns=constants.SEG_DB_GIS, inplace=True)

    ## change metric columns of second result
    res2.rename(columns={metric_name: metric_name + "_compared"}, inplace=True)

    # 2-Add geometry to occupancy data
    res2[constants.SEG_DB_SIDE] = res2.side_of_street.map({-1: "Gauche", 1: "Droite"})
    res2 = (
        res2.join(
            other=seg_gis.set_index([constants.SEG_DB_ID, constants.SEG_DB_SIDE])[
                ["geometry", constants.SEG_DB_STREET]
            ].drop_duplicates(),
            on=[constants.SEGMENT, constants.SEG_DB_SIDE],
            how="left",
        )
        .rename(columns={"geometry": constants.SEG_DB_GIS})
        .drop(columns=[constants.SEG_DB_SIDE])
        .drop_duplicates(keep="first")
    )
    ## as geopandas.GeoDataFrame
    res2 = gpd.GeoDataFrame(res2, geometry=constants.SEG_DB_GIS, crs=seg_gis.crs)

    # 3-Process occupancy of both year to make it comparable
    ## Aucune places, Travaux and Voie réservée have an occupancy of 0
    res2.loc[
        res2[metric_name + "_compared"].isin(["Travaux", "Voie réservée"]),
        metric_name + "_compared",
    ] = np.nan
    res1.loc[
        res1[metric_name].isin(
            ["Aucune places", "Aucune place", "Travaux", "Voie réservée"]
        ),
        metric_name,
    ] = np.nan

    ## Non parcourue have an occupancy of nan
    res2.loc[
        res2[metric_name + "_compared"].isin(["Non parcourue"]),
        metric_name + "_compared",
    ] = np.nan
    res1.loc[res1[metric_name].isin(["Non parcourue"]), metric_name] = np.nan

    ## filter street segment both in 2019 and 2021
    occ_merge = res2.merge(
        res1, on=[constants.SEGMENT, constants.SIDE_OF_STREET], how="inner"
    )

    ## set "N'a plus de stationnement" to stationnement changed
    occ_merge.loc[
        occ_merge[metric_name + "_compared"].isin(["Aucune places", "Aucune place"])
        & (occ_merge[metric_name] > 0),
        metric_name + "_compared",
    ] = "N'a plus de stationnements"
    occ_merge.loc[
        occ_merge[metric_name + "_compared"] == "N'a plus de stationnements",
        metric_name,
    ] = "N'a plus de stationnements"
    # remove nan values
    occ_merge = occ_merge[
        ~occ_merge[metric_name].isna() & ~occ_merge[metric_name + "_compared"].isna()
    ]

    ### retrieve data
    res1 = occ_merge[
        [constants.SEGMENT, constants.SIDE_OF_STREET, metric_name, constants.SEG_DB_GIS]
    ]
    res2 = occ_merge[
        [
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            metric_name + "_compared",
            constants.SEG_DB_GIS,
        ]
    ]

    # 4-Expand both network to plot all segment of parcours
    col_sec = (
        [constants.SECTEUR_NAME] if constants.SECTEUR_NAME in seg_gis.columns else []
    )
    res1 = expand_network(res1, geodbl=seg_gis).drop(columns=col_sec)
    res2 = expand_network(res2, geodbl=seg_gis).drop(columns=col_sec)

    # 6-Remove nan
    res2.dropna(inplace=True)
    res1.dropna(inplace=True)

    # 7-Compare the results
    def compare_occ(val1, val2):
        if pd.isna(val1) and pd.isna(val2):
            return np.nan
        if not pd.api.types.is_number(val1) and val1 == val2:
            return val1
        if not pd.api.types.is_number(val1) or pd.isna(val1):
            val1 = 0
        if not pd.api.types.is_number(val2) or pd.isna(val2):
            val2 = 0
        return val1 - val2

    compared = np.array(
        list(
            map(
                compare_occ,
                res2[metric_name + "_compared"].values,
                res1[metric_name].copy(),
            )
        )
    )

    return res1, res2, compared


def read_hr_saved_data(path):

    def convert_float(x):
        try:
            return float(x)
        except:
            return np.nan

    df = pd.read_csv(path).drop(columns="Unnamed: 0", errors="ignore")
    cols = [
        col
        for col in df.columns
        if col not in ["segment", "side_of_street_viz", "NomSecteur"]
    ]

    for col in cols:
        df[col] = df[col].apply(convert_float)

    df = df.groupby(
        ["segment", "side_of_street_viz"],
    ).agg(lambda x: restriction_aggfunc(x.to_list()))

    df = df[~df[cols].isna().all(axis=1)]
    return df, cols


def generate_random_plaque_from_hach(df: pd.DataFrame, mask: List[bool]):
    """Take a dataframe of anonymized vehicule's plate and create fake plates that
    passes into validity check function of the enhancer.

    Parameters
    ----------
    df: pandas.DataFrame
        Anonymized plates dataframe
    mask: List[bool]
        Index mask of Anonymized plates in df

    Returns
    -------
    pandas.DataFrame
    """

    plate_map = pd.DataFrame(
        data=[
            f'{i:03}{"".join(j)}'
            for j in itertools.combinations_with_replacement(
                "ABCDEFJFHIJKLMNOPQRSTUVWXYZ", 3
            )
            for i in range(1000)
            if j[0] == j[1] == j[2]
        ],
        columns=[constants.PLATE],
    )
    plate_map = plate_map.sample(frac=1, random_state=1234).reset_index(drop=True)
    # mask = df.time.dt.date == pandas.to_datetime('2023-10-16').date()
    nb_unique_plate = df[mask][constants.PLATE].unique().shape[0]
    mapping = {
        df[mask][constants.PLATE].unique()[i]: plate_map.loc[i, constants.PLATE]
        for i in range(nb_unique_plate)
    }

    df[constants.PLATE] = df[constants.PLATE].replace(mapping)

    return df


def xform_list_entre_to_dict(
    listValues: Iterable,
    keyList: Iterable,
    default: Any = None,
    valueVarName: str = "valueVarName",
) -> dict:
    """
    A function that accepts two lists and returns a dictionnary. Used inside
    functions when an argument is to be be received as a list but working with
    the data is easier with a dictionnary.

    Parameters
    ----------
    listValues : Iterable
        What will become the dictionnarie's values.
    keyList : Iterable
        What will become the dictionnarie's keys.
    default : Any, optional
        If listValues is empty, fill the values with 'defaul'. The default is None.
    valueVarName : str, optional
        A link to the argument's name for the sake of raising a detailed TypeError
        in case listValues is not properly passed.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    if not listValues:
        listValues = {key: default for key in keyList}
    elif isinstance(listValues, (tuple, list, np.ndarray)):
        listValues = {keyList[k]: listValues[k] for k in range(len(keyList))}
    else:
        raise TypeError(
            f"`{valueVarName}` must be None or one of {{tuple, list, np.ndarray}}, received {listValues.__class__}"
        )
    return listValues


##########################
###### EXCEPTIONS ########
##########################


class IncompleteDataError(Exception):
    """An exception signaling that an expected column in a dataframe is missing.

    Attributes
    ----------
    message : str
        The error message to displayed when raised.
    """

    def __init__(self, df: pd.DataFrame, *column, context=None):
        if len(column) == 1:
            message = f"Missing column `{column[0]}` for dataframe `{df}`."
        else:
            column = [f"`{c}`" for c in column]
            message = f"Missing columns {', '.join(column)} for dataframe `{df}`."

        if context is not None:
            message += f" {context}"
        self.message = message

        super().__init__(message)


##########################
###### WARNINGS ##########
##########################


class MissingDataWarning(UserWarning):
    """A warning signaling that some data is missing to fully complete the
    required analysis.

    Attributes
    ----------
    message : str
        The message to display when raised.
    """

    def __init__(self, message: str) -> None:
        """
        Parameters
        ----------
        message : str
            The message to display when raised.
        """
        super().__init__(message)
        self.message = message


T = TypeVar("T")
P = ParamSpec("P")


def deprecated(func: Callable[P, T]) -> Callable[P, T]:
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args: P.args, **kwargs: P.kwargs) -> T:
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func
