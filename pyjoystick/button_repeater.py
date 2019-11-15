import time
import threading
from pyjoystick.utils import PeriodicThread


__all__ = ['Repeater', 'ButtonRepeater', 'HatRepeater', 'ButtonHatRepeater']


class Repeater(object):
    """Scheduler to Manage multiple button repeats."""

    def __init__(self, first_repeat_timeout=1.0, repeat_timeout=0.5, check_timeout=0.1, key_repeated=None,
                 get_key_hash=None):
        super().__init__()

        if key_repeated is not None:
            self.key_repeated = key_repeated
        if get_key_hash is not None:
            self.get_key_hash = get_key_hash

        self.first_repeat_timeout = first_repeat_timeout
        self.repeat_timeout = repeat_timeout
        self._check_timeout = check_timeout

        self.thread = None
        self._name = "pyjoystick-ButtonRepeater"
        self._lock = threading.RLock()
        self.key_times = {}

    def key_repeated(self, key):
        """Add the Key to the event queue to be processed."""
        pass

    @property
    def check_timeout(self):
        """Timeout for when the keys should repeat."""
        return self._check_timeout

    @check_timeout.setter
    def check_timeout(self, value):
        """Timeout for when the keys should repeat."""
        self._check_timeout = value
        try:
            self.thread.interval = value
        except:
            pass

    @property
    def name(self):
        """Return the thread name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the thread name."""
        self._name = value
        try:
            self.thread.name = value
        except:
            pass

    @staticmethod
    def get_key_hash(key):
        """Return the hash for the given key."""
        if key.joystick:
            return '{}:{} {}'.format(key.joystick, key.keytype, key.number)
        else:
            return '{} {}'.format(key.keytype, key.number)

    def start(self):
        """Start the thread to check for button repeats"""
        self.thread = PeriodicThread(self.check_timeout, self._run)
        self.thread.name = self.name
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the thread to check for button repeats"""
        try:
            self.thread.join(0)
        except:
            pass
        self.thread = None

        with self._lock:
            self.key_times = {}

    def set(self, key):
        """Set the key to start or stop repeate based on the value."""
        if key.value:
            self.start_repeat(key)
        else:
            self.stop_repeat(key)

    def start_repeat(self, key):
        """Start a key repeating."""
        with self._lock:
            k = self.get_key_hash(key)
            if k not in self.key_times:
                self.key_times[k] = [time.time() + self.first_repeat_timeout, key]

    def stop_repeat(self, key):
        """Stop a key from repeating."""
        with self._lock:
            try:
                del self.key_times[self.get_key_hash(key)]
            except:
                pass

    def _run(self):
        """Run the event loop continuously."""
        with self._lock:
            for k, (t, key) in self.key_times.items():
                if time.time() > t:
                    new_key = key.copy()
                    new_key.is_repeat = True
                    self.key_repeated(new_key)
                    try:
                        self.key_times[k][0] = time.time() + self.repeat_timeout
                    except:
                        pass


class ButtonRepeater(Repeater):
    def start_repeat(self, key):
        """Start a key repeating."""
        if key.keytype == key.BUTTON:
            Repeater.start_repeat(self, key)


class HatRepeater(Repeater):
    def set(self, key):
        """Set the key to start or stop repeate based on the value."""
        value = key.value

        if key.keytype == key.HAT:
            try:
                k = self.get_key_hash(key)
                with self._lock:
                    if value == 0:
                        # Key needs to stop repeat!
                        self.stop_repeat(key)
                        return
                    elif self.key_times[k][1].value == value:
                        # Hat is repeating already
                        return
                    else:
                        # Hat value changed. Try repeating a different value.
                        self.stop_repeat(key)
                        value = True
            except:
                pass

        if value:
            self.start_repeat(key)
        else:
            self.stop_repeat(key)

    def start_repeat(self, key):
        """Start a key repeating."""
        if key.keytype == key.HAT:
            Repeater.start_repeat(self, key)


class ButtonHatRepeater(HatRepeater):
    def start_repeat(self, key):
        """Start a key repeating."""
        if key.keytype == key.BUTTON or key.keytype == key.HAT:
            Repeater.start_repeat(self, key)
