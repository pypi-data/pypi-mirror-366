"""Flask apis to perform automated movie manager operations"""

import json
import os
import traceback

from devs.moviemanager import MovieLibraryManager, MoviesSorter
from flask import Blueprint, Response, abort, jsonify, request, stream_with_context

bp = Blueprint('movie', __name__)


@bp.route('/moviefolders_sorter', methods=['GET'], strict_slashes=False)
def moviefolders_sorter():
    """Movies folder sorter api func
    URL = http://127.0.0.1:1501/moviefolders_sorter?base_path=/path&start_year=1950&year_interval=10
    """
    try:
        response = {}
        movie_sorter = MoviesSorter()  # call the movies sorter class
        # Access input params
        base_path = request.args.get('base_path')
        start_year = int(request.args.get('start_year'))
        year_interval = int(request.args.get('year_interval'))
        movie_sorter.sort_movie_folders(base_path, start_year, year_interval)
        response = movie_sorter.movement_status
    except Exception:
        response = {
            "message": "Failed in sorting movies in the base folder !",
            "error": traceback.format_exc()
        }
    return jsonify(response)


@bp.route('/movielist_sorter', methods=['GET'], strict_slashes=False)
def movielist_sorter():
    """Movies list sorter api func
    URL = http://127.0.0.1:1501/movielist_sorter?base_path=/path/file.txt&sort_by=imdb
    """
    try:
        response = {}
        movie_sorter = MoviesSorter()  # call the movies sorter class
        # Access input params
        base_path = request.args.get('base_path')
        sort_by = request.args.get('sort_by')
        movie_sorter.sort_movie_listing(base_path, sort_by)
        response = movie_sorter.movement_status
    except Exception:
        response = {
            "message": "Failed in sorting movies list",
            "error": traceback.format_exc()
        }
    return jsonify(response)


@bp.route('/moviegenre_tagger', methods=['GET'], strict_slashes=False)
def moviegenre_tagger():
    """Movies genre tagger api func
    URLs:
        http://127.0.0.1:1501/moviegenre_tagger?base_path=/path&exclude_subdirs=subdirA,subdirB&untag=True&save_summary=excel&logs=True&dry_run=True
        http://127.0.0.1:1501/moviegenre_tagger?base_path=/pathB&untag=True&save_summary=True&logs=True&dry_run=True
        http://127.0.0.1:1501/moviegenre_tagger?base_path=/pathB&untag=True&save_summary=False&logs=True&dry_run=True
    """
    try:
        # +++++++++++++++++
        # Access input params
        base_path = request.args.get('base_path')
        to_untag = eval(request.args.get('untag', 'False'))
        genre_brackets = request.args.get('brackets', 'curly')
        exclude_subdirs = [x.strip() for x in request.args.get('exclude_subdirs', '').split(',') if x.strip()]
        save_summary = {'json': 'json', 'excel': 'excel', 'True': True}.get(
            request.args.get('save_summary', False),
            False
        )
        write_logs = eval(request.args.get('logs', 'True'))
        dry_run = eval(request.args.get('dry_run', 'True'))

        # +++++++++++++++++
        # Invoke the movies manager class
        def generate():
            movie_manager = MovieLibraryManager(
                base_path, to_untag=to_untag, genre_brackets=genre_brackets, exclude_subdirs=exclude_subdirs,
                save_summary=save_summary, write_logs=write_logs, dry_run=dry_run
            )
            for line in movie_manager.tag():
                yield line + "\n"  # stream logs from tag()
            yield "\n" + "=" * 40 + "\n"
            yield "SUMMARY:\n"
            yield json.dumps(movie_manager.summary, indent=4)  # yield the final summary at the end
        # +++++++++++++++++
        # Return the response
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception:
        response = {
            "message": "Failed to attach genre tags to the movies in the base folder!",
            "error": traceback.format_exc()
        }
        return jsonify(response)


@bp.route('/movie_summarizer', methods=['GET'], strict_slashes=False)
def movie_summarizer():
    """Movies metadata summarizer api func
    URLs:
        http://127.0.0.1:1501/movie_summarizer?base_path=/path&year_interval=10&save_summary=False
        http://127.0.0.1:1501/movie_summarizer?base_path=/pathsubdirA,subdirB&year_interval=10&save_summary=False
    """
    try:
        # +++++++++++++++++
        # Access input params
        base_path = request.args.get('base_path')
        exclude_subdirs = [x.strip() for x in request.args.get('exclude_subdirs', '').split(',') if x.strip()]
        year_interval = int(request.args.get('year_interval', '10'))
        save_summary = eval(request.args.get('save_summary', 'False'))

        # +++++++++++++++++
        # Invoke the movies manager class
        def generate():
            movie_manager = MovieLibraryManager(
                base_path, exclude_subdirs=exclude_subdirs, year_interval=year_interval,
                save_summary=save_summary, write_logs=False
            )
            # Stream logs from summarize()
            for line in movie_manager.summarize():
                yield line + "\n"
            # Yield the final summary at the end
            yield "\n" + "=" * 40 + "\n"
            yield "SUMMARY:\n"
            yield json.dumps(movie_manager.summary, indent=4)
        # +++++++++++++++++
        # Get the response
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception:
        response = {
            "message": "Failed to summarize existing movies in the base folder !",
            "error": traceback.format_exc()
        }
    return jsonify(response)


@bp.route('/movie_mover', methods=['POST'], strict_slashes=False)
def movie_mover():
    """Movies mover (from .xlsx|.csv info) api func
    URL = http://127.0.0.1:1501/movie_mover?save_summary=True&dry_run=True\n
    payload = {
        "base_path": '/path/file.xlsx',
        "genre_brackets": 'curly',
        "genre_map": {
            "comedy-drama": 'comedy',
            "action drama": 'action',
            "action-drama": 'action'
        }
    }

    """
    try:
        response = {}
        # +++++++++++++++++
        # Access input params
        payload = request.json
        base_path = payload.get("base_path")
        genre_brackets = payload.get("genre_brackets", 'curly')
        genre_map = payload.get("genre_map", {})
        save_summary = eval(request.args.get('save_summary', 'False'))
        dry_run = eval(request.args.get('dry_run', 'True'))

        # +++++++++++++++++
        # Invoke the movies manager class
        def generate():
            movie_manager = MovieLibraryManager(
                base_path, genre_brackets=genre_brackets, genre_map=genre_map,
                save_summary=save_summary, dry_run=dry_run
            )
            # Stream logs from summarize()
            for line in movie_manager.move():
                yield line + "\n"
        # +++++++++++++++++
        # Get the response
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception:
        response = {
            "message": "Failed to move movies from the supplied input file !",
            "error": traceback.format_exc()
        }
    return jsonify(response)
