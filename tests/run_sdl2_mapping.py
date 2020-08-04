from pyjoystick.sdl2 import Key, Joystick, run_event_loop, get_mapping, set_mapping, get_mapping_name, is_trigger


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
