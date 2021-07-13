import os
import sys
import time
import threading

from pyjoystick.utils import files, as_file, change_path, rescale

with as_file(files('pyjoystick')) as PYJOYSTICK_DIR:
    with change_path(PYJOYSTICK_DIR):
        # os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        import pygame

from pyjoystick.stash import Stash
from pyjoystick.interface import HatValues, Key, Joystick as BaseJoystick


__all__ = ['Key', 'Joystick', 'run_event_loop', 'stop_event_wait',
           'get_init', 'init', 'quit', 'key_from_event',
           'refresh_joysticks']


PYGAME_LOCK = threading.RLock()


class Joystick(BaseJoystick):
    @classmethod
    def get_joysticks(cls):
        """Return a list of available joysticks."""
        # Check init
        if not get_init():
            init()

        return Stash(cls(i) for i in range(pygame.joystick.get_count()))

    def __new__(cls, identifier=None, *args, **kwargs):
        # Check init
        if not get_init():
            init()

        # Create the object
        joy = super().__new__(cls)

        if identifier is None:
            identifier = 0

        if isinstance(identifier, str):
            for i in range(pygame.joystick.get_count()):
                raw_joystick = pygame.joystick.Joystick(i)
                try:
                    if raw_joystick.get_name() == identifier:
                        joy.joystick = raw_joystick
                        break
                except:
                    pass
        else:
            joy.joystick = pygame.joystick.Joystick(identifier)

        try:
            if not joy.joystick.get_init():
                joy.joystick.init()
        except:
            pass

        try:
            joy.identifier = joy.joystick.get_id()
            joy.name = joy.joystick.get_name()
            joy.numaxes = joy.joystick.get_numaxes()
            joy.numbuttons = joy.joystick.get_numbuttons()
            joy.numhats = joy.joystick.get_numhats()
            joy.numballs = joy.joystick.get_numballs()
            joy.init_keys()
        except:
            pass

        return joy

    def is_available(self):
        """Return if this joystick is still active and available."""
        try:
            return self.joystick.get_init()
        except:
            return False

    def close(self):
        """Close the joystick."""
        try:
            self.joystick.quit()
        except:
            pass


def get_init(module=pygame):
    """Return if the given module is initialize."""
    if module != pygame:
        return module.get_init()
    return pygame.display.get_init()  # Pygame events require the display module


def init(module=pygame):
    """Initialize the given module."""
    if module != pygame:
        module.init()
        return

    # Main pygame init
    if not pygame.display.get_init():
        pygame.display.init()  # Pygame events require the display module
        pygame.joystick.init()

        # if not gui_running():
        pygame.display.set_mode((1, 1), pygame.NOFRAME)  # pygame requires some display.

        # Allowed events
        pygame.event.set_blocked([pygame.QUIT,
                                  pygame.ACTIVEEVENT,
                                  pygame.KEYDOWN,
                                  pygame.KEYUP,
                                  pygame.MOUSEMOTION,
                                  pygame.MOUSEBUTTONUP,
                                  pygame.MOUSEBUTTONDOWN,
                                  pygame.VIDEORESIZE,
                                  pygame.VIDEOEXPOSE,
                                  pygame.USEREVENT
                                  ])

        pygame.event.set_allowed([pygame.JOYAXISMOTION,
                                  pygame.JOYBALLMOTION,
                                  pygame.JOYHATMOTION,
                                  pygame.JOYBUTTONDOWN,
                                  pygame.JOYBUTTONUP])


def quit(module=pygame):
    """Quit and deinitialize the given module."""
    module.quit()


def key_from_event(event, joystick=None):
    """Every library type should implement a key_from_event function to convert an event into a key.

    Args:
        event (pygame.event.Event): Event that occurred
        joystick (Joystick)[None]: Joystick object

    Returns:
        key (Key)[None]: Key created from the event.
    """
    if joystick is None:
        try:
            joystick = Joystick(event.joy)
        except (AttributeError, ValueError):
            return None

    # Check the Joystick
    if event.type == pygame.JOYBUTTONDOWN:
        return Key(Key.BUTTON, event.button, 1, joystick)
    elif event.type == pygame.JOYBUTTONUP:
        return Key(Key.BUTTON, event.button, 0, joystick)
    elif event.type == pygame.JOYAXISMOTION:
        return Key(Key.AXIS, event.axis, event.value, joystick)
    elif event.type == pygame.JOYHATMOTION:
        value = HatValues.from_range(tuple(event.value), Key.HAT_CENTERED)
        return Key(Key.HAT, event.hat, value, joystick)
    elif event.type == pygame.JOYBALLMOTION:
        return Key(Key.BALL, event.ball, event.value, joystick)
    return None


def refresh_joysticks(joysticks=None):
    """Refresh the joystick list and return a list of all of the joysticks, new joysticks, and removed joysticks.

    Args:
        joysticks (list/Stash): List of pygame.joystick.Joystick objects.

    Returns:
        sticks (list): List of all pygame.joystick.Joystick objects.
        new (list): List of new joysticks where the names were not in the given list.
        removed (list): List of removed joysticks that were in the given list of joysticks, but were not found.
    """
    if joysticks is None:
        joysticks = []

    sticks = Stash()
    new = {}
    removed = {}

    with PYGAME_LOCK:
        pygame.joystick.quit()
        pygame.joystick.init()

    for i in range(pygame.joystick.get_count()):
        joy = Joystick(i)
        name = joy.get_name()

        if name in joysticks:
            sticks.append(joysticks[name])
        else:
            sticks.append(joy)
            new[name] = joy

    for joy in joysticks:
        name = joy.get_name()
        if name not in sticks:
            removed[name] = joy

    return sticks, new, removed


def get_events():
    try:
        return pygame.event.get(pump=True)
    except (AttributeError, Exception):
        pygame.event.pump()
        return pygame.event.get()


def stop_event_wait():
    """Post an event to break out of the event loop wait."""
    try:
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {}))  # Break out of wait
    except Exception:
        pass


def run_event_loop(add_joystick, remove_joystick, handle_key_event, alive=None, refresh_timeout=2, **kwargs):
    """Main function to run and handle events.

    Args:
        add_joystick (callable/function): Called when a new Joystick is found!
        remove_joystick (callable/function): Called when a Joystick is removed!
        handle_key_event (callable/function): Called when a new key event occurs!
        alive (callable/function)[None]: Function to return True to continue running. If None run forever
        refresh_timeout (int)[2]: Timeout for when to refresh the joysticks.
    """
    if alive is None:
        alive = lambda: True

    joysticks = Stash()
    last_refresh = 0  # For disconnect and reconnect

    if not get_init():
        init()

    # pygame.event.set_grab(True)

    while alive():
        try:
            # Refresh timeout
            if (time.time() - last_refresh) > refresh_timeout:
                joysticks, new, removed = refresh_joysticks(joysticks)
                for joy in removed.values():
                    remove_joystick(joy)
                for joy in new.values():
                    add_joystick(joy)
                last_refresh = time.time()

            events = get_events()
            if len(events) > 0:
                # Check events
                for event in events:  # pygame.event.get(pump=True)
                    key = key_from_event(event)
                    if key is not None:
                        handle_key_event(key)
            else:
                time.sleep(0.01)
        except:
            pass


# Attach a way to stop waiting by posting an event
run_event_loop.stop_event_wait = stop_event_wait
