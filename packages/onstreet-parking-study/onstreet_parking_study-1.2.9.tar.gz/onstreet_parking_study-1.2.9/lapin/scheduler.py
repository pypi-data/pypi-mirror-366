"""
Core processing for LAPI

Created on Wed Jun  9 10:12:27 2021

@author: lgauthier
@author: alaurent

This file  imported as a module and contains the following functions:

    * derive_delim_from_data - create natural geographic delimitation of
      a georeferenced data.
    * SchedulerDataStore - Keep track of data.
    * Scheduler - Class to handle LAPI analysis.
"""

import json
import logging
import os
from copy import deepcopy
from dataclasses import dataclass, field
from typing import cast

import geopandas as gpd
import pandas as pd
import shapely

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from lapin import constants
from lapin.configs.database import STAGING_DATABASE
from lapin.configs.user_conf import UserConfig
from lapin.constants import DEFAULT_CRS, MONTREAL_CRS
from lapin.core import (
    CollectedArea,
    Curbs,
    LprDataFrame,
    RoadNetwork,
    RoadNetworkDouble,
    TrajDataFrame,
)
from lapin.core._utils import (
    IncompleteDataError,
    json_keys_2_int,
    prepare_data_before_export,
)
from lapin.figures import STUDY_CRS
from lapin.figures import base as f_base
from lapin.figures import occup as f_occup
from lapin.figures import reassignement as f_report
from lapin.figures import rempla as f_rempla
from lapin.io.sql import get_engine, Base
from lapin.io.s3 import load_images_directory
from lapin.models.rempla import park_time_street
from lapin.tools.ctime import Ctime
from lapin.tools.utils import DAYS, DAYS_MAP, parse_days

logger = logging.getLogger(__name__)

NULL_RES = {
    "base": pd.DataFrame(),
    "capacity": pd.DataFrame(),
    "capacity_hour": pd.DataFrame(),
    "occ_hour": pd.DataFrame(),
    "occ_timeslot": pd.DataFrame(),
    "occ_optimal": gpd.GeoDataFrame(),
    "occ_worst_hour": gpd.GeoDataFrame(),
    "export_human_readable": gpd.GeoDataFrame(),
    "parking_time": pd.DataFrame(),
    "prov": pd.DataFrame(),
    "trips": pd.DataFrame(),
    "vehicle_sighted": pd.DataFrame(),
    "agg_secteur_occ": pd.DataFrame(),
    "df_report": pd.DataFrame(),
    "dist_report": pd.DataFrame(),
    "dist_max_report": pd.DataFrame(),
    "roads_id_report": [],
}


def derive_delim_from_data(data: pd.DataFrame, destination_crs: str = DEFAULT_CRS):
    """Create a polygon convex hull from any point dataframe with lat, lng
    columns. Column name must be consistant with constants DESTINATION_LNG and
    DESTINATION_LAT values.

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to create the bounding box from. Latitude and longitude
        columns names must be consistant with constants DESTINATION_LNG and
        DESTINATION_LAT values.
    destination_crs: str, default: epsg:4326
        Destination Coordinate Reference System of the geometry objects. Can be
        anything accepted by :meth:`pyproj.CRS.from_user_input()
        <pyproj.crs.CRS.from_user_input>`, such as an authority string
        (eg "EPSG:4326") or a WKT string.

    Returns
    -------
    gpd.GeoDataFrame
        The bouding box of data point as a convex_hull.
    """

    data = data.copy()
    data = gpd.GeoDataFrame(
        data=data,
        geometry=gpd.points_from_xy(
            x=data[constants.DESTINATION_LNG], y=data[constants.DESTINATION_LAT]
        ),
        crs=DEFAULT_CRS,
    )

    data.to_crs(crs=destination_crs, inplace=True)

    geom = data.unary_union.convex_hull

    return gpd.GeoDataFrame(
        data={"sector": ["default"]}, geometry=geom, crs=destination_crs
    )


@dataclass
class SchedulerDataStore:
    """
    Analysis input data storage. Take parked vehicule's dataset and other
    related one and store them.  Data must be in an correct format (i.e.
    passed to the data enhancer before).

    Parameters
    ----------
    lpr_data : LprDataFrame
        lapi collected data.
    veh_data : TrajDataFrame
        lapi vehicule collected data.
    roads : pandas.DataFrame
        Parking rules and capacity of road segments.
    roadsdb : geopandas.GeoDataFrame
        Geographical representation of road segments.
    trips : pandas.DataFrame (optional)
        DataFrame containing origin and destination for each vehicules that
        was sawn.
    grid_trips_origin : geopandas.GeoDataFrame (requiered if trips)
        Aggregation zone for trips origins.
    delim : geopandas.GeoDataFrame (optional) // Config
        Area studied.
    vis_delim : geopandas.GeoDataFrame (optional) // Config
        Division of the area for plotting purpose.
    """

    lpr_data: LprDataFrame
    veh_data: TrajDataFrame
    roads: RoadNetwork
    roadsdb: RoadNetworkDouble
    restriction_handler: Curbs
    trips: gpd.GeoDataFrame | None = None
    grid_trips_origin: gpd.GeoDataFrame | None = None
    delim: gpd.GeoDataFrame | None = None
    vis_delim: gpd.GeoDataFrame | None = None
    _regions: pd.DataFrame | None = None

    def __post_init__(self):
        if not isinstance(self.vis_delim, gpd.GeoDataFrame):
            convex_hull = self.roads.unary_union.convex_hull
            self.delim = gpd.GeoDataFrame(
                data=["Étude"],
                columns=[constants.SECTEUR_NAME],
                geometry=[convex_hull],
                crs=self.roads.crs,
            )
            self.vis_delim = gpd.GeoDataFrame(
                data=["Étude"],
                columns=[constants.SECTEUR_NAME],
                geometry=[convex_hull],
                crs=self.roads.crs,
            )
        self.vis_delim = self.vis_delim.to_crs(STUDY_CRS)
        self._regions = self.compute_regions(self.roadsdb)

        self._remove_point_ext_study()

    def _remove_point_ext_study(self):
        lpr = self.lpr_data.copy()
        veh = self.veh_data.copy()

        lpr = lpr.to_geodataframe()
        veh = veh.to_geodataframe()

        delim = cast(gpd.GeoDataFrame, self.delim)

        assert lpr.crs == delim.crs
        lpr = gpd.clip(lpr, delim)
        veh = gpd.clip(veh, delim)

        self.lpr_data = LprDataFrame(lpr.drop(columns="geometry"))
        self.veh_data = TrajDataFrame(veh.drop(columns="geometry"))

    @property
    def roads_by_sectors(self, predicate="within"):
        return gpd.sjoin(self.roadsdb, self.delim, how="left", predicate=predicate)

    @property
    def regions(self):
        if not isinstance(self._regions, pd.DataFrame) and not self._regions:
            logger.warning(
                "Regions havn't been set. Please set the region "
                + "before using it. Returning empty Dataframe."
            )
            return pd.DataFrame()
        return self._regions

    @regions.setter
    def regions(self, regions: pd.DataFrame):
        if not (
            constants.SEGMENT in regions.columns
            and constants.SIDE_OF_STREET in regions.columns
            and constants.SECTEUR_NAME in regions.columns
        ):
            raise IncompleteDataError(
                regions,
                f"{constants.SIDE_OF_STREET}, {constants.SIDE_OF_STREET} or"
                + f" {constants.SECTEUR_NAME}",
                "regions",
            )

        self._regions = regions

    def compute_regions(self, street):
        regions = gpd.sjoin(street, self.delim, predicate="within", how="inner")
        regions = regions.reset_index()
        regions = regions[
            [constants.SEGMENT, constants.SIDE_OF_STREET, constants.SECTEUR_NAME]
        ].drop_duplicates()
        return regions


@dataclass
class Scheduler:
    """Analysis framework. Take parked vehicule's position dataset as input to
    compute several evaluation metrics. Data must be in an correct format (i.e.
    passed to the data enhancer before).

    Parameters
    ----------
        config: UserConfig
        study: CollectedArea
        datastore: AnalyserDataStore
        res: dict[pd.DataFrame] = {}
        save_path: str = constants.CACHE
        cache_path: str = constants.CACHE
    """

    config: UserConfig
    study: CollectedArea
    datastore: SchedulerDataStore
    res: dict[str, pd.DataFrame] = field(default_factory=lambda: NULL_RES)
    save_path: str = constants.CACHE
    run_id: int | None = None
    conf_id: int | None = None
    db_load: bool = False

    @classmethod
    def from_datas(
        cls,
        conf: UserConfig,
        analysis_data: SchedulerDataStore,
        run_id: int | None = None,
        conf_id: int | None = None,
    ):
        """_summary_

        Parameters
        ----------
        conf : UserConfig
            _description_
        analysis_data: AnalyserDataStore
        Returns
        -------
        Analyser
            _description_
        """

        network_config = analysis_data.roads.create_network_config(
            uuid_list=list(analysis_data.veh_data[constants.UUID].unique()),
            desagregated_street_name=conf.ignore_agg_seg,
        )
        study = CollectedArea.from_dataframe(
            analysis_data.veh_data, analysis_data.restriction_handler
        )
        if study.segments:
            study.populate_road_geometry(analysis_data.roadsdb, force_expand=True)
            _ = study.merge_lpr_readings(
                analysis_data.lpr_data[
                    [
                        constants.SEGMENT,
                        constants.SIDE_OF_STREET,
                        constants.UUID,
                        constants.DATETIME,
                        constants.PLATE,
                    ]
                ]
            )
            study.update_with_config(
                network_config, json_keys_2_int(conf.vehicule_conf)
            )

            analysis_data.regions = analysis_data.compute_regions(study.street_geometry)

        if conf.work_folder == "postgres":
            work_folder = "postgres"
        else:
            work_folder = os.path.join(conf.work_folder, "resultat/")

        return cls(
            conf,
            study,
            analysis_data,
            save_path=work_folder,
            run_id=run_id,
            conf_id=conf_id,
        )

    def clear_result_memory(self):
        """Set self.res to NULL_RES"""
        self.res = NULL_RES

    def load_kpi_in_memory(self, days: str, hour_from: str, hour_to: str):
        """Compute all the analysis accordingly to the config file

        Parameters
        ----------

        Returns
        -------
        None

        """
        logger.info("computing analysis kpi")

        # Number of vehicules
        self.res["base"] = self._base(days, hour_from, hour_to)

        # Occupancy
        if self.config.act_occup:
            logger.info("computing occupation kpi")

            occ_h, occ_ts, veh_s, cap, res = self._occup(days, hour_from, hour_to)

            self.res["occ_hour"] = occ_h
            self.res["occ_timeslot"] = occ_ts
            self.res["vehicle_sighted"] = veh_s
            self.res["capacity"] = cap
            self.res["capacity_hour"] = self._capa()
            self.res["restrictions"] = res
            self.res["occ_optimal"] = self.study.occupancy_optimal(
                days, hour_from, hour_to
            )

            if self.config.comp_sect_agg:
                occ = self._occup_agg(days, hour_from, hour_to)
                self.res["agg_secteur_occ"] = occ

            self.res["occ_worst_hour"] = self.study.occupancy_worst_hour(
                days, hour_from, hour_to
            )

            self.res["export_human_readable"] = self.study.occupancy_time_aggregation(
                days=days,
                timeslot_beg=hour_from,
                timeslot_end=hour_to,
                export_human_readable=True,
                freq=self.config.analyse_freq,
                roads=self.datastore.roads,
            )

        # Reasssignement
        if self.config.act_report:
            logger.info("compution reassignement kpi")

            report_res = self.study.reassignement(
                roads=self.datastore.roads,
                street_name_to_report=self.config.report_street_name,
                days=days,
                timeslot_beg=hour_from,
                timeslot_end=hour_to,
            )

            self.res["df_report"] = report_res[0]
            self.res["dist_report"] = report_res[1]
            self.res["dist_max_report"] = report_res[2]
            self.res["roads_id_report"] = report_res[3]

        if self.config.act_rempla:
            logger.info("computing rotation kpi")
            # we need occupancy for this analysis
            if not self.config.act_occup:
                raise ValueError(
                    "Occupancy needs to be computed if parking" + " time is set"
                )

            pk_time = self._rempla(days, hour_from, hour_to)

            pk_time = prepare_data_before_export(pk_time, self.study.street_geometry)
            pk_time = pk_time.astype(
                {
                    "occ": "float",
                    "veh_sighted": "float",
                    constants.CAP_N_VEH: "float",
                    "day": "datetime64[s]",
                }
            )

            # parking time
            rempla = park_time_street(
                park_time=pk_time,
                res_handler=self.datastore.restriction_handler,
                seg_gis=self.datastore.roadsdb,
                handle_restriction=True,
            )

            pk_time = pk_time.reset_index()
            # save results
            self.res["parking_time"] = pk_time
            self.res["rempla"] = rempla

        if self.config.act_prov:
            logger.info("computing provenance kpi")
            self._prov()

    def _vis_delim_iterable(self) -> dict:
        # recover iterable shapely objects
        if isinstance(self.datastore.vis_delim, pd.core.series.Series):
            if constants.SECTEUR_NAME in self.datastore.vis_delim.index:
                vis_delim = {
                    constants.SECTEUR_NAME: self.datastore.vis_delim["geometry"]
                }
            else:
                vis_delim = {"Secteur 1": self.datastore.vis_delim["geometry"]}

        elif isinstance(self.datastore.vis_delim, pd.core.frame.DataFrame):
            if constants.SECTEUR_NAME in self.datastore.vis_delim.columns:
                if self.datastore.vis_delim.shape[0] > 1:
                    vis_delim = self.datastore.vis_delim.set_index(
                        constants.SECTEUR_NAME
                    )["geometry"].to_dict()
                else:
                    vis_delim = {
                        constants.SECTEUR_NAME: self.datastore.vis_delim[
                            "geometry"
                        ].iloc[0]
                    }

            else:
                if self.datastore.vis_delim.shape[0] > 1:
                    vis_delim = {
                        f"Secteur {i+1}": geom
                        for i, geom in enumerate(self.datastore.vis_delim["geometry"])
                    }
                else:
                    vis_delim = {
                        "Secteur 1": self.datastore.vis_delim["geometry"].iloc[0]
                    }
        else:
            raise NotImplementedError(
                "This type of delimitation is not impletmented. Use geodataframe or geoseries"
            )

        return vis_delim

    def _plot_capacity(
        self,
        vis_delim: dict[str, shapely.Polygon],
        day_hour_plot: bool = False,
        anotate_occ: bool = False,
        compass_rose: bool = False,
        map_leg_dpi_kwargs: dict = None,
    ):

        path = os.path.join(self.save_path, "capacity")
        os.makedirs(path, exist_ok=True)

        # overall capacity by visDelim
        capacity = self.datastore.restriction_handler.get_capacity(as_dataframe=True)
        capacity = prepare_data_before_export(
            capacity,
            self.datastore.roadsdb.set_index(
                [constants.SEGMENT, constants.SIDE_OF_STREET]
            ),
        )

        f_occup.segment_capacity_map(
            capacity,
            vis_delim,
            path,
            restrictions=True,
            basename=self.config.num_proj,
            normalized=False,
            rotation=self.config.vis_rotation,
            fig_buffer=self.config.vis_buffer,
            anotate=anotate_occ,
            compass_rose=compass_rose,
            **map_leg_dpi_kwargs,
        )

        # capacity by day and hour
        if day_hour_plot:
            os.makedirs(path + "/hours", exist_ok=True)
            for days, times in constants.CAP_DAYS_HOUR_TO_COMPUTE.items():
                hours = times["from"]
                ends = times["to"]
                steps = float(times["step"])

                for day in parse_days(days):
                    hour = Ctime.from_string(hours)
                    end = Ctime.from_string(ends)
                    step = Ctime.from_declared_times(hours=steps)
                    while hour <= end:
                        resh = self.datastore.restriction_handler
                        capacity = resh.get_capacity(
                            day=DAYS[day], hour=hour.as_datetime(), as_dataframe=True
                        )
                        capacity = prepare_data_before_export(
                            capacity,
                            self.datastore.roadsdb.set_index(
                                [constants.SEGMENT, constants.SIDE_OF_STREET]
                            ),
                        )
                        f_occup.segment_capacity_map(
                            capacity,
                            vis_delim,
                            path + "/hours",
                            restrictions=True,
                            basename=self.config.num_proj + f"{DAYS[day]}_{hour}_",
                            normalized=False,
                            rotation=self.config.vis_rotation,
                            fig_buffer=self.config.vis_buffer,
                            anotate=anotate_occ,
                            compass_rose=compass_rose,
                            save_geojson=True,
                            **map_leg_dpi_kwargs,
                        )
                        hour += step

    def plot(self, **kwargs):
        """Plotting function. Plot all desired graph for the analysis.

        Parameters
        ----------
        data: str or DataFrame (Default: 'Undefined')
            The dataFrame to analyse, if string, use the preloaded data in the
            analyser.
        transac_plot: boolean (Default: True)
            Indicate if transactions data from server should be plotted.
        plot_all_capacities: boolean (Default: False)
            Plot capacity for each hour.

        TODO
        ----
        1. Shoot what to plot in config file and make a function to excecute
        each plot based on this configuration.

        """
        vis_delim = self._vis_delim_iterable()

        # check for dpi overrides
        fig_dpi = kwargs.get("fig_dpi", 150)
        map_dpi = kwargs.get("map_dpi", 150)
        leg_dpi = kwargs.get("leg_dpi", 150)

        map_leg_dpi_kwargs = {}
        map_leg_dpi_kwargs["fig_dpi"] = fig_dpi if fig_dpi else 150
        map_leg_dpi_kwargs["map_dpi"] = map_dpi if map_dpi else 150
        map_leg_dpi_kwargs["leg_dpi"] = leg_dpi if leg_dpi else 150

        fig_dpi_kwargs = {}
        fig_dpi_kwargs["fig_dpi"] = fig_dpi

        map_dpi_kwargs = {}
        map_dpi_kwargs["map_dpi"] = map_dpi

        leg_dpi_kwargs = {}
        leg_dpi_kwargs["leg_dpi"] = leg_dpi

        # check for compass rose kwargs
        compass_rose = kwargs.get("compass_rose", True)

        add_cat_prc = kwargs.get("add_cat_prc", False)
        anotate_occ = kwargs.get("anotate_occ", self.config.anotation)
        anotate_cap = kwargs.get("anotate_cap", self.config.capa_along_occ)

        # base plot
        logger.info("plotting all required kpi")

        data_heat_map = self.datastore.lpr_data.to_geodataframe()
        data_heat_map = data_heat_map.to_crs(MONTREAL_CRS)
        data_heat_map["color_cat"] = "blue"
        data_heat_map["geometry"] = data_heat_map.buffer(2)

        # why is python so ugly
        rotation = self.config.vis_rotation[0] if self.config.vis_rotation else 0
        f_base._generic_plot_map(
            data_heat_map,
            col=None,
            delim=data_heat_map.unary_union.convex_hull,
            anotate=False,
            savepath=self.save_path + f"/{self.config.num_proj}_data_row_plot.png",
            rotation=rotation,
            compass_rose=compass_rose,
            dpi=300,
            normalized_val=False,
        )

        # segments capacity
        logger.info("plotting capacity")
        self._plot_capacity(
            vis_delim=vis_delim,
            day_hour_plot=self.config.plot_all_capa,
            anotate_occ=anotate_occ,
            compass_rose=compass_rose,
            map_leg_dpi_kwargs=map_leg_dpi_kwargs,
        )

        if self.config.act_occup:
            # Occupancy
            logger.info("plotting occupancy")

            path = os.path.join(self.save_path, "occ")
            os.makedirs(path, exist_ok=True)

            # occupancy by regions
            for sector, occ_reg in self.res["agg_secteur_occ"].groupby(
                constants.SECTEUR_NAME
            ):
                f_occup.hour_occupancy_barplot(
                    occ_reg.melt(
                        id_vars=constants.SECTEUR_NAME,
                        var_name="hour",
                        value_name="mean",
                    ),
                    savepath=f"{path}/{self.config.num_proj}_{sector}_",
                )

            cols = [
                col
                for col in self.res["occ_timeslot"].columns
                if col not in ["days", "geometry"]
            ]

            # occupancy by timeslot
            f_occup.occupancy_map(
                occ_df=self.res["occ_timeslot"],
                cols=cols,
                delims=vis_delim,
                savepath=path,
                basename=str(self.config.num_proj) + "_timeslot",
                add_cat_prc=add_cat_prc,
                anotate=anotate_occ,
                rotation=self.config.vis_rotation,
                fig_buffer=self.config.vis_buffer,
                compass_rose=compass_rose,
                leg_dpi=map_leg_dpi_kwargs.get("leg_dpi", None),
                map_dpi=map_leg_dpi_kwargs.get("map_dpi", None),
            )

            cols = [
                col
                for col in self.res["occ_hour"].columns
                if col
                not in [
                    constants.SEGMENT,
                    constants.SIDE_OF_STREET_VIZ,
                    constants.SEG_DB_GIS,
                    constants.SECTEUR_NAME,
                ]
            ]

            # occupancy by hour
            f_occup.occupancy_map(
                occ_df=self.res["occ_hour"],
                cols=cols,
                delims=vis_delim,
                savepath=path,
                basename=self.config.num_proj,
                add_cat_prc=add_cat_prc,
                anotate=anotate_occ,
                rotation=self.config.vis_rotation,
                fig_buffer=self.config.vis_buffer,
                compass_rose=compass_rose,
                capacity_df=self.res["capacity"] if anotate_cap else None,
                leg_dpi=map_leg_dpi_kwargs.get("leg_dpi", None),
                map_dpi=map_leg_dpi_kwargs.get("map_dpi", None),
            )

            # worst hour
            occ_worst_hour = self.res["occ_worst_hour"]
            occ_worst_hour["occ_worst_hour"] = [
                o if str(r) == "nan" else "Aucune place"
                for o, r in occ_worst_hour[["occ", "restrictions"]].values
            ]
            cap_worst_hr = occ_worst_hour.copy()
            cap_worst_hr = cap_worst_hr.drop(columns="occ_worst_hour")
            cap_worst_hr = cap_worst_hr.rename(
                columns={constants.CAP_N_VEH: "occ_worst_hour"}
            )
            cap_worst_hr["occ_worst_hour"] = [
                o if str(r) == "nan" else "Aucune place"
                for o, r in cap_worst_hr[["occ", "restrictions"]].values
            ]

            f_occup.occupancy_map(
                occ_df=occ_worst_hour,
                cols=["occ_worst_hour"],
                delims=vis_delim,
                savepath=path,
                basename=self.config.num_proj,
                add_cat_prc=add_cat_prc,
                anotate=anotate_occ,
                rotation=self.config.vis_rotation,
                fig_buffer=self.config.vis_buffer,
                compass_rose=compass_rose,
                capacity_df=cap_worst_hr if anotate_cap else None,
                leg_dpi=map_leg_dpi_kwargs.get("leg_dpi", None),
                map_dpi=map_leg_dpi_kwargs.get("map_dpi", None),
            )

        # Reassignement modelization
        if self.config.act_report:
            logger.info("plotting report")
            path = os.path.join(self.save_path, "report")
            os.makedirs(path, exist_ok=True)

            f_report.veh_reassignement_plot(
                self.res["df_report"],
                self.res["roads_id_report"],
                path,
                separe_plots=True,
            )
            f_report.veh_reassignement_plot(
                self.res["df_report"],
                self.res["roads_id_report"],
                path,
                separe_plots=False,
            )

        # Parking time
        if self.config.act_rempla:
            path = os.path.join(self.save_path, "rempla")
            os.makedirs(path, exist_ok=True)

            logger.info("plotting rempla")

            f_rempla.park_time_hist_plot(
                data=self.res["parking_time"],
                savepath=path,
                fig_base_name=self.config.num_proj,
                **fig_dpi_kwargs,
            )

            street = self.config.report_street_name
            if isinstance(street, str):
                street = [street]
            principal = self.datastore.roadsdb[
                self.datastore.roadsdb[constants.ROAD_NAME].isin(street)
            ].segment.values
            others = self.datastore.roadsdb[
                ~self.datastore.roadsdb[constants.ROAD_NAME].isin(street)
            ].segment.values

            numeric_cuts = {"Inf. à 2h": 2, "Entre 2h et 5h": 5, "Sup. à 5h": 24}

            occ_ts_rempla = self.res["occ_timeslot"].copy()
            # TODO: Decide which type of weight to put
            # occ_ts_rempla['weight'] = 1  # rm line to have capacity as weight

            idx_, y1_, y2_, y3_ = f_rempla.prepare_data_buterfly_plot(
                self.res["parking_time"][
                    self.res["parking_time"][constants.SEGMENT].isin(principal)
                ],
                occ_ts_rempla,
                numeric_cuts_rempla=numeric_cuts,
                handle_undetermined={
                    "undetermined": ["Inf. à 2h"],
                    "merged": ["Sup. à 5h"],
                },
            )
            fig = f_rempla.buterfly_parking_time_plot(
                idx_,
                y2_,
                y1_,
                y3_,
                title="Intensité de l'utilisation de l'espace de "
                + "stationnement selon la durée sur "
                + f'{", ".join(street)}',
            )
            fig.savefig(
                path
                + f"/{self.config.num_proj}"
                + "_categorisation_du_stationement_principale.png"
            )

            idx_, y1_, y2_, y3_ = f_rempla.prepare_data_buterfly_plot(
                self.res["parking_time"][
                    self.res["parking_time"][constants.SEGMENT].isin(others)
                ],
                occ_ts_rempla,
                numeric_cuts_rempla=numeric_cuts,
                handle_undetermined={
                    "undetermined": ["Inf. à 2h"],
                    "merged": ["Sup. à 5h"],
                },
            )
            fig = f_rempla.buterfly_parking_time_plot(
                idx_,
                y2_,
                y1_,
                y3_,
                title="Intensité de l'utilisation de l'espace de "
                + "stationnement selon la durée sur les rues adjacentes",
            )
            fig.savefig(
                path
                + f"/{self.config.num_proj}"
                + "_categorisation_du_stationement_adjacentes.png"
            )

        if self.config.act_prov:
            raise NotImplementedError(
                "Provenance has not been implemented since SAAQ does not"
                + "provide plates habitation"
            )

    def _save_file(self):
        new_line = "\n"
        # save base stats
        for name, data in self.res.items():
            if isinstance(data, (dict, list)):
                with open(
                    os.path.join(self.save_path, name + ".txt"), "w+", encoding="utf-8"
                ) as f:
                    f.write(str(data))
            elif isinstance(data, gpd.GeoDataFrame):
                data.to_file(
                    os.path.join(self.save_path, name + ".geojson"),
                    encoding="utf-8-sig",
                    driver="GeoJSON",
                )
            elif isinstance(data, pd.DataFrame):
                data = data.copy()

                if data.empty:
                    continue

                if constants.SEG_DB_GIS in data.columns:
                    data.drop(columns=constants.SEG_DB_GIS, inplace=True)

                sv_index = False
                if (data.index.name and data.index.name != "index") or (
                    data.index.names and data.index.names != "index"
                ):
                    sv_index = True

                data.to_csv(
                    os.path.join(self.save_path, name + ".csv"),
                    index=sv_index,
                    encoding="utf-8-sig",
                )

                # write some variable description file
                with open(
                    os.path.join(self.save_path, "var_help.txt"), "w", encoding="utf-8"
                ) as file:
                    file.write(
                        "SIDE_OF_STREET:"
                        + new_line
                        + new_line
                        + constants.SIDE_OF_STREET_INFO
                        + new_line
                    )
                    file.write(new_line)
                    file.write(
                        "OCCUPATION:"
                        + new_line
                        + new_line
                        + constants.OCCUPATION_INFO
                        + new_line
                    )

    def _save_postgres(self):
        result = pd.DataFrame(
            data=[],
            columns=[
                "result_name",
                "result_type",
                "result_period",
                "json_result",
                "fk_runs_id",
                "fk_config_id",
            ],
        )

        def append_result(df, new_row):
            df.loc[-1] = new_row
            df.index = df.index + 1
            df = df.sort_index()

        period = os.path.split(self.save_path)[-1]

        for name, data in self.res.items():
            if isinstance(data, (dict, list)):
                if data is None:
                    continue
                result_type = "json"
                json_result = data  # json.dumps(data)
            elif isinstance(data, gpd.GeoDataFrame | pd.DataFrame):
                if data.empty:
                    continue
                if data.index.name != "index":
                    data = data.reset_index()

                result_type = str(type(data))
                data = data.fillna("None")
                # easy handle non json data type
                json_result = json.loads(
                    json.dumps(data.to_dict(), default=str, sort_keys=True)
                )
            else:
                result_type = "not supported"
                json_result = {"data": str(data)}

            new_row = [
                name,
                result_type,
                period,
                json_result,
                self.run_id,
                self.conf_id,
            ]
            append_result(result, new_row)

        engine = get_engine(**STAGING_DATABASE)
        # Create tables
        Base.metadata.create_all(bind=engine)

        with Session(engine).begin() as db:
            try:
                result.to_sql(
                    name="results",
                    schema="lapin",
                    con=db.session.bind,
                    index=False,
                    dtype={"json_result": JSONB()},
                    if_exists="append",
                )
                db.commit()
            except Exception as e:
                db.rollback()
                raise e

    def save(self):
        """Save all data computed in the analysis.

        Parameters
        ----------
        enrich_with_sector_names: Boolean (Default: True)
            Add the sector name to the saved data if True.
        """
        logger.info("saving analysis results")

        if self.db_load:
            self._save_postgres()
        else:
            self._save_file()

    def launch(self, **kwargs) -> None | int:
        """Compute all the analysis defined in the analysis.

        Parameters
        ----------
        **kwargs:
            plotting parameters

        Returns
        -------
        None : Analysis perform without error
        -1 : Missing data for the analysis requested

        See Also
        --------
        lapin.scheduler.Scheduler.load_kpi_in_memory
        lapin.scheduler.Scheduler.plot
        lapin.scheduler.Scheduler.save
        """

        save_path = deepcopy(self.save_path)
        for days, hours in self.config.hour_bounds.items():
            for hour in hours:
                self.save_path = deepcopy(save_path)
                self.save_path = os.path.join(
                    self.save_path, f"{days}_{hour['from']}_a_{hour['to']}"
                )
                logger.info(
                    "launching computation for %s: %s to %s",
                    days,
                    hour["from"],
                    hour["to"],
                )
                os.makedirs(self.save_path, exist_ok=True)

                self.load_kpi_in_memory(
                    days, hour_from=hour["from"], hour_to=hour["to"]
                )
                self.plot(**kwargs)
                self.save()
                self.clear_result_memory()

        # reset save_path
        self.save_path = deepcopy(save_path)

        # load figs to s3
        if self.db_load:
            root_folder = f"{self.config.num_proj}-run-{self.run_id}"
            load_images_directory(
                dir_path=save_path, bucket="lapinfigs", root_folder=root_folder
            )

    def _base(self, days: str, hour_from: str, hour_to: str):
        """Compute base statistics on the data."""
        stats = self.study.number_of_vehicules_scanned(
            days=days, timeslot_beg=hour_from, timeslot_end=hour_to
        )

        return stats

    def _capa(self):

        cap = pd.DataFrame(
            index=pd.MultiIndex.from_tuples([], names=["jours", "heures", "secteur"])
        )
        for days, times in constants.CAP_DAYS_HOUR_TO_COMPUTE.items():
            hours = times["from"]
            ends = times["to"]
            steps = float(times["step"])

            for day in parse_days(days):
                hour = Ctime.from_string(hours)
                end = Ctime.from_string(ends)
                step = Ctime.from_declared_times(hours=steps)

                while hour <= end:
                    res_h = self.datastore.restriction_handler
                    capacity = res_h.get_capacity(
                        hour=hour.as_datetime(), day=DAYS[day], as_dataframe=True
                    )
                    hour += step

                    capacity = capacity.join(
                        other=self.datastore.roads_by_sectors.set_index(
                            [constants.SEGMENT, constants.SIDE_OF_STREET]
                        )[constants.SECTEUR_NAME],
                        on=[constants.SEGMENT, constants.SIDE_OF_STREET],
                    )
                    grouped = capacity.groupby(constants.SECTEUR_NAME)
                    for secteur, secteur_capa in grouped:
                        cap.loc[
                            (
                                DAYS_MAP[day],
                                hour.as_string(string_format="hhmm"),
                                secteur,
                            ),
                            "capacity",
                        ] = secteur_capa.nb_places_total.fillna(0).sum()

        cap = cap.reset_index().pivot_table(
            index=["jours", "heures"], columns="secteur"
        )
        cap = cap.droplevel(0, axis=1)

        return cap

    def _occup(self, days, hour_from, hour_to):
        """Compute occupancy the data and config passed to the Analyser

        Returns
        -------
        occh : geopandas.GeoDataFrame
            Aggregated occupancy by hour
        occts : pandas.DataFram
            Aggregated occupancy by timeslot
        """

        # Parse the hours bounds and compute for each day-hour the occupancy.
        # After computing multiple occupancy, aggregate it.

        (occ_h, veh_sighted, capacities, restrictions) = (
            self.study.occupancy_time_aggregation(
                days=days,
                timeslot_beg=hour_from,
                timeslot_end=hour_to,
                freq=self.config.analyse_freq,
            )
        )
        # occupancy timeslot
        occ_t, _, cap_t, _ = self.study.occupancy_time_aggregation(
            days=days,
            timeslot_beg=hour_from,
            timeslot_end=hour_to,
            freq=None,
        )
        # occ_t = occ_t.melt(
        #     id_vars=[
        #         constants.SEGMENT,
        #         constants.SIDE_OF_STREET,
        #         'days'
        #     ],
        #     value_name='occ',
        #     var_name='time_interval'
        # )

        if occ_h.empty:
            return None, None, None, None

        occ_h = prepare_data_before_export(
            occ_h,
            self.study.street_geometry,
            capacities,
            zero_weight_replace="Aucune place",
        )
        occ_ts = prepare_data_before_export(
            occ_t, self.study.street_geometry, cap_t, zero_weight_replace="Aucune place"
        )
        occ_ts.columns = ["mean_occ", "geometry"]
        occ_ts = occ_ts.join(
            other=cap_t.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])
        )
        occ_ts.columns = ["mean_occ", "geometry", "weight"]
        occ_ts.loc[occ_ts.weight.isna(), "weight"] = 0

        veh_sighted = prepare_data_before_export(
            veh_sighted,
            self.study.street_geometry,
            capacities,
            zero_weight_replace="Aucune place",
        )
        capacities = prepare_data_before_export(
            capacities,
            self.study.street_geometry,
        )
        restrictions = prepare_data_before_export(
            restrictions,
            self.study.street_geometry,
        )

        return occ_h, occ_ts, veh_sighted, capacities, restrictions

    def _occup_agg(self, days: str, hour_from: str, hour_to: str):
        """Compute the aggregated occupancy for all sector defined in config
        file.

        Paramters
        ---------
        occupancy : pandas.DataFrame
            Mean occupancy of parking spot observed by side of street

        veh_sighted : pandas.DataFrame
            Mean number of vehicules observed by side of street

        capacities : pandas.DataFrame
            Capacity by side_of_street.
        """

        occ = self.study.occupancy_by_regions(
            regions=self.datastore.regions,
            days=days,
            timeslot_beg=hour_from,
            timeslot_end=hour_to,
            freq=self.config.analyse_freq,
        )

        return occ

    def _rempla(self, days: str, hour_from: str, hour_to: str):
        """Basic remplacement calculation function.

        Parameters
        ----------
        handle_restriction: Boolean (Default: True).
            Do we remove from dataset all unpermited parked vehicule f
            orm data ?

        Returns
        -------
        rempla: Parking time computation for each parking instance.
        """
        rempl = self.study.parking_time(
            days=days, timeslot_beg=hour_from, timeslot_end=hour_to
        )
        return rempl

    def _prov(self):
        """Compute provenance of car in the data by the config passed
        to the Analyser.

        Parameters
        ----------
        handle_restriction : boolean
            Do we clean lapi lecture that are present on a restricted road ?

        Returns
        -------
        prov_by_reg : geopandas.GeoDataFrame
            Aggregated provenance by regions
        """
        raise NotImplementedError(
            "This has not been refactored since SAAQ stopped" + "giving us data"
        )
