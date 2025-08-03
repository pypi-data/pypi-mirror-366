from typing import Any, Dict, List, Callable, Union


class GRPCPipeline:
    '''
    A class to represent the gRPC pipeline for processing requests and responses.
    This class defines the steps involved in handling a request, including validation, endpoint execution, and response handling.
    Attributes
    ----------
    steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        A list of steps in the pipeline, where each step is a dictionary containing
        a method to execute and a boolean indicating whether the step should run.
    stream_steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        A list of steps for streaming requests, similar to `steps` but  tailored for streaming operations
    should_run_endpoint: bool
        A boolean indicating whether the endpoint step should run.
    should_run_before_all: bool
        A boolean indicating whether the before_all step should run.
    should_run_when_auth_required: bool
        A boolean indicating whether the when_auth_required step should run.
    should_run_after_all: bool
        A boolean indicating whether the after_all step should run.
    Methods
    ----------
    endpoint(request: Any, response: Any, endpoint: Any):
        Executes the endpoint logic for the request.
    before_all(request: Any, response: Any, endpoint: Any):
        Runs the before_all logic, typically used for pre-processing the request.
    when_auth_required(request: Any, response: Any, endpoint: Any):
        Runs the when_auth_required logic, typically used for handling authentication.
    after_all(request: Any, response: Any, endpoint: Any):
        Runs the after_all logic, typically used for post-processing the response.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__before_all: Callable[[Any, Any, Any], None] = kwargs.get('before_all', lambda request, response, endpoint: None)
        self.__when_auth_required: Callable[[Any, Any, Any], None] = kwargs.get('when_auth_required', lambda request, response, endpoint: None)
        self.__after_all: Callable[[Any, Any, Any], None] = kwargs.get('after_all', lambda request, response, endpoint: None)

    @property
    def steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required},
            {'method': self.endpoint, 'should_run': self.should_run_endpoint},
            {'method': self.after_all, 'should_run': self.should_run_after_all},
        ]

    @property
    def stream_steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required}
        ]

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
        if not endpoint.requires_auth:
            return
        self.__when_auth_required(request, response, endpoint.requirements)

    @property
    def should_run_after_all(self) -> bool:
        return self.__after_all is not None and callable(self.__after_all)

    def after_all(self, request: Any, response: Any, endpoint: Any) -> None:
        self.__after_all(request, response, endpoint.requirements)
