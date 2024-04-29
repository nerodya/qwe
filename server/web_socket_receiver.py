import time
from asyncio import AbstractEventLoop

import asyncio
import websockets

from threading import Thread
from server.incoming_message_handler import IncomingMessageHandler
from application_property import config
from util.parser import Parser

dalay_process = 0.1


class WebSocketReceiver:

    def __init__(self, queue: IncomingMessageHandler):
        config.load()

        self.host = config.web_socket.receive.host
        self.port = config.web_socket.receive.port

        self.queue = queue

    async def websocket_handler(self, ws: websockets):
        async for message in ws:
            try:
                time.sleep(dalay_process)
                data = Parser.map_json_to_object(message)
                self.queue.add_message(data)
            except ValueError as e:
                error_message = "Ошибка при парсинге JSON: {}".format(str(e))
                await ws.send(error_message)

    def do_start(self, loop: AbstractEventLoop):
        asyncio.set_event_loop(loop=loop)
        ws = websockets.serve(ws_handler=self.websocket_handler, host=self.host, port=self.port)
        loop.run_until_complete(ws)
        loop.run_forever()

    def start(self):
        Thread(target=self.do_start, args=[asyncio.new_event_loop()]).start()
