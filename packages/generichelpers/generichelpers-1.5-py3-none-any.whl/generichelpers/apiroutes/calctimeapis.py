"""Flask apis to perform various time calculation operations"""

import re
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request
from configs import TIME_KEYS_MAP_FULL
from utils.timeutils import CalculateTime

bp = Blueprint('calctime', __name__)


class CalcTimeAssist(object):
    """Wrapper class for time-related computations"""
    def __init__(self):
        pass  # initialize with empty constructor

    def compute_total_elapsed_time(self, time_list, to_units='YMD', include_enddate=True, format_type=1):
        elapsed_time = CalculateTime().derive_aggtime(time_list, to_units, include_enddate)
        lapsed_time = CalculateTime().derive_lapsed_time(time_list, to_units, include_enddate)
        calc_dict = {
            'elapsed_time': CalculateTime().stringify_timeunits(elapsed_time, format_type),
            'lapsed_time': CalculateTime().stringify_timeunits(lapsed_time, format_type)
        }
        output_time = [
            f"Total time: {calc_dict['elapsed_time']}",
            f"Lapsed time: {calc_dict['lapsed_time']}"
        ]
        return output_time

    def compute_age(self, dob_date: str, target_date="present", include_enddate=True, multi_units=True, format_type=1):
        if not CalculateTime().check_date_format(dob_date, '%d-%b-%Y'):
            raise ValueError("DOB should be 'dd-mm-yyyy' format (e.g. '16-Jul-2010'). Check again !")
        if not (CalculateTime().check_date_format(target_date, '%d-%b-%Y') or (target_date == 'present')):
            todays_date = datetime.today().strftime('%d-%b-%Y')
            match_str = re.compile(r'^(before|after)\s+(.*)$', re.IGNORECASE).match(target_date)
            date_direction, target_date = match_str.groups() if match_str else ('after', '')
            date_direction, target_date = date_direction.lower(), re.sub(r'\s+', ' ', target_date).strip()
            target_date = CalculateTime().derive_new_date(todays_date, target_date, date_direction)
        time_tuple = (dob_date, target_date)
        all_formats = ['YMD', 'M', 'W', 'D', 'h', 'm', 's'] if multi_units else ['YMD']
        all_formats = {s: '-'.join([TIME_KEYS_MAP_FULL[fmt]+'s' for fmt in list(s)]) for s in all_formats}
        age_dict = {s: CalculateTime().derive_elapsed_time(time_tuple, s, include_enddate) for s in all_formats}
        age_dict = {k: CalculateTime().stringify_timeunits(v, format_type) for k, v in age_dict.items()}
        output_age = [f'Age in {all_formats[k]}: {v}' for k, v in age_dict.items()]
        return output_age


@bp.route('/calctime/convert', methods=['GET'], strict_slashes=False)
def convert_func():
    """API func for deriving new date before/after the given date
    URL = http://127.0.0.1:1501/calctime/convert?time_str=12days210hrs500mins50secs&units=YMD&format=1
    """
    try:
        time_str = request.args.get('time_str', '')
        to_units = request.args.get('units', 'YMD')
        format_type = int(request.args.get('format', 1))
        time_dict = CalculateTime().extract_timeunits(time_str)
        convert_dict = CalculateTime().convert_timeunits(time_dict, to_units)
        convert_str = CalculateTime().stringify_timeunits(convert_dict, format_type)
        given_str = CalculateTime().stringify_timeunits(time_dict, format_type)
        response = [f"Given time: {given_str}", f"Converted time: {convert_str}"]
    except Exception:
        response = {
            "message": "Failed in time conversion. Check inputs again !",
            "error": traceback.format_exc()
        }
    return jsonify(response)


@bp.route('/calctime/new_date', methods=['GET'], strict_slashes=False)
def newdate_func():
    """API func for deriving new date before/after the given date
    URL = http://127.0.0.1:1501/calctime/new_date?current_date=10-Jul-2024&before=2Years3Months10days
    """
    try:
        todays_date = datetime.today().strftime('%d-%b-%Y')
        curr_date = request.args.get('current_date', todays_date)
        date_direction = 'before' if 'before' in request.args else 'after'
        new_date_str = request.args.get(date_direction, '')
        response = f"The new date is: '{CalculateTime().derive_new_date(curr_date, new_date_str, date_direction)}'"
    except Exception:
        response = {
            "message": "Failed in deriving the new date. Check inputs again !",
            "error": traceback.format_exc()
        }
    return jsonify(response)


@bp.route('/calctime/get_age', methods=['GET', 'POST'], strict_slashes=False)
def get_age_func():
    """API func for age computation
    URL = http://127.0.0.1:1501/calctime/get_age?units=multi&enddate=True&format=1
    """
    if request.method == 'GET':
        return 'I am Alive'
    try:
        multi_units = True if request.args.get('units', 'multi') == 'multi' else False
        include_enddate = eval(request.args.get('enddate', True))
        format_type = int(request.args.get('format', 1))
        dob_date = request.json.get('DOB')
        target_date = request.json.get('target_date', 'present')
        response = CalcTimeAssist().compute_age(dob_date, target_date, include_enddate, multi_units, format_type)
    except Exception:
        response = {
            "message": "Age couldn't be derived. Check inputs again !",
            "error": traceback.format_exc()
        }
        # raise
    return jsonify(response)


@bp.route('/calctime/total_time', methods=['GET', 'POST'], strict_slashes=False)
def total_time_func():
    """API func for total time computation
    URL = http://127.0.0.1:1501/calctime/total_time?units=YMD&enddate=True&format=1
    """
    if request.method == 'GET':
        return 'I am Alive'
    try:
        to_units = request.args.get('units', 'YMD')
        include_enddate = eval(request.args.get('enddate', True))
        format_type = int(request.args.get('format', 1))
        time_list = request.json.get('time_list', [])
        response = CalcTimeAssist().compute_total_elapsed_time(time_list, to_units, include_enddate, format_type)
    except Exception:
        response = {
            "message": "Total time couldn't be derived. Check inputs again !",
            "error": traceback.format_exc()
        }
        raise
    return jsonify(response)
