#!/usr/bin/env python
# serialize.py

import torch # noqa
import numpy as np # noqa

from .exceptions import call_or_error


@call_or_error
def serialize_data(data):
    if isinstance(data, torch.Tensor):
        return data.detach().tolist()
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(v) for v in data]
    return data