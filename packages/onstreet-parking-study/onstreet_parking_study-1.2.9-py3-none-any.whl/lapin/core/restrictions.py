"""
Engine for restrictions

@author: alaurent
@author: lgauthier
"""

import copy
import datetime
import itertools
import locale
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import ClassVar
from typing import Tuple, List

import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
import shapely
from shapely.ops import transform
from numpy.lib import recfunctions as rfn

from . import LprDataFrame
from ..tools.ctime import Ctime
from .. import constants
from ..tools.utils import parse_days

logger = logging.getLogger(__name__)

INTERDICTION_MAPPING = {
    "Entrée Charretière": "Aucune place",
    "Entrée Charettière": "Aucune place",
    "Borne fontaine": "Aucune place",
    "Arrêt de bus": "Aucune place",
    "Premier/Dernier 5m": "Aucune place",
    "Interdiction": "Aucune place",
    "Entretien": "Aucune place",
    "Non parcourue": "Non parcourue",
    "Traverse piétonne": "Aucune place",
    "Taxi": "Aucune place",
    "SPVM": "Aucune place",
    "Livraison": "Aucune place",
}

DFLT_CLEANING_FROM = datetime.datetime(year=1999, month=4, day=1)
DFLT_CLEANING_TO = datetime.datetime(year=1999, month=12, day=1)

NULL_REG = {
    "deb": 0.0,
    "fin": 0.0,
    "res_date_debut ": np.nan,
    "res_date_fin": np.nan,
    "res_days": np.nan,
    "res_hour_from": np.nan,
    "res_hour_to": np.nan,
    "res_type": "Non parcourue",
    "restrictions": "Non parcourue",
    "longueur_non_marquée": 0.0,
    "nb_places_total": 0,
}


def crs_reproject(
    shape: shapely.Geometry, from_crs: str, to_crs: str
) -> shapely.Geometry:
    """project a Shapely shape from a crs to another

    Parameters
    ----------
    shape: shapely.Geometry
        The geometry to convert
    origin_crs: value
        Coordinate Reference System of the geometry objects. Can be anything
        accepted by :meth:`pyproj.CRS.from_user_input()
        <pyproj.crs.CRS.from_user_input>`, such as an authority string
        (eg "EPSG:4326") or a WKT string.
    destination_crs: value
        Coordinate Reference System of to project the geometry objects. Can be
        anything accepted by :meth:`pyproj.CRS.from_user_input()
        <pyproj.crs.CRS.from_user_input>`, such as an authority string (eg.
        "EPSG:4326") or a WKT string.
    """
    dest_crs = pyproj.CRS(to_crs)
    orig_crs = pyproj.CRS(from_crs)
    projection = pyproj.Transformer.from_crs(
        orig_crs, dest_crs, always_xy=True
    ).transform
    t_pt = transform(projection, shape)

    return t_pt


def compute_lr_double_over_simple(
    geom: shapely.LineString,
    geom_lr: list,
    m_start: float,
    m_end: float,
    total_length: float,
) -> Tuple[float, float, float]:
    """Apply a Linear Referencing done on the curb to the filament
    representation of the road network.

    Parameters
    ----------
    geom: shapely.LineString
        filament vector of the road expressed in latitude and longitude.
        Must be in 'epsg:4326'
    geom_lr: list
        First and Last point of the line on the goebase double.
    m_start: float
        Linear reference of the start point on the geobase double.
    m_end: float
        Linear reference of the end point on the geobase double.
    total_length: float
        Length of the geobase double segment

    Returns
    -------
    Typle
        First point as LR, last point as LR, segment size.
    """

    geom = crs_reproject(geom, from_crs="epsg:4326", to_crs="epsg:32188")

    if abs(m_end - m_start) == total_length:
        return (0, geom.length, geom.length)

    assert len(geom_lr) == 2, "Linear referenced vector must be of size 2"

    pt_start, pt_end = geom_lr
    pt_start = crs_reproject(pt_start, from_crs="epsg:4326", to_crs="epsg:32188")
    pt_end = crs_reproject(pt_end, from_crs="epsg:4326", to_crs="epsg:32188")

    # Here the idea is to cope for regulation that should go to the end of
    # the troncon but don't because of user inputs. So if the start/end is
    # less than the size of a vehicle we extend it.
    perc = np.round((constants.VEH_SIZE - 1) / total_length, 2)
    if m_start <= 0 + total_length * perc:
        return 0, geom.project(pt_end), geom.length
    if m_end >= total_length - total_length * perc:
        return geom.project(pt_start), geom.length, geom.length

    return geom.project(pt_start), geom.project(pt_end), geom.length


def overlaping_intervals(intervals: np.array) -> list[Tuple[int, int, float]]:
    """Does interval overlaps

    Parameters
    ----------
    intervals : np.array | list[tuple[flaot, float]]
        Intervals

    Returns
    -------
    Tuple[bool, np.array]
        Are interval orverlapping
    """
    overlaps = []
    i = j = 0
    for curr_beg, curr_end in intervals:
        j = 0
        for beg, end in intervals:
            if i == j:
                continue
            if curr_beg < end and curr_end > beg:
                overlap = [i, j, min(curr_end - beg, end - curr_beg)]
                if [overlap[1], overlap[0], overlap[2]] in overlaps:
                    continue
                overlaps.append(overlap)
            j += 1
        i += 1

    return overlaps


def _is_on_hour_interval(
    hour_from: str, hour_to: str, timestamp: datetime.datetime
) -> bool:
    """Check if datetime of the collected point is on the interval of
    the regulation.

    Parameters
    ----------
    hour_from : string
        Starting hour interval in string format e.g.: "00:00"
    hour_to : string
        Ending hour interval in string format e.g.: "15:00"
    datetime : datetime.datetime
        Time to check.

    Returns
    -------
    b : boolean
        True if datime between interval, False otherwise.
    """
    if pd.isna(hour_from) and pd.isna(hour_to):
        return True

    hour_from = Ctime.from_string(hour_from)
    hour_to = Ctime.from_string(hour_to)
    time = Ctime.from_declared_times(
        hours=timestamp.hour, minutes=timestamp.minute, seconds=timestamp.second
    )

    return hour_from <= time <= hour_to


def _is_on_day_interval(
    days: str, timestamp: datetime.date | datetime.datetime
) -> bool:
    """Check if datetime of the collected point is on the day
    interval.

    Parameters
    ----------
    days : string
        Day of regulation, it's exprimed as the first three letter
        of french days and "+" and "-" operator.

        Example : "lun-jeu" means from monday (lundi) to thursday (jeudi).
                  "lun+jeu" means monday (lundi) and thursday (jeudi).
    datetime : datetime.datetime
       Date to check

    Returns
    -------
    b : boolean
        True if datetime in days, False otherwise.
    """
    if pd.isna(days):
        return True
    return timestamp.weekday() in parse_days(days)


def _is_on_cleaning_period(
    date: datetime.date, cleaning_from: datetime.date, cleaning_to: datetime.date
) -> bool:

    if pd.isna(cleaning_from) or pd.isna(cleaning_to):
        return True

    if isinstance(date, datetime.datetime):
        date = date.date()

    cleaning_from = cleaning_from.replace(year=date.year)
    cleaning_to = cleaning_to.replace(year=date.year)

    return cleaning_from <= date <= cleaning_to


SideOfStreet = Enum(
    value="SideOfStreet",
    names=[("LEFT", -1), ("RIGHT", 1), ("BOTH_SIDE", 0)],
)


@dataclass
class PeriodNull(object):
    """Null period"""

    _instance = None

    def _null_eq(self, *args):
        """
        Custom equality function that returns True for itself and None, and
        False for everything else
        """
        if args[0] is None:
            return True
        elif isinstance(args[0], PeriodNull):
            return True
        return False

    def _null(self):
        """
        Custom internal function to return None for most behaviors when
        checking the results of additions, substractions, ect.
        """
        return None

    __eq__ = __ne__ = __ge__ = __gt__ = __le__ = __lt__ = _null_eq
    __add__ = __iadd__ = __radd__ = _null
    __sub__ = __isub__ = __rsub__ = _null
    __mul__ = __imul__ = __rmul__ = _null
    __div__ = __idiv__ = __rdiv__ = _null
    __mod__ = __imod__ = __rmod__ = _null
    __pow__ = __ipow__ = __rpow__ = _null
    __and__ = __iand__ = __rand__ = _null
    __xor__ = __ixor__ = __rxor__ = _null
    __or__ = __ior__ = __ror__ = _null
    __truediv__ = __itruediv__ = __rtruediv__ = _null
    __floordiv__ = __ifloordiv__ = __rfloordiv__ = _null
    __lshift__ = __ilshift__ = __rlshift__ = _null
    __rshift__ = __irshift__ = __rrshift__ = _null
    __neg__ = __pos__ = __abs__ = __invert__ = _null
    __call__ = __getattr__ = _null
    __getitem__ = _null

    def __divmod__(self, other):
        """
        Divmod needs to return two anwsers so cannot be included in _null.
        """
        return self, self

    __rdivmod__ = __divmod__

    __hash__ = None

    def __new__(cls, *args, **kwargs):
        if PeriodNull._instance is None:
            PeriodNull._instance = object.__new__(cls, *args, **kwargs)
        return PeriodNull._instance

    def __bool__(self):
        return False

    def __repr__(self):
        return "<PeriodNull>"

    def __setattr__(self, index, value):
        return None

    def __setitem___(self):
        return None

    def __str__(self):
        return ""


perioddt = np.dtype(
    [
        ("start_time", "datetime64[s]"),
        ("end_time", "datetime64[s]"),
        ("days", np.unicode_, 27),
        ("max_duration", np.int64),
        ("start_date", "datetime64[D]"),
        ("end_date", "datetime64[D]"),
    ]
)


@dataclass
class Period:
    """Handle period"""

    start_time: Ctime = None
    end_time: Ctime = None
    days: str = None
    max_duration: int = None
    start_date: datetime.date = None
    end_date: datetime.date = None

    def __init__(
        self,
        start_time: Ctime = None,
        end_time: Ctime = None,
        days: str = None,
        max_duration: int = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> None:

        if not (start_date or days or start_time):
            self._period = PeriodNull
        else:
            self._period = Period

        self.start_time = start_time
        self.end_time = end_time
        self.days = days if days else None
        self.max_duration = max_duration
        self.start_date = start_date
        self.end_date = end_date

        self.__post_init__()

    def __post_init__(self):
        if (
            self.start_time
            and self.start_time.hhmm == 0
            and self.end_time
            and self.end_time.hhmm == 2359
        ):
            self.start_time = None
            self.end_time = None

        if self.days and (
            self.days == "lun+mar+mer+jeu+ven+sam+dim" or self.days == "lun-ven"
        ):
            self.days = None

        if (
            self.start_date
            and self.start_date.month == 1
            and self.start_date.day == 1
            and self.end_date
            and self.end_date.month == 12
            and self.end_date.day == 31
        ):
            self.start_date = None
            self.end_date = None

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame):
        """Create Period from dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            Period dataframe.

        Returns
        -------
        Period
            Instance of Period.
        """
        start_time = data.start_time
        end_time = data.end_time
        days = data.days
        max_duration = data.max_duration
        start_date = data.start_date
        end_date = data.end_date

        if start_time.year == 1970:
            start_time = None
            end_time = None
        else:
            start_time = Ctime.from_datetime(start_time)
            end_time = Ctime.from_datetime(end_time)

        if start_date.year == 1970:
            start_date = None
            end_date = None
        else:
            start_date = start_date.date()
            end_date = end_date.date()

        return cls(start_time, end_time, days, max_duration, start_date, end_date)

    @classmethod
    def from_json(cls, array: dict = None):
        """Create Period form json

        Parameters
        ----------
        array : dict
            Json of a Period

        Returns
        -------
        Period
            Period instance
        """
        if array is None:
            return cls()

        start_month = array.get("mois_debut", None)
        start_day = array.get("jour_debut", None)
        end_month = array.get("mois_fin", None)
        end_day = array.get("jour_fin", None)
        days = "+".join([j[:3] for j in array.get("jours", [])])
        start_time = array.get("heure_debut", None)
        end_time = array.get("heure_fin", None)
        max_stay = array.get("duree_maximale", None)

        time_interval = (None, None)
        if start_time and end_time:
            time_interval = (Ctime.from_string(start_time), Ctime.from_string(end_time))

        locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
        date_interval = (None, None)
        if start_month and end_month:
            date_interval = (
                datetime.datetime.strptime(
                    f"{start_month} {start_day}", "%B %d"
                ).date(),
                datetime.datetime.strptime(f"{end_month} {end_day}", "%B %d").date(),
            )

        return cls(*time_interval, days, max_stay, *date_interval)

    def has_day_regulation(self) -> bool:
        """
        Returns
        -------
        bool
            Period has day regulation
        """
        return bool(self.days)

    def has_date_regulation(self) -> bool:
        """
        Returns
        -------
        bool
            Period has date regulation
        """
        return bool(self.start_date) and bool(self.end_date)

    def has_time_regulation(self) -> bool:
        """
        Returns
        -------
        bool
            Period has time regulation
        """
        return bool(self.start_time) and bool(self.end_time)

    def has_max_duration_regulation(self) -> bool:
        """
        Returns
        -------
        bool
            Period has a max duration
        """
        return bool(self.max_duration)

    def is_empty(self) -> bool:
        """
        Returns
        -------
        bool
            Period is a NullPeriod
        """
        if isinstance(self._period, PeriodNull):
            return True
        return not (
            self.has_date_regulation()
            or self.has_time_regulation()
            or self.has_day_regulation()
        )

    def is_active_on(
        self, time: np.datetime64 | datetime.date | datetime.time = None
    ) -> bool:
        """Is period active at given time

        Parameters
        ----------
        time : np.datetime64 | datetime.date | datetime.time, optional
            Time to check if the regulation is active, default None. If
            None, then it's check if it's always on.

        Returns
        -------
        bool
            Period is active at given time
        """
        if self.is_empty():
            return True
        if not time:
            return False

        res = True
        if isinstance(time, datetime.time):
            # day should be empy
            res = res and not self.has_date_regulation()
            time = datetime.datetime.combine(datetime.date(1970, 1, 1), time)
            if self.has_time_regulation():
                res = res and _is_on_hour_interval(
                    hour_from=self.start_time.as_string(),
                    hour_to=self.end_time.as_string(),
                    timestamp=time,
                )
        elif isinstance(time, datetime.date) and not isinstance(
            time, datetime.datetime
        ):
            # time should be empty
            res = res and not self.has_time_regulation()
            if self.has_date_regulation():
                res = res and _is_on_cleaning_period(
                    time, self.start_date, self.end_date
                )
            res = res and _is_on_day_interval(self.days, time)

        else:
            # date and hour should be checked
            if self.has_date_regulation():
                res = res and _is_on_cleaning_period(
                    time, self.start_date, self.end_date
                )
            if self.has_day_regulation():
                res = res and _is_on_day_interval(self.days, time)
            if self.has_time_regulation():
                res = res and _is_on_hour_interval(
                    hour_from=self.start_time.as_string(),
                    hour_to=self.end_time.as_string(),
                    timestamp=time,
                )

        return res

    def __key(self):
        if self.is_empty():
            return (None, None, None, None, None, None)
        return (
            (
                self.start_time.as_datetime(time_only=False)
                if self.start_time
                else datetime.datetime(1970, 1, 1, 0, 0, 0)
            ),
            (
                self.end_time.as_datetime(time_only=False)
                if self.start_time
                else datetime.datetime(1970, 1, 1, 0, 0, 0)
            ),
            self.days if self.days else "",
            self.max_duration if self.max_duration else -1,
            self.start_date if self.start_date else datetime.datetime(1970, 1, 1),
            self.end_date if self.start_date else datetime.datetime(1970, 1, 1),
        )

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if isinstance(other, Period):
            return self.__key() == other.__key()

        return NotImplemented

    def __lt__(self, other):
        if self.start_time == other.start_time:
            return self.end_time < other.end_time

        return self.start_time < other.start_time

    def __data__(self):
        if self.is_empty():
            arr = np.empty(1, dtype=perioddt)
            arr["max_duration"] = -1
            return arr

        return np.array(self.__key(), dtype=perioddt)

    def as_numpy(self):
        """Numpy representation.

        Returns
        -------
        perioddt
            Period as numpy.
        """
        return self.__data__()


locationdt = np.dtype([("loc_start", np.float64), ("loc_end", np.float64)])


@dataclass
class Location:
    """Location class"""

    start: np.float64 = np.nan
    end: np.float64 = np.nan

    def is_on(self, pos: np.float64) -> bool:
        """Check if position on location.

        Parameters
        ----------
        seg_beg : float
            Start position of the segment regulation on the road.
        seg_end : float
            End position of the segment regulation on the road.
        position : float
            Position we want to check.

        Returns
        -------
        b : bool
            True if position on segment, False otherwise

        Example
        -------

        beg   pos   end
        --|-----@-----|-----   -> Return True

        beg         end pos
        --|-----------|---@-   -> Return False

        """
        # length is covering the whole thing
        if self.start == np.nan and self.end == np.nan:
            return True
        # length is not covering the whole thing and position is Null
        if pos is None:
            return True

        return self.start <= pos <= self.end

    def __key(self):
        return (self.start, self.end)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.start == other.start and self.end == other.end

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Location):
            if self.start == other.start:
                return self.end < other.end
            return self.start < other.start

        return NotImplemented

    def __data__(self):
        return [self.start, self.end]

    def as_numpy(self):
        """Return numpy representation

        Returns
        -------
        loactiondt
            Numpy object
        """
        return np.array(self.__key(), dtype=locationdt)


regulationdt = np.dtype([("name", np.unicode_, 50), ("period", perioddt)])


@dataclass(init=True)
class Regulation:
    """Regulation class"""

    priority: ClassVar[list[str]] = constants.CAP_PRIORITY
    name: str = "Non parcourue"
    period: Period = Period()
    _attributes: dict = None
    _priority: int = np.inf

    def __post_init__(self):
        try:
            self._priority = self.priority.index(self.name)
        except ValueError:
            self._priority = np.inf

    def is_active(self, time: np.datetime64 = None) -> bool:
        """_summary_

        Parameters
        ----------
        position : np.float64
            _description_
        time : np.datetime64
            _description_

        Returns
        -------
        bool
            _description_
        """
        return self.period.is_active_on(time)

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame):
        """Create Regulation from dataframe

        Parameters
        ----------
        data : pandas.DataFrame
            DataFrame containing Regulation

        Returns
        -------
        Regulation
        """
        data = data.copy()
        data = data.fillna(np.nan).replace([np.nan], [None])
        name = data["name"]
        if name == "":
            name = None

        period = Period.from_dataframe(data)

        if name is None and period.is_empty():
            return

        return cls(name=name, period=period)

    @classmethod
    def from_json(cls, regulation: dict):
        """Create Regulation from JSON

        Parameters
        ----------
        regulation : dict
            JSON representation of Regulation

        Returns
        -------
        Regulation
        """

        name = regulation["type"]
        periods = Period.from_json(regulation)
        attributes = {
            "zone": regulation.get("zone", np.nan),
            "res_max_stay": regulation.get("duree_maximale", np.nan),
        }

        return cls(name, periods, attributes)

    def __key(self):
        return (self.name, self.period, self._attributes)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if isinstance(other, Regulation):
            return self.__key() == other.__key()

        return NotImplemented

    def __lt__(self, other):
        return self._priority < other._priority

    def __data__(self):
        return np.array((self.name, self.period.as_numpy()), dtype=regulationdt)

    def as_numpy(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        data = self.__data__()
        return np.array(data, dtype=regulationdt)


divisiondt = np.dtype(
    [("location", locationdt), ("regulation", regulationdt), ("spot_number", np.int64)]
)


@dataclass(init=True)
class SegmentDivision:
    """SegmentDivision class. This a CDS base."""

    location: Location = Location()
    regulations: list[Regulation] = field(default_factory=list)
    spot_number: int = -1
    _size: np.float64 = field(init=False)
    _veh_size: ClassVar[float] = constants.VEH_SIZE
    _is_sorted_reg: bool = False

    def __post_init__(self):
        self._size = self.location.end - self.location.start
        self.regulations = sorted(self.regulations)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if isinstance(other, SegmentDivision):
            return (
                self.location == other.location
                and self.spot_number == other.spot_number
            )

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SegmentDivision):
            return self.location < other.location

        return NotImplemented

    def __data__(self):
        locs = self.location.as_numpy()
        regls = np.array(
            [reg.as_numpy() for reg in self.regulations], dtype=regulationdt
        )

        if regls.size < 1:
            empty_div = np.empty(1, dtype=divisiondt)
            empty_div["location"] = locs
            empty_div["spot_number"] = self.spot_number
            empty_div["regulation"]["period"]["max_duration"] = -1
            return empty_div

        locs_padd = list(itertools.repeat(locs, regls.size))
        spot_padd = list(itertools.repeat(self.spot_number, regls.size))

        return np.rec.fromarrays((locs_padd, regls, spot_padd), dtype=divisiondt)

    @property
    def size(self) -> float:
        """Size of the division.

        Returns
        -------
        float
        """
        return self._size

    @size.setter
    def size(self, size: float) -> None:
        self._size = size

    @property
    def veh_size(self) -> float:
        """Vehicule size on this division.

        Returns
        -------
        float
        """
        return self._veh_size

    @veh_size.setter
    def veh_size(self, veh_size: float) -> None:
        self._veh_size = veh_size

    def is_empty(self) -> bool:
        """True if the SegmentDivision is empty
        Returns
        -------
        bool
        """
        if not self.regulations:
            return True

        return False

    def has_regulations(self) -> bool:
        """
        Returns True if the segment has at least one regulation, False
        otherwise.
        """
        return bool(self.regulations)

    def point_is_on(self, position: np.float64) -> bool:
        """True if position on the division.

        Parameters
        ----------
        position : np.float64
            Linear reference of the point on the segment line where
            SegmentDivision is defined.

        Returns
        -------
        bool
        """
        return self.location.is_on(position)

    def _sort_reg(self):
        if not self._is_sorted_reg:
            self.regulations = sorted(self.regulations)

    def get_active_reg(
        self, time: np.datetime64 = None, ignore_reg: list[str] | None = None
    ) -> Regulation:
        """Return the active regulation at given time. If several regulations
        are active at the same time, sort by priority.

        Parameters
        ----------
        time : np.datetime64, optional
            Given time, by default None
        ignore_regs: list, optional
            Regulation to ignore, by default None

        Returns
        -------
        Regulation
            Active regulation
        """
        if not ignore_reg:
            ignore_reg = []

        self._sort_reg()
        regs_active = [
            reg.is_active(time) if reg.name not in ignore_reg else False
            for reg in self.regulations
        ]

        if not any(regs_active):
            return None

        return self.regulations[np.argmax(regs_active)]

    def is_restriction_on_div(self, time: np.datetime64 = None) -> bool:
        """True if there is an active regulation at given time.

        Parameters
        ----------
        time : np.datetime64, optional
            Given time, by default None.

        Returns
        -------
        bool
        """
        self._sort_reg()
        regs_active = [reg.is_active(time) for reg in self.regulations]

        if regs_active:
            return regs_active[np.argmax(regs_active)]

        return False

    def get_capacity(self, time: np.datetime64 = None) -> float:
        """Return the capacity of the division at given time.

        Parameters
        ----------
        time : np.datetime64, optional
            Given time, by default None.

        Returns
        -------
        float
            Capacity of the division.
        """
        if self.is_restriction_on_div(time=time):
            return 0

        if self.spot_number > -1:
            return self.spot_number

        self._size = self.location.end - self.location.start
        return np.round(self._size / self._veh_size)

    def finalize(
        self,
        veh_size: float = None,
        regulation_ignored: list[str] = None,
        seg_beg: float = None,
        seg_end: float = None,
    ):
        """After initializatio, make sure all information are coherent.

        Parameters
        ----------
        veh_size : float, optional
            size of the vehicule on this division, by default None.
        regulation_ignored : list[str], optional
            Regulation that should not be taken into account, by default None.
        seg_beg: float, optional
            Start of the Division on the segment, by default None.
        seg_end: float, optional
            End of the Division on the segment, by default None.
        """

        if veh_size:
            self.veh_size = veh_size
        else:
            self.veh_size = constants.VEH_SIZE
        if regulation_ignored:
            regs = [
                reg for reg in self.regulations if reg.name not in regulation_ignored
            ]
            self.regulations = sorted(regs)

        if pd.isna(self.location.start):
            self.location.start = seg_beg
        if pd.isna(self.location.end):
            self.location.end = seg_end

        self._size = self.location.end - self.location.start

    def as_numpy(self):
        """Representation of the Divison as numpy

        Returns
        -------
        segmentdivisiondt
        """
        return self.__data__()

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame):
        """Create a Division by dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame representaion of the Division.

        Returns
        -------
        SegmentDivsion
        """

        start = data.iloc[0].loc_start
        end = data.iloc[0].loc_end
        restrictions = data.apply(Regulation.from_dataframe, axis=1).to_list()
        restrictions = [res for res in restrictions if res]
        spot_number = data.iloc[0].spot_number

        return cls(Location(start, end), restrictions, spot_number)

    @classmethod
    def from_json(cls, regulation: dict):
        """Create a Division by JSON

        Parameters
        ----------
        regulation : dict
            JSON representation of the Division

        Returns
        -------
        SegmentDivision
        """
        # firt point
        pt_reg_start = shapely.Point(regulation["geometry"]["coordinates"][0])
        # last point
        pt_reg_end = shapely.Point(regulation["geometry"]["coordinates"][-1])
        # geometry line
        road_geom = regulation["street_geom"]

        # linear referencing
        if regulation["properties"]["realStart"] > regulation["properties"]["realEnd"]:
            # regulation is reversed
            start_loc, end_loc, _ = compute_lr_double_over_simple(
                road_geom,
                [pt_reg_start, pt_reg_end],
                regulation["properties"]["realEnd"],
                regulation["properties"]["realStart"],
                regulation["properties"]["parentLength"],
            )
        else:
            start_loc, end_loc, _ = compute_lr_double_over_simple(
                road_geom,
                [pt_reg_start, pt_reg_end],
                regulation["properties"]["realStart"],
                regulation["properties"]["realEnd"],
                regulation["properties"]["parentLength"],
            )

        # handle permanent restrictions
        definition = regulation["properties"]["definition"]
        if definition["interdiction_complete"]:
            res_type = definition.get("type_interdiction", "Interdiction")
            res_type = "Interdiction" if not res_type else res_type
            definition["restrictions"].append({"type": res_type})

        location = Location(start_loc, end_loc)

        regulations = [Regulation.from_json(r) for r in definition["restrictions"]]
        # check if it's a complete interdiction
        extended_attributes = definition.get(
            "extended_attributes", {"number_of_pkaces": ""}
        )
        spot_number = extended_attributes.get("number_of_places", -1)
        spot_number = -1 if spot_number == "" else int(spot_number)

        return cls(location, regulations, spot_number)


def undo_overlap_segment_divisions(
    div1: SegmentDivision, div2: SegmentDivision
) -> Tuple[SegmentDivision, SegmentDivision, Tuple[str, str]]:
    """Reshape divison if they are overlaping.

    Parameters
    ----------
    div1 : SegmentDivision
        First division.
    div2 : SegmentDivision
        Second division.

    Returns
    -------
    Tuple[SegmentDivision, SegmentDivision]
        Divisions reshaped.
    """
    if div1 < div2:
        middle_ground = (div1.location.end + div2.location.start) / 2
        div1.location.end = middle_ground
        div2.location.start = middle_ground
        key = ("end", "start")
    else:
        middle_ground = (div2.location.end + div1.location.start) / 2
        div2.location.end = middle_ground
        div1.location.start = middle_ground
        key = ("start", "end")

    return div1, div2, key


def index_positions(divs: List[Tuple[float, float]]) -> dict[float, int]:
    """Create an index for the divisions by starting and ending point.

    Parameters
    ----------
    divs : List[Tuple[float, float]]
        Division start and end.

    Returns
    -------
    dict[float, int]
    """
    idx_div_position = {}
    for idx_div, (start, end) in enumerate(divs):
        try:
            idx_div_position[start].append(idx_div)
        except KeyError:
            idx_div_position[start] = [idx_div]
        try:
            idx_div_position[end].append(idx_div)
        except KeyError:
            idx_div_position[end] = [idx_div]

    return idx_div_position


def reshape_divisions(
    divs_pos: List[Tuple[float, float]], divisions: List[SegmentDivision]
) -> list[SegmentDivision]:
    """Reshape divisions if they overlap.

    Parameters
    ----------
    divs_pos : List[Tuple[float, float]]
        Poisition of each divisions
    divisions : List[SegmentDivision]
        List of the divisions to reshape

    Returns
    -------
    list[SegmentDivision]
        repashaped position

    Example
    -------
    TODO
    """
    indexed_positions = index_positions(divs_pos)
    divisions = np.array(divisions)

    all_positions = list(
        zip(
            sorted(indexed_positions.items())[:-1],
            sorted(indexed_positions.items())[1:],
        )
    )
    curr = []
    res = []
    for (start, idx_s), (end, _) in all_positions:
        still_going = [reg for reg in curr if reg not in idx_s]
        new_start = [reg for reg in idx_s if reg not in curr]

        if not (new_start or still_going):
            curr = still_going + new_start
            continue

        spot_number = max(div.spot_number for div in divisions[still_going + new_start])
        if spot_number > -1:
            active_regulations = list(
                {
                    reg
                    for div in divisions[still_going + new_start]
                    for reg in div.regulations
                    if div.spot_number > -1
                }
            )
        else:
            active_regulations = list(
                {
                    reg
                    for div in divisions[still_going + new_start]
                    for reg in div.regulations
                }
            )

        res.append(
            SegmentDivision(
                location=Location(start, end),
                regulations=active_regulations,
                spot_number=spot_number,
            )
        )

        curr = still_going + new_start

    return res


@dataclass
class Segment:
    """Street representation where division are present."""

    segment_id: int
    side_of_street: int
    divisions: list[SegmentDivision]
    geometry: shapely.LineString
    beg: np.float64 = field(init=False)
    end: np.float64 = field(init=False)
    _id: np.int64 = field(init=False)
    _veh_size: ClassVar[float] = constants.VEH_SIZE

    segmentdt: ClassVar[np.dtype] = np.dtype(
        [
            ("id", np.uint64),
            ("side_of_street", np.int64),
            ("div", divisiondt),
            ("geometry", shapely.LineString),
            ("seg_beg", np.int64),
            ("seg_end", np.int64),
        ]
    )

    def __post_init__(self):
        self.beg = 0
        self.end = crs_reproject(self.geometry, "epsg:4326", "epsg:32188").length
        self._id = self.segment_id * 10
        self._id += self.side_of_street if self.side_of_street >= 0 else 2

    def __lt__(self, other):
        return self._id < other._id

    def __add__(self, other):
        if not isinstance(other, Segment):
            raise NotImplementedError

        if not self.divisions:
            self.divisions = other.divisions
            return self

        if not other.divisions:
            return self

        # sort on both start and end
        list1 = self.divisions
        list2 = copy.deepcopy(other.divisions)
        list1 = sorted(list1)
        list2 = sorted(list2)
        curr = []
        while list1 and list2:
            if list1[0] < list2[0]:
                curr.append(list1.pop(0))
            elif list1[0] > list2[0]:
                curr.append(list2.pop(0))
            else:
                list1[0].regulations.extend(list2.pop(0).regulations)
                curr.append(list1.pop(0))

        if list1:
            curr.extend(list1)
        if list2:
            curr.extend(list2)

        self.divisions = curr

        return self

    def __eq__(self, other):
        return self._id == other._id

    def __data__(self):
        if len(self.divisions) > 0:
            divs = [div.as_numpy() for div in self.divisions]
            divs = np.concatenate(divs)
            nb_div = divs.size
            sid = list(itertools.repeat(self.segment_id, nb_div))
            side = list(itertools.repeat(self.side_of_street, nb_div))
            geom = list(itertools.repeat(self.geometry, nb_div))
            beg = list(itertools.repeat(self.beg, nb_div))
            end = list(itertools.repeat(self.end, nb_div))
            return np.rec.fromarrays(
                (sid, side, divs, geom, beg, end), dtype=self.segmentdt
            )

        return np.array(
            [
                (
                    self.segment_id,
                    self.side_of_street,
                    np.empty(1, dtype=divisiondt),
                    self.geometry,
                    self.beg,
                    self.end,
                )
            ],
            dtype=self.segmentdt,
        )

    @property
    def id(self):
        """Id of the segment

        Returns
        -------
        int
        """
        return self._id

    @property
    def veh_size(self) -> float:
        """Vehicule size used for this segment.

        Returns
        -------
        float
        """
        return self._veh_size

    @veh_size.setter
    def veh_size(self, veh_size: float) -> None:
        self._veh_size = veh_size

    def as_numpy(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        return self.__data__()

    def _assert_marked_div_do_not_overlap(self) -> None:
        """If division has a number of parking spot set (it is marked), then
        it should not be overlapped by any divisions.

        Raises
        ------
        ValueError
            Marked parking should not overlap
        ValueError
            Tryied to undo the overlapping and failed
        ValueError
            Tryied to undo the overlapping and failed
        """
        intervals = [
            [div.location.start, div.location.end]
            for div in self.divisions
            if div.spot_number > -1
        ]
        divisions_id = [
            i for i, div in enumerate(self.divisions) if div.spot_number > -1
        ]
        overlaps = overlaping_intervals(intervals)

        if not overlaps:
            return

        msg = "Marked parking spot divisions should not overlap."
        modified_div = []

        for id_div1, id_div2, dist in overlaps:
            msg += f"\n Divisions {divisions_id[id_div1]} and "
            msg += (
                f"{divisions_id[id_div2]} overlaps by {dist}"
                + f"on segment {self._id}."
            )
            if dist < 1:
                msg += " It has been corrected."

                new_div1, new_div2, key = undo_overlap_segment_divisions(
                    self.divisions[divisions_id[id_div1]],
                    self.divisions[divisions_id[id_div2]],
                )

                if (id_div1, key[0]) in modified_div:
                    msg += "A div cannot be modified two time at the same spot"
                    raise ValueError(msg, self.divisions[divisions_id[id_div1]])

                if (id_div2, key[1]) in modified_div:
                    msg += "A div cannot be modified two time at the same spot"
                    raise ValueError(msg, self.divisions[divisions_id[id_div2]])

                self.divisions[divisions_id[id_div1]] = new_div1
                self.divisions[divisions_id[id_div2]] = new_div2

                modified_div.append((id_div1, key[0]))
                modified_div.append((id_div2, key[1]))

        if any(dist > 1 for _, _, dist in overlaps):
            raise ValueError(msg)

        logger.warning(msg)

    def _clean_marked_division(self):
        """Marked division should not overalp with not marked division.
        If this is the case, check if it can be corrected or delete them.
        """
        marked_divisions_pos = {
            i: [div.location.start, div.location.end]
            for i, div in enumerate(self.divisions)
            if div.spot_number > -1
        }
        unmark_divisions_pos = {
            i: [div.location.start, div.location.end]
            for i, div in enumerate(self.divisions)
            if div.spot_number == -1
        }

        to_rm = []
        for _, (mark_start, mark_end) in marked_divisions_pos.items():
            for i, (umark_start, umark_end) in unmark_divisions_pos.items():
                # check if it as been deleted
                if i in to_rm:
                    continue
                # unmarked cover the marked one
                if umark_start < mark_start and umark_end > mark_end:
                    continue
                # unmark is contained in the marked one
                if mark_start <= umark_start and mark_end >= umark_end:
                    to_rm.append(i)
                    continue
                # umark intersect with marked div
                if umark_start < mark_end and umark_end > mark_start:
                    if umark_start < mark_start:
                        self.divisions[i].location = Location(umark_start, mark_start)
                        self.divisions[i].size = mark_start - umark_start
                        unmark_divisions_pos[i] = [umark_start, mark_start]
                    else:
                        self.divisions[i].location = Location(mark_end, umark_end)
                        self.divisions[i].size = umark_end - mark_end
                        unmark_divisions_pos[i] = [mark_end, umark_end]

        # remove divisions
        self.divisions = [div for j, div in enumerate(self.divisions) if j not in to_rm]

    def _complete_div(self):
        """Every inch of the segment should have a divsion on it. If division
        was not defined, create empty division for this part of the segment.
        """
        divisions_pos = (
            [div.location.start, div.location.end] for div in sorted(self.divisions)
        )

        empty_div = []
        last_point = self.beg
        try:
            curr_div = next(divisions_pos)
            while last_point < self.end:
                if last_point != curr_div[0]:
                    empty_div.append(
                        SegmentDivision(location=Location(last_point, curr_div[0]))
                    )
                    last_point = curr_div[0]
                else:
                    last_point = curr_div[1]
                    curr_div = next(divisions_pos)
        except StopIteration:
            pass
        if last_point < self.end:
            empty_div.append(SegmentDivision(location=Location(last_point, self.end)))

        if empty_div:
            self.divisions.extend(empty_div)

        self.divisions = sorted(self.divisions)

    def finalize(self, veh_size: float = None, regulation_ignored: list[str] = None):
        """Make sure divisison on the segment respect all the properties.

        Parameters
        ----------
        veh_size: float, optional
            Size of the parked vehicule on the segment, by default None.
        regulation_ignored: list[str], optional
            List of regulation name to ignore for capacity, by default None.
        """
        # set veh_size
        self.veh_size = veh_size if veh_size else constants.VEH_SIZE

        # pass parameters to all divisions
        for div in self.divisions:
            div.finalize(
                veh_size=veh_size,
                regulation_ignored=regulation_ignored,
                seg_beg=self.beg,
                seg_end=self.end,
            )

        # remove null division
        self.divisions = [div for div in self.divisions if div.size > 0]

        # curblr div format to cds format
        self._clean_marked_division()
        self._assert_marked_div_do_not_overlap()
        current_divisions_pos = [
            [div.location.start, div.location.end] for div in self.divisions
        ]
        self.divisions = reshape_divisions(current_divisions_pos, self.divisions)
        self._complete_div()

        # Since we have recreated all division, re-finalize
        for div in self.divisions:
            div.finalize(
                veh_size=veh_size,
                regulation_ignored=regulation_ignored,
                seg_beg=self.beg,
                seg_end=self.end,
            )

    def get_capacity(self, time: np.datetime64 = None) -> float:
        """Return the capacity of the segment at given time.

        Parameters
        ----------
        time : np.datetime64, optional
            Given time, by default None

        Returns
        -------
        float
        """
        return sum(div.get_capacity(time=time) for div in self.divisions)

    def get_capacity_by_reg(self, time: np.datetime64 = None) -> dict[str, int]:
        """Return the capacity of each regulation on the street. Can be
        parametered by time.

        Parameters
        ----------
        time : np.datetime64, optional
            time for the capacity query, by default None

        Returns
        -------
        dict[str, int]
            Dictionary with the name of the restriction and its capacity.
        """
        cap_by_reg = {}

        for div in self.divisions:
            try:
                name = div.get_active_reg(time=time).name
            except AttributeError:
                name = "Aucune restrictions"
            try:
                cap_by_reg[name] += np.round(div.size / div.veh_size, 0)
            except KeyError:
                cap_by_reg[name] = np.round(div.size / div.veh_size, 0)

        return cap_by_reg

    def get_regulation_name(self, time: np.datetime64) -> str:
        """Return the name of the regulation is this regulation cover the whole
        street at all time, e.g. non surveyed street.

        Returns
        -------
        str
            Name of the active regulation
        """
        if self.get_capacity(time) > 0:
            return None

        regs = [
            div.get_active_reg(time).name
            for div in self.divisions
            if div.get_active_reg(time)
        ]

        regs, counts = np.unique(regs, return_counts=True)

        return regs[np.argmax(counts)]

    def is_restriction(
        self,
        position: float,
        time: np.datetime64,
        return_capacity: bool = False,
        ignore_reg: list[str] | None = None,
    ) -> Tuple[bool, str, float]:
        """Is there an active restriction on the segment at given time and
        position

        Parameters
        ----------
        position : float
            Position on the segment.
        time : np.datetime64
            Given time
        return_capacity : bool, optional
            Return capacity if True, by default False
        ignore_reg : list[str], optional
            List of regulation name to ignore, by default None

        Returns
        -------
        Tuple[bool, str, float]
            Is restricted, active regulation name, capacity
        """
        reg = None
        for div in self.divisions:
            if div.point_is_on(position):
                reg = div.get_active_reg(time, ignore_reg)
                break

        cap = np.nan
        if return_capacity:
            cap = self.get_capacity(time=time)

        if reg:
            return (True, reg.name, cap)

        return (False, None, cap)

    @classmethod
    def from_json(cls, segment: dict):
        """Load Segment from JSON

        Parameters
        ----------
        segment : dict
            JSON representation of a segment

        Returns
        -------
        _type_
            _description_
        """
        segment_id = segment["properties"]["id_trc"]
        side_of_street = (
            SideOfStreet.RIGHT.value
            if segment["properties"]["cote_rue_id"] % 10 == 1
            else SideOfStreet.LEFT.value
        )
        street_geom = segment["street_geom"]

        # non surveyed
        if segment["properties"]["non_parcouru"]:
            return cls(
                segment_id,
                side_of_street,
                [
                    SegmentDivision(
                        location=Location(),
                        regulations=[Regulation(name="Non parcourue")],
                        spot_number=-1,
                    )
                ],
                street_geom,
            )

        divisions = [SegmentDivision.from_json(segment)]
        divisions = [div for div in divisions if div is not None]

        return cls(segment_id, side_of_street, divisions, street_geom)


def _parse_curbnsap_instance(regulation: dict, geometry: shapely.LineString) -> Segment:
    # regulation creation
    regulation["street_geom"] = geometry

    return Segment.from_json(regulation)


def _merge_segment(segments: list[Segment]) -> list[Segment]:
    segments = sorted(segments)

    result = []
    curr_segment = segments[0]
    for segment in segments:
        if segment == curr_segment:
            curr_segment += segment
        else:
            result.append(curr_segment)
            curr_segment = segment
    result.append(curr_segment)

    return result


@dataclass
class Curbs(object):
    """Collection of Segment."""

    curbs: dict[int, Segment]
    parameters: dict = field(default_factory=dict)

    def __post_init__(self):
        for _, seg in self.curbs.items():
            seg.finalize(
                veh_size=self.parameters.get("veh_size", None),
                regulation_ignored=self.parameters.get("regulation_ignored", None),
            )

    def __data__(self):
        records_seg = [seg.as_numpy() for seg in self.curbs.values()]
        return np.concatenate(records_seg, dtype=Segment.segmentdt)

    @classmethod
    def from_json(cls, regulations: list, roads: gpd.GeoDataFrame, **kwargs):
        """Load collection from JSON.

        Parameters
        ----------
        regulations : list
            JSON collection.
        roads : gpd.GeoDataFrame
            Road network geometry.
        **kwargs : dict
            'veh_size' and 'regulation_ignored'

        Returns
        -------
        Curbs
        """
        roads = roads.copy()
        roads = roads.set_index(constants.SEGMENT)
        roads = roads.to_crs("epsg:4326")
        regulations = copy.deepcopy(regulations)

        # get geometries
        id_trc = [r["properties"]["id_trc"] for r in regulations]
        try:
            roads_geom = roads.loc[id_trc, "geometry"].values
        except KeyError:
            id_trc = [id_ for id_ in id_trc if id_ in roads.index.values]
            roads_geom = roads.loc[id_trc, "geometry"].values

        segments = map(_parse_curbnsap_instance, regulations, roads_geom)
        segments = _merge_segment(list(segments))

        return cls(dict(zip([seg.id for seg in segments], segments)), parameters=kwargs)

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame, **kwargs):
        """Load collection from dataframe

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe of Segment collection
        **kwargs : dict
            'veh_size' and 'regulation_ignored'

        Returns
        -------
        Curbs
        """
        data = data.copy()
        data["_id"] = data["id"] * 10
        data["_id"] += [sos if sos == 1 else 2 for sos in data.side_of_street]
        data["_id"] = data["_id"].astype(int)
        data["geometry"] = data["geometry"].apply(shapely.from_wkt)

        curbs = {}
        for segment_id, segment_data in data.groupby("_id"):
            curbs[segment_id] = Segment(
                segment_id=segment_data.iloc[0].id,
                side_of_street=segment_data.iloc[0].side_of_street,
                divisions=[],
                geometry=segment_data.iloc[0].geometry,
            )

        for (segment_id, _, _), div_data in data.groupby(
            ["_id", "loc_start", "loc_end"]
        ):
            curbs[segment_id].divisions.append(SegmentDivision.from_dataframe(div_data))

        return cls(curbs, parameters=kwargs)

    def _parse_dates_params(
        self,
        time: datetime.datetime | None,
        hour: datetime.time | None,
        day: str | None,
    ) -> datetime.datetime | datetime.time | datetime.date:
        msg = ""
        if time is not None and (hour is not None or day is not None):
            msg = "Param `hour` and `day` cannot be set if `time` is set."

        if msg:
            raise ValueError(msg)

        if time:
            return time

        if hour and not day:
            return hour

        if day and not hour:
            date = pd.to_datetime("today")
            date += datetime.timedelta(days=(parse_days(day)[0] - date.weekday()) % 7)
            return date.date()

        if day and hour:
            date = pd.to_datetime("today")
            date += datetime.timedelta(days=(parse_days(day)[0] - date.weekday()) % 7)
            return datetime.datetime.combine(date.date(), hour)

        date = None

        return date

    def get_capacity(
        self,
        time: np.datetime64 = None,
        hour: datetime.time = None,
        day: str = None,
        as_dataframe: bool = False,
    ) -> dict[int, float]:
        """Return capacity of the Curbs

        Parameters
        ----------
        time : np.datetime64, optional
            Given time. Cannot be set if hour and day are set, by default None
        hour : datetime.time, optional
            For a specific hour, by default None.
        day : str, optional
            For a specific day, by default None

        Returns
        -------
        dict[int, float]
            Capacities for all segment.
        """
        time = self._parse_dates_params(time, hour, day)

        cap = {k: seg.get_capacity(time=time) for k, seg in self.curbs.items()}

        if as_dataframe:
            cap = pd.DataFrame.from_dict(
                cap, orient="index", columns=[constants.CAP_N_VEH]
            )
            cap.index.name = "cote_rue_id"
            cap = cap.reset_index()
            cap["segment"] = cap.cote_rue_id // 10
            cap["side_of_street"] = [
                -1 if c % 10 == 2 else c % 10 for c in cap.cote_rue_id
            ]

        return cap

    def get_regulation_name(
        self, time: np.datetime64 = None, hour: datetime.time = None, day: str = None
    ) -> dict[int, str]:
        """Return the name of the regulation is this regulation cover the whole
        street at all time, e.g. non surveyed street.

        Returns
        -------
        dict[int, str]
            Name of the active regulation
        """

        time = self._parse_dates_params(time, hour, day)
        regs = {k: seg.get_regulation_name(time) for k, seg in self.curbs.items()}
        return regs

    def get_capacity_by_reg(
        self, time: np.datetime64 = None, hour: datetime.time = None, day: str = None
    ) -> dict[str, int]:
        """Capacity by regulations names.

        Parameters
        ----------
        time : np.datetime64, optional
            Given time. Cannot be set if hour and day are set, by default None
        hour : datetime.time, optional
            For a specific hour, by default None.
        day : str, optional
            For a specific day, by default None

        Returns
        -------
        dict[str, int]
        """
        time = self._parse_dates_params(time, hour, day)
        cap_per_reg = {}

        for _, seg in self.curbs.items():
            cap = seg.get_capacity_by_reg(time)
            for reg_name, capacity in cap.items():
                if reg_name in cap_per_reg:
                    cap_per_reg[reg_name] += capacity
                else:
                    cap_per_reg[reg_name] = capacity

        return cap_per_reg

    def get_segment_regulation_name(
        self,
        segment: int,
        side_of_street: int,
        time: np.datetime64 = None,
        hour: datetime.time = None,
        day: str = None,
    ) -> str:
        """
        For a specific segment, return the name of the regulation if this
        regulation cover the whole street at all time, e.g. non surveyed
        street.

        Parameters
        ----------
        segment : int
            Segment id.
        side_of_street : int
            Side of street.
        time : np.datetime64, optional
            Given time. Cannot be set if hour and day are set, by default None
        hour : datetime.time, optional
            For a specific hour, by default None.
        day : str, optional
            For a specific day, by default None

        Returns
        -------
        str
        """

        time = self._parse_dates_params(time, hour, day)

        seg_id = int(segment) * 10
        seg_id += int(side_of_street) if side_of_street >= 0 else 2

        if seg_id not in self.curbs:
            return np.nan

        return self.curbs[seg_id].get_regulation_name(time)

    def get_segment_capacity(
        self,
        segment: int,
        side_of_street: int,
        time: np.datetime64 = None,
        hour: datetime.time = None,
        day: str = None,
    ) -> float:
        """Capacity of a specific segment.

        Parameters
        ----------
        segment : int
            Segment id.
        side_of_street : int
            Side of street.
        time : np.datetime64, optional
            Given time. Cannot be set if hour and day are set, by default None
        hour : datetime.time, optional
            For a specific hour, by default None.
        day : str, optional
            For a specific day, by default None

        Returns
        -------
        float
        """
        time = self._parse_dates_params(time, hour, day)

        seg_id = int(segment) * 10
        seg_id += int(side_of_street) if side_of_street >= 0 else 2

        if seg_id not in self.curbs:
            return np.nan

        return self.curbs[seg_id].get_capacity(time=time)

    def apply_restriction_on_lprdataframe(
        self,
        lpr_df: LprDataFrame,
        return_capacity: bool = False,
        ignore_reg: list[str] | None = None,
    ) -> LprDataFrame:
        """Apply restriction for each parking instance of a LprDataFrame.

        Parameters
        ----------
        lpr_df : LprDataFrame

        Returns
        -------
        LprDataFrame
            Columns 'is_restrict' and 'restrictions' added.
        """

        lpr_df = lpr_df.copy()
        lpr_df["seg_id"] = lpr_df[constants.SEGMENT].astype(int) * 10
        lpr_df["seg_id"] += [
            sos if sos >= 0 else 2 for sos in lpr_df[constants.SIDE_OF_STREET]
        ]

        lpr_df = lpr_df.set_index("seg_id")

        curb_idx = list(self.curbs.keys())
        data_idx = lpr_df.index
        comon_idx = np.intersect1d(curb_idx, data_idx)

        restrict = lpr_df.loc[comon_idx].apply(
            lambda x: self.curbs[x.name].is_restriction(
                position=x[constants.POINT_ON_STREET],
                time=x["datetime"],
                return_capacity=return_capacity,
                ignore_reg=ignore_reg,
            ),
            axis=1,
        )

        restrict = np.array(
            [[is_res, res_name, cap] for is_res, res_name, cap in restrict.to_list()]
        )

        lpr_df[constants.CAP_IS_RESTRICT] = False
        lpr_df[constants.CAP_RESTRICTIONS] = ""

        if return_capacity:
            lpr_df[constants.CAP_N_VEH] = np.nan
            lpr_df.loc[comon_idx, constants.CAP_N_VEH] = np.array(
                restrict[:, 2], dtype=float
            )

        lpr_df.loc[comon_idx, constants.CAP_IS_RESTRICT] = np.array(
            restrict[:, 0], dtype=bool
        )
        lpr_df.loc[comon_idx, constants.CAP_RESTRICTIONS] = np.array(
            restrict[:, 1], dtype=np.unicode_
        )

        lpr_df.reset_index(inplace=True, drop=True)

        return lpr_df

    def as_numpy(self):
        """Return Curbs as numpy.

        Returns
        -------
        np.array[segmentdt]
        """
        return self.__data__()

    def to_dataframe(self):
        """Return Curbs as dataframe

        Returns
        -------
        pandas.DataFrame
        """
        arr = self.__data__()
        arr_without_geom = rfn.drop_fields(arr, "geometry")
        flatten_dtype = np.dtype(list(rfn.flatten_descr(arr_without_geom.dtype)))
        df = pd.DataFrame(arr_without_geom.view(flatten_dtype))
        df["geometry"] = arr["geometry"]

        return df
