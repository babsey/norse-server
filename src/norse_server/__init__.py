from importlib import metadata # noqa

try:
    __version__ = metadata.version("norse-server")
except metadata.PackageNotFoundError:
    pass

del metadata
