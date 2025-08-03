from unittest import mock, TestCase
from unittest.mock import Mock, patch

from chilo_api.cli.server.grpc import GRPCServer
from chilo_api.core.types.server_settings import ServerSettings
from chilo_api.cli.logger import CLILogger
from chilo_api.core.router import Router


class MockArgs:
    api = 'api_grpc.py'
    host = '127.0.0.1'
    port = 3000
    handlers = 'tests/unit/mocks/grpc/handlers/valid'
    protobufs = 'tests/unit/mocks/grpc/protobufs'
    api_config = Mock(spec=Router)
    enable_reflection = True


class GRPCServerTest(TestCase):

    def setUp(self):
        self.mock_server_args = Mock(spec=ServerSettings)
        self.mock_server_args.handlers = 'test/handlers'
        self.mock_server_args.port = 50051
        self.mock_server_args.protobufs = 'test/protobufs'
        self.mock_server_args.api_config = Mock(spec=Router)
        self.mock_server_args.enable_reflection = True
        self.mock_logger = Mock(spec=CLILogger)
        self.grpc_server = GRPCServer(self.mock_server_args, self.mock_logger)

    @mock.patch('chilo_api.cli.server.grpc.grpc.server')
    def test_run_server_success(self, mock_grpc_server):
        server_args = MockArgs()
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        grpc_server.run()
        mock_grpc_server.assert_called_once()
        self.assertTrue(grpc_server.__dict__['_GRPCServer__dynamic_servers'])

    def test_run_server_failure_no_handlers(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/mocks/grpc/bad/handlers'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No gRPC handlers found in the specified directory', str(context.exception))

    def test_run_server_failure_no_modules(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/rest/handlers/valid'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No gRPC endpoint methods found in the provided modules.', str(context.exception))

    def test_run_server_failure_bad_proto_file(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/bad_proto'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('Error generating gRPC code for', str(context.exception))

    def test_run_server_failure_bad_service_definition(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/bad_service'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No matching servicer class found for', str(context.exception))

    def test_run_server_failure_duplicate_method_definition(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/duplicate_method'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('already exists', str(context.exception))

    @patch('grpc.server')
    def test_keyboard_interrupt_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock(side_effect=KeyboardInterrupt())
        mock_server.stop = Mock()
        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()

        mock_server.stop.assert_called_once_with(grace=3)
        self.mock_logger.log_message.assert_called_once_with('Server stopped by user.')

    @patch('grpc.server')
    def test_general_exception_handling(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        test_exception = Exception("Test connection error")
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock(side_effect=test_exception)
        mock_server.stop = Mock()
        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()

        mock_server.stop.assert_called_once_with(grace=0)
        self.mock_logger.log_message.assert_called_once_with(f'An error occurred while running the gRPC server: {test_exception}')

    @patch('grpc.server')
    def test_add_insecure_port_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        port_exception = Exception("Port already in use")
        mock_server.add_insecure_port = Mock(side_effect=port_exception)
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):

                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.stop.assert_called_once_with(grace=0)
        self.mock_logger.log_message.assert_called_once_with(f'An error occurred while running the gRPC server: {port_exception}')

    @patch('grpc.server')
    def test_wait_for_termination_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        termination_exception = Exception("Server terminated unexpectedly")
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock(side_effect=termination_exception)
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()
        mock_server.stop.assert_called_once_with(grace=0)
        self.mock_logger.log_message.assert_called_once_with(f'An error occurred while running the gRPC server: {termination_exception}')

    @patch('grpc.server')
    def test_successful_server_run_no_exceptions(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock()
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()
        mock_server.stop.assert_not_called()
        self.mock_logger.log_message.assert_not_called()

    def test_exception_message_formatting(self):
        test_cases = [
            (ConnectionError("Connection refused"), "Connection refused"),
            (OSError("Address already in use"), "Address already in use"),
            (ValueError("Invalid port number"), "Invalid port number"),
            (RuntimeError("Server initialization failed"), "Server initialization failed")
        ]

        for exception, expected_message in test_cases:
            with patch('grpc.server') as mock_grpc_server:
                mock_server = Mock()
                mock_grpc_server.return_value = mock_server
                mock_server.add_insecure_port = Mock()
                mock_server.start = Mock(side_effect=exception)
                mock_server.stop = Mock()
                self.mock_logger.reset_mock()

                with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
                    with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                            with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                                with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                                    with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                        self.grpc_server.run()

                expected_log_message = f'An error occurred while running the gRPC server: {expected_message}'
                self.mock_logger.log_message.assert_called_once_with(expected_log_message)
