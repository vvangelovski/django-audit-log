VERSION = (0, 8, 1, 'test')

if VERSION[-1] != "final":  # pragma: no cover
    __version__ = '.'.join(map(str, VERSION))
else:  # pragma: no cover
    __version__ = '.'.join(map(str, VERSION[:-1]))
