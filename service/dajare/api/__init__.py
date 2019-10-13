"""This module collects all namespaces under a single API."""
from flask_restplus import Api

from .generate import api as generate_api

api = Api(
    title='Dajare Generation API',
    version='0.1',
    description='A simple example REST API for Dajare generation',
)

api.add_namespace(generate_api)
