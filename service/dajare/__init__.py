"""
Hello World REST Application.

Assembles all the REST endpoints.
"""

import os

from flask import Flask

from .api import api


this_dir = os.path.dirname(__file__)
static_folder = os.path.abspath(os.path.join(this_dir, '..', 'static'))

app = Flask(__name__,
            static_url_path='/static',
            static_folder=static_folder)
api.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)
