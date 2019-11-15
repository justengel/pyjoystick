from pyjoystick.sdl2 import Key, Joystick, run_event_loop


if __name__ == '__main__':
    import time
    import argparse

    P = argparse.ArgumentParser(description='Run a thread event loop.')
    P.add_argument('--lib', type=str, default='sdl', choices=['sdl', 'pygame'],
                   help='Library to run the thread event loop with.')
    P.add_argument('--timeout', type=float, default=float('inf'), help='Time to run for')
    P.add_argument('--keytype', type=str, default=None, choices=[Key.AXIS, ])

    devices = Joystick.get_joysticks()
    print("Devices:", devices)

    monitor = devices[0]
    monitor_keytypes = [Key.AXIS]


    def print_add(joy):
        print('Added', joy, '\n', end='\n', flush=True)

    def print_remove(joy):
        print('Removed', joy, '\n', end='\n', flush=True)

    def key_received(key):
        if monitor is None:
            print(key, '==', key.value)
        elif key.joystick == monitor:
            monitor.update_key(key)

            keys = '\t'.join((format_key(k) for k in monitor.keys if k.keytype in monitor_keytypes))
            print('\r', keys, end='', flush=True)

    def format_key(key):
        try:
            value = key.value
            if isinstance(value, float):
                value = '{:2.2f}'.format(key.value)
            else:
                value = str(value)
        except:
            if key.value is None:
                value = '0'
            else:
                value = '{:5}'.format(key.value)
        return '{} {} == {:>5}'.format(key.keytype, key.number, value)

    run_event_loop(print_add, print_remove, key_received)
