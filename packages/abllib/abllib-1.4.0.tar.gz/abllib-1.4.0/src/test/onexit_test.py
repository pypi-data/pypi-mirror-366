"""Module containing tests for the abllib.onexit module"""

import pytest

from abllib import error, onexit

# pylint: disable=protected-access

def test_register():
    """Ensure that registering the same callback multiple times raises an error"""

    def func1():
        pass

    onexit.register("func1", func1)

    with pytest.raises(error.RegisteredMultipleTimesError):
        onexit.register("func1", func1)

    with pytest.raises(error.RegisteredMultipleTimesError):
        onexit.register("func1", func1)

def test_deregister():
    """Ensure that deregistering the same callback multiple times raises an error"""

    def func1():
        pass

    onexit.register("func1", func1)

    onexit.deregister("func1")

    with pytest.raises(error.NameNotFoundError):
        onexit.deregister("func1")

    with pytest.raises(error.NameNotFoundError):
        onexit.deregister("func1")

def test_register_single():
    """Ensure that registering the callbacks seperately works correctly"""

    def func1():
        pass

    onexit.register_normal_exit("func1", func1)

    onexit.deregister("func1")

    onexit.register_sigterm("func1", func1)

    onexit.deregister("func1")

    onexit.register_normal_exit("func1", func1)
    onexit.register_sigterm("func1", func1)

    onexit.deregister("func1")

def test_deregister_single():
    """Ensure that deregistering the callbacks seperately works correctly"""

    def func1():
        pass

    onexit.register("func1", func1)

    onexit.deregister_normal_exit("func1")

    onexit.register("func1", func1)

    onexit.deregister_sigterm("func1")

    onexit.register("func1", func1)

    onexit.deregister_normal_exit("func1")
    onexit.deregister_sigterm("func1")

def test_register_all():
    """Ensure that all register functions work together correctly"""

    def func1():
        pass

    onexit.register("func1", func1)

    onexit.deregister("func1")

    onexit.register("func1", func1)

def test_call_atexit():
    """Ensure that atexit function calls callbacks correctly"""

    data = [False]
    def func1():
        data[0] = True

    onexit.register("func1", func1)

    onexit._atexit_func()

    assert data[0]

def test_call_signal():
    """Ensure that signal function calls callbacks correctly"""

    data = [False]
    def func1():
        data[0] = True

    onexit.register("func1", func1)

    onexit._signal_func(None, None)

    assert data[0]

def test_dotname():
    """Ensure that names containing a "." work as expected"""

    data = [False]
    def func1():
        data[0] = True

    onexit.register("func1.cb", func1)

    onexit._atexit_func()

    assert data[0]
