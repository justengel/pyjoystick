from pyjoystick.sdl2 import sdl2, Key, Joystick, ControllerEventLoop, get_mapping, set_mapping


if __name__ == '__main__':
    import time
    import argparse
    devices = Joystick.get_joysticks()
    print("Devices:", devices)

    monitor = devices[0]
    monitor_keytypes = [Key.AXIS]

    for k, v in get_mapping(monitor).items():
        print(k, ":", v)

    set_mapping(monitor, {'lefttrigger': Key(Key.BUTTON, 0), 'righttrigger': Key(Key.BUTTON, 1),
                          'a': Key(Key.AXIS, 2), 'b': Key(Key.AXIS, 5)})

    print()
    print("New mapping:")
    for k, v in get_mapping(monitor).items():
        print(k, ":", v)


#################################
def print_add(joy):
    print('Added', joy)


def print_remove(joy):
    print('Removed', joy)


def key_received(key):
    # Make joystick key and event key values match
    monitor.update_key(key)

    # Get mapping name
    key_name = key.joystick.key_mapping.get(key, None)
    if not key_name:
        return

    if key_name == 'a':
        # A button pressed do action
        print('Action on button A')
    else:
        print('Key:', key_name, 'Value:', key.value, 'Joystick:', key.joystick)


ControllerEventLoop(print_add, print_remove, key_received).run()
