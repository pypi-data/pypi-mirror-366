""" Movie manager utilities --
    - Sort movies files/folders (in year buckets)
    - Sort movie listings (by year/IMDB)
    - Attach genre tag to movies from Wiki
    - Summarize movie files/folders
    - List metadata of all released movies, given a year & language
"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

from __future__ import absolute_import

import asyncio
import json
import os
import re
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path
from typing import Dict, List, Literal, Union
from urllib.parse import quote

import aiohttp
import pandas as pd
import pycountry
import requests
from bs4 import BeautifulSoup
from configs import CONFIG, SECRETS
from imdb import IMDb
from tmdbv3api import Discover, Genre, Movie, TMDb
from utils.dtypesutils import DtypesOpsHandler
from utils.fileopsutils import FileopsHandler
from utils.logger import Logger
from utils.textclean import PreprocessText
from utils.timeutils import CalculateTime


class MoviesSorter():
    """Class for sorting movies files/folders/listings"""
    def __init__(self):
        pass  # initialized class with empty constructor

    def _form_sorting_folders(self, start_year: int, year_interval: int):
        """Form the list of year-wise sorting folders"""
        current_year = datetime.now().year
        years_list = [str(yr) for yr in range(start_year, current_year+1, year_interval)]
        if current_year % year_interval:
            years_list.append(str(current_year))
        len_range = range(len(years_list))
        sorting_folders = ["-".join(years_list[i:i+2]) for i in len_range if i+1 in len_range]
        return sorting_folders

    def _find_bracket_indices(self, text_str: str):
        """Find indices of all valid bracket pairs in a str"""
        bracket_pairs = {'(': ')', '{': '}', '[': ']', '<': '>'}
        bracket_stack, bracepair_ids = [], []
        for idx, char in enumerate(text_str):
            if char in bracket_pairs.keys():
                bracket_stack.append((char, idx))
            elif char in bracket_pairs.values():
                if bracket_stack and char == bracket_pairs[bracket_stack[-1][0]]:
                    bracepair_ids.append((bracket_stack.pop()[1], idx))
        return bracepair_ids

    def _find_enclosed_content(self, name_str: str, search_idx: int = -1):
        """Find contents within bracket pairs of a movie name. The current convenion is:
        - last bracket pairs indicate movie year
        - second last bracket pairs indicate movie genre

        Examples:
        - *Black Swan {psychological horror} [2010]*
        - *Boys Don't Cry {biographical} [1999]*

        Args:
            name_str (str): Movie name string
            search_idx (int, optional): Index of the bracket pair to extract. Defaults to -1 (the last pair).

        Returns:
            fetched_contents (int, str, optional): The extracted content as a string or integer if possible
                or `None` if no matching bracket pair is found.
        """
        bracepair_ids = self._find_bracket_indices(name_str)
        if not bracepair_ids:
            return None
        search_idx = search_idx if abs(search_idx) <= len(bracepair_ids) else 0
        bracket_ids = bracepair_ids[search_idx]
        fetched_contents = name_str[bracket_ids[0] + 1: bracket_ids[1]]

        # Attempt to return content as integer, otherwise return string
        try:
            return int(fetched_contents)
        except ValueError:
            return fetched_contents.strip() if fetched_contents.strip() else None

    def _sort_movie_groups(self, movie_groups: dict, sort_by='year'):
        """Sort list of movies in `movie_groups` by `sort_by` param"""
        sorted_groups = {}
        sort_idx = 1 if sort_by == 'year' else 2
        for _key, _movies in movie_groups.items():
            _key = re.sub(r'^\n\n+', '', _key)
            movies_with_yrimdb = [DtypesOpsHandler.flatten_iterable((s, re.split(r'\s+', re.sub(
                r'[^0-9\.]', ' ', s))[1:-2])) for s in _movies]
            movies_with_yrimdb = [(s[0], eval(s[1]), eval(s[2])) for s in movies_with_yrimdb]
            movies_with_yrimdb = sorted(movies_with_yrimdb, key=lambda x: x[sort_idx], reverse=True)  # sort the list
            sorted_groups[_key] = [s[0] + '\n\n' if s[0][-1] != '\n' else s[0] for s in movies_with_yrimdb]
        return sorted_groups

    def _create_formatted_movies_str(self, movie_groups: dict):
        """Create formatted movie str from list of movies in `movie_groups`"""
        format_movies_str = ""
        for _key, _movies in movie_groups.items():
            tot_movies = len(_movies)
            format_movies_str += _key if isinstance(_key, str) else ""
            item_nos = [f'{i}. ' for i in range(1, 1 + tot_movies)]
            format_movies_str += "".join([x + y for x, y in zip(item_nos, _movies)])
        return format_movies_str

    def _find_folder_for_movie(self, sorting_folders: List[str], movie_year: Union[int, None]):
        """Find the specific sorting folder for a given movie year"""
        if not (sorting_folders and movie_year):
            return ''
        for id, f in enumerate(sorting_folders):
            try:
                st_yr, end_yr = f.split('-')
                if int(st_yr) <= movie_year < int(end_yr):
                    return f
            except Exception:
                return ''

    def sort_movie_folders(self, base_folder: str, start_year: int, year_interval: int):
        """Sort individual movies to respective folders"""
        base_items = os.listdir(base_folder)
        sorting_folders = self._form_sorting_folders(start_year, year_interval)
        if not (sorting_folders and base_items):
            return
        [os.makedirs(os.path.join(base_folder, f), exist_ok=True) for f in sorting_folders]
        movieyrs_dict = {f: self._find_folder_for_movie(sorting_folders, self._find_enclosed_content(f, -1)) for f in base_items}
        movement_status = {"moved": [], "not_moved": []}  # dict to track movement success of movie folders
        for movie_name, sort_folder in movieyrs_dict.items():
            try:
                shutil.move(os.path.join(base_folder, movie_name), os.path.join(base_folder, sort_folder))
                movement_status["moved"].append(movie_name)
            except Exception:
                movement_status["not_moved"].append(movie_name)
        # Finally remove the empty folders from 'sorting_folders', which are left adter the sorting process
        for f in sorting_folders:
            try:
                os.rmdir(os.path.join(base_folder, f))
            except Exception:
                pass
        self.movement_status = movement_status

    def sort_movie_listing(self, movie_list: str, sort_by='year', to_save=True):
        """Sort list of movies, saved as a text file. Sorting to be done by 'year' or 'imdb'."""
        movement_status, sorted_movies = "", ""
        movies_listing, movie_groups, group_name = FileopsHandler.import_file(movie_list), {}, ""
        movie_names = re.split(r'\d+\.\s', movies_listing)  # split on numberings -- "1.", "2." etc.
        movie_names = DtypesOpsHandler.flatten_iterable(
            [[s + '[IMDB]' if not i and 'IMDB' in _str else s for i, s in enumerate(
                _str.split('[IMDB]', 1))] for _str in movie_names])  # split on '[IMDB]'
        movie_names = [x + y if bool(re.fullmatch(r'\n+', y)) else x for x, y in zip(movie_names[:-1], movie_names[1:])]
        movie_names = [s for s in movie_names if s and not bool(re.fullmatch(r'\n+', s))]
        # Group the movies category-wise
        for idx, _name in enumerate(movie_names):
            if any(_char.isdigit() for _char in _name):
                movie_groups.update({group_name: [_name]}) if not movie_groups.get(
                    group_name) else movie_groups[group_name].append(_name)
            else:
                group_name = _name
        movie_groups = self._sort_movie_groups(movie_groups, sort_by)  # Sort 'movie_groups' based on 'sort_by' param
        sorted_movies = self._create_formatted_movies_str(movie_groups)  # final formatted movies
        tot_movies = sum([len(v) for k, v in movie_groups.items()])
        movement_status = "Total {} movie names sorted successfully !".format(tot_movies)
        if to_save:
            _dir, _filename = os.path.dirname(movie_list), os.path.splitext(os.path.basename(movie_list))[0]
            FileopsHandler.save_files(sorted_movies, _dir, f'{_filename}_sorted', '.txt')
        self.sorted_movies, self.movement_status = sorted_movies, movement_status


class MovieLibraryManager:
    """
    Utility class for managing and analyzing a local movie library.

    Features
    -----------
    - Tag movie folders or files with genre information scraped from Wikipedia.
    - Traverse folder structures to identify movie folders and standalone video files.
    - Count and summarize statistics, e.g.:
        * Total movies in the base path
        * Number of movie folders with external subtitles
        * Total folders and standalone video files
        * Total movies by year, category and file types
    - Provide utilities for cleaning and standardizing movie file and folder names.

    Args
    -----------
    base_path (str):
        Root path containing movie folders/files. It can also be a .json/.csv/.excel file \
        containing movie names to search for. In the later case when the path is a file, it should have \
        'movie_name' as a key/column containing the movie names.

    to_untag (bool, optional):
        Whether to remove genre tags instead of attaching them (useful for debugging). Defaults to `False`.

    genre_brackets (str, optional):
        Type of bracket used for attaching or untagging genres. \
        Valid options: ['round', 'curly', 'square', 'angle']. Defaults to 'curly'.

    exclude_subdirs (list, optional):
        List of subdirectories to exclude when searching the \
        base folder for movie files. An empty list (default) means all subdirs will be searched.

    year_interval (int, optional):
        Interval of years for grouping movies in the summary. Defaults to 10.

    save_summary (str, bool, optional):
        Format of saving the summary output. Defaults to 'excel'.
        - Valid options: ['json', 'excel', True, False].
        - If `True`, both 'json' and 'excel' version will be saved.
        - If `False`, output summary won't be saved.

    genre_map (dict, optional):
        A dict to rename some genres, used in `summarize()` and `move()` utilities. Defaults to empty dict.

    write_logs (bool, optional):
        Whether to maintain a log file in the working directory. Defaults to `True`.

    dry_run (bool, optional):
        If `True`, shows what would happen without changing files. Defaults to `False`.

    Usage
    -----------
    The generator utilities `tag()` and `summarize()` can be called via api as well as terminal.
    Below shows a sample terminal call.
    ```python
    base_path = '/Users/ratnadipadhikari/Desktop/Movies'
    manager = MovieLibraryManager(base_path, summary_path=True, write_logs=False, dry_run=True)
    for _ in manager.tag():
        pass
    print(json.dumps(manager.summary, indent=2))
    ```
    """
    def __init__(
        self,
        base_path: str,
        to_untag=False,
        genre_brackets: Literal['round', 'curly', 'square', 'angle'] = 'curly',
        exclude_subdirs=[],
        year_interval=10,
        genre_map: Dict = {},
        save_summary: Literal['json', 'excel', True, False] = 'excel',
        write_logs=True,
        dry_run=False,
    ):
        """The `MovieLibraryManager` class init module"""
        self.base_url = "https://en.wikipedia.org"
        self.base_path = base_path
        self.to_untag = to_untag
        self.bracket_type = genre_brackets
        self.exclude_subdirs = exclude_subdirs
        self.year_interval = year_interval or 10  # default 10
        self.genre_map = genre_map
        self.save_summary = save_summary
        self.dry_run = dry_run
        self.bracket_map = {
            'round': ('(', ')'),
            'curly': ('{', '}'),
            'square': ('[', ']'),
            'angle': ('<', '>'),
        }  # bracket-pairs map dict

        # +++++++++++++++++
        # Write log immediately outside 'generic-helpers' (if write_logs=True)
        global LOGGER
        log_path = Path(os.getcwd())
        log_path = Path(*log_path.parts[:log_path.parts.index('generic-helpers')]) \
            if 'generic-helpers' in log_path.parts else log_path
        log_path = str(log_path / "movie_manager.log") if write_logs else ""
        LOGGER = Logger(log_path, timestamp=True, mode="w")

    def log(self, msg):
        """Prints to terminal, and yields to browser if streaming."""
        print(msg, flush=True)
        return msg  # Return so it can be yielded if needed

    def find_common_word(self, names: List[str]):
        """Return the word (token) common to all strings in the given list of movies if
        - no year info or same year for all the
        - there is a word common across all the names in the list
        - else return `False`.

        Examples
        -----------
        ```
            ['Sholay', 'Sholay', 'Sholay-21', 'Sholay 1975'] --> 'Sholay'
            ['Aradhana 1969', 'Aradhana 1969', 'Aradhana DvD'] --> 'Aradhana'
            ['Bombay movie', 'Bombay  CD DvD', 'Bombay'] --> 'Bombay'
            ['Sholay', 'Aradhana 1969', 'Bombay'] --> False
            ['Sarkar [2005]', 'Sarkar Raj[2008]'] --> False
        ```

        """
        if not names:
            return False
        clean_names = [
            PreprocessText().spaces_clean(
                PreprocessText().spchars_remove(
                    self.clean_movie_name(s), ' ', False
                )
            ) for s in names
        ]
        word_sets = [set(s.lower().split()) for s in clean_names]
        common_words = set.intersection(*word_sets)
        if common_words:
            found_years = set(
                DtypesOpsHandler.flatten_iterable(
                    [y for name in clean_names if (y := self.extract_years(name))])
            )
            if len(found_years) > 1:
                return False
            return max(common_words, key=len)
        return False

    @staticmethod
    def is_junk(file_name, junk_list=[]):
        """Identifies if a file is a junk one, based on listed junk files in 'junk_list'"""
        return any(fnmatch(file_name.lower(), pattern.lower()) for pattern in junk_list)

    def scan_all_movies(self, file_exts=[]):
        """
        Recursively walks through the master path and find movie folders and/or standalone files
        matching given file extensions.

        Args:
            file_exts (list, optional): list of file extensions to match \
                (e.g. ['.mp4', '.avi'], ['.srt', '.sub]). Defaults to an empty list, in which case returns \
                empty movie paths list.

        Returns:
            movie_paths (list of str): List containing paths to movie folders/files.
        """
        movie_paths, drop_list = [], []
        # +++++++++++++++++
        # Check if the path is a .json/.csv/.excel file
        if os.path.isfile(self.base_path):
            movie_file = FileopsHandler().import_file(self.base_path)
            movie_paths = (
                [mname for d in movie_file if (mname := d.get('movie_name')) and pd.notna(mname)]
                if isinstance(movie_file, list)
                else movie_file['movie_name'].dropna().tolist()  # for dataframe containing movie names
                if isinstance(movie_file, pd.DataFrame) and 'movie_name' in movie_file.columns
                else []
            )
            return movie_paths

        # +++++++++++++++++
        # Walks through the base dir and find all movie folders/files
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_subdirs]  # exclude subdirs (need-based)
            for d in dirs:
                d_path = os.path.join(root, d)
                d_items = [f for f in os.listdir(d_path) if not self.is_junk(f, CONFIG["junk_files"])]
                has_no_subdirs = all(not os.path.isdir(os.path.join(d_path, e)) for e in d_items)
                video_files = [
                    f for f in d_items
                    if os.path.splitext(f)[-1].lower() in file_exts
                ]
                # +++++++++++++++++
                # Append 'd_path' only if has no subdirs and either has common
                # file names or at least some non-video files
                if has_no_subdirs:
                    if video_files and self.find_common_word([d] + d_items) or 0 < len(video_files) < len(d_items):
                        movie_paths.append(d_path)
            for f in files:
                if os.path.splitext(f)[-1].lower() in file_exts:
                    movie_paths.append(os.path.join(root, f))
        # +++++++++++++++++
        # Drops redundant duplicate containers/files/folders
        [drop_list.append(p) for p in movie_paths if os.path.exists(p) and os.path.dirname(p) in movie_paths]
        movie_paths = [p for p in movie_paths if p not in set(drop_list)]
        return movie_paths

    def fetch_soup(self, path, cache=set()):
        """Fetch Wikipedia path, return soup and disambiguation flag."""
        url, soup, is_disambig = f'{self.base_url}{path}', None, False
        if url in cache:
            return soup, is_disambig, cache
        try:
            resp = requests.get(url, timeout=10)
            cache.add(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                is_disambig = bool(soup.find('table', {'id': 'disambigbox'}))
        except Exception as e:
            print(f" → Failed fetching {url}: {e}")
        finally:
            return soup, is_disambig, cache

    def extract_years(self, movie_name):
        """Extracts years from a movie name.

        Rules
        -----------
        An year is a 4 digit num, surrounded by non-digit boundaries.
        Entire movie name being a 4-digit number (e.g. '2012') is not a year.

        Examples
        -----------
        - Drishyam 2 (2022) --> 2022
        - Dhoom.1[2004]Dvdrip-x264.mkv --> 2004
        - Gangs Of Wasseypur 2 2012.mkv --> 2012
        - 2012.mp4 --> ''
        - Titanic.DvdRip.avi --> ''
        ```

        Returns
        -----------
        List of years (empty if none).
        """
        clean_name = self.clean_movie_name(movie_name)
        yrs = [int(y) for y in re.findall(r'(?<!\d)\d{4}(?!\d)', clean_name, re.UNICODE)]
        return [] if len(yrs) == 1 and clean_name.strip() == str(yrs[0]) else yrs

    @staticmethod
    def extract_genre(soup):
        """Find genre phrase in the first paragraph of `soup`."""
        try:
            for para in soup.select('p'):
                text = para.get_text(" ", strip=True)
                lower_text = text.lower()
                if any(term in lower_text for term in ('drama', 'play', 'film')):
                    match = re.search(r"is (?:a|an) .*?\b(drama|play|film)\b", text, re.IGNORECASE)
                    if match:
                        # Reject if 'novel' or 'story' occur before the match
                        span_start = match.start()
                        prior_text = lower_text[:span_start]
                        if re.search(r"\b(novel|story)\b", prior_text):
                            continue
                        return match.group(0)
        except Exception:
            return None

    def explore_links(self, soup, depth):
        """Follow links in a disambig page, searching for genre. Prioritize film-like links first."""
        if not soup or depth <= 0:
            return None

        links = soup.select('div.mw-parser-output > ul li a[href]')
        sorted_links = sorted(
            links,
            key=lambda a: -int(bool(re.search(r'film', a.get('href', '').lower() + a.get_text().lower())))
        )  # prioritize links mentioning 'film'

        for link in sorted_links:
            href = link.get('href')
            if href.startswith('/wiki/'):
                new_soup, is_disambig, _ = self.fetch_soup(href)
                genre = self.extract_genre(new_soup)
                if genre:
                    return genre
                if is_disambig:
                    genre = self.explore_links(new_soup, depth - 1)
                    if genre:
                        return genre
        return None

    @staticmethod
    def generate_wiki_titles(movie_name):
        """Produce likely Wikipedia titles for a given movie name."""
        # movie_name = re.sub(r'[^A-Za-z0-9 ]+', '', movie_name)
        # movie_name = re.sub(r'\s+', ' ', movie_name).strip()
        parts = movie_name.split(" ")
        lang_search_list = [w.title() for w in CONFIG["genre_strip_words"] if w not in (
            'film', 'is a', 'is an', 'language', 'movie')]  # common languages to search for
        wiki_titles = []
        if parts[-1].isdigit() and len(parts[-1]) == 4:
            base = quote("_".join(parts[:-1]))
            year = parts[-1]
            wiki_titles += [
                f'/wiki/{base}_{year}',
                f'/wiki/{base}_({year}_film)',
                f'/wiki/{base}_(film)',
                f'/wiki/{base}_film',
                f'/wiki/{base}',
                *[
                    variant
                    for w in lang_search_list
                    for variant in (
                        f'/wiki/{base}_({year}_{w}_film)',
                        f'/wiki/{base}_({w}_film)',
                    )
                ]
            ]
        else:
            base = quote("_".join(parts))
            wiki_titles += [
                f'/wiki/{base}_(film)',
                f'/wiki/{base}_film',
                f'/wiki/{base}',
                *[
                    f'/wiki/{base}_({w}_film)'
                    for w in lang_search_list
                ]
            ]
        # wiki_titles = DtypesOpsHandler.flatten_iterable(wiki_titles)
        return wiki_titles

    def search_wikipedia(self, movie_name):
        """
        Search Wikipedia for genre phrase, handling:
        - disambiguation pages
        - following all relevant links
        - caching
        - recursion depth
        """
        cache_set, max_depth = set(), 2

        # +++++++++++++++++
        # Main search
        wiki_titles = self.generate_wiki_titles(movie_name)
        for curr_title in wiki_titles:
            soup, is_disambig, cache_set = self.fetch_soup(curr_title, cache_set)
            genre_phrase = self.extract_genre(soup)
            if genre_phrase:
                return genre_phrase
            if is_disambig:
                genre_phrase = self.explore_links(soup, max_depth)
                if genre_phrase:
                    return genre_phrase
        return ''

    def check_genre_and_year(self, movie_name, genre, year):
        """Check existence of 'genre' and 'year' in the given movie name. These should exist as surrounded
        by valid brackets, provided in `self.genre_brackets`.
        """
        IsEnclosed = lambda text: False if text is None or pd.isna(text) or str(text).strip() == "" else any(
            re.search(rf"{re.escape(lb)}\s*{re.escape(str(text))}\s*{re.escape(rb)}", movie_name, re.IGNORECASE)
            for lb, rb in self.bracket_map.values()
        )
        return IsEnclosed(genre), IsEnclosed(year)

    def untag_movie_name(self, movie_name, strip_name, tag_type='year'):
        """Strip tag (year|genre info) from a movie name (helpful for debug purpose)"""
        if not strip_name:
            return movie_name
        if tag_type != 'year' and not isinstance(strip_name, str):
            return movie_name
        replce_dict = {
            f"{l}{strip_name}{r}": ""
            for (l, r) in self.bracket_map.values()
        }
        return (
            re.sub(
                r'\s+',
                ' ',
                PreprocessText().replace_string(
                    movie_name, replce_dict
                )
            ).strip()
        )

    @staticmethod
    def clean_movie_name(name):
        """Clean original movie names, e.g.
            - Bohemian.Rhapsody[2018].mkv -> Bohemian Rhapsody 2018
            - Oppenheimer.720p.BluRay [2023].mkv -> Oppenheimer 2023
            - 2012.720p.DvDRip [2009].avi -> 2012 2013
        """
        return (
            " ".join(
                w
                for w in re.sub(
                    r'[\[\]\(\)\._–—]',
                    ' ',
                    re.sub(
                        r'\.\w+$', '', name.strip()
                    ) if any(name.strip().lower().endswith(ext) for ext in CONFIG["video_exts"]) else name.strip()
                ).split()
                if w.lower() not in CONFIG["movie_strip_words"]
            ).strip()
        )  # '\.\w+$' matches a dot followed by alphanumerics to the end (removes .mkv, .mp4, .avi, etc.)

    @staticmethod
    def clean_genre_phrase(phrase):
        """Clean extracted movie genre phrase"""
        processor = PreprocessText()
        return (
            re.sub(
                r'^[^\w\d]+|[^\w\d]+$',
                '',
                processor
                .spaces_clean(
                    re.sub(
                        r'\d+|\[[^\]]*\]|\([^\)]*\)|\{[^\}]*\}',
                        '',
                        processor.replace_string(
                            phrase.lower(),
                            dict.fromkeys(CONFIG["genre_strip_words"], '')
                        )
                    )
                )
            )
            .strip()
        ) or ''

    def get_all_movies(self, movie_paths: list):
        """Fetch all movies from 'movie_paths' list and creates a df with columns: `name|language|genre|year`"""
        movies_list = []
        language_list = [w for w in CONFIG["genre_strip_words"] if w not in (
            'film', 'is a', 'is an', 'language', 'movie')]
        for path in movie_paths:
            movie_name = os.path.basename(path)
            year, genre = (
                y if isinstance(y := MoviesSorter()._find_enclosed_content(movie_name, -1), int) else
                int(m.group()) if (m := re.search(r'\b(19|20)\d{2}\b', movie_name)) else None,
                g if isinstance(g := MoviesSorter()._find_enclosed_content(movie_name, -2), str) else ''
            )

            getFileExt = lambda p: os.path.splitext(p)[-1].lower()  # lambda to get file ext from path name
            file_exts = (
                getFileExt(path) if os.path.isfile(path)
                else ', '.join(
                    set([getFileExt(f) for f in os.listdir(path) if getFileExt(f) in CONFIG["video_exts"]])
                )
            )

            cleaned_name = self.untag_movie_name(movie_name, year) if year else movie_name
            cleaned_name = self.clean_movie_name(
                self.untag_movie_name(cleaned_name, genre, 'genre') if genre else cleaned_name
            )

            # ---------------------------------
            # Regex matches a language name only if:
            #   - it appears as a standalone word
            #   - OR is separated by special characters (. _ - / etc.)
            #
            # Examples matched:
            #   "English_Movies"     → English
            #   "All.English.Movies" → English
            #
            # Examples NOT matched:
            #   "Indiana.Jones"            → (no match for "Indian")
            #   "Bengalian_Movies"         → (no match for "Bengali")
            #
            # Prevents false positives where language appears inside other words.
            # ---------------------------------
            movie_language = (
                x[0] if (x := [
                    lang.title()
                    for lang in language_list
                    if re.search(
                        rf'(^|[ ./_\-\(\)\[\]\{{\}}]){re.escape(lang)}($|[ ./_\-\(\)\[\]\{{\}}])',
                        path,
                        re.IGNORECASE
                    )
                ]) else ''
            )

            # ---------------------------------
            # The regex matches ... examples
            # ---------------------------------

            movies_list.append({
                "movie_name": movie_name,
                "clean_name": cleaned_name,
                "language": movie_language,
                "genre": genre,
                "year": year,
                "file_exts": file_exts,
                "path": path
            })
        return movies_list

    @staticmethod
    def append_year_to_name(original_name, year):
        """Append year in square brackets at the end of the movie name"""
        if not year:
            return original_name
        file_ext = next((ext for ext in CONFIG["video_exts"] if original_name.lower().endswith(ext)), None)
        year_tag = f"[{year}]"
        return (
            original_name.replace(file_ext, f' {year_tag}{file_ext}')
            if file_ext
            else original_name + f' {year_tag}'
        )

    def append_genre_to_name(self, original_name, genre):
        """Append genre, enclosed in supported brackets before the year"""
        if not genre:
            return original_name
        b_left, b_right = self.bracket_map.get(self.bracket_type, ('{', '}'))
        genre_tag = f"{b_left}{genre}{b_right}"
        year_match = re.search(r'(\[\d{4}\]|\(\d{4}\))', original_name)
        if year_match:
            year_str = year_match.group(0)
            new_name = original_name.replace(year_str, f'{genre_tag} {year_str}')
        else:
            file_ext = next((ext for ext in CONFIG["video_exts"] if original_name.lower().endswith(ext)), None)
            new_name = (
                original_name.replace(file_ext, f' {genre_tag}{file_ext}')
                if file_ext
                else original_name + f' {genre_tag}'
            )
        return new_name

    def move_and_rename(self, old_path, new_path):
        """Move entire contents to new path"""
        if self.dry_run:
            yield self.log(f' → DRY RUN: Would move "{old_path}" → "{new_path}"')
            return
        if not os.path.exists(old_path):
            yield self.log(f' → Non-existent path, not moved: "{old_path}" → "{new_path}"')
            return
        if os.path.isdir(old_path):
            shutil.move(old_path, new_path)
            yield self.log(f' → Folder moved: "{old_path}" → "{new_path}"')
        else:
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(old_path, new_path)
            yield self.log(f' → File moved: "{old_path}" → "{new_path}"')

    def save(self, save_file=None, save_name=''):
        """Save generated summary (default) or other file"""
        save_file = save_file if save_file is not None else self.summary
        save_name = save_name if save_name else 'movies_summary'
        file_type = '.json' if isinstance(save_file, (list, dict)) else \
            '.xlsx' if isinstance(save_file, pd.DataFrame) else None
        summary_path = (
            (self.base_path if os.path.isdir(self.base_path) else os.path.dirname(self.base_path))
            if self.save_summary in ('json', 'excel', True) else False
        )

        # +++++++++++++++++
        # Save file if exists else by default save summary
        FileopsHandler().save_files(
            save_file,
            summary_path,
            save_name,
            file_type,
            default=str,
            indent=4,
            header=True,
            index=False
        )

    def tag(self):
        """Main movie genre tagger utility"""
        start_time = time.monotonic()
        utility_phrase = 'untagging' if self.to_untag else 'tagging'
        movie_paths = self.scan_all_movies(CONFIG["video_exts"])
        total_movies = len(movie_paths)
        tag_key_phrase = 'untagged_name' if self.to_untag else 'tagged_name'
        self.summary = []
        yield self.log(f"--------Found {total_movies} movie folders/files !")

        # +++++++++++++++++
        # Process each movie path
        for cntr, movie_path in enumerate(movie_paths, 1):
            original_name = os.path.basename(movie_path)
            yield self.log(f'\n--------[{cntr}/{total_movies}]Processing movie → "{original_name}"')
            genre_cleaned = MoviesSorter()._find_enclosed_content(original_name, -2)
            if self.to_untag:
                genre_cleaned = genre_cleaned if isinstance(genre_cleaned, str) else ''
                if genre_cleaned:
                    tag_status = 'stripped'
                else:
                    tag_status = 'skipped'
                    yield self.log(' → No genre info found. Skipping untagging.')
                    continue
                new_name = self.untag_movie_name(original_name, genre_cleaned, 'genre')
                new_path = os.path.join(os.path.dirname(movie_path), new_name)
            else:
                if isinstance(genre_cleaned, str):
                    tag_status, new_name, new_path = 'skipped', original_name, movie_path
                    yield self.log(f' → Genre: "{genre_cleaned}" already exists. Skipping search.')
                else:
                    cleaned_name = self.clean_movie_name(original_name)
                    genre_phrase = self.search_wikipedia(cleaned_name)
                    genre_cleaned = self.clean_genre_phrase(genre_phrase)
                    tag_status = 'tagged' if genre_cleaned else 'skipped'

                    yield self.log(f' → Genre phrase from Wiki: "{genre_phrase}"')
                    yield self.log(f' → Cleaned genre: "{genre_cleaned}"')

                    new_name = self.append_genre_to_name(original_name, genre_cleaned)
                    new_path = os.path.join(os.path.dirname(movie_path), new_name)

                    if not genre_cleaned:
                        yield self.log(" → No genre found. Skipping rename.")
            # +++++++++++++++++
            if genre_cleaned and os.path.isdir(self.base_path):
                yield from self.move_and_rename(movie_path, new_path)
            self.summary.append({
                "movie_name": original_name,
                tag_key_phrase: new_name,
                "original_path": movie_path,
                "new_path": new_path,
                "genre": genre_cleaned,
                "status": tag_status
            })

        # +++++++++++++++++
        # save summary file
        for t in ('json', 'excel'):
            if self.save_summary in (t, True):
                self.save() if t == 'json' else self.save(pd.DataFrame(self.summary))
        yield self.log(f"\n--------Finished tagging of {total_movies} movie folders/files !")

        yield self.log(f"--------Genre {utility_phrase} completed in time: {CalculateTime().get_runtime(start_time)}")

    def summarize(self):
        """Provide various summary stats for movie files/folders in the base path, such as:
            - Total no. of movies in the base path
            - No. of movie folders with external subtitles
            - Total folders and standalone video files
            - Total movies by year, category and file types
        """
        yield self.log("--------Summarizing existing movies in the given path !")
        folder_paths, file_paths = [], []
        movie_paths = self.scan_all_movies(CONFIG["video_exts"])
        if not movie_paths:
            yield self.log("--------No movie file/folder found inside the base path !")
            yield self.log("--------Finished movies summarization !")
            self.summary = {}
            return
        movies_with_subs = self.scan_all_movies(CONFIG["subtitle_exts"])
        [file_paths.append(p) if os.path.isfile(p) else folder_paths.append(p) for p in movie_paths]
        total_movies, total_movies_with_subs = len(movie_paths), len(movies_with_subs)
        total_folders, total_files = len(folder_paths), len(file_paths)

        # +++++++++++++++++
        # Contents extraction from movies
        contents_dict = {
            (mname := os.path.basename(f)): (
                MoviesSorter()._find_enclosed_content(mname, -1),
                MoviesSorter()._find_enclosed_content(mname, -2)
            )
            for f in movie_paths
        }
        # +++++++++++++++++
        # Fetching year-groups & genre categories
        all_years = sorted([v[0] if isinstance(v[0], int) else 9999 for k, v in contents_dict.items()])
        all_genres = sorted([v[1] if isinstance(v[1], str) else '#no_genre_info' for k, v in contents_dict.items()])
        start_year = all_years[0] - all_years[0] % self.year_interval  # find start_year as the closest lower multiple of year_interval # type: ignore
        year_groups = MoviesSorter()._form_sorting_folders(start_year, self.year_interval)
        year_groups = [yrg if (yrg := MoviesSorter()._find_folder_for_movie(year_groups, k)) else '#no_year_info' for k in all_years]
        # +++++++++++++++++
        # Count # movies in each year-group, genre-group, extension-group
        year_counts, genre_counts = Counter(v for v in year_groups), Counter(v for v in all_genres)
        ext_counts = Counter()
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_subdirs]
            ext_counts.update(
                os.path.splitext(f.lower())[-1]
                for f in files
                if os.path.splitext(f.lower())[-1] in CONFIG["video_exts"]
            )
        # +++++++++++++++++
        # Get all movies in the base path as a df
        all_movies = self.get_all_movies(movie_paths)

        # +++++++++++++++++
        # Now form the summary dict and save
        self.summary = {
            "base_path": self.base_path,
            "movies": total_movies,
            "movie_folders": total_folders,
            "standalone_movie_files": total_files,
            "movies_with_subtitles": total_movies_with_subs,
            "unique_genres": len([k for k in genre_counts if k != '#no_genre_info']),
            "year_groups": dict(year_counts),
            "extension_groups": dict(ext_counts),
            "genre_groups": dict(genre_counts)
        }
        # +++++++++++++++++
        # save summary file
        self.save_summary = True if self.save_summary else False
        self.save()
        self.save(pd.DataFrame(all_movies), 'all_movies')

        yield self.log("--------Finished movies summarization !")

    def move(self):
        """Move renamed movies from old path to new path from an .csv|.xlsx file

        The file should have columns: `movie_name|clean_name|language|genre|year|file_exts|path`
        """
        start_time = time.monotonic()
        yield self.log("--------Started mover process for movies in the given file !")
        mover_data = FileopsHandler().import_file(self.base_path)
        if not isinstance(mover_data, pd.DataFrame):
            self.log("--------[Exit] Please check the input file !")
            return
        if not set(CONFIG["mover_data_cols"]) <= set(mover_data.columns):
            self.log("--------[Exit] The input file lacks required columns!")
            return
        mover_data = mover_data.dropna(subset=['movie_name', 'path']).fillna('')
        total_movies = mover_data.shape[0]
        self.summary = []
        yield self.log(f"--------Found {total_movies} movies to move !")

        # +++++++++++++++++
        # Process each movie
        for cntr, (_, crow) in enumerate(mover_data.iterrows(), 1):
            movie_name, clean_name, genre, year, old_path = [crow[col] for col in CONFIG["mover_data_cols"]]
            yield self.log(f'\n--------[{cntr}/{total_movies}]Processing movie → "{movie_name}"')
            clean_name = clean_name if clean_name else movie_name
            year = int(eval(str(year))) if year else ''
            genre = g_new if (g_new := self.genre_map.get(genre, genre)) else genre  # to change genres

            # -------validate file ext-------
            fext_1 = s if (s := Path(movie_name).suffix).lower() in CONFIG["video_exts"] else ''
            fext_2 = s if (s := Path(clean_name).suffix).lower() in CONFIG["video_exts"] else ''
            new_name = clean_name if fext_1 == fext_2 else re.sub(fext_2, '', clean_name) + fext_1

            # -------Append genre & year (if not already)-------
            has_genre, has_year = self.check_genre_and_year(clean_name, genre, year)
            new_name = self.append_year_to_name(new_name, year) if not has_year else new_name
            new_name = self.append_genre_to_name(new_name, genre) if not has_genre else new_name
            new_path = os.path.join(os.path.dirname(old_path), new_name)

            # -------move file/folder-------
            move_status = (
                'to_move' if self.dry_run
                else 'moved' if os.path.exists(os.path.dirname(new_path))
                else "skipped"
            )
            yield from self.move_and_rename(old_path, new_path)

            # +++++++++++++++++
            # Now form the summary
            self.summary.append({
                "movie_name": movie_name,
                "clean_name": clean_name,
                "new_name": new_name,
                "old_path": old_path,
                "new_path": new_path,
                "status": move_status
            })
        # +++++++++++++++++
        # save summary file
        for t in ('json', 'excel'):
            if self.save_summary in (t, True):
                self.save() if t == 'json' else self.save(pd.DataFrame(self.summary))
        yield self.log(f"\n--------Mover process completed for {total_movies} movie files/folders !")

        yield self.log(f"--------Mover process completed in time: {CalculateTime().get_runtime(start_time)}")


class MovieFetcher:
    """
    Utility class to fetch and compile movie metadata from TMDb and IMDb based on language and year.

    Features
    ----------
    - Discover and list movies released in a given year and language using TMDb API.
    - Enrich movie data with runtime, genres, and IMDb|TMDB rating.
    - Support exporting movie metadata as pandas DataFrame or JSON.

    Args
    ----------
    api_key (str) : Your TMDb API key for authenticating requests.
    year (int) : Year of movie release to filter on.
    language (str, optional) : ISO 639-1 language code for filtering original language (default is 'en').
    en_info (bool, optional) : Whether to extract title & overview info in English. Defaults to `False`.
    sort_by (str, optional) : Field to sort the movie list by. One of 'rating', 'release_date', or 'runtime'. Defaults to 'rating'.
    max_pages (int, optional) : Number of result pages to fetch from TMDb. Defaults to 2.

    Usage
    -----------
    The movie metadata fetcher utility `fetch()`can be called via api as well as terminal.
    Below shows a sample terminal call.
    ```python
    fetcher = MovieFetcher(language='hi', api_key='YOUR_TMDB_API_KEY')  # Hindi
    all_movies = fetcher.fetch(2023, max_pages=2)
    movies_df = pd.DataFrame(all_movies)
    print(movies_df[['title', 'genres', 'rating']].head())
    ```
    """
    def __init__(
        self,
        api_key='',
        year: int = '',
        language: str = 'en',
        en_info=True,
        sort_by='rating',
        max_pages=2
    ):
        self.imdb = IMDb()
        self.tmdb = TMDb()
        self.discover_api = Discover()
        self.movie_api = Movie()
        self.genre_api = Genre()
        self.tmdb.api_key = SECRETS.get("tmdb_api_key") or api_key
        self.tmdb.language = getattr(lang, 'alpha_2') if (lang := self._resolve_language(language)) else ''
        self.en_info = en_info
        self.sort_by = sort_by
        self.year = year if year else datetime.now().year
        self.max_pages = max_pages
        self.run_time = ''
        self.all_movies = []
        self.genre_map = self._load_genres()

    def _load_genres(self):
        """Preload genre id → name mapping"""
        return {g.id: g.name for g in self.genre_api.movie_list()}

    def _map_genres(self, genre_ids: list):
        """Map genre IDs to a comma-separated genre string"""
        if not genre_ids:
            return ''
        genres = {self.genre_map.get(gid) for gid in genre_ids}
        clean_genres = sorted(g for g in genres if g)  # remove nulls
        return ', '.join(clean_genres)

    @staticmethod
    def _resolve_language(language: str):
        """Resolves a language string to both ISO code and full name"""
        lang = language.strip().lower()
        try:
            lang = pycountry.languages.lookup(lang)
            if hasattr(lang, 'alpha_2'):
                return lang
        except Exception:
            return {}

    def _get_runtime(self, movie_id: int):
        """Fetch runtime via TMDb movie details"""
        run_time, details = None, self.movie_api.details(movie_id)
        mins = details.get('runtime')
        if mins:
            td = timedelta(minutes=mins)
            hr, rem = divmod(td.seconds, 3600)
            mins, _ = divmod(rem, 60)
            run_time = f'{hr}h {mins}m'
        return run_time

    async def _fetch_imdb_rating(self, session: aiohttp.ClientSession, imdb_id: str):
        """Internal coroutine to fetch IMDb rating from a movie's IMDb ID"""
        url = f'https://www.imdb.com/title/{imdb_id}/'
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        imdb_meta = dict.fromkeys(['title', 'overview', 'rating', 'vote_count'])
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    data = json.loads(script_tag.string)
                    agg = data.get("aggregateRating", {})
                    imdb_meta = {
                        "title": data.get("name"),
                        "overview": data.get("description"),
                        "rating": float(r) if (r := agg.get("ratingValue")) else None,
                        "vote_count": int(v) if (v := agg.get("ratingCount")) else None
                    }
        except Exception:
            pass
        return imdb_id, imdb_meta

    async def _fetch_all_imdb_ratings(self, imdb_ids: list[str]):
        """Internal coroutine to fetch ratings for a list of IMDb IDs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_imdb_rating(session, imdb_id) for imdb_id in imdb_ids]
            results = await asyncio.gather(*tasks)
        return dict(results)

    def _process_movie(self, movie):
        """Extract metadata for a movie"""
        credits = self.movie_api.credits(movie.id)
        movie_cast = ', '.join([member["name"] for member in credits.get("cast", [])._json][:5])
        runtime = self.movie_api.details(movie.id, {}).get('runtime')
        movie_type = 'short' if runtime and runtime <= 40 else 'feature'
        countries = self.movie_api.details(movie.id, {}).get("production_countries", [])
        countries = ', '.join([c["iso_3166_1"] for c in countries]) if countries else ''

        return {
            "title": movie.title,
            "imdb_id": self.movie_api.external_ids(movie.id).get("imdb_id"),
            "tmdb_id": movie.id,
            "release_date": movie.release_date,
            "countries": countries,
            "runtime": self._get_runtime(movie.id),
            "type": movie_type,
            "rating": movie.vote_average,
            "vote_count": movie.vote_count,
            "rating_source": 'tmdb',
            "cast": movie_cast,
            "overview": movie.overview,
            "original_language": movie.original_language,
            "genres": self._map_genres(movie.genre_ids)
        }

    def fetch(self):
        """
        Fetches movies by year and language with enriched metadata info that includes \
            title, release-date, run-time, rating (TMDb fallback) and overview.
        """
        start_time = time.monotonic()
        all_movies, batch_size, sleep_per_batch = [], 10, 2.5  # batching to prevent API throttling
        for batch_start in range(1, self.max_pages + 1, batch_size):
            batch_end = min(batch_start + batch_size, self.max_pages + 1)

            for page in range(batch_start, batch_end):
                query = {
                    "primary_release_year": self.year,
                    "with_original_language": self.tmdb.language,
                    "page": page,
                    "sort_by": "popularity.desc"
                }
                (
                    all_movies
                    .append(r) if (r := self.discover_api.discover_movies(query))
                    and getattr(r, "results", None) else None
                )

            if batch_end < self.max_pages + 1:
                time.sleep(sleep_per_batch)

        all_movies = list(chain.from_iterable(all_movies))  # flatten list of pages → list of movie objects

        # Parallel process using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=32) as executor:
            self.all_movies = list(executor.map(self._process_movie, all_movies))

        # Get IMDb metadata and patch only non-null IMDb fields
        imdb_ids = [movie["imdb_id"] for movie in self.all_movies]
        imdb_meta = asyncio.run(self._fetch_all_imdb_ratings(imdb_ids))
        for movie in self.all_movies:
            meta_info = imdb_meta.get(movie.get("imdb_id"))
            if not meta_info:
                continue
            keys_check = ['title', 'overview', 'rating', 'vote_count'] if self.en_info else ['rating', 'vote_count']
            movie.update({k: v for k, v in meta_info.items() if k in keys_check and v is not None})
            if meta_info.get("rating") is not None:
                movie["rating_source"] = 'imdb'

        # Sort fetched movie list based on the sort_by param
        sort_fallbacks = {"rating": 0.0, "runtime": '', "release_date": ''}
        self.all_movies.sort(
            key=lambda m: sv if (sv := m.get(self.sort_by)) else sort_fallbacks.get(self.sort_by, ''),
            reverse=True
        )
        self.run_time = CalculateTime().get_runtime(start_time)


if __name__ == '__main__':
    print('python version:', sys.version)
    print('cwd:', os.getcwd())
