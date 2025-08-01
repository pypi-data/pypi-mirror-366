"""Various time-related computation utils (elapsed/lapsed times etc.)"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

from __future__ import absolute_import

import re
import time
from collections import Counter, defaultdict
from datetime import datetime
from functools import reduce

from configs import SECONDS_UNITS_MAP, TIME_KEYS_MAP_FULL, TIME_KEYS_MAP_SHORT
from dateutil.relativedelta import relativedelta


class CalculateTime(object):
    """The time computation class"""
    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]
        self.todays_date = datetime.today().strftime('%d-%b-%Y')

    @staticmethod
    def get_runtime(start_time: time.monotonic):
        """Get total run time of a func as hh:mm:ss.sss"""
        h, rem = divmod(time.monotonic() - start_time, 3600)
        m, s = divmod(rem, 60)
        elapsed_time = f"{int(h):02}:{int(m):02}:{s:06.3f}"
        return elapsed_time

    def check_date_format(self, date_str, date_format):
        """Check if a given date str: `date_str` is of specific format: `date_format`"""
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    def find_day(self, date_str: str):
        """Returns the day of the week in full (e.g. Monday, Tuesday etc.) for given
        date string of the form: '13-Jul-2024'.
        """
        date_obj = datetime.strptime(date_str, '%d-%b-%Y')
        return date_obj.strftime('%A')

    def derive_elapsed_time(self, time_tuple: tuple, to_units='s', include_enddate=True):
        """Derive total elapsed time from `time_tuple`.
        - `time_tuple`: a tuple of the form `(from_date, to_date)`, e.g.
        `('18-Oct-2021', '29-Mar-2024')`, `('10-Apr-2024', 'present')`
        """
        todays_date = datetime.strptime(self.todays_date, '%d-%b-%Y')
        from_date = todays_date if time_tuple[0] == 'present' else datetime.strptime(time_tuple[0], '%d-%b-%Y')
        to_date = todays_date if time_tuple[1] == 'present' else datetime.strptime(time_tuple[1], '%d-%b-%Y')
        to_date += relativedelta(days=1) if include_enddate else relativedelta(days=0)
        date_delta = to_date - from_date
        time_units = {'D': date_delta.days}
        if not to_units:
            return date_delta
        return self.convert_timeunits(time_units, to_units)

    def extract_timeunits(self, time_str):
        """Takes a `time_str` in one of the forms
        - '2 Years 5 Months 11 Days', '2Years, 5Months, 11Days', '2Years 5Months 11Days'
        - '2 Weeks 5 Months 11 Days', '3 Qtrs, 2 Weeks 4 hours'
        - '2 Y 5 M 11 D', '2Y, 5M, 11D', '2Y 5M 11D'
        - Any other valid str of the `'YQMWDhms'` format

        Returns:
            A dict, extracting time units e.g.: `{'Y': 2, 'M': 5, 'D': 11, 'h': 10}`
        """
        get_pat = lambda s: r'(?P<m>\d+)\s*(Mi|min|m)' if s == 'm' else \
            r'(?P<M>\d+)\s*(Mo|mo|Mn|mn|M)' if s == 'M' else f"(?P<{s}>\d+)\s*[{s.upper()}{s.lower()}]"
        fmt_str, extract_units = re.sub(r'[^a-zA-Z0-9]+', '', time_str).strip(), {}
        [extract_units.update(mp.groupdict()) for s in 'YQMWDhms' if (mp := re.search(get_pat(s), fmt_str))]
        extract_units = {k: int(v) for k, v in extract_units.items() if v}
        return extract_units

    def extract_from_reldelta(self, rdelta_obj):
        """Extract desired time units from a `relativedelta` object."""
        if not isinstance(rdelta_obj, relativedelta):
            return dict.fromkeys('YQMWDhms', 0)
        extract_units = {
            'Y': rdelta_obj.years,
            'Q': rdelta_obj.months // 3,
            'M': rdelta_obj.months % 3,
            'W': rdelta_obj.days // 7,
            'D': rdelta_obj.days % 7,
            'h': rdelta_obj.hours,
            'm': rdelta_obj.minutes,
            's': rdelta_obj.seconds,
        }
        return extract_units

    def convert_to_reldelta(self, time_dict: dict):
        """Convert a given `time_dict` to appropriate `relativedelta` object.
        >>> time_dict = {'Y': 2, 'M': 5, 'Q': 1, 'W': 2, 'D': 17, 'h': 4, 'm': 30, 's': 45}
        rdelta_obj = relativedelta(years=+2, months=+8, days=+31, hours=+4, minutes=+30, seconds=+45)
        """
        total_months = time_dict.get('M', 0) + 3 * time_dict.get('Q', 0)
        rdelta_obj = relativedelta(
            years=time_dict.get('Y', 0),
            months=total_months,
            weeks=time_dict.get('W', 0),
            days=time_dict.get('D', 0),
            hours=time_dict.get('h', 0),
            minutes=time_dict.get('m', 0),
            seconds=time_dict.get('s', 0)
        )
        return rdelta_obj

    def derive_new_date(self, curr_date, new_date_str, date_direction='after'):
        """Returns the new date before/after the `curr_date`.

        Parameters
        ----------
        curr_date (str): The `curr_date` -- should be provide in the format: '13-Jul-2024'\n
        new_date_str (str): The new date str of the form --
        - '2 years 3 months 10 days', '7 Days, 13 Hrs'
        - '1 years, 2 Qtrs, 3 weeks, 10 days', '120 hrs, 520 minutes, 400 secs'\n
        date_direction (str): The direction of computation, must be one of `'before'` or `'after'`
        """
        start_date = datetime.strptime(curr_date, '%d-%b-%Y')  # parse current date
        time_dict = self.extract_timeunits(new_date_str)
        rdelta = self.convert_to_reldelta(time_dict)
        # +++++++++++++++++
        # Calculate new date based on direction
        if date_direction == 'after':
            new_date = start_date + rdelta
        elif date_direction == 'before':
            new_date = start_date - rdelta
        else:
            raise ValueError("Direction should be either 'after' or 'before'")
        return new_date.strftime('%d-%b-%Y')

    def derive_relative_date(self, curr_time_str, reqd_time_str, ref_date=None):
        """For given time expression as per reference date, finds the date that satisfies the
        desired time expression.

        Parameters
        --------
            curr_time_str (str): the current time str
            reqd_time_str (str): the desired time str
            ref_date (str, `None`): the ref date of the form: '30-Jul-2024'. If `None`, today's date is taken

        Examples
        --------
        >>> curr_time_str='8yrs 2mnths 12days'
            reqd_time_str='10yrs, 5mnths, 22days'
            ref_date='30-Jul-2024'
            output='09-Nov-2026'
            # if today it is '8yrs 2mnths 12days', then when will it be '10yrs 5mnths 22days'?
        >>> curr_time_str='8yrs 2mnths 12days'
            reqd_time_str='5yrs, 8mnths, 20days'
            ref_date='30-Jul-2024'
            output='11-Nov-2018'
            # if today it is '8yrs 2mnths 12days', then when was it '5yrs, 8mnths, 20days'?
        """
        ref_date = datetime.strptime(ref_date, '%d-%b-%Y') if ref_date else datetime.today()
        curr_time_dict = self.extract_timeunits(curr_time_str)
        reqd_time_dict = self.extract_timeunits(reqd_time_str)
        curr_rdelta = self.convert_to_reldelta(curr_time_dict)
        reqd_rdelta = self.convert_to_reldelta(reqd_time_dict)
        delta_diff = reqd_rdelta - curr_rdelta
        rel_date = (ref_date + delta_diff).strftime('%d-%b-%Y')
        return rel_date

    def convert_timeunits(self, time_dict: dict, to_units='YMD'):
        """Convert a given `time_units` dict to another desired time units dict"""
        if not (set(to_units) <= set('YQMWDhms')):
            return dict.fromkeys('YQMWDhms', 0)
        if not (set(time_dict) <= set('YQMWDhms')):
            return dict.fromkeys(to_units, 0)
        total_secs = reduce(lambda x, y: x+y, [time_dict[k]*SECONDS_UNITS_MAP[k] for k in time_dict])
        return self.convert_seconds(total_secs, to_units)

    def convert_seconds(self, time_secs: int, to_units=''):
        """Convert time seconds to one or multiple time units as below--
        - `Y`: years; `Q`: quarters; `M`: months; `W`: weeks; `D`: days
        - `h`: hour; `m`: minutes; `s`: seconds\n
        The param: `to_units` is a str of valid units, e.g. `to_units='hms'`. It defaults to an empty str.\n
        Returns a dict with keys as above and values as the converted time units.
        """
        units_to_consider = list(to_units) if to_units else list(SECONDS_UNITS_MAP)
        units_to_consider = {k: v for k, v in SECONDS_UNITS_MAP.items() if k in units_to_consider}
        converted_units, remaining_secs = {}, time_secs
        for unit, secs_in_unit in units_to_consider.items():
            converted_units[unit], remaining_secs = divmod(remaining_secs, secs_in_unit)
        return converted_units

    def stringify_timeunits(self, time_dict: dict, use_format=1):
        """Stringify a dict of time units, as follows --
        >>> time_dict = {'Y': 2, 'M': 1, 'Q': 1, 'W': 2, 'm': 10, 's': 5} returns
            time_str = '2 yrs, 1 mnth, 1 qtr, 2 wks, 10 mins, 5 secs'  # use_format=1
            time_str = '2 Years, 1 Month, 1 Qtr, 2 Weeks, 10 minutes, 5 seconds'  # use_format=2
            time_str = '2Y 1M 1Q 2W 10m 5s'  # use_format=3
        """
        units_map = TIME_KEYS_MAP_SHORT if use_format == 1 else TIME_KEYS_MAP_FULL \
            if use_format == 2 else dict(zip('YQMWDhms', 'YQMWDhms'))
        units_dict = {k: v for k, v in time_dict.items() if k in 'YQMWDhms'}
        time_str = [f'{v} {units_map[k]}' + ('' if v in (0, 1) else 's') for k, v in units_dict.items()] \
            if use_format in (1, 2) else [str(v) + k for k, v in units_dict.items()]
        time_str = ', '.join(time_str) if use_format in (1, 2) else ' '.join(time_str)
        return time_str

    def derive_aggtime(self, time_list: list, to_units='YMD', include_enddate=True):
        """Agg time from given time list. The `time_list` has the following forms --
        >>> time_list = [
            '0 Years 2 Months 26 Days',
            '2 Years 5 Months 11 Days',
            '5 Years 8 Months 16 Days',
            '2 Years 2 Months 21 Days',
        ]  # here the time strs can be of any valid Y/M/D format (see <self.separate_times()>)
        >>> time_list = [
            ('19-Aug-2013', '09-Nov-2015'),
            ('21-Dec-2015', '17-Sep-2021'),
            ('18-Oct-2021', '29-Mar-2024'),
            ('10-Apr-2024', 'present')
        ]
        """
        agg_time = defaultdict(int)
        [agg_time.update({k: agg_time[k] + v}) for t in time_list for k, v in (self.extract_timeunits(
            t).items() if isinstance(t, str) else self.derive_elapsed_time(t, to_units, include_enddate).items())]
        return self.convert_timeunits(agg_time, to_units)

    def derive_lapsed_time(self, time_list: list, to_units='YMD', include_enddate=True):
        """Find total lapsed time from a list of time tuples of the form --
        >>> time_list = [
            ('19-Aug-2013', '09-Nov-2015'),
            ('21-Dec-2015', '17-Sep-2021'),
            ('18-Oct-2021', '29-Mar-2024'),
            ('10-Apr-2024', 'present')
        ]
        """
        checkFlag = all([isinstance(t, (tuple, list)) for t in time_list])
        if not checkFlag:
            return dict.fromkeys(to_units, 0)
        todays_date = datetime.strptime(self.todays_date, '%d-%b-%Y')
        time_list = sorted(time_list, key=lambda x: todays_date if x[0] == 'present' else datetime.strptime(x[0], '%d-%b-%Y'))
        # +++++++++++++++++
        # Find total time and agg time in secs
        agg_secs = Counter()
        [agg_secs.update(self.derive_elapsed_time(t, 's', include_enddate)) for t in time_list]
        total_secs = self.derive_elapsed_time((time_list[0][0], time_list[-1][1]), 's', include_enddate)
        return self.convert_seconds(total_secs['s'] - agg_secs['s'], to_units)
