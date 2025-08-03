# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 21:22:32 2020
@author: Ratnadip Adhikari
"""

# ================================================
import json
import time
import re
import yaml
import pkg_resources
import pandas as pd
import inspect
from concurrent.futures import ThreadPoolExecutor
from undecorated import undecorated
from datetime import timedelta

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')
# +++++++++++++++++
# Set python options
from IPython.core import display
pd.set_option('display.max_columns', None)
# pd.reset_option('display.max_columns')
# print('python version: ', python_version())
# print('script path: ', os.path.join(os.path.dirname(__file__),''))
# print('sys.version: ', sys.version)
# ================================================


# ==================================
# Decorator to compute elapsed time for any function
# ==================================
"""
## Quick helps on decorated functions
# from undecorated import undecorated ##[for stripping decorator from a function]
%load inspect.getsource(function_name)
# =================
For loading the base function that is decorated
%load inspect.getsource(base_func_name.__closure__[0].cell_contents)
%load inspect.getsource(undecorated(base_func_name))
help(undecorated(base_func_name)) #for console help
# =================
func_2 = base_func_name.__closure__[0].cell_contents
func_2 = undecorated(base_func_name)
"""
def elapsedTime(func):
    """"This is a decorator to compute elapsed time for any function.
    Add arguments inside the ``calcTime()`` func if the target func uses arguments.
    The ``print_el_time`` parameter controls the printing and it should be present in the target
    function. Else, by default elapsed time will be printed after that function call.
    """
    def calcTime(*args, **kwargs):
        # storing time before function execution
        st_time = time.monotonic()
        ret_val = func(*args, **kwargs)
        end_time = time.monotonic()
        el_time = timedelta(seconds=end_time - st_time)  # find elapsed time
        argsDict = {k: v for k, v in kwargs.items()}
        if 'print_el_time' in argsDict:
            if argsDict['print_el_time']:
                print('Elapsed time for <{0}> func is: {1}'.format(func.__name__, el_time))
        else:
            print('Elapsed time for <{0}> func is: {1}'.format(func.__name__, el_time))
        return ret_val
    return calcTime


def null_handler(obj, ret_val):
    """Return `ret_val` if 'obj' is `None` or empty"""
    if not obj:
        return ret_val
    return obj


def map_processing(func, args, to_unpack=False):
    """Map lambda processing of multiple calls of a func"""
    res = map(lambda p: func(*p), args) if to_unpack else map(func, args)
    return list(res)


def multi_threading(func, args, workers, to_unpack=False):
    """Multithreading execution of a func"""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        res = executor.map(lambda p: func(*p), args) if to_unpack else executor.map(func, args)
    return list(res)


def get_func_attrs(attrs_dict: dict, func_obj, to_strip=True, to_print=True):
    """Returns valid attributes for func: `func_name` from the passed `attrs_dict`. The `func_obj` can
    accept class too in some cases. The param: `to_strip` is for removing decorators from `func_name`."""
    # dict of <func_name> (args, default_vals)
    try:
        func_sign = inspect.signature(undecorated(func_obj)).parameters if to_strip \
            else inspect.signature(func_obj).parameters
        func_attrs = {k: str(v) for k, v in func_sign.items()}
        for k, v in func_attrs.items():
            assign_v = (
                v.replace("{}=".format(k), "").replace("{}: ".format(k), "")
                if any(re.findall(r"=|:", v))
                else "__NON_DEFAULT__"
            )
            try:
                assign_v = eval(assign_v)
            except Exception:
                pass
            func_attrs[k] = assign_v
        # +++++++++++++++++
        if attrs_dict:
            func_attrs = dict(func_sign)
            func_attrs = {k: v for k, v in attrs_dict.items() if k in func_attrs.keys()}
    except Exception:
        func_attrs = {}
    if to_print:
        print(json.dumps(func_attrs, indent=4, default=str))
    return func_attrs


def get_obj_attributes(class_obj, exclude_attrs=[]):
    """Extract custom attributes (not functions or built-in attribute) from a class object"""
    custom_attributes, all_attrs = {}, dir(class_obj)
    for attr_name in all_attrs:
        attr_value = getattr(class_obj, attr_name)
        if not (callable(attr_value) or attr_name.startswith("__") or attr_name in exclude_attrs):
            custom_attributes[attr_name] = attr_value
    return custom_attributes


def structure_yaml(input_path, output_path):
    """Reads an unstructured YAML file, formats it, and saves the structured YAML file."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=4)
        print(f"Structured YAML saved to: {output_path}")
    except Exception as e:
        print(f"Error processing YAML: {e}")


def get_pkg_info(pkg_list, get_full=False, to_print=True, include_deps=False, include_path=False):
    """
    Retrieves version and optional metadata for installed Python packages.

    Args:
        pkg_list (list): Package names or prefixes, e.g., ['pandas', 'tensorflow', 'tf-'].
        get_full (bool, optional): If `True`, retrieves all installed packages starting with the given prefix.
        to_print (bool, optional): If `True`, prints the package info.
        include_deps (bool, optional): If `True`, includes package dependencies.
        include_path (bool, optional): If `True`, includes the installation path of the package.

    Returns:
        dict: A dictionary with package names as keys and version/info as values.
    """
    pkg_info = {}
    installed_pkgs = {dist.project_name.lower(): dist for dist in pkg_resources.working_set}

    for query in pkg_list:
        is_matched = False
        for name, dist in installed_pkgs.items():
            if get_full and name.startswith(query.lower()) or name == query.lower():
                is_matched = True
                info = {"version": dist.version}
                if include_deps:
                    info["dependencies"] = [str(r) for r in dist.requires()]
                if include_path:
                    info["location"] = dist.location
                pkg_info[dist.project_name] = info
        if not is_matched:
            pkg_info[query] = {"error": 'either package not installed or no matching prefix'}

    if to_print:
        for pkg, info in pkg_info.items():
            if "error" in info:
                print(f"{pkg}: {info['error']}")
            else:
                print(f"{pkg}=={info['version']}")
                if include_deps:
                    print(f"  ↪ deps: {info['dependencies']}")
                if include_path:
                    print(f"  ↪ path: {info['location']}")
    return pkg_info
