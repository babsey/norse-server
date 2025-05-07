#!/usr/bin/env python
# serialize.py

import torch # noqa
import numpy as np # noqa

from .exceptions import call_or_error


@call_or_error
def serialize_data(data):
    if isinstance(data, torch.Tensor):
        return serialize_data(data.detach().tolist())
    elif isinstance(data, np.ndarray):
        return serialize_data(ata.tolist())
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, dict):
        return dict([(serialize_data(k), serialize_data(v)) for k, v in data.items()])
    elif isinstance(data, (list, tuple)):
        return [serialize_data(v) for v in data]
    return data