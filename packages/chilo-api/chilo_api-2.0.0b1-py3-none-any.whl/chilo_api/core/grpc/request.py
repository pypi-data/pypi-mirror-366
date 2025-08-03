from typing import Any
from google.protobuf.json_format import MessageToDict

from chilo_api.core.grpc.wsgi import GRPCWSGIPlaceHolder
from chilo_api.core.rest.request import Request


class GRPCRequest(Request):
    '''
    A class to represent a gRPC request.
    Attributes
    ----------
    body: Any
        The request body in its dict format
    raw: Any
        The raw request data as sent by the client
    context: Any
        The gRPC context for the request, used for metadata and other gRPC-specific features
    '''

    def __init__(self, rpc_request, context) -> None:
        super().__init__(wsgi=GRPCWSGIPlaceHolder(), timeout=None)  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__wsgi = GRPCWSGIPlaceHolder()  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__timeout = 100000  # NOSONAR Timeout is not applicable in gRPC context
        self.__text = ''  # NOSONAR Text is not applicable in gRPC context
        self.__route = ''  # NOSONAR Route is not applicable in gRPC context
        self.__path_params = {}  # NOSONAR Path parameters are not applicable in gRPC context
        self.__context = context
        self.__rpc_request = rpc_request

    @property
    def body(self) -> Any:
        try:
            return MessageToDict(self.__rpc_request, preserving_proto_field_name=True)
        except Exception:
            return self.raw

    @property
    def raw(self) -> Any:
        return self.__rpc_request

    @property
    def context(self) -> Any:
        return self.__context

    @context.setter
    def context(self, context: Any) -> None:
        pass  # Context is managed by gRPC and does not require setting in this normalizer NOSONAR
