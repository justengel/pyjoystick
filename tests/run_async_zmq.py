import asyncio
import zmq
from zmq.asyncio import Context
from pyjoystick.sdl2 import Key, Joystick, run_event_loop, async_event_loop


devices = Joystick.get_joysticks()
print("Devices:", devices)

monitor = devices[0]
monitor_keytypes = [Key.AXIS]
context = Context()
PUBLISHER = None


def get_pub():
    global PUBLISHER
    return PUBLISHER


def set_pub(pub):
    global PUBLISHER
    PUBLISHER = pub


async def send(data):
    global PUBLISHER
    await PUBLISHER.send(data)


async def print_add(joy):
    await send('ADD: ' + str(joy))
    print('Added', joy, '\n', end='\n', flush=True)


async def print_remove(joy):
    await send('REMOVE: ' + str(joy))
    print('Removed', joy, '\n', end='\n', flush=True)


async def key_received(key):
    if monitor is None:
        print(key, '==', key.value)
    elif key.joystick == monitor:
        await send('EVENT: ' + str(key))
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


async def main():
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://localhost:5557")
    set_pub(pub)

    await asyncio.gather(
            do_receiver(),
            do_subscriber(),
            )

asyncio.run(main())
