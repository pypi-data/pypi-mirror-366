from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `spatialise_soil_prediction.resources` module.

    This is used so that we can lazily import `spatialise_soil_prediction.resources` only when
    needed *and* so that users can just import `spatialise_soil_prediction` and reference `spatialise_soil_prediction.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("spatialise_soil_prediction.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
