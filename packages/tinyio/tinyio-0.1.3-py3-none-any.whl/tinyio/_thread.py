import ctypes
import threading
from collections.abc import Callable, Iterable
from typing import ParamSpec, TypeVar, cast

from ._core import CancelledError, Coro
from ._sync import Semaphore


_T = TypeVar("_T")
_Params = ParamSpec("_Params")
_Return = TypeVar("_Return")


def run_in_thread(fn: Callable[_Params, _Return], /, *args: _Params.args, **kwargs: _Params.kwargs) -> Coro[_Return]:
    """A `tinyio` coroutine for running the blocking function `fn(*args, **kwargs)` in a thread.

    If this coroutine is cancelled then the cancellation will be raised in the thread as well; vice-versa if the
    function call raises an error then this will propagate to the coroutine.

    **Arguments:**

    - `fn`: the function to call.
    - `*args`: arguments to call `fn` with.
    - `**kwargs`: keyword arguments to call `fn` with.

    **Returns:**

    A coroutine that can be `yield`ed on, returning the output of `fn(*args, **kwargs)`.
    """

    is_exception = None
    result = None

    def target():
        nonlocal result, is_exception
        try:
            result = fn(*args, **kwargs)
            is_exception = False
        except BaseException as e:
            result = e
            is_exception = True

    t = threading.Thread(target=target)

    try:
        t.start()
        while is_exception is None:
            yield
    except BaseException as e:
        # We can end up here if an `tinyio.CancelledError` arises out of the `yield`, or from an exogeneous
        # `KeyboardInterrupt`, or from re-raising the error out of our thread.
        thread_id = t.ident
        assert thread_id is not None
        # Raise a `CancelledError` in the thread that is running the task. This allows the thread to do any cleanup.
        # This is not readily supported and needs to be done via ctypes, see: https://gist.github.com/liuw/2407154.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(CancelledError))
        t.join()
        # Our thread above has now completed.
        if is_exception and type(e) is CancelledError:
            # We were cancelled.
            #
            # Note that we raise this regardless of whether `result` is itself a `CancelledError`. It's probably the
            # error we triggered via `ctypes` above, but in principle the function may have caught that and done
            # something else.
            # Either way, we are but the humble purveyors of this message back to the event loop: raise it.
            result = cast(BaseException, result)
            context = result.__context__
            cause = result.__cause__
            try:
                raise result
            except BaseException as e:
                # try-and-immediately-except is a trick to remove the current frame from the traceback.
                # This smoothly links up the `run_in_thread` invocation with the frame in `target`, with no weird
                # `raise result` frame halfway through.
                # In addition we also need to preserve the `__context__` (and `__cause__`?) as the `raise` overwrites
                # this with the current context.
                # Curiously this doesn't seem to work if we unify this with the `else` branch of the `try/except/else`
                # below, despite ostensibly then being outside of the `except BaseException` context. Whatever, this
                # version works correctly!
                assert e.__traceback__ is not None
                e.__traceback__ = e.__traceback__.tb_next
                e.__context__ = context
                e.__cause__ = cause
                raise
        else:
            # Probably a `KeyboardInterrupt`, forward it on.
            raise
    else:
        if is_exception:
            try:
                raise cast(BaseException, result)
            except BaseException as e:
                assert e.__traceback__ is not None
                e.__traceback__ = e.__traceback__.tb_next
                raise
        else:
            return cast(_Return, result)


class ThreadPool:
    """A wrapper around `tinyio.run_in_thread` to launch at most `value` many threads at a time."""

    def __init__(self, max_threads: int):
        """**Arguments:**

        - `value`: the maximum number of threads to launch at a time.
        """

        self._semaphore = Semaphore(max_threads)

    def run_in_thread(
        self, fn: Callable[_Params, _Return], /, *args: _Params.args, **kwargs: _Params.kwargs
    ) -> Coro[_Return]:
        """Like `tinyio.run_in_thread(fn, *args, **kwargs)`.

        Usage is `output = yield pool.run_in_thread(...)`
        """
        with (yield self._semaphore()):
            out = yield run_in_thread(fn, *args, **kwargs)
        return out

    def map(self, fn: Callable[[_T], _Return], /, xs: Iterable[_T]) -> Coro[list[_Return]]:
        """Like `[tinyio.run_in_thread(fn, x) for x in xs]`.

        Usage is `output_list = pool.map(...)`
        """
        return (yield [self.run_in_thread(fn, x) for x in xs])
