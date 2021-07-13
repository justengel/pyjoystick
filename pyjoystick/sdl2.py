import os
import sys
import platform
import ctypes

from pyjoystick.utils import files, as_file, change_path, rescale
from pyjoystick.stash import Stash
from pyjoystick.interface import Key, Joystick as BaseJoystick

# ========== SDL2 Pathing ==========
with as_file(files('pyjoystick')) as PYJOYSTICK_DIR:  # Find SDL2 resource files properly
    if 'windows' in platform.architecture()[1].lower():
        if '64' in platform.architecture()[0]:
            os.environ.setdefault('PYSDL2_DLL_PATH', os.path.join(PYJOYSTICK_DIR, 'sdl2_win64'))
        else:
            os.environ.setdefault('PYSDL2_DLL_PATH', os.path.join(PYJOYSTICK_DIR, 'sdl2_win32'))

    import sdl2
# ========== END SDL2 Pathing ==========



__all__ = ['Key', 'Joystick', 'run_event_loop', 'stop_event_wait',
           'sdl2', 'get_init', 'init', 'quit', 'key_from_event',
           'get_guid', 'get_str_mapping', 'get_mapping', 'get_mapping_name', 'make_str_mapping', 'set_mapping',
           'is_trigger']


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

    def is_available(self):
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


def get_str_mapping(joystick):
    """Return the mapping string for the joystick.

    https://wiki.libsdl.org/SDL_GameControllerAddMapping?highlight=%28%5CbCategoryGameController%5Cb%29%7C%28CategoryEnum%29

    Note:
        Hat keys have a value that is returned to make it easy to map a hat value to a function.

    Args:
        joystick (Joystick/str): Joystick object or String GUID

    Returns:
        map_str (string): The mapping string that is returned from sdl2
    """
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

    if map_str is not None:
        try:
            map_str = map_str.decode('utf-8')
        except:
            pass
        return map_str
    return ''


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
    map_str = get_str_mapping(joystick)

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


def make_str_mapping(joystick, mapping):
    """Make the button mapping.
    Note:
        Hat keys should have a set value for the proper quadrant.

    Args:
        joystick (Joystick/str): Joystick object or String GUID
        mapping (dict): Dictionary of name: Key values to map to the joystick/game controller.

    Returns:
        map_str (str): String mapping to give to sdl2
    """
    # Mapping String
    guid = joystick
    name = joystick
    try:
        guid = joystick.guid.decode('utf-8')
    except (AttributeError, Exception):
        try:
            guid = sdl2.SDL_JoystickGetGUID(joystick.guid)
        except (AttributeError, Exception):
            try:
                guid = sdl2.SDL_JoystickGetGUID(joystick)
            except (AttributeError, Exception):
                pass
    try:
        name = joystick.name
    except (AttributeError, Exception):
        pass

    keys = ','.join(('{}:{}'.format(name, _key_to_mapping(key))
                     for name, key in mapping.items() if _is_key_mapping(key)))
    map_str = ','.join((str(guid), str(name), keys))
    return map_str


def set_mapping(joystick, mapping):
    """Set the button mapping.

    Note:
        Hat keys should have a set value for the proper quadrant.

    Args:
        joystick (Joystick/str): Joystick object or String GUID
        mapping (dict): Dictionary of name: Key values to map to the joystick/game controller.

    Raises:
        ValueError: If the mapping was invalid.

    Returns:
        success (int): If 1 the mapping was added. If 0 the prefious mapping was updated
    """
    map_str = make_str_mapping(joystick, mapping)
    res = sdl2.SDL_GameControllerAddMapping(map_str.encode('utf-8'))
    if res == -1:
        raise ValueError('Invalid game controller mapping! Tried mapping "{}".'.format(map_str))
    return res


def _is_key_mapping(key):
    keytype = key.keytype
    return keytype == Key.BUTTON or keytype == Key.AXIS or keytype == Key.HAT


def _key_to_mapping(key):
    if key.keytype == Key.BUTTON:
        return 'b{}'.format(key.number)
    elif key.keytype == Key.AXIS:
        return 'a{}'.format(key.number)
    elif key.keytype == Key.HAT:
        return 'h{}.{}'.format(key.number, key.value)
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
        # Prioritize GameController mapping?
        if not sdl2.SDL_GameControllerGetAttached(joystick.gamecontroller):
            key_name = str(get_mapping_name(joystick, Key(Key.AXIS, axis_id))).lower()
            return 'trigger' in key_name
    except:
        pass

    # Check the left trigger
    try:
        bind = sdl2.SDL_GameControllerGetBindForAxis(joystick.gamecontroller, sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT)
        if bind.bindType == sdl2.SDL_CONTROLLER_BINDTYPE_AXIS and bind.value.axis == axis_id:
            return True
    except:
        pass

    # Check the right trigger
    try:
        bind = sdl2.SDL_GameControllerGetBindForAxis(joystick.gamecontroller, sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT)
        if bind.bindType == sdl2.SDL_CONTROLLER_BINDTYPE_AXIS and bind.value.axis == axis_id:
            return True
    except:
        pass

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


def stop_event_wait():
    """Post an event to break out of the event loop wait."""
    try:
        user_event = sdl2.SDL_Event()
        user_event.type = sdl2.SDL_USEREVENT
        user_event.user.code = 2
        user_event.user.data1 = None
        user_event.user.data2 = None
        sdl2.SDL_PushEvent(ctypes.byref(user_event))
    except:
        pass


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


# Attach a way to stop waiting by posting an event
run_event_loop.stop_event_wait = stop_event_wait
