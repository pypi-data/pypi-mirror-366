# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic-zarr",
# ]
# ///
import numpy as np
from pydantic import model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec
from typing import Self

class MyGroup(GroupSpec):
    @model_validator(mode='after')
    def arrays_must_be_3d(self) -> Self:
        # check that the arrays are all 3D
        for name, member in self.members.items():
            if isinstance(member, ArraySpec) and len(member.shape) != 3:
                raise ValueError(f"Array {name} ({member}) is not 3D")
        return self

arr = ArraySpec.from_array(np.arange(10)) # not 3D
try:
   invalid = MyGroup(members={"bar": arr})
except ValueError as e:
    print(e)

# this works
arr_3d = ArraySpec.from_array(np.arange(10).reshape(1, 1, 10))
valid = MyGroup(members={"bar": arr_3d})
print(valid.model_dump())