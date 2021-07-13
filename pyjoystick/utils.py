import os
import sys
import platform
import time
import threading
import contextlib


__all__ = ['is_py27', 'files', 'as_file', 'deadband', 'change_path', 'rescale', 'PeriodicThread']


is_py27 = sys.version_info < (3, 0)

try:
    from importlib.resources import files, as_file
except (ImportError, Exception):
    try:
        from importlib_resources import files, as_file
    except (ImportError, Exception):
        import inspect
        from pathlib import Path
        Traversable = Path

        def files(module):
            if isinstance(module, str):
                if '.' in module:
                    # Import the top level package and manually add a directory for each "."
                    toplvl, remain = module.split('.', 1)
                else:
                    toplvl, remain = module, ''

                # Get or import the module
                try:
                    module = sys.modules[toplvl]
                    path = Path(inspect.getfile(module))
                except (KeyError, Exception):
                    try:
                        module = __import__(toplvl)
                        path = Path(inspect.getfile(module))
                    except (ImportError, Exception):
                        module = toplvl
                        path = Path(module)

                # Get the path of the module
                if path.with_suffix('').name == '__init__':
                    path = path.parent

                # Find the path from the top level module
                for pkg in remain.split('.'):
                    path = path.joinpath(pkg)
            else:
                path = Path(inspect.getfile(module))
            if path.with_suffix('').name == '__init__':
                path = path.parent
            return path

        @contextlib.contextmanager
        def as_file(path):
            p = str(path)
            if not os.path.exists(p):
                p = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), str(path))
            if not os.path.exists(p):
                p = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), '', str(path))

            yield p


def deadband(val, dead=0.2, scale=1):
    """Return the deadband value for the controller Axis.

    Args:
        val (float): Raw controller value -1 to 1.
        dead (float)[0.2]: Deadband value
        scale (int) [1]: 100, 10, 1 indicates the range -100 to 100 ...
    """
    val = float(val)
    dead = abs(float(dead))

    # Check if the deadband is the same as the scale
    if dead == scale:
        dead = scale * 0.99

    if val >= dead:
        val -= dead
    elif val <= -dead:
        val += dead
    else:
        val = 0

    val = (val/(scale-dead)) * scale
    return val


@contextlib.contextmanager
def change_path(path):
    """Temporarily change the sys.path for imports"""
    try:
        ch_path = sys.path.index(path)
    except:
        ch_path = -1
        
    if ch_path != -1:
        sys.path.pop(ch_path)
    
    yield
    
    if ch_path != -1:
        sys.path.insert(ch_path, path)


def rescale(value, curr_min, curr_max, new_min, new_max):
    """Convert the value from one scale to a new scale.
    
    Args:
        value (int/float/object): Value to convert to the new scale
        curr_max (int/float): Current maximum value for the current scale.
        curr_min (int/float): Current minimum value for the current scale.
        new_max (int/float): New maximum value for the new scale.
        new_min (int/float): New minimum value for the new scale.
        
    Returns:
        value (int/float/object): New value that was converted to the new scale
    """
    return ((value - curr_min) / (curr_max - curr_min)) * (new_max - new_min) + new_min


class PeriodicThread(threading.Thread):
    def __init__(self, interval, target=None, name=None, args=None, kwargs=None, daemon=None):
        """Create a thread that will run a function periodically.
        Args:
            interval (int/float): How often to run a function in seconds.
        """
        self.interval = interval
        self.alive = threading.Event()
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
        super(PeriodicThread, self).__init__(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)

        if is_py27:
            self._args = self.__args
            self._kwargs = self.__kwargs
            self._started = self.__started
            self._target = self.__target

        if self._target is None and hasattr(self, '_run'):
            if is_py27:
                self.__target = self._run
            self._target = self._run

    def start(self):
        """Start running the thread."""
        self.alive.set()
        if not self._started.is_set():
            super(PeriodicThread, self).start()

    def stop(self):
        """Stop running the thread."""
        try:
            self.alive.clear()
        except:
            pass

    def run(self):
        """The thread will loop through running the set _target method (default _run()). This
        method can be paused and restarted.
        """
        while self.alive.is_set():
            # Run the thread method
            start = time.time()
            self._target(*self._args, **self._kwargs)
            try:
                sleep = self.interval - (time.time() - start)
                if sleep > 0:
                    time.sleep(sleep)
            except ValueError:
                pass  # sleep time less than 0

    def join(self, timeout=None):
        """Join the thread closing it."""
        self.stop()
        super(PeriodicThread, self).join(timeout=timeout)

    def __enter__(self):
        """Enter statement for use of 'with' statement."""
        self.start()
        return self

    def __exit__(self, ttype, value, traceback):
        """Exit statement for use of the 'with' statement."""
        try:
            self.join(0)  # Make sure join has a 0 timeout so it is not blocking while exiting
        except RuntimeError:
            pass

        return ttype is None  # Return False if there was an error
