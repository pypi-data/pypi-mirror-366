from typing import Any, Callable, Type, Optional, Union

import grpc

from chilo_api.core.rest.response import Response
from chilo_api.core.grpc.wsgi import GRPCWSGIPlaceHolder


class GRPCResponse(Response):
    '''
    A class to represent a gRPC response.
    Attributes
    ----------
    body: Any
        The return body of the response in its original format
    code: int
        Status code to be returned to requester
    grpc_code: grpc.StatusCode
        gRPC status code corresponding to the HTTP status code
    context: Any
        gRPC context for response handling
    has_errors: bool
        Determines if the response contains errors
    rpc_response: Any
        The gRPC response object to be returned
    Methods
    ----------
    set_error(key_path: str, message: str):
        Sets an error in the response with a consistent format
    get_response() -> Any:
        Returns the gRPC response object, setting the context code and details if there are errors.
        This method is used to finalize the response before sending it back to the client.
        It checks if there are errors or if the body is None, returning an empty response in those cases.
        Otherwise, it returns the gRPC response with the body data.
    '''

    def __init__(self, **kwargs) -> None:
        super().__init__(wsgi=GRPCWSGIPlaceHolder(), environ={}, server_response={})  # Overwrite WSGI behavior for gRPC context NOSONAR
        self.__code: int = 200  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__cors: Optional[Union[bool, str]] = None  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__compress: bool = False  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__mimetype: str = ''  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__server_response: dict = {}  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__wsgi: GRPCWSGIPlaceHolder = GRPCWSGIPlaceHolder()  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__environ: dict = {}  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__headers: dict = {}  # NOSONAR Overwrite WSGI behavior for gRPC context
        self.__body: Optional[Any] = None
        self.__rpc_response: Type[Any] = kwargs['rpc_response']
        self.__context: Optional[Any] = kwargs.get('context', None)
        self.__has_errors: bool = False
        self.__http_grpc_code_mapping: dict[int, grpc.StatusCode] = {
            200: grpc.StatusCode.OK,
            400: grpc.StatusCode.INVALID_ARGUMENT,
            401: grpc.StatusCode.UNAUTHENTICATED,
            404: grpc.StatusCode.NOT_FOUND,
            408: grpc.StatusCode.DEADLINE_EXCEEDED,
            429: grpc.StatusCode.RESOURCE_EXHAUSTED,
            403: grpc.StatusCode.PERMISSION_DENIED,
            500: grpc.StatusCode.INTERNAL,
            501: grpc.StatusCode.UNIMPLEMENTED,
            502: grpc.StatusCode.UNAVAILABLE,
            503: grpc.StatusCode.UNAVAILABLE,
            504: grpc.StatusCode.DEADLINE_EXCEEDED,
            505: grpc.StatusCode.UNIMPLEMENTED,
            511: grpc.StatusCode.UNAVAILABLE
        }

    @property
    def body(self) -> Any:
        return self.__body

    @body.setter
    def body(self, body) -> None:
        self.__body = body

    @property
    def code(self) -> int:
        if self.__code == 200 and self.has_errors:
            self.__code = 400
        return self.__code

    @code.setter
    def code(self, code: int) -> None:
        self.__code = code

    @property
    def grpc_code(self) -> grpc.StatusCode:
        return self.__http_grpc_code_mapping.get(self.code, grpc.StatusCode.UNKNOWN)

    @property
    def context(self) -> Any:
        return self.__context

    @context.setter
    def context(self, context: Any) -> None:
        pass  # Context is managed by gRPC and does not require setting in this normalizer NOSONAR

    @property
    def has_errors(self) -> bool:
        return self.__has_errors

    @property
    def rpc_response(self) -> Callable[..., Any]:
        return self.__rpc_response

    def set_error(self, key_path: str, message: str) -> None:
        self.__has_errors = True
        self.__context.set_details(f'{key_path}: {message}')  # type: ignore

    def get_response(self) -> Any:
        self.context.set_code(self.grpc_code)
        if self.has_errors or self.body is None:
            return self.rpc_response()  # Return an empty response if there are errors
        return self.rpc_response(**self.body)
