from asyncio import AbstractEventLoop

import asyncio
import websockets

from threading import Thread
from server.message_queue import QueueMessage
from application_property import config
from util.parser import Parser


class WebSocketReceiver:

    def __init__(self, queue: QueueMessage):
        config.load()

        self.host = config.web_socket.receive.host
        self.port = config.web_socket.receive.port

        self.queue = queue

    async def websocket_handler(self, ws: websockets):
        async for message in ws:

            # Для отладки
            # print('Received:', message)

            try:
                # Создаем объект сообщения от абонентов
                data = Parser.map_json_to_object(message)
                self.queue.add_message(data)
            except ValueError as e:
                print('Error parsing')
                raise e

    def do_start(self, loop: AbstractEventLoop):
        asyncio.set_event_loop(loop)

        ws = websockets.serve(self.websocket_handler, self.host, self.port)

        loop.run_until_complete(ws)
        loop.run_forever()

    def start(self):
        Thread(target=self.do_start, args=[asyncio.new_event_loop()]).start()
