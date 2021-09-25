from .__meta__ import version as __version__

from .utils import deadband, change_path, rescale, PeriodicThread
from .stash import Stash
from .button_repeater import Repeater, ButtonRepeater, HatRepeater, ButtonHatRepeater
from .interface import Key, Joystick

try:
    from .sdl2 import Joystick as SDLJoystick, run_event_loop as run_sdl_loop
except (ImportError, Exception):
    SDLJoystick = None
    run_sdl_loop = None

try:
    from .sdl2_async import run_event_loop as run_sdl_loop_async
except (ImportError, SyntaxError, Exception):
    run_sdl_loop_async = None

from .run_thread import ThreadEventManager
from .run_process import MultiprocessingEventManager
