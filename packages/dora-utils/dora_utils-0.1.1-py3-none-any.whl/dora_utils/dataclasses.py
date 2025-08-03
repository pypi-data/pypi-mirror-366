import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Type, Union

import numpy as np
import pyarrow as pa
from dacite import from_dict

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def to_arrow(obj: Union["DataclassInstance", dict]) -> tuple[pa.Array, dict]:
    """Convert a dataclass or dict to a pyarrow array and metadata."""
    raw = obj if isinstance(obj, dict) else asdict(obj)
    numpy_paths: list[str] = []
    numpy_dtypes: dict[str, str] = {}

    stack = [("", raw)]
    while stack:
        path, current = stack.pop()
        if isinstance(current, dict):
            for k, v in current.items():
                full_path = f"{path}.{k}" if path else k
                stack.append((full_path, v))
        elif isinstance(current, list):  # type: ignore
            for i, v in enumerate(current):
                full_path = f"{path}[{i}]"
                stack.append((full_path, v))
        elif isinstance(current, np.ndarray):
            container = raw
            subkeys = path.split(".")
            for k in subkeys[:-1]:
                container = container[k]
            container[subkeys[-1]] = current.tolist()
            numpy_paths.append(path)
            numpy_dtypes[path] = str(current.dtype)

    metadata = {
        "class_name": obj.__class__.__name__,
        "numpy_fields": json.dumps(numpy_paths),
        "numpy_dtypes": json.dumps(numpy_dtypes),
    }

    return pa.array([raw]), metadata


def from_arrow(arr: pa.Array, metadata: dict, cls: Type) -> Any:
    """Convert a pyarrow array and metadata to a dataclass instance."""
    if len(arr) != 1:
        raise ValueError("Expected pa.Array of length 1")

    data = arr[0].as_py()
    numpy_paths = json.loads(metadata["numpy_fields"])
    numpy_dtypes = json.loads(metadata.get("numpy_dtypes", "{}"))

    def set_nested(path: str, root: dict, dtype: np.dtype | None = None) -> None:
        keys = path.split(".")
        d = root
        for k in keys[:-1]:
            d = d[k]
        leaf = keys[-1]
        if dtype:
            d[leaf] = np.array(d[leaf], dtype=dtype)
        else:
            d[leaf] = np.array(d[leaf])

    for path in numpy_paths:
        dtype = numpy_dtypes.get(path)
        set_nested(path, data, dtype=np.dtype(dtype) if dtype else None)

    return from_dict(data_class=cls, data=data)


def from_event(event: dict, cls: Type) -> Any:
    """Convert an event to a dataclass instance."""
    return from_arrow(event["value"], event["metadata"], cls)
