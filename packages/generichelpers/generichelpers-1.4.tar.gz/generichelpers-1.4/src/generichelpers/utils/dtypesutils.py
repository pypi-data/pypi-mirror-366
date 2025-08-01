"""Data types (list, tuple, dict) operations utils"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

import ctypes
import math
import os
import re
import warnings
from collections import Counter
from copy import deepcopy
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')


class DtypesOpsHandler(object):
    """Datatypes (list, tuple, dict) ops class"""
    def __init__(self):
        pass  # initialized class with empty constructor

    @staticmethod
    def merge_dicts(iter_dicts, to_update=True):
        """Merge iterable (list/tuple) of dicts to a single dict"""
        merged_dict = {}
        if to_update:
            [merged_dict.update(d) for d in iter_dicts]
        else:
            merged_dict = {
                k: [d.get(k) for d in iter_dicts if k in d]
                for k in set().union(*iter_dicts)
            }
        return merged_dict

    @staticmethod
    def list_item_ids(input_list):
        """Function to get ids of list items (including duplicated items)"""
        ids_lst, uniq_lst = [], []
        for item in input_list:
            item_ids = [i for i, x in enumerate(input_list) if x == item]
            if item_ids not in ids_lst:
                ids_lst.append(item_ids)
                uniq_lst.append(item)
        uniq_els_ids = [v for v in zip(uniq_lst, ids_lst)]
        try:
            uniq_els_ids = {k: v for k, v in zip(uniq_lst, ids_lst)}
        except Exception:
            pass
        return uniq_els_ids

    @staticmethod
    def list_minmaxmedian(lst: list):
        """Compute Min, Max and Median of the given list"""
        list_min, list_max, list_median = None, None, None
        lst = [v for v in lst if isinstance(v, (int, float))]
        if lst:
            list_min, list_max, list_median = round(min(lst)), round(max(lst)), round(np.median(lst))
        return list_min, list_max, list_median

    @staticmethod
    def minmax_map(lst: list, map_range=(0, 1), round_digit=None):
        """Map a given list of numbers within `map_range`"""
        minmax_mapped = []
        lst = [v for i, v in enumerate(lst) if isinstance(v, (int, float))]
        if lst:
            map_min, map_max = map_range
            nos_mn, nos_mx = min(lst), max(lst)
            minmax_mapped = [map_min]*len(lst) if map_min == map_max else [
                (x - nos_mn) / (nos_mx - nos_mn) * (map_max - map_min) + map_min for x in lst]
            minmax_mapped = [round(x, round_digit) for i, x in enumerate(minmax_mapped)]
        return minmax_mapped

    @staticmethod
    def distribute_list(lst: list, gen_size=None, round_digit=None):
        """Distribute a list of numbers to generate a new list of given size"""
        distr_list = []
        if lst:
            gen_size = len(lst) if not gen_size else gen_size
            nos_mn, nos_mx = min(lst), max(lst)
            gen_interval = (nos_mx - nos_mn) / (gen_size - 1)
            distr_list = [nos_mn + gen_interval * i for i in range(gen_size)]
            if round_digit is not False:
                distr_list = [round(v, round_digit) for v in distr_list]
        return distr_list

    @staticmethod
    def list_percentiles(lst: list, ptile_range=(0, 50, 100), round_digit=None):
        """Compute percentiles of the given list"""
        lst = [v for v in lst if isinstance(v, (int, float))]
        if not (lst and ptile_range):
            return []
        ptile_range = ptile_range if isinstance(ptile_range, (list, tuple)) else [ptile_range]
        ptiles = [int(p) if p.is_integer() else round(p, round_digit) for p in np.percentile(lst, ptile_range)]
        ptiles = ptiles[0] if len(ptiles) == 1 else ptiles
        return ptiles

    @staticmethod
    def list_frequencies(input_lst: list, tot_len=None, round_digit=None):
        """This function finds the freq of each element in `input_lst` and returns a dict of the form:
        output_dict = {key: (v1,v2)} where v1-->freq, v2-->percentage freq for the element key of `input_lst`."""
        # =================
        tot_len = len(input_lst) if not tot_len else tot_len
        freq_dict = dict(Counter(input_lst))
        freq_dict = {k: (freq_dict[k], round(freq_dict[k]/tot_len, round_digit)) for k in freq_dict}
        return freq_dict

    @staticmethod
    def flatten_iterable(iterable, seqtypes=(list, tuple)):
        """This func flattens an arbitrarily nested list/tuple."""
        flattened_item = list(iterable) if isinstance(iterable, tuple) else iterable.copy()
        try:
            for i, x in enumerate(flattened_item):
                while isinstance(x, seqtypes):
                    flattened_item[i:i+1] = x
                    x = flattened_item[i]
        except IndexError:
            pass
        if isinstance(iterable, tuple):
            return tuple(flattened_item)
        return flattened_item

    @staticmethod
    def _flatten_dict(nested_dict, sep='.', base_key=True):
        """This function flattens nested dict to a single-depth dict

        Args:
            nested_dict (dict): A nested dict.
            sep (str, None, optional): Nested records separator. if None, only the last key name
                will be used. Defaults to '.'.
            base_key (str, bool, optional): The base key to use (if required). This is when `nested_dict`
                is of the form: `nested_dict = {key: {dict}}`. Defaults to ``True``.

        Returns:
            The flattened dict.
        """
        flattened_dict = {}
        _nested_dict = deepcopy(nested_dict)  # to prevent updating original dict
        kv = [*_nested_dict.items()]  # extract key, value from _dict
        bkey_dict = {}
        if base_key and len(kv) == 1:
            _key, _val = [*_nested_dict.items()][0]
            b_key = _key
            if isinstance(base_key, str):
                b_key = base_key
            bkey_dict = {b_key: _key}
        for k, v in kv:
            if isinstance(v, dict):
                if sep:
                    _kv = [*v.items()]
                    v.clear()
                    [v.update(({"{}{}{}".format(k, sep, _k): _v})) for _k, _v in _kv];
                flattened_dict.update(DtypesOpsHandler.flatten_dict(v, sep, False))
            else:
                flattened_dict.update({k: v})
        flattened_dict = {**bkey_dict, **flattened_dict}
        del _nested_dict
        return flattened_dict

    @staticmethod
    def flatten_dict(d, parent_key='', sep='_'):
        """This function flattens nested dict to a single-depth dict"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DtypesOpsHandler.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def bucket_numeric_values(numericVal=(int, float), bucket_dict={}, bucketList=[]):
        """Function to bucket large numeric values"""
        # from_pow, to_pow = math.floor(math.log10(numericVal)), math.ceil(math.log10(numericVal))
        if not bucketList:
            bucketList = [v[0] for v in bucket_dict.values()]
        if not numericVal:
            return numericVal
        repl_list = [('K', ''.join(['0']*3)), ('M', ''.join(['0']*6)), ('B', ''.join(['0']*9)), ('\\+', '-np.inf')]
        modif_bucket_dict = {}
        for idx, _item in enumerate(bucketList):
            if not (idx or '-' in _item):
                _item = f'-np.inf--{_item}'
            for tup in repl_list:
                _item = re.sub(tup[0], tup[1], _item)
            modif_bucket_dict[idx] = _item
        # Derive the bucket for 'numericVal'
        for key, bucket in modif_bucket_dict.items():
            bucket_split = bucket.split('-') if '--' not in bucket else bucket.split('--')
            brange = [eval(v) for v in bucket_split]
            if brange[0] <= numericVal < brange[1]:
                return bucketList[key]

    @staticmethod
    def format_datetime(datetime_obj, time_format: str):
        """Format a given `datetime_obj` using the `time_format`"""
        return datetime_obj.strftime(time_format) if isinstance(datetime_obj, datetime) else ""

    @staticmethod
    def format_obj_size(size_bytes):
        """Obtain a Python object's (list/dict/tuple etc.) size in a pretty readable format"""
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes/p, 2)
        return "%s %s" % (s, size_name[i])

    @staticmethod
    def is_hidden(filepath):
        """Check if a path contains hidden file"""
        name = os.path.basename(filepath)
        if re.match(r"^(~\$|\.)", name):
            return True
        if os.name == 'nt':  # Windows check
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
                return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 0x2
            except Exception:
                return False
        return False

    def summarize_files(self, base_path, file_types=None, exclude_hidden=False):
        """Provide various summary stats for files in the base path, such as:
        - Total no. of files of each type in the base path
        - Total no. of files of each type inside subdirs
        - A consolidated list of files of each type as
            * `file_name | file_ext | file_size_bytes | file_size| created_date | modified_date | file_path`

        Args:
            base_path (str): The base path to scan for.
            file_types (list, None, optional): A list of file exts to scan for. If `None`, scans for all \
                file exts in the base path.
            exclude_hidden (bool, optional): Flag indicating whether to exclude hidden subdirs. Defaults to `False`.
        """
        all_files, file_summary = [], {}
        file_types_ = deepcopy(file_types)
        if file_types_ is None:
            file_types_ = []
        isempty_types = False if file_types_ else True  # flag for recording empty file_types_
        f_summary = {ext: 0 for ext in file_types_}  # stand-alone files
        sd_summary = {ext: 0 for ext in file_types_}  # files inside subdirs
        hidden_summary = {ext: 0 for ext in file_types_}  # hidden files

        for root, dirs, files in os.walk(base_path):
            if exclude_hidden:
                dirs[:] = [d for d in dirs if not self.is_hidden(os.path.join(root, d))]
            is_subdir = os.path.abspath(root) != os.path.abspath(base_path)
            for f in files:
                ext = e.lower() if (e := os.path.splitext(f)[1]) else os.path.basename(f).lower()
                if isempty_types:
                    file_types_.append(ext)  # empty file_types_ handler
                for summary_dict in (f_summary, sd_summary, hidden_summary):
                    summary_dict.setdefault(ext, 0)
                if ext in file_types_:
                    fpath = os.path.join(root, f)
                    try:
                        stat = os.stat(fpath)
                    except FileNotFoundError:
                        continue  # handle broken symlinks or race conditions
                    all_files.append({
                        "file_name": f,
                        "file_ext": ext,
                        "file_size_bytes": stat.st_size,
                        "file_size": self.format_obj_size(stat.st_size),
                        "created_date": datetime.fromtimestamp(stat.st_ctime),
                        "modified_date": datetime.fromtimestamp(stat.st_mtime),
                        "file_path": fpath
                    })
                    f_summary[ext] += 1
                    if is_subdir:
                        sd_summary[ext] += 1
                    if self.is_hidden(fpath):
                        hidden_summary[ext] += 1

        # +++++++++++++++++
        # Get the final summary dict
        for ext in file_types_:
            file_summary.update({
                ext: {
                    "total_files": f_summary[ext],
                    "total_hidden_files": hidden_summary[ext],
                    "total_files_in_subdirs": sd_summary[ext]
                }
            })

        summary_df = pd.DataFrame(all_files)
        return file_summary, summary_df
