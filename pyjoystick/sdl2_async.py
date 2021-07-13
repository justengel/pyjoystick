import asyncio
import inspect
import functools
import ctypes
from pyjoystick.sdl2 import Key, Joystick, EventLoop, \
    JoystickEventLoop as BaseJoystickEventLoop, ControllerEventLoop as BaseControllerEventLoop, stop_event_wait, \
    sdl2, get_init, init, quit, key_from_event, joystick_key_from_event, controller_key_from_event, \
    get_str_mapping, get_mapping, get_mapping_name, get_key_mapping, make_str_mapping, set_mapping, \
    is_trigger, get_guid, rescale


__all__ = ['Key', 'Joystick', 'EventLoop', 'JoystickEventLoop', 'ControllerEventLoop',
           'stop_event_wait', 'run_event_loop',
           'sdl2', 'get_init', 'init', 'quit', 'key_from_event', 'joystick_key_from_event', 'controller_key_from_event',
           'get_str_mapping', 'get_mapping', 'get_mapping_name', 'get_key_mapping', 'make_str_mapping', 'set_mapping',
           'is_trigger', 'get_guid', 'rescale']


GLOBAL_LOOP = None


def get_loop():
    """Get the current async event loop."""
    global GLOBAL_LOOP
    if GLOBAL_LOOP is not None:
        return GLOBAL_LOOP

    try:
        GLOBAL_LOOP = asyncio.get_running_loop()
        return GLOBAL_LOOP
    except (AttributeError, RuntimeError, TypeError, RuntimeError, Exception):
        try:
            GLOBAL_LOOP = asyncio.get_event_loop()
            return GLOBAL_LOOP
        except (AttributeError, TypeError, RuntimeError, Exception):
            return GLOBAL_LOOP


async def call_async(callback=None, *args, LOOP=None, **kwargs):
    """Call the given callback function. This function can be a normal function or a coroutine."""
    if LOOP is None:
        LOOP = get_loop()

    if inspect.iscoroutinefunction(callback):
        return await callback(*args, **kwargs)
    elif callable(callback):
        return await LOOP.run_in_executor(None, functools.partial(callback, *args, **kwargs))


async def stop_event_wait_async(LOOP=None):
    """Post an event to break out of the event loop wait."""
    if LOOP is None:
        LOOP = get_loop()
    return await LOOP.run_in_executor(None, stop_event_wait)


class AsyncEventLoop(EventLoop):
    @property
    def loop(self):
        """Return the async loop. This can be set in the __init__ with kwargs."""
        loop = getattr(self, '_loop', None)
        if loop is None:
            loop = get_loop()
        return loop

    @loop.setter
    def loop(self, value):
        setattr(self, '_loop', value)

    async def call_event_async(self, event):
        """Call the given event with the registered event type function."""
        # If event.type not registered try None as a general event handler.
        callback = self.event_handler.get(event.type, self.event_handler.get(None, None))
        return await call_async(callback, event, LOOP=self.loop)

    async def run_async(self):
        try:
            self.alive.set()
        except (AttributeError, Exception):
            pass

        async for event in self:
            await self.call_event_async(event)

    async def stop_event_wait_async(self):
        """Post an event to break out of the event loop wait."""
        return await self.loop.run_in_executor(None, stop_event_wait)

    def __aiter__(self):
        return self

    async def __anext__(self):
        while self.is_alive():
            # Wait for an event
            if await self.loop.run_in_executor(None, sdl2.SDL_WaitEventTimeout, ctypes.byref(self.event), 2000) != 0:
                return self.event  # If the event was successful return the event

        # If not alive raise stop
        raise StopAsyncIteration


EventLoop.loop = AsyncEventLoop.loop
EventLoop.call_event_async = AsyncEventLoop.call_event_async
EventLoop.run_async = AsyncEventLoop.run_async
EventLoop.stop_event_wait_async = AsyncEventLoop.stop_event_wait_async
EventLoop.__aiter__ = AsyncEventLoop.__aiter__
EventLoop.__anext__ = AsyncEventLoop.__anext__


class JoystickEventLoop(BaseJoystickEventLoop):
    def __init__(self, add=None, remove=None, handle_key=None, key_from_event=joystick_key_from_event,
                 alive=None, event=None, timeout=2000, **kwargs):
        super().__init__(add=add, remove=remove, handle_key=handle_key, key_from_event=key_from_event, alive=alive,
                         event=event, timeout=timeout, **kwargs)

        # Register base events
        self.register(sdl2.SDL_JOYDEVICEADDED, self.on_add_async)
        self.register(sdl2.SDL_JOYDEVICEREMOVED, self.on_remove_async)
        self.register(None, self.on_key_event_async)  # Every other event

    async def on_add_async(self, event):
        try:
            await call_async(self.add, self.get_joystick(event))
        except (AttributeError, Exception):
            pass

    async def on_remove_async(self, event):
        try:
            await call_async(self.remove, self.get_joystick(event))
        except (AttributeError, Exception):
            pass

    async def on_key_event_async(self, event):
        key = await call_async(self.key_from_event, event, self.get_joystick(event))
        if key is not None:
            await call_async(self.handle_key, key)


class ControllerEventLoop(BaseControllerEventLoop):
    def __init__(self, add=None, remove=None, handle_key=None, key_from_event=controller_key_from_event,
                 alive=None, event=None, timeout=2000, **kwargs):
        super().__init__(add=add, remove=remove, handle_key=handle_key, key_from_event=key_from_event, alive=alive,
                         event=event, timeout=timeout, **kwargs)

        # Register base events
        self.register(sdl2.SDL_CONTROLLERDEVICEADDED, self.on_add_async)
        self.register(sdl2.SDL_CONTROLLERDEVICEREMOVED, self.on_remove_async)
        self.register(sdl2.SDL_CONTROLLERDEVICEREMAPPED, self.on_mapped_async)
        self.register(None, self.on_key_event_async)  # Every other event

    async def on_add_async(self, event):
        try:
            await call_async(self.add, self.get_joystick(event))
        except (AttributeError, Exception):
            pass

    async def on_remove_async(self, event):
        try:
            await call_async(self.remove, self.get_joystick(event))
        except (AttributeError, Exception):
            pass

    async def on_mapped_async(self, event):
        try:
            await self.loop.run_in_executor(None, self.on_mapped, event)
        except (AttributeError, Exception):
            pass

    async def on_key_event_async(self, event):
        key = await call_async(self.key_from_event, event, self.get_joystick(event))
        if key is not None:
            await call_async(self.handle_key, key)


async def run_event_loop(add, remove, handle_key, alive=None, **kwargs):
    """Run the an event loop to process SDL Events.

    Args:
        add (callable/function): Called when a new Joystick is found!
        remove (callable/function): Called when a Joystick is removed!
        handle_key (callable/function): Called when a new key event occurs!
        alive (callable/function)[None]: Function to return True to continue running. If None run forever
    """
    event_loop = JoystickEventLoop(add, remove, handle_key, alive=alive, key_from_event=key_from_event, **kwargs)
    await event_loop.run_async()  # Inherited through EventLoop. Yeah I get it it's a little weird.


# Attach a way to stop waiting by posting an event
run_event_loop.stop_event_wait = stop_event_wait
run_event_loop.stop_event_wait_async = stop_event_wait_async
