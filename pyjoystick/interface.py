from .stash import Stash


__all__ = ['KeyTypes', 'HatValues', 'Key', 'Joystick']


class KeyTypes:
    AXIS = "Axis"
    BUTTON = "Button"
    HAT = "Hat"
    BALL = "Ball"
    ALL_KEYTYPES = ','.join((AXIS, BUTTON, HAT, BALL))

    @classmethod
    def has_keytype(cls, keytype, key_types):
        try:
            if keytype == cls.ALL_KEYTYPES or str(keytype) in key_types:
                return True
        except (TypeError, ValueError, Exception):
            pass
        return False


class HatValues:
    HAT_CENTERED = 0
    HAT_UP = 1
    HAT_RIGHT = 2
    HAT_DOWN = 4
    HAT_LEFT = 8
    HAT_RIGHTUP = 3
    HAT_RIGHTDOWN = 6
    HAT_LEFTUP = 9
    HAT_LEFTDOWN = 12

    ALL_HAT_VALUES = (HAT_CENTERED | HAT_UP | HAT_RIGHT | HAT_DOWN | HAT_LEFT |
                      HAT_RIGHTUP | HAT_RIGHTDOWN | HAT_LEFTUP | HAT_LEFTDOWN)


class Key(object):
    # Key Types
    KeyTypes = KeyTypes
    AXIS = KeyTypes.AXIS
    BUTTON = KeyTypes.BUTTON
    HAT = KeyTypes.HAT
    BALL = KeyTypes.BALL
    ALL_KEYTYPES = KeyTypes.ALL_KEYTYPES
    has_keytype = staticmethod(KeyTypes.has_keytype)

    # HAT Values (Guessing they are more bit flags than enums.)
    HatValues = HatValues
    HAT_CENTERED = HatValues.HAT_CENTERED
    HAT_UP = HatValues.HAT_UP
    HAT_RIGHT = HatValues.HAT_RIGHT
    HAT_DOWN = HatValues.HAT_DOWN
    HAT_LEFT = HatValues.HAT_LEFT
    HAT_RIGHTUP = HatValues.HAT_RIGHTUP
    HAT_RIGHTDOWN = HatValues.HAT_RIGHTDOWN
    HAT_LEFTUP = HatValues.HAT_LEFTUP
    HAT_LEFTDOWN = HatValues.HAT_LEFTDOWN
    ALL_HAT_VALUES = HatValues.ALL_HAT_VALUES

    def __init__(self, keytype, number, value=None, joystick=None, is_repeat=False, override=False):
        self.keytype = keytype
        self.number = number
        self.value = value
        self.joystick = joystick
        self.is_repeat = is_repeat
        self.override = override

    def get_value(self):
        if self.value is None:
            return 0
        return self.value

    def set_value(self, value):
        self.value = value

    def update_value(self, joystick=None):
        if joystick is None:
            joystick = self.joystick
        try:
            v = joystick.get_key(self).get_value()
            self.value = v
        except:
            pass

    def copy(self):
        return self.__class__(self.keytype, self.number, self.value, self.joystick,
                              is_repeat=False, override=self.override)

    def __str__(self):
        if self.joystick:
            return '{}: {} {}'.format(self.joystick, self.keytype, self.number)
        else:
            return '{} {}'.format(self.keytype, self.number)

    def __repr__(self):
        if self.joystick:
            return '<{module}.{name} {joystick}: {keytype} {number} at {id}>'.format(
                    module=self.__module__, name=self.__class__.__name__, id=id(self),
                    joystick=self.joystick, keytype=self.keytype, number=self.number)
        else:
            return '<{module}.{name} {keytype} {number} at {id}>'.format(
                    module=self.__module__, name=self.__class__.__name__, id=id(self),
                    joystick=self.joystick, keytype=self.keytype, number=self.number)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        try:
            if other.keytype == self.keytype and other.number == self.number:
                # Check if joysticks match if they are not None
                if other.joystick is not None and self.joystick is not None:
                    return other.joystick == self.joystick
                return True
            return False
        except:
            pass
        try:
            return str(self) == str(other)
        except:
            return False


class Joystick(object):
    @classmethod
    def get_joysticks(cls):
        """Return a list of available joysticks."""
        # return []
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super().__init__()

        # Optional predefined variables (use with __new__)
        self.joystick = getattr(self, 'joystick', None)  # Internal joystick object

        self.identifier = getattr(self, 'identifier', -1)
        self.name = getattr(self, 'name', '')
        self.numaxes = getattr(self, 'numaxes', -1)
        self.numbuttons = getattr(self, 'numbuttons', -1)
        self.numhats = getattr(self, 'numhats', -1)
        self.numballs = getattr(self, 'numballs', -1)

        self.axis = getattr(self, 'axis', Stash())
        self.button = getattr(self, 'button', Stash())
        self.hat = getattr(self, 'hat', Stash())
        self.ball = getattr(self, 'ball', Stash())
        self.keys = getattr(self, 'keys', Stash(self.axis + self.button + self.hat + self.ball))

        self.deadband = getattr(self, 'deadband', 0.2)

        self.init_keys()

    def init_keys(self):
        """Initialize the keys."""
        self.axis = Stash(Key(Key.AXIS, i, None, self) for i in range(self.get_numaxes()))
        self.button = Stash(Key(Key.BUTTON, i, None, self) for i in range(self.get_numbuttons()))
        self.hat = Stash(Key(Key.HAT, i, None, self) for i in range(self.get_numhats()))
        self.ball = Stash(Key(Key.BALL, i, None, self) for i in range(self.get_numballs()))
        self.keys = Stash(self.axis + self.button + self.hat + self.ball)

    def is_active(self):
        """Return if this joystick is still active and available."""
        raise NotImplementedError

    def close(self):
        """Close the joystick."""
        raise NotImplementedError

    def get_key(self, key):
        """Return the key for the given key."""
        key_attr = getattr(self, str(key.keytype).lower())  # self.axis, self.button, self.hat, or self.ball
        return key_attr[key.number]

    def update_key(self, key):
        """Update the value for a given key."""
        self.get_key(key).set_value(key.value)

    def get_id(self):
        """Return the joystick id."""
        return self.identifier

    def get_name(self):
        """Return the name of the joystick."""
        return self.name

    def get_numaxes(self):
        """Return the number of axes."""
        return self.numaxes

    def get_axis(self, number):
        """Return the current value for the given axes."""
        return self.axis[number].get_value()

    def get_numbuttons(self):
        """Return the number of buttons."""
        return self.numbuttons

    def get_button(self, number):
        """Return the value for the given button number."""
        return self.button[number].get_value()

    def get_numhats(self):
        """Return the number of hats."""
        return self.numhats

    def get_hat(self, number):
        """Return the (hat [0], hat [1]) value for the given hat number."""
        return self.hat[number].get_value()

    def get_numballs(self):
        """Return the number of track balls."""
        return self.numballs

    def get_ball(self, number):
        """Return the current value for the given axes."""
        return self.ball[number].get_value()

    def get_deadband(self):
        """Return the deadband for this joystick axis."""
        return self.deadband

    def set_deadband(self, value):
        """Return the deadband for this joystick axis."""
        self.deadband = value

    def __eq__(self, other):
        name, ident, joystick = self.get_name(), self.get_id(), self.joystick
        try:
            return name == other.get_name() or ident == other or (joystick == other.joystick and joystick is not None)
        except:
            pass
        try:
            return name == other or ident == other or (joystick == other and joystick is not None)
        except:
            pass
        return False

    def __int__(self):
        return self.get_id()

    def __str__(self):
        return self.get_name()

    def __hash__(self):
        return hash('{} {}'.format(self.identifier, self.name))

    def __getstate__(self):
        return {
            'joystick': None,
            'identifier': self.identifier,
            'name': self.name,
            'numaxes': self.numaxes,
            'numbuttons': self.numbuttons,
            'numhats': self.numhats,
            'numballs': self.numballs,

            'axis': self.axis,
            'button': self.button,
            'hat': self.hat,
            'ball': self.ball,
            'keys': self.keys,

            'deadband': self.deadband
            }

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)
