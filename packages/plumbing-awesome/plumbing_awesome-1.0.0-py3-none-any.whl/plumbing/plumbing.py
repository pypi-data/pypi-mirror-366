from typing import Any, Self
from typing_extensions import Callable


class Plumber:
    def __init__(self, value: Any) -> None:
        self.value = value

    def pipe(self, function: Callable[[Any], Any]) -> Self:
        self.value = function(self.value)
        return self
