"""Flask API app creator module"""

from __future__ import absolute_import

import os
import sys
from pathlib import Path

from flask import Flask

from . import moviemanageapis

sys.path = [p for i in range(1, 4) if (p := os.path.abspath(Path(__file__).parents[i])) not in sys.path] + sys.path


def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False

    from . import calctimeapis

    app.register_blueprint(moviemanageapis.bp)
    app.register_blueprint(calctimeapis.bp)

    @app.route("/isalive")
    def isalive():
        return '<b style="color:blue;">Alive</b> - Helper APIs'

    return app
