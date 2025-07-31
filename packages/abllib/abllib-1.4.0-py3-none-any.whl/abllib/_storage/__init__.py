"""An internal module containing json-like storages"""

# pylint: disable=protected-access

from ._base_storage import _BaseStorage
from ._internal_storage import _InternalStorage

InternalStorage = _InternalStorage()
# pylint: disable-next=protected-access
InternalStorage._init()

__exports__ = [
    _BaseStorage,
    InternalStorage
]
