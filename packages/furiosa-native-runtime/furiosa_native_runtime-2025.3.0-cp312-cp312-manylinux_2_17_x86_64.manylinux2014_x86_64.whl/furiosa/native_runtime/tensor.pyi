from typing import Union

import numpy as np

from furiosa.native_runtime import Axis, DataType, Tensor, TensorArray, TensorDesc

__all__ = [
    "Axis",
    "DataType",
    "Tensor",
    "TensorArray",
    "TensorDesc",
    "numpy_dtype",
]

def numpy_dtype(
    value: Union[np.ndarray, np.generic, TensorDesc, DataType],
) -> np.dtype: ...
def rand(value: TensorDesc) -> np.ndarray: ...
def zeros(value: TensorDesc) -> np.ndarray: ...
