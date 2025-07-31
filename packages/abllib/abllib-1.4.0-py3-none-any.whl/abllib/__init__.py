"""
Ableytner's library for Python

Contains many general-purpose functions which can be used across projects.
"""

from . import alg, error, fs, fuzzy, log, onexit, pproc, storage, wrapper
from .log import get_logger, LogLevel
from .storage import CacheStorage, VolatileStorage, PersistentStorage, StorageView
from .wrapper import Lock, Semaphore, NamedLock, NamedSemaphore

__exports__ = [
    alg,
    error,
    fs,
    fuzzy,
    log,
    onexit,
    pproc,
    storage,
    wrapper,
    get_logger,
    LogLevel,
    Lock,
    Semaphore,
    NamedLock,
    NamedSemaphore,
    CacheStorage,
    VolatileStorage,
    PersistentStorage,
    StorageView
]
