import sys
import threading
import traceback
import contextlib
from collections import OrderedDict

from qtpy import QtCore


__all__ = ['get_updater', 'set_updater', 'ThreadUpdater']


MAIN_UPDATER = None


def get_updater():
    """Return the main updater."""
    global MAIN_UPDATER

    if MAIN_UPDATER is None:
        # Create a default updater
        MAIN_UPDATER = ThreadUpdater()

    return MAIN_UPDATER


def set_updater(updater):
    """Set the main updater."""
    global MAIN_UPDATER
    MAIN_UPDATER = updater


class ThreadUpdater(QtCore.QObject):
    """General timer that will call functions on an interval."""

    starting = QtCore.Signal()
    stopping = QtCore.Signal()

    def __init__(self, timeout=1/30, parent=None):
        super().__init__(parent)
        self._timeout = timeout
        self._running = False
        self._tmr = QtCore.QTimer()
        self._tmr.setSingleShot(False)
        self._tmr.timeout.connect(self.update)

        self._call_latest = OrderedDict()
        self._latest_lock = threading.RLock()
        self._call_in_main = OrderedDict()
        self._main_lock = threading.RLock()
        self._always_call = OrderedDict()
        self._always_lock = threading.RLock()

        self.starting.connect(self.start)
        self.stopping.connect(self.stop)

    @contextlib.contextmanager
    def restart_on_change(self, restart=None):
        """Context manager to stop and restart the timer if it is running."""
        if restart is None:
            restart = self.is_running()
        if restart:
            self.stop()
            yield
            self.start()
        else:
            yield

    def get_timeout(self):
        """Return the update timer interval in seconds."""
        return self._timeout

    def set_timeout(self, value):
        """Set the update timer interval in seconds."""
        with self.restart_on_change(self.is_running()):
            self._timeout = value
            self._tmr.setInterval(int(self.get_timeout() * 1000))

    def is_running(self):
        """Return if running."""
        return self._running

    def stop(self, set_state=True):
        """Stop the updater timer."""
        try:
            self._tmr.stop()
        except:
            pass
        if set_state:
            self._running = False

    def start(self):
        """Start the updater timer."""
        self.stop(set_state=False)
        self._running = True
        self._tmr.start()

    def ensure_running(self):
        """If the updater is not running send a safe signal to start it."""
        if not self.is_running():
            self._running = True
            self.starting.emit()

    def register_continuous(self, func, *args, **kwargs):
        """Register a function to be called on every update continuously."""
        with self._always_lock:
            self._always_call[func] = (args, kwargs)
        self.ensure_running()

    def unregister_continuous(self, func):
        """Unregister a function to be called on every update continuously."""
        with self._always_lock:
            try:
                self._always_call.pop(func, None)
            except:
                pass

    def call_latest(self, func, *args, **kwargs):
        """Call the most recent values for this function in the main thread on the next update call."""
        with self._latest_lock:
            self._call_latest[func] = (args, kwargs)
        self.ensure_running()

    def now_call_latest(self, func, *args, **kwargs):
        """Call the latest value in the main thread. If this is the main thread call now."""
        if threading.current_thread() == threading.main_thread():
            func(*args, **kwargs)
        else:
            self.call_latest(func, *args, **kwargs)

    def call_in_main(self, func, *args, **kwargs):
        """Call this function in the main thread on the next update call."""
        with self._main_lock:
            try:
                self._call_in_main[func].append((args, kwargs))
            except (KeyError, IndexError, Exception):
                self._call_in_main[func] = [(args, kwargs)]
        self.ensure_running()

    def now_call_in_main(self, func, *args, **kwargs):
        """Call in the main thread. If this is the main thread call now."""
        if threading.current_thread() == threading.main_thread():
            func(*args, **kwargs)
        else:
            self.call_in_main(func, *args, **kwargs)

    def update(self):
        """Run the stored function calls."""
        with self._always_lock:
            always = self._always_call.copy()
        with self._latest_lock:
            latest, self._call_latest = self._call_latest, OrderedDict()
        with self._main_lock:
            main, self._call_in_main = self._call_in_main, OrderedDict()

        for func, (args, kwargs) in always.items():
            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
                print('Error in {}'.format(func.__name__), file=sys.stderr)

        for func, (args, kwargs) in latest.items():
            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
                print('Error in {}'.format(func.__name__), file=sys.stderr)

        for func, li in main.items():
            for args, kwargs in li:
                try:
                    func(*args, **kwargs)
                except Exception:
                    traceback.print_exc()
                    print('Error in {}'.format(func.__name__), file=sys.stderr)
