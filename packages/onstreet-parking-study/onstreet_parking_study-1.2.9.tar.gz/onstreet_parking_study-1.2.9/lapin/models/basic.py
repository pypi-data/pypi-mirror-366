"""
Created on Wed Jun  9 10:12:56 2021

@author: lgauthier
@author: alaurent
"""

import numpy as np
import pandas as pd

from lapin.models.utils import slice_data_by_hour
from lapin import constants


def compute_observation_stats(
    lapi_enhance: pd.DataFrame,
    days: str = "lun-dim",
    timeslot_beg: str = "00h00",
    timeslot_end: str = "23h59",
) -> pd.DataFrame:
    """
    this function compute basic stats on lapi data : count of the total number
    of vehicule, and count disctinct vehicule by day.

    parameters
    ----------
    lapi_enhance : pandas.dataframe
        the sighting data, must have been ran through the enhancement process
        beforehand.
    timeslot_beg : str
        starting hour in format f"{hh}h{mm}".
    timeslot_end : str
        ending hour in format f"{hh}h{mm}".

    returns
    -------
    base_stats : pandas.dataframe
        the basics observations statistics.

    """
    lapi_enhance = lapi_enhance.copy()

    lapi_enhance = slice_data_by_hour(
        lapi_enhance, days, timeslot_beg, timeslot_end, "datetime"
    )

    # make something usefull of datetime
    lapi_enhance.datetime = pd.to_datetime(lapi_enhance.datetime)

    base_stats = pd.concat(
        [
            lapi_enhance.pivot_table(
                values=constants.PLATE,
                index=lapi_enhance.datetime.dt.date,
                aggfunc="count",
            ).rename(columns={constants.PLATE: "nb_plaques"}),
            lapi_enhance.pivot_table(
                values=constants.PLATE,
                index=lapi_enhance.datetime.dt.date,
                aggfunc=lambda x: len(x.unique()),
            ).rename(columns={constants.PLATE: "nb_plaques_unq"}),
            lapi_enhance.pivot_table(
                values=constants.DATETIME,
                index=lapi_enhance.datetime.dt.date,
                aggfunc=lambda x: np.unique((x.dt.hour)).shape[0],
            ).rename(columns={constants.DATETIME: "nb_hours"}),
        ],
        axis=1,
    )

    ttal = [
        "subtotal",
        lapi_enhance.shape[0],
        lapi_enhance[constants.PLATE].unique().shape[0],
        lapi_enhance.datetime.dt.hour.unique().shape[0],
    ]
    base_stats = pd.concat(
        [
            base_stats,
            pd.DataFrame(
                data=[ttal],
                columns=[
                    constants.DATETIME,
                    "nb_plaques",
                    "nb_plaques_unq",
                    "nb_hours",
                ],
            ).set_index(constants.DATETIME),
        ],
        axis=0,
    )

    base_stats["period_name"] = f"{days} : {timeslot_beg} - {timeslot_end}"

    return base_stats
