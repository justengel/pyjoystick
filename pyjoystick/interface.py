from .stash import Stash


__all__ = ['KeyTypes', 'HatValues', 'Key', 'Joystick']


class KeyTypes:
    """Types of keys the controller could report (Axis, Button, Hat, Ball)."""
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
    """Have values and converters. Values are numbered like bit flags."""
    HAT_CENTERED = 0
    HAT_UP = 1
    HAT_RIGHT = 2
    HAT_DOWN = 4
    HAT_LEFT = 8
    HAT_RIGHTUP = HAT_UPRIGHT = 3
    HAT_RIGHTDOWN = HAT_DOWNRIGHT = 6
    HAT_LEFTUP = HAT_UPLEFT = 9
    HAT_LEFTDOWN = HAT_DOWNLEFT = 12

    ALL_HAT_VALUES = (HAT_CENTERED | HAT_UP | HAT_RIGHT | HAT_DOWN | HAT_LEFT |
                      HAT_UPRIGHT | HAT_DOWNRIGHT | HAT_UPLEFT | HAT_DOWNLEFT)

    HAT_NAME_CENTERED = 'Centered'
    HAT_NAME_UP = 'Up'
    HAT_NAME_RIGHT = 'Right'
    HAT_NAME_DOWN = 'Down'
    HAT_NAME_LEFT = 'Left'
    HAT_NAME_UPRIGHT = HAT_NAME_RIGHTUP = 'Up Right'
    HAT_NAME_DOWNRIGHT = HAT_NAME_RIGHTDOWN = 'Down Right'
    HAT_NAME_UPLEFT = HAT_NAME_LEFTUP = 'Up Left'
    HAT_NAME_DOWNLEFT = HAT_NAME_LEFTDOWN = 'Down Left'

    HAT_CONVERTER = {
        HAT_CENTERED: HAT_NAME_CENTERED, HAT_UP: HAT_NAME_UP, HAT_RIGHT: HAT_NAME_RIGHT, HAT_DOWN: HAT_NAME_DOWN,
        HAT_LEFT: HAT_NAME_LEFT, HAT_UPRIGHT: HAT_NAME_UPRIGHT, HAT_DOWNRIGHT: HAT_NAME_DOWNRIGHT,
        HAT_UPLEFT: HAT_NAME_UPLEFT, HAT_DOWNLEFT: HAT_NAME_DOWNLEFT,
        }

    NAME_CONVERTER = {name: value for value, name in HAT_CONVERTER.items()}

    HAT_TO_RANGE = {
        HAT_CENTERED: (0, 0), HAT_NAME_CENTERED: (0, 0),
        HAT_UP: (0, 1), HAT_NAME_UP: (0, 1),
        HAT_RIGHT: (1, 0), HAT_NAME_RIGHT: (1, 0),
        HAT_DOWN: (0, -1), HAT_NAME_DOWN: (0, -1),
        HAT_LEFT: (-1, 0), HAT_NAME_LEFT: (-1, 0),
        HAT_RIGHTUP: (1, 1), HAT_NAME_RIGHTUP: (1, 1),
        HAT_RIGHTDOWN: (1, -1), HAT_NAME_RIGHTDOWN: (1, -1),
        HAT_LEFTUP: (-1, 1), HAT_NAME_LEFTUP: (-1, 1),
        HAT_LEFTDOWN: (-1, -1), HAT_NAME_LEFTDOWN: (-1, -1),
        }

    HAT_FROM_RANGE = {
        (0, 0): HAT_CENTERED,
        (0, 1): HAT_UP,
        (1, 0): HAT_RIGHT,
        (0, -1): HAT_DOWN,
        (-1, 0): HAT_LEFT,
        (1, 1): HAT_RIGHTUP,
        (1, -1): HAT_RIGHTDOWN,
        (-1, 1): HAT_LEFTUP,
        (-1, -1): HAT_LEFTDOWN,
        }

    HAT_NAME_FROM_RANGE = {
        (0, 0): HAT_NAME_CENTERED,
        (0, 1): HAT_NAME_UP,
        (1, 0): HAT_NAME_RIGHT,
        (0, -1): HAT_NAME_DOWN,
        (-1, 0): HAT_NAME_LEFT,
        (1, 1): HAT_NAME_RIGHTUP,
        (1, -1): HAT_NAME_RIGHTDOWN,
        (-1, 1): HAT_NAME_LEFTUP,
        (-1, -1): HAT_NAME_LEFTDOWN,
        }

    @classmethod
    def convert_to_hat_name(cls, hat_value):
        """Return the given hat_value as a string name"""
        return cls.HAT_CONVERTER.get(hat_value, str(hat_value))

    @classmethod
    def convert_to_hat_value(cls, hat_name):
        """Return the given hat_name as an integer value. If -1 is returned it is an invalid value."""
        try:
            value = int(hat_name)
        except (TypeError, ValueError, Exception):
            value = -1
        return cls.NAME_CONVERTER.get(hat_name, value)

    @classmethod
    def as_range(cls, hat, default=None):
        if default is None:
            default = hat
        return cls.HAT_TO_RANGE.get(hat, default)

    @classmethod
    def from_range(cls, hat, default=None):
        if default is None:
            default = hat
        return cls.HAT_FROM_RANGE.get(hat, default)

    @classmethod
    def name_from_range(cls, hat, default=None):
        if default is None:
            default = hat
        return cls.HAT_NAME_FROM_RANGE.get(hat, default)


class Key(object):
    """Key that the controller received. This stores the key type, value, and other properties to use."""
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
    HAT_RIGHTUP = HAT_UPRIGHT = HatValues.HAT_UPRIGHT
    HAT_RIGHTDOWN = HAT_DOWNRIGHT = HatValues.HAT_DOWNRIGHT
    HAT_LEFTUP = HAT_UPLEFT = HatValues.HAT_UPLEFT
    HAT_LEFTDOWN = HAT_DOWNLEFT = HatValues.HAT_DOWNLEFT
    ALL_HAT_VALUES = HatValues.ALL_HAT_VALUES

    HAT_NAME_CENTERED = HatValues.HAT_NAME_CENTERED
    HAT_NAME_UP = HatValues.HAT_NAME_UP
    HAT_NAME_RIGHT = HatValues.HAT_NAME_RIGHT
    HAT_NAME_DOWN = HatValues.HAT_NAME_DOWN
    HAT_NAME_LEFT = HatValues.HAT_NAME_LEFT
    HAT_NAME_UPRIGHT = HAT_NAME_RIGHTUP = HatValues.HAT_NAME_UPRIGHT
    HAT_NAME_DOWNRIGHT = HAT_NAME_RIGHTDOWN = HatValues.HAT_NAME_DOWNRIGHT
    HAT_NAME_UPLEFT = HAT_NAME_LEFTUP = HatValues.HAT_NAME_UPLEFT
    HAT_NAME_DOWNLEFT = HAT_NAME_LEFTDOWN = HatValues.HAT_NAME_DOWNLEFT

    convert_to_hat_name = staticmethod(HatValues.convert_to_hat_name)
    convert_to_hat_value = staticmethod(HatValues.convert_to_hat_value)
    convert_to_hat_range = staticmethod(HatValues.as_range)

    def __init__(self, keytype, number, value=None, joystick=None, is_repeat=False, override=False):
        self.keytype = keytype
        self.number = number
        self.raw_value = None
        self.joystick = joystick
        self.is_repeat = is_repeat
        self.override = override

        self.set_value(value)

    def get_hat_name(self):
        """Return the value as a HAT name."""
        if self.keytype != self.HAT:
            raise TypeError('The Key must be a HAT keytype in order to get the hat name.')
        return self.convert_to_hat_name(self.raw_value)

    def get_hat_range(self):
        """Return the key as a range (right[1]/left[-1], up[1]/down[-1])."""
        if self.keytype != self.HAT:
            raise TypeError('The Key must be a HAT keytype in order to get the hat name.')
        return self.convert_to_hat_range(self.raw_value)

    def get_proper_value(self):
        """Return the value between -1 and 1. Hat values act like buttons and will be 1 or 0.
        Use get_hat_name to check the keytype.
        """
        if self.raw_value is None:
            return 0
        elif self.raw_value > 1:
            return 1
        return self.raw_value

    def get_value(self):
        """Return the value of the key"""
        if self.raw_value is None:
            return 0
        return self.raw_value

    def set_value(self, value):
        """Set the value of the key"""
        self.raw_value = value

    value = property(get_value, set_value)

    def update_value(self, joystick=None):
        """Set this key's value from the set or given joystick's associated key value."""
        if joystick is None:
            joystick = self.joystick
        try:
            v = joystick.get_key(self).get_value()
            self.value = v
        except:
            pass

    def copy(self):
        """Create a copy of the key."""
        return self.__class__(self.keytype, self.number, self.value, self.joystick,
                              is_repeat=False, override=self.override)

    @classmethod
    def to_keyname(cls, key):
        """Return this key as a string keyname.

          * Format is "{minus}{keytype} {number}".
          * Hat format is "{keytype} {number} {hat_name}"

        Examples
            * "Axis 0" - For Axis 0 with a positive or 0 value.
            * "-Axis 1" - For an Axis Key that has a negative value and needs to be inverted.
            * "Button 0" - Buttons wont have negative values
            * "Hat 0 [Left Up]" - Hat values also give the key value as a hat name.
        """
        prefix = ''
        if key.value and key.value < 0:
            prefix = '-'

        if key.keytype == cls.HAT:
            return '{}{} {} [{}]'.format(prefix, key.keytype, key.number, key.get_hat_name())
        else:
            return '{}{} {}'.format(prefix, key.keytype, key.number)

    @classmethod
    def from_keyname(cls, keyname, joystick=None):
        """Return a new key from the given keyname."""
        # Remove any joystick name attached
        keyname = str(keyname)
        if ':' in keyname:
            keyname = keyname.split(':', 1)[-1].strip()

        # Split the keyname
        keytype, number = keyname.split(' ', 1)

        # Check if the keyname starts with a negative.
        value = None
        if keytype.startswith('-'):
            value = -1
            keytype = keytype[1:].strip()

        # Check if the number has '['
        if '[' in number:
            number, hat_name = number.split('[', 1)
            number = number.strip()
            value = int(cls.convert_to_hat_value(hat_name.replace(']', '').strip()))
        number = int(number)

        return Key(keytype, number, value, joystick=joystick)

    @property
    def keyname(self):
        return self.to_keyname(self)

    @keyname.setter
    def keyname(self, keyname):
        new_key = self.from_keyname(keyname)
        self.keytype = new_key.keytype
        self.number = new_key.number
        if self.value:
            self.value = new_key.value

    def __str__(self):
        return self.to_keyname(self)

    def __repr__(self):
        if self.joystick:
            return '<{module}.{name} {joystick}: {keyname} at {id}>'.format(
                    module=self.__module__, name=self.__class__.__name__, id=id(self),
                    joystick=self.joystick, keyname=self.keyname)
        else:
            return '<{module}.{name} {keyname} at {id}>'.format(
                    module=self.__module__, name=self.__class__.__name__, id=id(self),
                    joystick=self.joystick, keyname=self.keyname)

    def __hash__(self):
        return hash('{} {}'.format(self.keytype, self.number))

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

    def is_available(self):
        """Return if this joystick is still active and available."""
        raise NotImplementedError

    def close(self):
        """Close the joystick."""
        raise NotImplementedError

    def get_key(self, key):
        """Return the key for the given key."""
        key_attr = getattr(self, str(key.keytype).lower())  # self.axis, self.button, self.hat, or self.ball
        return key_attr[key.number]

    def get_key_value(self, key):
        """Return the current value of this joystick's key for the given key."""
        return self.get_key(key).get_value()

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
        name, my_id, joystick = self.get_name(), self.get_id(), self.joystick
        try:
            return name == other.get_name() or my_id == other or (joystick == other.joystick and joystick is not None)
        except:
            pass
        try:
            is_id = not isinstance(other, bool) and my_id == other
            return is_id or name == other or (joystick == other and joystick is not None)
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
