from typing import Any, Dict, List, Callable, Optional, Union
from chilo_api.core.validator import Validator


class RestPipeline:
    '''    
    A class to represent the REST pipeline for processing requests and responses.
    This class defines the steps involved in handling a request, including validation, endpoint execution, and response handling.
    Attributes
    ----------
    steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        A list of steps in the pipeline, where each step is a dictionary containing
        a method to execute and a boolean indicating whether the step should run.
    stream_steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        A list of steps for streaming requests, similar to `steps` but tailored for streaming operations
    before_all: Callable[[Any, Any, Any], None]
        A method to run before all other steps, typically used for pre-processing the request.
    when_auth_required: Callable[[Any, Any, Any], None]
        A method to run when authentication is required, typically used for handling authentication logic.
    after_all: Callable[[Any, Any, Any], None]
        A method to run after all other steps, typically used for post-processing the response.
    validator: Validator
        An instance of the Validator class used for validating requests and responses against OpenAPI specifications.
    openapi_validate_request: Optional[bool]
        A flag indicating whether to validate requests against OpenAPI specifications.
    openapi_validate_response: Optional[bool]
        A flag indicating whether to validate responses against OpenAPI specifications.
    Methods
    ----------
    endpoint(request: Any, response: Any, endpoint: Any):
        Executes the endpoint logic for the request.
    before_all(request: Any, response: Any, endpoint: Any):
        Runs the before_all logic, typically used for pre-processing the request.
    when_auth_required(request: Any, response: Any, endpoint: Any):
        Runs the when_auth_required logic, typically used for handling authentication.
    run_request_validation(request: Any, response: Any, endpoint: Any):
        Validates the request against OpenAPI specifications if `openapi_validate_request` is False.
    run_request_validation_openapi(request: Any, response: Any, endpoint: Any):
        Validates the request against OpenAPI specifications if `openapi_validate_request` is True.
    run_response_validation(request: Any, response: Any, endpoint: Any):
        Validates the response against OpenAPI specifications if `openapi_validate_response` is False.
    run_response_validation_openapi(request: Any, response: Any, endpoint: Any):
        Validates the response against OpenAPI specifications if `openapi_validate_response` is True.
    after_all(request: Any, response: Any, endpoint: Any):
        Runs the after_all logic, typically used for post-processing the response.
    should_run_endpoint: bool
        A boolean indicating whether the endpoint step should run.
    should_run_before_all: bool
        A boolean indicating whether the before_all step should run.
    should_run_when_auth_required: bool
        A boolean indicating whether the when_auth_required step should run.
    should_run_request_validation: bool
        A boolean indicating whether the run_request_validation step should run.
    should_run_request_validation_openapi: bool
        A boolean indicating whether the run_request_validation_openapi step should run.
    should_run_response_validation: bool
        A boolean indicating whether the run_response_validation step should run.
    should_run_response_validation_openapi: bool
        A boolean indicating whether the run_response_validation_openapi step should run.
    should_run_after_all: bool
        A boolean indicating whether the after_all step should run. 
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__openapi_validate_request: Optional[bool] = kwargs.get('openapi_validate_request')
        self.__openapi_validate_response: Optional[bool] = kwargs.get('openapi_validate_response')
        self.__before_all: Callable[[Any, Any, Any], None] = kwargs.get('before_all', lambda request, response, endpoint: None)
        self.__when_auth_required: Callable[[Any, Any, Any], None] = kwargs.get('when_auth_required', lambda request, response, endpoint: None)
        self.__after_all: Callable[[Any, Any, Any], None] = kwargs.get('after_all', lambda request, response, endpoint: None)
        self.__validator: Validator = Validator(**kwargs)
        self.__validator.auto_load()

    @property
    def steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required},
            {'method': self.run_request_validation, 'should_run': self.should_run_request_validation},
            {'method': self.run_request_validation_openapi, 'should_run': self.should_run_request_validation_openapi},
            {'method': self.endpoint, 'should_run': self.should_run_endpoint},
            {'method': self.run_response_validation, 'should_run': self.should_run_response_validation},
            {'method': self.run_response_validation_openapi, 'should_run': self.should_run_response_validation_openapi},
            {'method': self.after_all, 'should_run': self.should_run_after_all},
        ]

    @property
    def stream_steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required}
        ]  # pragma: no cover

    @property
    def should_run_endpoint(self) -> bool:
        return True

    def endpoint(self, request: Any, response: Any, endpoint: Any) -> None:
        endpoint.run(request, response)

    @property
    def should_run_before_all(self) -> bool:
        return self.__before_all is not None and callable(self.__before_all)

    def before_all(self, request: Any, response: Any, endpoint: Any) -> None:
        self.__before_all(request, response, endpoint.requirements)

    @property
    def should_run_when_auth_required(self) -> bool:
        return self.__when_auth_required is not None and callable(self.__when_auth_required)

    def when_auth_required(self, request: Any, response: Any, endpoint: Any) -> None:
        if not ((self.__openapi_validate_request and self.__validator.request_has_security(request)) or endpoint.requires_auth):
            return  # pragma: no cover
        self.__when_auth_required(request, response, endpoint.requirements)

    @property
    def should_run_request_validation(self) -> bool:
        return not self.__openapi_validate_request

    def run_request_validation(self, request: Any, response: Any, endpoint: Any) -> None:
        if not endpoint.has_requirements:
            return
        self.__validator.validate_request_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_request_validation_openapi(self) -> bool:
        return bool(self.__openapi_validate_request)

    def run_request_validation_openapi(self, request: Any, response: Any, endpoint: Any) -> None:
        self.__validator.validate_request_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_response_validation(self) -> bool:
        return not self.__openapi_validate_response

    def run_response_validation(self, request: Any, response: Any, endpoint: Any) -> None:
        if not endpoint.has_required_response:
            return
        self.__validator.validate_response_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_response_validation_openapi(self) -> bool:
        return bool(self.__openapi_validate_response)

    def run_response_validation_openapi(self, request: Any, response: Any, endpoint: Any) -> None:
        self.__validator.validate_response_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_after_all(self) -> bool:
        return self.__after_all is not None and callable(self.__after_all)

    def after_all(self, request: Any, response: Any, endpoint: Any) -> None:
        self.__after_all(request, response, endpoint.requirements)
