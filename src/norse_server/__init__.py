from importlib import metadata as _metadata # noqa

__version__ = _metadata.version("norse-server")
del _metadata