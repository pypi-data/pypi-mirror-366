"""A module containing json-like storages"""

from ._cache_storage import _CacheStorage
from ._persistent_storage import _PersistentStorage
from ._storage_view import _StorageView
from ._threadsafe_storage import _ThreadsafeStorage
from ._volatile_storage import _VolatileStorage

# pylint: disable=protected-access

def initialize(filename: str = "storage.json", save_on_exit: bool = False):
    """
    Initialize the storage module.

    If save_on_exit is set to True, automatically calls PersistentStorage.save_to_disk on application exit.
    """

    VolatileStorage.initialize()

    PersistentStorage.initialize(filename, save_on_exit)

CacheStorage = _CacheStorage()
PersistentStorage = _PersistentStorage()
VolatileStorage = _VolatileStorage()

StorageView = _StorageView()
StorageView._init()

__exports__ = [
    initialize,
    CacheStorage,
    PersistentStorage,
    StorageView,
    VolatileStorage,
    _CacheStorage,
    _PersistentStorage,
    _StorageView,
    _ThreadsafeStorage,
    _VolatileStorage
]
