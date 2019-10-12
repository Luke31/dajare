"""This module implements prediction API."""
from collections import namedtuple

from flask_restplus import Namespace, Resource, fields

from prometheus_client import Histogram

from dajare.model import GenerationModel

api = Namespace('generate', description='Generation related operations')

generation = api.model('Generation', {
    'output': fields.Boolean(description='The final dajare')
})

GenerateParam = namedtuple('GenerateParam', 'name type required help')

generate_parser = api.parser()
generate_parser.add_argument('input', type=str, required=True)

LATENCY = Histogram('request_latency_seconds', 'Request Latency')


@api.route('/')
class Generate(Resource):
    """Resource providing model prediction."""

    @api.expect(generate_parser)
    @api.marshal_with(generation)
    @LATENCY.time()
    def post(self):
        """Call model prediction for the given parameters.

        :returns: Prediction instance.
        """
        # Parses and validates input arguments
        # In case of validation error HTTP 400 will be returned
        data = generate_parser.parse_args()
        return GenerationModel.predict(data), 200
