import ctypes

# ========== SDL2 Pathing ==========
import os
import sys
import platform

from pyjoystick.utils import PYJOYSTICK_DIR, change_path, rescale

# ========== SDL2 Pathing ==========
if 'windows' in platform.architecture()[1].lower():
    if '64' in platform.architecture()[0]:
        os.environ.setdefault('PYSDL2_DLL_PATH', os.path.join(PYJOYSTICK_DIR, 'sdl2_win64'))
    else:
        os.environ.setdefault('PYSDL2_DLL_PATH', os.path.join(PYJOYSTICK_DIR, 'sdl2_win32'))
# ========== END SDL2 Pathing ==========

with change_path(PYJOYSTICK_DIR):
    import sdl2

from pyjoystick.stash import Stash
from pyjoystick.interface import Key, Joystick as BaseJoystick


__all__ = ['Key', 'Joystick', 'run_event_loop',
           'get_init', 'init', 'quit', 'key_from_event',
           'get_guid', 'get_mapping', 'get_mapping_name', 'is_trigger']


class Joystick(BaseJoystick):
    @classmethod
    def get_joysticks(cls):
        # Check init
        if not get_init():
            init()

        return Stash(cls(i) for i in range(sdl2.SDL_NumJoysticks()))  # Use identifier not instance id.

    def __new__(cls, identifier=None, instance_id=None, *args, **kwargs):
        # Check init
        if not get_init():
            init()

        # Create the object
        joy = super().__new__(cls)

        if instance_id is not None:
            # Create the underlying joystick from the instance id.
            # SDL_JOYDEVICEREMOVED and all other SDL_JOY#### events give the instance id
            joy.joystick = sdl2.SDL_JoystickFromInstanceID(instance_id)
            # print('Instance ID:', raw_joystick, SDL_JoystickGetAttached(raw_joystick))
        else:
            # Create the underlying joystick from the enumerated identifier
            # SDL_JOYDEVICEADDED and SDL_NumJoysticks use open
            if identifier is None:
                identifier = 0
            if isinstance(identifier, str):
                # Get the joystick from the name or None if not found!
                for i in range(sdl2.SDL_NumJoysticks()):
                    raw_joystick = sdl2.SDL_JoystickOpen(i)
                    try:
                        if sdl2.SDL_JoystickName(raw_joystick).decode('utf-8') == identifier:
                            joy.joystick = raw_joystick
                            break
                    except:
                        pass
            else:
                joy.joystick = sdl2.SDL_JoystickOpen(identifier)
            # print('ID:', raw_joystick, SDL_JoystickGetAttached(raw_joystick))

        try:
            joy.identifier = sdl2.SDL_JoystickID(sdl2.SDL_JoystickInstanceID(joy.joystick)).value
            # joy.identifier = SDL_JoystickInstanceID(raw_joystick)
            joy.name = sdl2.SDL_JoystickName(joy.joystick).decode('utf-8')
            joy.numaxes = sdl2.SDL_JoystickNumAxes(joy.joystick)
            joy.numbuttons = sdl2.SDL_JoystickNumButtons(joy.joystick)
            joy.numhats = sdl2.SDL_JoystickNumHats(joy.joystick)
            joy.numballs = sdl2.SDL_JoystickNumBalls(joy.joystick)
            joy.init_keys()
        except:
            pass

        # Try to get the gamepad object
        try:
            joy.gamecontroller = sdl2.SDL_GameControllerOpen(joy.identifier)
            # FromInstanceId does not Attach!
            # joy.gamecontroller = SDL_GameControllerFromInstanceID(SDL_JoystickInstanceID(joy.joystick)
            # print('ID:', SDL_GameControllerGetAttached(joy.gamecontroller))
        except:
            joy.gamecontroller = None

        try:
            joy.guid = get_guid(joy.joystick)  # Using this is more reliable for the GameController stuff
        except:
            pass

        return joy

    def is_active(self):
        """Return if this joystick is still active and available."""
        try:
            return sdl2.SDL_JoystickGetAttached(self.joystick)
        except:
            return False

    def close(self):
        """Close the joystick."""
        try:
            sdl2.SDL_GameControllerClose(self.gamecontroller)
        except:
            pass
        try:
            sdl2.SDL_JoystickClose(self.joystick)
        except:
            pass


def get_init(module=sdl2.SDL_INIT_GAMECONTROLLER):
    """Return if the given module was initialized.

    Note:
        SDL_INIT_GAMECONTROLLER also initializes the joystick subsystem.
    """
    return sdl2.SDL_WasInit(module)


def init(module=sdl2.SDL_INIT_GAMECONTROLLER, *args, **kwargs):
    """Initialize the given module.

    Note:
        SDL_INIT_GAMECONTROLLER also initializes the joystick subsystem.
    """
    if get_init(module):
        quit(module)
    sdl2.SDL_Init(module)


def quit(module=sdl2.SDL_INIT_EVERYTHING):
    """Quit the given module.

    Note:
        SDL_INIT_GAMECONTROLLER also initializes the joystick subsystem.
    """
    try:
        sdl2.SDL_QUIT(module)
    except:
        pass


def get_guid(joystick):
    """Return the GUID from the given joystick object.

    Args:
        joystick (Joystick/SDL_Joystick): SDL2 joystick object

    Returns:
        guid (str): GUID String.
    """
    try:
        joystick = joystick.joystick
    except:
        pass
    guid = sdl2.SDL_JoystickGetGUID(joystick)
    guid_buff = ctypes.create_string_buffer(33)
    sdl2.SDL_JoystickGetGUIDString(guid, guid_buff, ctypes.sizeof(guid_buff))
    return guid_buff.value


def get_mapping(joystick):
    """Return the button mapping.

    Note:
        Hat keys have a value that is returned to make it easy to map a hat value to a function.

    Args:
        joystick (Joystick/str): Joystick object or String GUID

    Returns:
        d (dict): Dictionary of {name: Key} mappings
    """
    # Mapping dictionary
    mapping = {}
    map_str = None

    # ===== FROM GameController =====
    if map_str is None:
        try:
            map_str = sdl2.SDL_GameControllerMapping(joystick.gamecontroller)
        except:
            try:
                map_str = sdl2.SDL_GameControllerMapping(joystick)
            except:
                pass

    # ===== FROM GUID =====
    if map_str is None:
        try:
            guid = sdl2.SDL_JoystickGetGUIDFromString(joystick.guid)
            map_str = sdl2.SDL_GameControllerMappingForGUID(guid)
        except:
            try:
                guid = sdl2.SDL_JoystickGetGUID(joystick)
                map_str = sdl2.SDL_GameControllerMappingForGUID(guid)
            except:
                pass

    # Check the type
    if map_str is None:
        return mapping
    try:
        map_str = map_str.decode('utf-8')
    except:
        pass

    for item in map_str.split(','):
        if ":" in item:
            name, key = item.split(':', 1)
            if key.startswith('b'):
                mapping[name] = Key(Key.BUTTON, int(key[1:]), joystick=joystick)
            elif key.startswith('a'):
                mapping[name] = Key(Key.AXIS, int(key[1:]), joystick=joystick)
            elif key.startswith('h'):
                key, val = key.split('.', 1)
                mapping[name] = Key(Key.HAT, int(key[1:]), value=int(val), joystick=joystick)
    return mapping


def get_mapping_name(joystick, key):
    """Return the mapping name currently associated with this key."""
    for name, k in get_mapping(joystick).items():
        if key.keytype == k.keytype and key.number == k.number:
            if key.keytype == k.HAT:  # Hat also checks for the value
                if k.value == key.value:
                    return name
            else:
                return name
    return None


def is_trigger(joystick, axis_id):
    """Return if the given joystick axis is a trigger (Don't want triggers scaled from -1 resting to 1).

    Args:
          joystick (SDLJoystick): Joystick object
          axis_id (int): Axis number to check

    Returns:
          is_trigger (bool): If True this axis is a trigger.
    """
    try:
        if not sdl2.SDL_GameControllerGetAttached(joystick.gamecontroller):
            return 'trigger' in str(get_mapping_name(joystick, Key(Key.AXIS, axis_id))).lower()
    except:
        return False

    # Check the left trigger
    try:
        bind = sdl2.SDL_GameControllerGetBindForAxis(joystick.gamecontroller, sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT)
        if bind.bindType == sdl2.SDL_CONTROLLER_BINDTYPE_AXIS and bind.value.axis == axis_id:
            return True
    except:
        try:
            return 'trigger' in str(get_mapping_name(joystick, Key(Key.AXIS, axis_id))).lower()
        except:
            pass

    # Check the right trigger
    try:
        bind = sdl2.SDL_GameControllerGetBindForAxis(joystick.gamecontroller, sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT)
        if bind.bindType == sdl2.SDL_CONTROLLER_BINDTYPE_AXIS and bind.value.axis == axis_id:
            return True
    except:
        try:
            return 'trigger' in str(get_mapping_name(joystick, Key(Key.AXIS, axis_id))).lower()
        except:
            pass

    return False


def key_from_event(event, joystick=None):
    """Every library type should implement a key_from_event function to convert an event into a key.

    Args:
        event (SDL_Event): Event that occurred
        joystick (Joystick)[None]: Joystick object

    Returns:
        key (Key)[None]: Key created from the event.
    """
    if joystick is None:
        try:
            joystick = Joystick(instance_id=event.jdevice.which)
        except (ValueError, TypeError, Exception):
            return None

    if event.type == sdl2.SDL_JOYBUTTONDOWN:
        return Key(Key.BUTTON, event.jbutton.button, 1, joystick)
    elif event.type == sdl2.SDL_JOYBUTTONUP:
        return Key(Key.BUTTON, event.jbutton.button, 0, joystick)
    elif event.type == sdl2.SDL_JOYAXISMOTION:
        value = event.jaxis.value
        if is_trigger(joystick, event.jaxis.axis):
            value = rescale(value, -32768, 32767, 0, 1)  # Make triggers rest at 0
        else:
            value = rescale(value, -32768, 32767, -1, 1)
        return Key(Key.AXIS, event.jaxis.axis, value, joystick)
    elif event.type == sdl2.SDL_JOYHATMOTION:
        return Key(Key.HAT, event.jhat.hat, event.jhat.value, joystick)
    elif event.type == sdl2.SDL_JOYBALLMOTION:
        # WIP (NOT TESTED)
        return Key(Key.BALL, event.jball.ball, event.jball.value, joystick)
    return None


def run_event_loop(add_joystick, remove_joystick, handle_key_event, alive=None, **kwargs):
    """Run the an event loop to process SDL Events.

    Args:
        add_joystick (callable/function): Called when a new Joystick is found!
        remove_joystick (callable/function): Called when a Joystick is removed!
        handle_key_event (callable/function): Called when a new key event occurs!
        alive (callable/function)[None]: Function to return True to continue running. If None run forever
    """
    if alive is None:
        alive = lambda: True

    if not get_init():
        init()

    event = sdl2.SDL_Event()
    while alive():
        if sdl2.SDL_WaitEventTimeout(ctypes.byref(event), 2000) != 0:
            # Check the event
            if event.type == sdl2.SDL_JOYDEVICEADDED:
                try:
                    # NOTE: event.jdevice.which is the id to use for SDL_JoystickOpen()
                    joy = Joystick(identifier=event.jdevice.which)
                    add_joystick(joy)
                except:
                    pass
            elif event.type == sdl2.SDL_JOYDEVICEREMOVED:
                try:
                    # NOTE: event.jdevice.which is the id to use for SDL_JoystickFromInstanceID()
                    joy = Joystick(instance_id=event.jdevice.which)
                    remove_joystick(joy)
                except:
                    pass
            else:
                # NOTE: event.jdevice.which is the id to use for SDL_JoystickFromInstanceID()
                joy = Joystick(instance_id=event.jdevice.which)
                key = key_from_event(event, joy)
                if key is not None:
                    handle_key_event(key)
