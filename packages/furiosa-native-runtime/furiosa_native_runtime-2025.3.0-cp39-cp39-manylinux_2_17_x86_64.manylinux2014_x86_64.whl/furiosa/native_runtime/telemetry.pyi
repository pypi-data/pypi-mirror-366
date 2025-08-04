from typing import ContextManager, TypeVar

from furiosa.native_runtime.telemetry import ProfilerRecordObject

class Profiler(ContextManager["Profiler"]):
    _Self = TypeVar("_Self", bound=Profiler)
    def __new__(
        cls,
        name: str,
        path: str,
    ) -> Profiler: ...
    @property
    def output_path(self) -> str: ...

profiler = Profiler

def record(
    name: str, category: Optional[str], *, kwargs: Optional[dict[str, Any]]
) -> ProfilerRecordObject: ...

__all__ = ["profiler", "Profiler", "ProfilerRecordObject", "record"]
