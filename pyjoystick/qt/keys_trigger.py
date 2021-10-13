"""
    slatcontroller.keys_trigger
    SeaLandAire Technologies
    @author: jengel

The BindKeys in this module work with two main objects an OrderedDict of keys called "keys". The
"keys" variable holds the key values and uses those values in the keys_pressed signal. The
"key_translator" object is a regular dictionary that helps take in user input keys and modify the
"keys" dictionary values.
"""
import os
import collections
import copy
import threading

from qtpy import QtCore, QtGui, QtWidgets
from resource_man.qt import QIcon
from pyjoystick.resources import KEYBOARD_ACTIVE_IMG, KEYBOARD_INACTIVE_IMG


__all__ = ["KEYBOARD_ACTIVE_IMG", "KEYBOARD_INACTIVE_IMG",
           "BindKeys", "WASDController", "ArrowController", "GimbalController"]


class BindKeys(QtCore.QObject):
    """Event Filter for binding keys.

    Example:
        DEFAULT_KEYS = collections.OrderedDict([("up", 0), ("down", 0), ("zoom", 0)])
        DEFAULT_TRANSLATOR = {QtCore.Qt.Key_Up: "up", QtCore.Qt.Key_Down: "down",
                              QtCore.Qt.Key_Minus: ("zoom", -1, True), QtCore.Qt.Key_Equal: ("zoom", 1, True)}

    Args:
        default_keys (OrderedDict)[None]: OrderedDictionary of ("key name", default value)
        key_translator (dict/NormalKey)[None]: Key translator
            {Actual key:  ("key name", modify_value, send_on_release, send_repeat)}
    """

    keys_pressed = QtCore.Signal(collections.OrderedDict)

    KEYBOARD_ACTIVE_IMG = KEYBOARD_ACTIVE_IMG
    KEYBOARD_INACTIVE_IMG = KEYBOARD_INACTIVE_IMG

    DEFAULT_KEYS = collections.OrderedDict()
    DEFAULT_TRANSLATOR = {} # Translate keyboard keys to key names or (key names, modifier)

    def __init__(self, key_values=None, key_translator=None):
        super().__init__()

        self._is_active = False
        self.key_translator = {}
        self.keys = collections.OrderedDict()

        self.initKeyBindings(key_values, key_translator)

        # Icon and button
        self.icon = None
        self._inactive_icon = None
        self._active_icon = None
        self.init_icon()
    # end Constructor
    
    def init_icon(self):
        """Create the icon."""
        try:
            self._active_icon = QIcon(self.KEYBOARD_ACTIVE_IMG)
        except:
            self._active_icon = QIcon()
            
        try:
            self._inactive_icon = QIcon(self.KEYBOARD_INACTIVE_IMG)
        except:
            self._inactive_icon = QIcon()
 
        self.icon = QtWidgets.QPushButton(self._inactive_icon, "", None)
        self.icon.is_gamepad = self
        self.icon.clicked.connect(self.toggle_active)
        self.icon.setToolTip(self.__class__.__name__ + " using the keyboard.")
    # end init_icon
    
    def get_init(self):
        """Return if the keybinding was initialized. (More of a compatibility method for the
        controllers).
        """
        return True
    
    def is_active(self):
        """Return if the key trigger is active."""
        return self._is_active
    
    def set_active(self, value=True):
        """Set if the keyboard should be active or not."""
        if value:
            self._is_active = True
            if threading.current_thread() == threading.main_thread():
                self.icon.setIcon(self._active_icon)
        else:
            self._is_active = False
            if threading.current_thread() == threading.main_thread():
                self.icon.setIcon(self._inactive_icon)
        
    def toggle_active(self):
        """Toggle the active state on or off."""
        self.set_active(not self.is_active())

    def initKeyBindings(self, key_values=None, key_translator=None):
        """Initialize the key bindings."""
        if key_values is None:
            key_values = self.DEFAULT_KEYS
        if key_translator is None:
            key_translator = self.DEFAULT_TRANSLATOR

        # Deep copy does not work for QtCore.Qt.Key_...
        for key in key_values:
            self.keys[key] = key_values[key]

        # Deep copy does not work for QtCore.Qt.Key_...    
        for key in key_translator:
            self.key_translator[key] = key_translator[key]
    # end initKeyBindings

    def set_key_value(self, key, value, send_key=True):
        """Set a specific key's value."""
        self.keys[key] = value
        if send_key: # Not repeat or allow sending repeat
            self.keys_pressed.emit(copy.deepcopy(self.keys))
    # end set_key_value

    def on_key_press(self, key, wasautorepeat=False):
        """When one of the set keys is pressed modify the parameters and emit the signal."""
        if not self.is_active():
            return

        # Modify the value from the second part of the key
        modify = 1
        send_autorepeat = True
        if isinstance(key, (tuple, list)):
            send_autorepeat = (len(key) <= 3 or key[3])
            # Check for a modify value and do not modify value if this was an autorepeat
            if len(key) > 1:
                modify = key[1]
            key = key[0]

        # Set the key value
        value = self.keys[key]
        if not wasautorepeat:
            value += modify
        self.set_key_value(key, value, not wasautorepeat or send_autorepeat)
    # end on_key_press

    def on_key_release(self, key, wasautorepeat=False):
        """When one of the set keys is released modify the parameters and emit the signal."""
        if not self.is_active():
            return

        # Check for send on release
        modify = 1
        send_release = False
        if isinstance(key, (tuple, list)):
            send_release = (len(key) > 2 and key[2])
            # Check for a modify value and do not modify value if this was an autorepeat
            if len(key) > 1:
                modify = key[1]
            key = key[0]

        # Set the key value
        value = self.keys[key]
        if not wasautorepeat:
            value -= modify
        self.set_key_value(key, value, not wasautorepeat and send_release)
    # end on_key_release

    def keyPressEvent(self, event):
        """Press a key."""
        key = self.key_translator.get(event.key(), None)
        if key is not None:
            self.on_key_press(key, event.isAutoRepeat())
            event.accept()
            return True
        else:
            return super().keyPressEvent(event)
    # end keyPressEvent

    def keyReleaseEvent(self, event):
        """Release a key."""
        key = self.key_translator.get(event.key(), None)
        if key is not None:
            self.on_key_release(key, event.isAutoRepeat())
            event.accept()
        return super().keyReleaseEvent(event)
    # end keyReleaseEvent

    def eventFilter(self, receiver, event):
        """Event filter for key press and release setting the key values and sending the signal."""
        etype = event.type()
        if etype == QtCore.QEvent.KeyPress:
            # Set the key value
            key = self.key_translator.get(event.key(), None)
            if key is not None:
                self.on_key_press(key, event.isAutoRepeat())
                return True

        elif etype == QtCore.QEvent.KeyRelease:
            # Release the key value
            key = self.key_translator.get(event.key(), None)
            if key is not None:
                self.on_key_release(key, event.isAutoRepeat())
                return True

        elif etype == QtCore.QEvent.FocusIn:
            receiver.grabKeyboard()
            return True
        elif etype == QtCore.QEvent.FocusOut:
            receiver.releaseKeyboard()
            return True

        return super().eventFilter(receiver, event)


class WASDController(BindKeys):
    DEFAULT_KEYS = collections.OrderedDict([("w", 0), ("a", 0), ("s", 0), ("d", 0)])
    DEFAULT_TRANSLATOR = {QtCore.Qt.Key_W: "w", QtCore.Qt.Key_A: "a", 
                          QtCore.Qt.Key_S: "s", QtCore.Qt.Key_D: "d"}


class ArrowController(BindKeys):
    DEFAULT_KEYS = collections.OrderedDict([("up", 0), ("right", 0), ("down", 0), ("left", 0), ("zoom", 0)])
    DEFAULT_TRANSLATOR = {QtCore.Qt.Key_Up: "up", QtCore.Qt.Key_Down: "down",
                          QtCore.Qt.Key_Left: "left", QtCore.Qt.Key_Right: "right"}


class GimbalController(BindKeys):
    DEFAULT_KEYS = collections.OrderedDict([("pan", 0), ("tilt", 0), ("zoom", 0), ("command", 0)])
    DEFAULT_TRANSLATOR = {QtCore.Qt.Key_Up: ("tilt", 0.2, True), QtCore.Qt.Key_Down: ("tilt", -0.2, True),
                          QtCore.Qt.Key_Left: ("pan", -0.2, True), QtCore.Qt.Key_Right: ("pan", 0.2, True),
                          QtCore.Qt.Key_Minus: ("zoom", -1, True),
                          QtCore.Qt.Key_Equal: ("zoom", 1, True),
                          QtCore.Qt.Key_1: ("command", 1, True),  # Toggle IR
                          QtCore.Qt.Key_2: ("command", 2, True),  # Toggle Laser
                          }
