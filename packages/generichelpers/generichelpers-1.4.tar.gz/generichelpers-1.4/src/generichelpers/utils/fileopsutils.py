"""File operations utils"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

import gzip
import inspect
import json
import os
import pickle
import platform
import re
import tarfile
import warnings
import zipfile
from copy import deepcopy
from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import wx
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')


class FileopsHandler(object):
    """Fileops performer class"""
    def __init__(self):
        pass  # initialized class with empty constructor

    @staticmethod
    def _get_file_path(**kwargs):
        """
        Get the file path through a selection prompt.

        Returns
        -------
        The full file path.
        """
        argsDict = {k: v for k, v in kwargs.items()}
        wx_app = wx.App(None)
        wx_style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None,style=wx_style,**argsDict)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
        else:
            file_path = None
        dialog.Destroy()
        return file_path

    @staticmethod
    def import_file(file_path=None, msg_str='Enter the file path', *args, **kwargs):
        """
        Imports a file (json, dict, list, dataframe etc.) from a given path. The accepted formats are:
        '.csv','.xlsx','.p','.zip','.gz','.json','.txt'. Also, imports from a '.zip' file,
        having multiple .csv/.xlsx files is supported.

        Parameters
        ----------
        file_path : str or bool, optional
            The full path of the file to import. if ``None`` or ``True``, the function will ask for the file
            path in a dialogue box.
        msg_str: str, default ``None``
            The file selection prompt message.
        compression: str, default 'infer'
            The file compression type. Valid options are: {'p_zip', 'p_gzip', 'infer', 'gzip', 'bz2',
            'zip', 'xz', None}. The types 'p_zip' and 'p_gzip' mean 'pickle zip' and 'pickle gzip' files
            respectively, while others are <pd.read_csv> permissible 'compression' options.
        *args/**kwargs
            The required arguments for <pd.read_csv> or <pd.read_excel> functions.

        Returns
        -------
        The imported dataframe or dictionary.
        """
        # =======================
        getPath, getFile = deepcopy(file_path), None
        # Return the path itself if it is not str, bool or None -- dataframe/Series/list etc.
        if not isinstance(getPath, (type(None), bool, str, bytes)):
            return getPath
        if isinstance(getPath, str) and not os.path.exists(getPath):
            return getPath
        if getPath in [None, True]:
            getPath = FileopsHandler._get_file_path() if msg_str is None \
                else FileopsHandler._get_file_path(message=msg_str)
        if getPath in [None, False]:
            return getFile
        # =======================
        argsDict = {k: v for k, v in kwargs.items()}
        fileType = os.path.splitext(getPath)[1]
        # Recursive import for zip file containing multiple files
        if (fileType == '.zip') and (kwargs.get("compression") not in ['p_zip', 'p_gzip']):
            getFile = dict()
            zip_file = zipfile.ZipFile(getPath, 'r', compression=zipfile.ZIP_DEFLATED)
            filesList = zipfile.ZipFile.namelist(zip_file)
            for idx in filesList:
                idxType = os.path.splitext(idx)[1]
                getFile[idx] = json.loads(zip_file.read(idx)) if idxType == '.json' else \
                    FileopsHandler.import_file(file_path=zip_file.read(idx), *args, **kwargs)
            if all([getFile[key] is None for key in getFile]):
                getFile = None

        # =======================
        # Individual file imports
        # =======================
        excludeType = ['.json', '.txt', '.p', '.pkl', '.pickle', '.zip', '.gzip']
        # Import '.csv'
        funcArgs = dict(inspect.signature(pd.read_csv).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if (getFile is None) and (fileType not in excludeType):
            try:
                getFile = pd.read_csv(getPath, **subArgsDict)
            except Exception:
                pass
        if (getFile is None) and (fileType not in excludeType):
            try:
                getFile = pd.read_csv(StringIO(str(getPath, 'utf-8')), **subArgsDict)
            except Exception:
                pass
        # +++++++++++++++++
        # Import '.xlsx'
        funcArgs = dict(inspect.signature(pd.read_excel).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if (getFile is None) and (fileType not in excludeType):
            try:
                getFile = pd.read_excel(getPath, **subArgsDict)
            except Exception:
                pass
        # +++++++++++++++++
        # Import '.p','.pkl','.pickle' file
        if getFile is None:
            try:
                getFile = pickle.load(open(getPath, "rb"))
            except Exception:
                pass
        # +++++++++++++++++
        # Import 'p_zip' file
        if getFile is None:
            try:
                zip_file = zipfile.ZipFile(getPath, 'r', compression=zipfile.ZIP_DEFLATED)
                getFile = pickle.loads(zip_file.read(zipfile.ZipFile.namelist(zip_file)[0]))
                zip_file.close()
            except Exception:
                pass
        # +++++++++++++++++
        # Import 'p_gzip' file
        if getFile is None:
            try:
                gz_file = gzip.GzipFile(getPath, 'rb')
                getFile = pickle.loads(gz_file.read())
                gz_file.close()
            except Exception:
                pass
        # +++++++++++++++++
        # Import '.json' file
        if (getFile is None) and (fileType == '.json'):
            try:
                with open(getPath) as json_file:
                    getFile = json.load(json_file)
                json_file.close()
            except Exception:
                pass
        # +++++++++++++++++
        # Import '.txt' file
        if (getFile is None) and (fileType == '.txt'):
            try:
                with open(getPath) as text_file:
                    getFile = text_file.read()
                text_file.close()
            except Exception:
                pass
        # +++++++++++++++++
        # Import '.pkl','.p.zip','.p.gzip' files
        if getFile is None:
            try:
                getFile = pd.read_pickle(getPath)
            except Exception:
                pass

        # =======================
        # Further formatting
        # =======================
        if isinstance(getFile, dict) and (len(getFile) == 1):
            getFile = getFile[list(getFile.keys())[0]]
        if isinstance(getFile, pd.DataFrame):
            getFile.index.name = None
            # Remove 'Unnamed' columns
            unnamed_cols = getFile.columns[getFile.columns.str.contains(
                'unnamed', flags=re.IGNORECASE, regex=True)].tolist()
            getFile = getFile.drop(columns=unnamed_cols)
        return getFile

    @staticmethod
    def get_savename(base_fpath, base_fname, to_check='files', use_suffix='count', notpresent_suffix=''):
        """Counts files of the form `base_fname` in `base_fpath` and returns the appropriate new file/folder name
        - `suffix_type`: it can be one of: 'count', 'datetime' or ''
        """
        if use_suffix == 'datetime':
            name_suffix = '_' + datetime.today().strftime('%d%b%y_%H%M%S')
        elif use_suffix == 'count':
            os.makedirs(base_fpath, exist_ok=True)
            list_items = os.listdir(base_fpath) if to_check == 'files' else next(os.walk(base_fpath))[1]
            name_suffix, sfx_clist, checkFlag = '', [], False
            for f in list_items:
                if base_fname in f.split('.')[0]:
                    checkFlag = True
                    sfx_val = f.split('.')[0].split(base_fname)[-1].split('_')[-1]
                    try:
                        sfx_clist.append(int(sfx_val))
                    except Exception:
                        pass
            try:
                name_suffix = '_' + str(max(sfx_clist)+1)
            except Exception:
                name_suffix = '_1'
            if not checkFlag:
                name_suffix = notpresent_suffix  # No file/folder of the form `base_fname` present in 'base_fpath'
        else:
            name_suffix = str(use_suffix)
        return base_fname + name_suffix

    @staticmethod
    def save_files(fileToSave, file_path=None, file_name=None, save_file_type=None,
                   use_suffix='count', *args, **kwargs):
        """
        Saves a file (``dataframe``, ``series`` or ``dict`` of ``dataframes``/``series``) to
        the specified path. In case of a dict, the components will be saved in different sheets of an
        excel file or as a pickled zip file.

        Parameters
        ----------
        fileToSave : ``dataframe`` or ``dict``
            The file to save.
        file_path :  str, bool, default ``None``
            The full path of the file to import. if ``None`` or ``True``, the file will be saved in working
            directory. If ``False``, the function will just return ``False`` without saving anything.
        file_name : str, default ``None``
            The save file name. if ``None``, the file will be saved with the name: 'saved_file.<file_type>'
        use_suffix : str, default 'count'
            The suffix to add with the file name. This param is helpful if `<save_files(...)>` is run multiple
            times with the same `file_path` and `file_name`, e.g. during codes testing etc. The options are:

            - 'count' (default) : incremental suffix based on count of the files with name `file_name` in `file_path`.
            - 'datetime' : current date and time str is used as suffix.
            - In case of any other str passed, it will be simply added after 'file_name'.

        save_file_type :
            The type to which the file is to be saved. Valid options are: {'.csv', '.xlsx', '.p', '.zip', '.gz',
            'p_zip','p_gzip','.pkl','.pickle','.json','.txt'}. If ``None``, then a '.csv' will be used to save a
            ``dataframe`` and '.xlsx' will be used to save the components of a ``dict``.
        *args/**kwargs
            The valid arguments for <pd.DataFrame.to_csv> or <pd.DataFrame.to_excel>.

        Returns
        -------
        The function returns ``True`` if file save is a success, else ``False``.
        """
        # =======================
        # Obtain file save path and save name
        if file_path is False:
            return False
        file_path_ = os.getcwd() if file_path in [True, None] else file_path
        file_name_ = 'saved_file_' + datetime.today().strftime('%d%b%y_%H%M%S') if file_name is None else file_name
        os.makedirs(file_path_, exist_ok=True)
        file_name_ = FileopsHandler.get_savename(file_path_, file_name_, 'files', use_suffix, '')  # get save name
        # =======================
        # Individual files saving
        # =======================
        argsDict = {k: v for k, v in kwargs.items()}
        fileType = '.csv' if (save_file_type is None) and (not isinstance(fileToSave, dict)) else save_file_type
        # Save as '.csv'
        funcArgs = dict(inspect.signature(pd.DataFrame.to_csv).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if fileType == '.csv':
            try:
                fileToSave.to_csv(os.path.join(file_path_, file_name_+fileType), **subArgsDict)
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as '.zip'
        if fileType == '.zip':
            try:
                compression_opts = dict(method='zip', archive_name=file_name_+'.csv')
                fileToSave.to_csv(os.path.join(file_path_, file_name_+fileType),
                                  compression=compression_opts, **subArgsDict)
                return True
            except Exception:
                pass
            # For saving components of a dict in one zip folder
            funcArgs = dict(inspect.signature(pd.DataFrame.to_csv).parameters)
            subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
            try:
                zip_file = zipfile.ZipFile(os.path.join(file_path_, file_name_+'.zip'), 'w',
                                           compression=zipfile.ZIP_DEFLATED)
                for key in fileToSave:
                    zip_file.writestr(key+'.csv', fileToSave[key].to_csv(**subArgsDict), zipfile.ZIP_DEFLATED)
                zip_file.close()
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as '.xlsx'
        funcArgs = dict(inspect.signature(pd.DataFrame.to_excel).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if fileType == '.xlsx':
            try:
                fileToSave.to_excel(os.path.join(file_path_, file_name_+fileType), **subArgsDict)
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as Save as pickled zip
        funcArgs = dict(inspect.signature(pickle.dumps).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if fileType == 'p_zip':
            try:
                zip_file = zipfile.ZipFile(os.path.join(file_path_, file_name_+'.zip'), 'w',
                                           compression=zipfile.ZIP_DEFLATED)
                zip_file.writestr(file_name_+'.p', pickle.dumps(fileToSave, **subArgsDict))
                                # Can specify "protocol=pickle.HIGHEST_PROTOCOL" or a no. between 0-5
                zip_file.close()
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save dict as gz
        if fileType == '.gz':
            try:
                gz_file = gzip.GzipFile(os.path.join(file_path_, file_name_+fileType), 'wb')
                gz_file.write(pickle.dumps(fileToSave, **subArgsDict))
                                # Can specify "protocol=pickle.HIGHEST_PROTOCOL" or a no. between 0-5
                gz_file.close()
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as '.p' or '.pickle' pickle file
        funcArgs = dict(inspect.signature(pickle.dump).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if fileType in ['.p', '.pickle']:
            try:
                pickle.dump(fileToSave, open(os.path.join(file_path_, file_name_+fileType), "wb"), **subArgsDict)
                                # Can specify "protocol=pickle.HIGHEST_PROTOCOL" or a no. between 0-5
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save dataframe as '.pkl' file
        funcArgs = dict(inspect.signature(pd.to_pickle).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if isinstance(fileToSave, pd.DataFrame) and fileType in ['.pkl', 'p_zip', 'p_gzip']:
            try:
                fileToSave.to_pickle(os.path.join(file_path_, file_name_+fileType), **subArgsDict)
                                # Can specify "protocol=pickle.HIGHEST_PROTOCOL" or a no. between 0-5
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as '.json' file
        funcArgs = dict(inspect.signature(json.dump).parameters)
        subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
        if fileType == '.json':
            try:
                json.dump(fileToSave, open(os.path.join(file_path_, file_name_+fileType), 'w'), **subArgsDict)
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Save as '.txt' file
        if fileType == '.txt':
            try:
                with open(os.path.join(file_path_, file_name_+fileType), 'w') as text_file:
                    text_file.write(fileToSave)
                text_file.close()
                return True
            except Exception:
                pass
        # +++++++++++++++++
        # Saving components of a dict
        if isinstance(fileToSave, dict) and fileType is None:
            try:
                dictKeys = list(fileToSave.keys())
                if (len(fileToSave) == 1) and (not isinstance(fileToSave[dictKeys[0]], dict)):
                    funcArgs = dict(inspect.signature(pd.DataFrame.to_csv).parameters)
                    subArgsDict = {x: argsDict[x] for x in argsDict.keys() if x in funcArgs.keys()}
                    fileToSave[dictKeys[0]].to_csv(os.path.join(file_path_, file_name_+'.csv'), **subArgsDict)
                else:
                    funcArgs = dict(inspect.signature(pd.DataFrame.to_excel).parameters)
                    subArgsDict = {x: argsDict[x] for x in argsDict.keys() if (
                        x in funcArgs.keys()) and (x != 'sheet_name')}
                    writer = pd.ExcelWriter(os.path.join(file_path_, file_name_+'.xlsx'))
                    for indKey in dictKeys:
                        if not isinstance(fileToSave[indKey], dict):
                            fileToSave[indKey].to_excel(writer, sheet_name=str(indKey), **subArgsDict)
                        else:
                            FileopsHandler.save_files(fileToSave=fileToSave[indKey], file_path=file_path_,
                                                      file_name=indKey, use_suffix=use_suffix, **argsDict)
                    writer.save()
                    # writer.close()
                return True
            except Exception:
                pass
        # =======================
        return False

    @staticmethod
    def jupy_save_files(all=True, zip_type='tar', file_name='saved_data.tar.gz', home_dir='./',
                        ftyp_to_save=['.py', '.ipynb', '.csv', '.p', '.pkl']):
        """
        Saves files from the Jupyter home directory as a compressed .tar.gz/.zip folder for backup.
        Provide "ftyp_to_save" to specify the types of files to save.
        """
        if zip_type == 'tar':
            if all:
                # !tar chvfz file_name *
                tar = tarfile.open(file_name, "w:gz")
                for dirname, subdirs, files in os.walk(home_dir):
                    tar.add(dirname)
                    for file in files:
                        if (ftyp_to_save is None) or any(x in file for x in ftyp_to_save):
                            tar.add(os.path.join(dirname, file))
                tar.close()
            else:
                # os.makedirs(os.path.dirname(file_name), exist_ok=True)
                # os.remove(file_name)
                get_files = [f for f in os.listdir(home_dir) if os.path.isfile(os.path.join(home_dir,f))]
                tar = tarfile.open(file_name, "w:gz")
                for file in get_files:
                    if any(x in file for x in ftyp_to_save):
                        tar.add(file)
                tar.close()
        else:
            if all:
                # !tar chvfz file_name *
                zip = zipfile.ZipFile(file_name, 'w',compression=zipfile.ZIP_DEFLATED)
                for dirname, subdirs, files in os.walk(home_dir):
                    zip.write(dirname, compress_type=zipfile.ZIP_DEFLATED)
                    for file in files:
                        if (ftyp_to_save is None) or any(x in file for x in ftyp_to_save):
                            zip.write(os.path.join(dirname, file), compress_type=zipfile.ZIP_DEFLATED)
                zip.close()
            else:
                # os.makedirs(os.path.dirname(file_name), exist_ok=True)
                # os.remove(file_name)
                get_files = [f for f in os.listdir(home_dir) if os.path.isfile(os.path.join(home_dir,f))]
                zip = zipfile.ZipFile(file_name, 'w',compression=zipfile.ZIP_DEFLATED)
                for file in get_files:
                    if any(x in file for x in ftyp_to_save):
                        zip.write(file, compress_type=zipfile.ZIP_DEFLATED)
                zip.close()

    @staticmethod
    def jupy_extr_files(file_name='saved_data.tar.gz', zip_type='tar', folder_name='saved_data'):
        """Extracts all saved files from a .tar.gz folder to the Jupyter home directory"""
        if zip_type == 'tar':
            tar = tarfile.open(file_name, "r:gz")
            tar.extractall(folder_name)
            tar.close()
        else:
            zip = zipfile.ZipFile(file_name, 'r')
            zip.extractall(folder_name)
            zip.close()

    @staticmethod
    def ipynb_from_html(html_file_name=None, save_file_name='notebook.ipynb'):
        """
        The code uses "BeautifulSoup" and "JSON" to convert html notebook to ipynb.
        The trick is to look at the JSON schema of a notebook and emulate that.
        The code selects only input code cells and markdown cells.

        - URL = http://nbviewer.jupyter.org/url/jakevdp.github.com/downloads/notebooks/XKCD_plots.ipynb
        - response = urllib.request.urlopen(url)
        """
        # for local html file
        url = os.path.abspath(html_file_name)
        response = open(url)
        text = response.read()
        soup = BeautifulSoup(text, 'lxml')
        # see some of the html
        # print(soup.div)

        dictionary = {'nbformat': 4, 'nbformat_minor': 1, 'cells': [], 'metadata': {}}
        for d in soup.findAll("div"):
            if 'class' in d.attrs.keys():
                for clas in d.attrs["class"]:
                    if clas in ["text_cell_render", "input_area"]:
                        # code cell
                        if clas == "input_area":
                            cell = {}
                            cell['metadata'] = {}
                            cell['outputs'] = []
                            cell['source'] = [d.get_text()]
                            cell['execution_count'] = None
                            cell['cell_type'] = 'code'
                            dictionary['cells'].append(cell)

                        else:
                            cell = {}
                            cell['metadata'] = {}

                            cell['source'] = [d.decode_contents()]
                            cell['cell_type'] = 'markdown'
                            dictionary['cells'].append(cell)
        open(save_file_name, 'w').write(json.dumps(dictionary))

    @staticmethod
    def normalize_path(path_str: str):
        """Normalizes any input path across Windows/Linux/macOS/WSL"""
        if not path_str:
            return ''

        path_str = path_str.strip().strip('"').strip("'")

        # Convert Windows-style (C:\...) to Unix-like on WSL
        if platform.system().lower() == 'linux' and re.match(r'^[A-Za-z]:\\', path_str):
            drive, tail = path_str[0], path_str[3:].replace('\\', '/')
            return f"/mnt/{drive.lower()}/{tail}"

        # Convert WSL (/mnt/c/...) to Windows style (optional)
        if platform.system().lower() == 'windows' and path_str.startswith("/mnt/"):
            match = re.match(r"/mnt/([a-z])/([^:]*)", path_str)
            if match:
                drive, tail = match.groups()
                tail_converted = tail.replace('/', '\\')
                return f"{drive.upper()}:\\{tail_converted}"

        # Fallback to absolute resolved path
        return str(Path(path_str).expanduser().resolve())
