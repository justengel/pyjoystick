if __name__ == '__main__':
    from pyjoystick.pygame import Key, Joystick, run_event_loop

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
            value = '{:2.2f}'.format(key.value)
        except:
            if key.value is None:
                value = ''
            else:
                value = '{:5}'.format(key.value)
        return '{} {} == {:>5}'.format(key.keytype, key.number, value)

    run_event_loop(print_add, print_remove, key_received)
