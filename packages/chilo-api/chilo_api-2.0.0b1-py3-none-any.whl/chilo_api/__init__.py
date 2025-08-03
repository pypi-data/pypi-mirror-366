from typing import Union

from chilo_api.core.router import Router as Chilo
from chilo_api.core import logger as logger
from chilo_api.core.logger.decorator import log as log
from chilo_api.core.requirements import requirements
from chilo_api.core.rest.request import Request as RestRequest
from chilo_api.core.rest.response import Response as RestResponse
from chilo_api.core.grpc.request import Request as GRPCRequest
from chilo_api.core.grpc.response import Response as GRPCResponse

Request = Union[RestRequest, GRPCRequest]
Response = Union[RestResponse, GRPCResponse]
