import contextlib
import time
import threading

from pyjoystick.stash import Stash
from pyjoystick.utils import PeriodicThread


class ThreadEventManager(object):
    def __init__(self, event_loop=None, add_joystick=None, remove_joystick=None, handle_key_event=None, alive=None,
                 button_repeater=None, activity_timeout=0.01):
        super().__init__()

        if alive is None:
            alive = threading.Event()

        self.activity_timeout = activity_timeout
        self._button_repeater = None

        self.event_loop = event_loop
        self.joysticks = Stash()
        self.alive = alive
        self.proc = None
        self.worker = None
        self.event_lock = threading.RLock()
        self.event_list = Stash()

        if add_joystick is not None:
            self.add_joystick = add_joystick
        if remove_joystick is not None:
            self.remove_joystick = remove_joystick
        if handle_key_event is not None:
            self.handle_key_event = handle_key_event
        if button_repeater is not None:
            self.set_button_repeater(button_repeater)

    def add_joystick(self, joy):
        """Save the added joystick."""
        pass

    def remove_joystick(self, joy):
        """Remove the given joystick."""
        pass

    def handle_key_event(self, key):
        """Function to handle key event happens"""
        pass

    def get_button_repeater(self):
        """Return the button repeater."""
        return self._button_repeater

    def set_button_repeater(self, value):
        """Set the button repeater."""
        self._button_repeater = value
        try:
            self._button_repeater.key_repeated = self._update_key_event
        except:
            pass

    button_repeater = property(get_button_repeater, set_button_repeater)

    def save_joystick(self, joy):
        """Save the added joystick."""
        self.joysticks.append(joy)

        # Run the callback handler
        self.add_joystick(joy)

    def delete_joystick(self, joy):
        """Delete the removed joystick."""
        try:
            self.joysticks.remove(joy)
        except:
            pass

        # Run the callback handler
        self.remove_joystick(joy)

    def save_key_event(self, key):
        """Save the initial key event."""
        try:
            joy = self.joysticks[key.joystick]
            key.joystick = joy
        except:
            pass

        try:
            self.button_repeater.set(key)
        except:
            pass

        self._update_key_event(key)

    def _update_key_event(self, key):
        """Update the event list from the key event."""
        with self.event_lock:
            try:
                joy = self.joysticks[key.joystick]
                key.joystick = joy
                joy.update_key(key)
            except:
                pass

            if key.keytype == key.BUTTON or key not in self.event_list:
                self.event_list.append(key)

    def process_events(self):
        """Process all of the saved events."""
        with self.event_lock:
            li, self.event_list = self.event_list, []

            for k in li:
                try:
                    k.update_value(self.joysticks[k.joystick])
                except:
                    pass

                # Run the callback handler
                self.handle_key_event(k)

    @contextlib.contextmanager
    def run_during(self):
        """Context manager to temporarily run the manager if the manager is not already running."""
        if not self.is_running():
            self.start()
            yield
            self.stop()
        else:
            yield

    def wait(self, conditional=None, timeout=float('inf'), sleep_func=None):
        """Wait for the given timeout or conditional function to return false.

        Args:
            conditional (callable)[None]: Callable that returns True to keep waiting. If raises error stop waiting.
            timeout (float/int)[float('inf')]: Time for when to stop waiting.
            sleep_func (callable)[None]: How to sleep and wait (ex. time.sleep(0.001)). If raises error stop waiting.
        """
        if sleep_func is None:
            sleep_func = lambda: time.sleep(0.01)
        if conditional is None:
            conditional = lambda: True
        elif not callable(conditional):
            conditional = lambda: conditional

        start = time.time()
        try:
            while (time.time() - start) < timeout and conditional():
                sleep_func()
        except (ValueError, TypeError, Exception):  # If any error occurs stop waiting.
            pass

    def find_key(self, joysticks=None, key_types=None, timeout=float("inf"), sleep_func=None):
        """Wait and return the next key that is pressed.

        Args:
            joysticks (list/Joystick)[None]: Joystick(s) to allow events for.
            key_types (list/KeyTypes)[None]: List of key type. Found with Key.KeyTypes.Axis
            timeout (float/int)[float('inf')]: Timeout to wait.
            sleep_func (callable)[None]: How to sleep and wait (time.sleep(0.01)).

        Returns:
            key (Key)[None]: If found return the first Key else return None.
        """
        if joysticks is None:
            joysticks = []
        elif not isinstance(joysticks, list):
            joysticks = list(joysticks)
        if key_types is None:
            key_types = []

        data = {'found key': None}

        def filter_find_key(key):
            is_joystick = len(joysticks) == 0 or key.joystick in joysticks
            is_key_type = len(key_types) == 0 or key.has_keytype(key.keytype, key_types)
            is_valid_value = key.keytype != key.AXIS or abs(key.value) > 0
            if is_joystick and is_key_type and is_valid_value and data['found key'] is None:
                data['found key'] = key

        def is_not_found():
            return data['found key'] is None

        # Change the event handler
        old_handle_key_event, self.handle_key_event = self.handle_key_event, filter_find_key

        with self.run_during():
            self.wait(is_not_found, timeout, sleep_func)

        # Reset event handler
        self.handle_key_event = old_handle_key_event

        return data['found key']

    def run(self, event_loop, add_joystick, remove_joystick, handle_key_event, alive=None, button_repeater=None):
        """Run the an event loop to process SDL Events.

        Args:
            event_loop (callable/function): Event loop function to run.
            add_joystick (callable/function): Called when a new Joystick is found!
            remove_joystick (callable/function): Called when a Joystick is removed!
            handle_key_event (callable/function): Called when a new key event occurs!
            alive (callable/function)[None]: Function to return True to continue running. If None run forever
            button_repeater (ButtonRepeater): Thread to start which will monitor button keys and trigger repeating.
        """
        if alive is None:
            alive = lambda: True

        if button_repeater is not None:
            button_repeater.start()

        event_loop(add_joystick, remove_joystick, handle_key_event, alive=alive)

    def is_running(self):
        """Return if the event loop is running."""
        return self.alive.is_set()

    def start(self):
        """Start running the event loop."""
        self.stop()

        self.alive.set()
        self.proc = threading.Thread(target=self.run,
                                     args=(self.event_loop, self.save_joystick, self.delete_joystick,
                                           self.save_key_event),
                                     kwargs={'alive': self.is_running, 'button_repeater': self.button_repeater})
        self.proc.daemon = True
        self.proc.start()

        self.worker = PeriodicThread(self.activity_timeout, self.process_events)
        self.worker.alive = self.alive  # stop when this event stops
        self.worker.daemon = True
        self.worker.start()
        return self

    def stop(self):
        """Stop running the event loop."""
        try:
            self.alive.clear()
        except:
            pass
        try:
            self.proc.join(0)
        except:
            pass
        self.proc = None
        try:
            self.worker.join(0)
        except:
            pass
        self.worker = None
        return self

    def __enter__(self):
        if not self.is_running():
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return exc_type is None

    def __getstate__(self):
        return {'activity_timeout': self.activity_timeout,
                'button_repeater': self.button_repeater,
                'event_loop': self.event_loop,
                'joysticks': Stash(),
                'alive': self.alive,
                'proc': None,
                'worker': None,
                'event_list': Stash(),
                }

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

        if getattr(self, 'event_lock', None) is None:
            self.event_lock = threading.RLock()


if __name__ == '__main__':
    import time
    import argparse
    from pyjoystick import Key, ButtonRepeater, HatRepeater, ButtonHatRepeater
    try:
        from pyjoystick.sdl2 import Joystick as SDLJoystick, run_event_loop as run_sdl_loop
    except:
        SDLJoystick = None
        run_sdl_loop = None
    try:
        from pyjoystick.pygame import Joystick as PygameJoystick, run_event_loop as run_pygame_loop
    except:
        PygameJoystick = None
        run_pygame_loop = None

    # Parse the command line arguments
    P = argparse.ArgumentParser(description='Run a thread event loop.')
    P.add_argument('--lib', type=str, default='sdl', choices=['sdl', 'pygame'],
                   help='Library to run the thread event loop with.')
    P.add_argument('--timeout', type=float, default=float('inf'), help='Time to run for')
    P.add_argument('--device', type=int, default=None, help='Device index to monitor.')
    P.add_argument('--keytype', type=str, default=Key.ALL_KEYTYPES,
                   choices=[Key.AXIS, Key.BUTTON, Key.HAT, Key.BALL, Key.ALL_KEYTYPES], help='Key type to monitor.')

    ARGS = P.parse_args()

    TIMEOUT = ARGS.timeout
    DEVICE = ARGS.device
    KEYTYPES = ARGS.keytype

    if ARGS.lib == 'pygame':
        run_event_loop = run_pygame_loop
        Joystick = PygameJoystick
    else:
        run_event_loop = run_sdl_loop
        Joystick = SDLJoystick

    print("Devices:")
    for joy in Joystick.get_joysticks():
        print('\t', '{}.'.format(joy.get_id()), joy.get_name())

    def print_add(joy):
        print('Added', joy, '\n', end='\n', flush=True)

    def print_remove(joy):
        print('Removed', joy, '\n', end='\n', flush=True)

    def key_received(key):
        if DEVICE is None:
            print(key, '==', key.value)
        elif key.joystick == DEVICE:
            DEVICE.update_key(key)

            keys = '\t'.join((format_key(k) for k in DEVICE.keys if k.keytype in KEYTYPES))
            print('\r', keys, end='', flush=True)

    def format_key(key):
        try:
            value = key.value
            if isinstance(value, float):
                value = '{:2.2f}'.format(key.value)
            else:
                value = str(value)
        except:
            if key.value is None:
                value = '0'
            else:
                value = '{:5}'.format(key.value)
        return '{} {} == {:>5}'.format(key.keytype, key.number, value)

    # Run the event loop
    with ThreadEventManager(run_event_loop, print_add, print_remove, key_received, button_repeater=ButtonHatRepeater()):
        try:
            time.sleep(TIMEOUT)
        except:
            while True:
                time.sleep(1000)
