from typing import Any, ContextManager, Dict, List, Optional, Tuple, TypeVar, Union

from furiosa.native_runtime import (
    Axis,
    DataType,
    FuriosaRuntimeError,
    FuriosaRuntimeWarning,
    Model,
    ModelSource,
    Tensor,
    TensorArray,
    TensorDesc,
)

__all__ = [
    "FuriosaRuntimeError",
    "FuriosaRuntimeWarning",
    "ModelSource",
    "Axis",
    "DataType",
    "Tensor",
    "TensorArray",
    "TensorDesc",
    "Model",
    "Runtime",
    "Runner",
    "Submitter",
    "Receiver",
    "create_runner",
    "create_queue",
]

class Runtime(ContextManager["Runtime"]):
    _Self = TypeVar("_Self", bound=Runtime)
    def __new__(
        cls,
        device: Optional[str] = None,
    ) -> Runtime: ...
    def create_runner(
        self,
        model: ModelSource,
        *,
        worker_num: Optional[int] = None,
        batch_size: Optional[int] = None,
        compiler_config: Optional[dict[str, Any]] = None,
    ) -> Runner: ...
    def create_queue(
        self,
        model: ModelSource,
        *,
        worker_num: Optional[int] = None,
        batch_size: Optional[int] = None,
        input_queue_size: Optional[int] = None,
        output_queue_size: Optional[int] = None,
        compiler_config: Optional[dict[str, Any]] = None,
    ) -> Tuple[Submitter, Receiver]: ...
    def close(self) -> bool: ...
    def __enter__(self: _Self) -> _Self: ...
    def __exit__(self, type, value, traceback) -> None: ...

class Runner(ContextManager["Runner"]):
    _Self = TypeVar("_Self", bound=Runner)
    @property
    def model(self) -> Model: ...
    def allocate(self) -> List[Tensor]: ...
    def run(self, inputs: Union[Tensor, List[Tensor]]) -> List[Tensor]: ...
    def run_with(self, output_names: List[str], inputs: Dict[str, Tensor]) -> List[Tensor]: ...
    def close(self) -> bool: ...
    def __enter__(self: _Self) -> _Self: ...
    def __exit__(self, type, value, traceback) -> None: ...

class Submitter(ContextManager["Submitter"]):
    _Self = TypeVar("_Self", bound=Submitter)
    @property
    def model(self) -> Model: ...
    def allocate(self) -> List[Tensor]: ...
    def submit(
        self,
        inputs: Union[Tensor, List[Tensor]],
        context: Optional[Any] = None,
    ) -> None: ...
    def close(self) -> bool: ...
    def __enter__(self: _Self) -> _Self: ...
    def __exit__(self, type, value, traceback) -> None: ...

class Receiver(ContextManager["Receiver"]):
    _Self = TypeVar("_Self", bound=Receiver)
    @property
    def model(self) -> Model: ...
    def recv(
        self,
        timeout: Optional[Union[int, float]] = None,
    ) -> Tuple[Optional[Any], List[Tensor]]: ...
    def close(self) -> bool: ...
    def __enter__(self: _Self) -> _Self: ...
    def __exit__(self, type, value, traceback) -> None: ...
    def __iter__(self: _Self) -> _Self: ...
    def __next__(self) -> Tuple[Optional[Any], List[Tensor]]: ...

def create_runner(
    model: ModelSource,
    *,
    device: Optional[str] = None,
    worker_num: Optional[int] = None,
    batch_size: Optional[int] = None,
    compiler_config: Optional[dict[str, Any]] = None,
) -> Runner: ...
def create_queue(
    model: ModelSource,
    *,
    device: Optional[str] = None,
    worker_num: Optional[int] = None,
    batch_size: Optional[int] = None,
    input_queue_size: Optional[int] = None,
    output_queue_size: Optional[int] = None,
    compiler_config: Optional[dict[str, Any]] = None,
) -> Tuple[Submitter, Receiver]: ...
