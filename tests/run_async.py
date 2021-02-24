import asyncio
from pyjoystick.sdl2 import Key, Joystick, run_event_loop, async_event_loop


if __name__ == '__main__':
    import time
    from typing import Union
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

    clients = []

    async def send(msg: Union[str, bytes]):
        str_msg = msg
        if isinstance(msg, str):
            msg = msg.encode()
        else:
            str_msg = msg.decode()

        for client in clients:
            client.write(msg)
        await asyncio.gather((client.drain() for client in clients))
        print(str_msg + '\n', end='\n', flush=True)


    async def print_add(joy):
        await send('ADD: ' + str(joy))


    async def print_remove(joy):
        await send('REMOVE: ' + str(joy))


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


    async def add_client(reader, writer):
        clients.append(writer)

    async def run_server():
        server = await asyncio.start_server(add_client, '127.0.0.1', 8898)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def main():
        await asyncio.gather(run_server(),
                             async_event_loop(print_add, print_remove, key_received))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    for client in clients:
        print('Close the connection')
        client.close()
        await client.wait_closed()
    loop.close()
