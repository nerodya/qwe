import time

from flask import Flask, Response
from threading import Thread
from flask_socketio import SocketIO
from application_property import config
from server.message_queue import QueueMessage
from flask import Flask, render_template
from util.parser import Parser

t = False

class FlaskApp:

    def __init__(self, queue: QueueMessage):
        config.load()

        self.host = config.web_socket.deliver.host
        self.port = config.web_socket.deliver.port

        self.app = Flask(__name__)
        self.socketIO = SocketIO(self.app)

        self.app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

        self.queue = queue

        @self.app.route('/w', methods=['GET'])
        def get_message():
            global t
            t = True
            return ""

        @self.app.route('/', methods=['GET'])
        def index():
            return render_template('index.html')

        # @self.app.route('/message')
        # def handle_message():

        @self.socketIO.on('connect')
        def connection():
            Thread(target=self.stream_data, daemon=True).start()
            print('connecting client')
            self.socketIO.emit('connection', 'connection')

    def stream_data(self):
        while True:
            time.sleep(1)
            global t
            print(t)
            response = Parser.map_object_to_json(self.queue.get_message())
            print('response')
            self.socketIO.emit('message', response)  # Отправляем ответное сообщение клиенту

    def start(self):
        self.socketIO.run(self.app, self.host, self.port, allow_unsafe_werkzeug=True)
