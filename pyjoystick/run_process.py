import traceback
import time
import threading
import multiprocessing as mp
from queue import Empty

from pyjoystick.stash import Stash
from pyjoystick.utils import PeriodicThread
from pyjoystick.run_thread import ThreadEventManager


class MultiprocessingEventManager(ThreadEventManager):
    def __init__(self, event_loop=None, add_joystick=None, remove_joystick=None, handle_key_event=None, alive=None,
                 button_repeater=None, activity_timeout=0.01):
        if alive is None:
            alive = mp.Event()
        self.proc = None
        self.queue = mp.Queue()
        super().__init__(event_loop=event_loop, add_joystick=add_joystick, remove_joystick=remove_joystick,
                         handle_key_event=handle_key_event, alive=alive, button_repeater=button_repeater,
                         activity_timeout=activity_timeout)

    def send_cmd(self, name, *args, **kwars):
        """Send a command to the main process."""
        self.queue.put((name, args, kwars))

    def _save_joystick(self, joy):
        self.save_joystick(joy)
        self.send_cmd('save_joystick', joy)

    def _delete_joystick(self, joy):
        self.delete_joystick(joy)
        self.send_cmd('delete_joystick', joy)

    def _handle_key_event(self, key):
        """Function to handle key event happens"""
        self.send_cmd('handle_key_event', key)

    def process_queue(self):
        """Continually process the Queue data."""
        while self.is_running():
            try:
                func_name, args, kwargs = self.queue.get(timeout=2)
                func = getattr(self, func_name, None)
                if func:
                    func(*args, **kwargs)
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

    def run(self, event_loop, add_joystick, remove_joystick, handle_key_event, alive=None, button_repeater=None,
            queue=None):
        """Run the an event loop to process SDL Events.

        Args:
            event_loop (callable/function): Event loop function to run.
            add_joystick (callable/function): Called when a new Joystick is found!
            remove_joystick (callable/function): Called when a Joystick is removed!
            handle_key_event (callable/function): Called when a new key event occurs!
            alive (callable/function)[None]: Function to return True to continue running. If None run forever
            button_repeater (ButtonRepeater): Thread to start which will monitor button keys and trigger repeating.
            queue (mp.Queue): Queue to communicate with the main process.
        """
        self.alive = alive
        self.button_repeater = button_repeater
        self.queue = queue

        # Run process events on a timer
        self.worker = PeriodicThread(self.activity_timeout, self.process_events)
        self.worker.alive = self.alive  # stop when this event stops
        self.worker.daemon = True
        self.worker.start()

        if button_repeater is not None:
            button_repeater.start()
        event_loop(add_joystick, remove_joystick, handle_key_event, alive=self.is_running)

    def start(self):
        """Start running the event loop."""
        self.stop()

        self.alive.set()
        self.proc = mp.Process(target=self.run,
                               args=(self.event_loop, self._save_joystick, self._delete_joystick, self._handle_key_event),
                               kwargs={'alive': self.alive, 'button_repeater': self.button_repeater,
                                       'queue': self.queue})
        self.proc.daemon = True
        self.proc.start()

        self.worker = threading.Thread(target=self.process_queue)
        self.worker.daemon = True
        self.worker.start()
