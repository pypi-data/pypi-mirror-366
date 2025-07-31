# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic_zarr @ git+https://github.com/d-v-b/pydantic-zarr.git@fill-value-fix",
#     "xarray",
#     "rich"
# ]
# ///

from typing import Any
from typing_extensions import Annotated
import xarray as xr
from pydantic_zarr.v3 import GroupSpec, ArraySpec
from pydantic import BaseModel, BeforeValidator, Field
import pandas as pd
import numpy as np
from rich import print
store = {}
np.random.seed(0)
temperature = 15 + 8 * np.random.randn(2, 3, 4)
precipitation = 10 * np.random.rand(2, 3, 4)
lon = [-99.83, -99.32]
lat = [42.25, 42.21]
instruments = ["manufac1", "manufac2", "manufac3"]
time = pd.date_range("2014-09-06", periods=4)
reference_time = pd.Timestamp("2014-09-05")

ds = xr.Dataset(
    data_vars={
        "temperature": (["loc", "instrument", "time"], temperature),
        "precipitation": (["loc", "instrument", "time"], precipitation),
    },
    coords={
        "lon": ("loc", lon),
        "lat": ("loc", lat),
        "instrument": instruments,
        "time": time,
        "reference_time": reference_time,
    },
    attrs={"description": "Weather related data."},
)

class CoordinateAttrs(BaseModel):
    _FillValue: object

class DataVariableAttrs(BaseModel):
    FillValue: object = Field(alias="_FillValue")
    # whyyyyyyyy is attributes["coordinates"] a string, and not a list of strings....
    coordinates: Annotated[tuple[str, ...], BeforeValidator(lambda v: tuple(v.split()))]

class ScalarCoordinate(ArraySpec):
    dimension_names: None = None
    shape: tuple[()]

class ArrayCoordinate(ArraySpec[CoordinateAttrs]):
    dimension_names: tuple[str, ...]

class DataArray(ArraySpec[DataVariableAttrs]):
    dimension_names: tuple[str, ...]

class DataSetGroup(GroupSpec[Any, DataArray | ArrayCoordinate | ScalarCoordinate]):
    def data_vars(self) -> dict[str, DataArray]:
        """
        Return the schemas for the data variables
        """
        return {k: v for k, v in self.members.items() if isinstance(v, DataArray)}

    def coord_vars(self) -> dict[str, ArrayCoordinate | ScalarCoordinate]:
        """
        Return the schemacs for the coordinate variables
        """
        return {
            k: v for k, v in self.members.items() if isinstance(v, ArrayCoordinate | ScalarCoordinate)
        }

stored = ds.to_zarr(store=store)
raw_group = GroupSpec.from_zarr(stored.zarr_group)
# uncomment to see the raw schema
# print(pzg.model_dump())

parsed_group = DataSetGroup.from_zarr(stored.zarr_group)
print(parsed_group.data_vars())
print(parsed_group.coord_vars())
