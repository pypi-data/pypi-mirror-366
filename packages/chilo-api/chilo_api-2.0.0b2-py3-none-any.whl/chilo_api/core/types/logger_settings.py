from typing_extensions import TypedDict, Any, NotRequired, Callable, List, Union, Dict


class LoggerSettings(TypedDict, total=False):
    condition: NotRequired[Callable[[Any], bool]]
    level: NotRequired[str]
