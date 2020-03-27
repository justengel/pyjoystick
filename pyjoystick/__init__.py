from .__meta__ import version as __version__

from .utils import PYJOYSTICK_DIR, change_path, rescale, PeriodicThread
from .button_repeater import Repeater, ButtonRepeater, HatRepeater, ButtonHatRepeater
from .interface import Key, Joystick

try:
    from .sdl2 import Joystick as SDLJoystick, run_event_loop as run_sdl_loop
except:
    SDLJoystick = None
    run_sdl_loop = None

from .run_thread import ThreadEventManager
# from .run_process import MultiprocessingEventManager
