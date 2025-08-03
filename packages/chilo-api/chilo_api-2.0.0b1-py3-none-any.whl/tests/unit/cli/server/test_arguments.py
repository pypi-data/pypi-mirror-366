import unittest
from chilo_api.cli.server.arguments import ServerArguments


class MockArgs:
    api = 'api_rest.py'
    host = '127.0.0.1'
    port = 3000
    reload = False
    verbose = False


class MockApi:
    api_type = 'rest'
    api = 'api_rest.py'
    host = '127.0.0.1'
    port = 3000
    reload = False
    verbose = False
    timeout = None
    handlers = 'tests/mocks/handlers'
    protobufs = 'tests/unit/mocks/grpc/protobufs'
    openapi_validate_request = False
    openapi_validate_response = False
    enable_reflection = True


class ArgumentsTest(unittest.TestCase):

    def test_route(self):
        mock_args = MockArgs()
        mock_api = MockApi()
        server_args = ServerArguments(mock_args, mock_api)  # type: ignore
        self.assertEqual(server_args.handlers, mock_api.handlers)
        self.assertEqual(server_args.protobufs, mock_api.protobufs)
        self.assertEqual(server_args.api_type, mock_api.api_type)
        self.assertIsInstance(server_args.api_config, MockApi)
