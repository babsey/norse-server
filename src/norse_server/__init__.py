from importlib import metadata # noqa

try:
    __version__ = metadata.version("norse-server")
    del metadata
except:
    pass
