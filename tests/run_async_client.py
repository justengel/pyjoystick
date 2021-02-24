import asyncio


async def tcp_print_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8898)

    message = ''
    while message != 'quit':
        data = await reader.read(4096)
        message = data.decode('utf-8')
        print(message)

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_print_client())
