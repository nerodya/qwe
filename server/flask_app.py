import os
import time
from threading import Thread

from flasgger import Swagger
from flask import Flask, render_template
from flask import Response, request
from flask_socketio import SocketIO

import server.message_queue
from application_property import config
from server.message_queue import QueueMessage
from util.parser import Parser

streaming_mode_enabled = False  # Передача данных по web-socket
message_interval = 1  # Интервал отправки сообщений в секундах


class FlaskApp:

    def __init__(self, queue: QueueMessage):
        config.load()

        self.host = config.web_socket.deliver.host
        self.port = config.web_socket.deliver.port

        self.app = Flask(__name__)
        self.socketIO = SocketIO(self.app)
        self.swagger = Swagger(self.app)

        self.app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

        self.queue = queue

        @self.app.route('/w', methods=['GET'])
        def get_message():
            global t
            t = True
            return ''

        @self.app.route('/', methods=['GET'])
        def index():
            '''
                Это пример приветствия
                Этот ресурс принимает имя и возвращает приветствие.
                ---
                parameters:
                  - name: name
                    in: path
                    type: string
                    required: true
                    description: Имя, которое нужно приветствовать
                responses:
                  200:
                    description: Приветствие
                '''
            return render_template('index.html')

        @self.socketIO.on('connect')
        def connection():
            Thread(target=self.stream_data, daemon=True).start()
            print('connecting client')
            self.socketIO.emit('connection', 'connection')

        @self.app.route('/filter', methods=['POST'])
        def set_filter_block():
            """
                Фильтрация данных
                Этот ресурс принимает два параметра JSON: number_block и number_sub для фильтрации данных.
                Если хотя бы один параметр передан, возвращается успешный ответ с перечислением принятых параметров.
                Если ни один параметр не был передан, возвращается код ошибки 400.
                Если запрос не является POST-запросом, возвращается код ошибки 405.
                ---
                parameters:
                  - in: body
                    name: body
                    required: false
                    description: Параметры фильтрации данных
                    schema:
                      type: object
                      properties:
                        number_block:
                          type: integer
                          description: Номер блока для фильтрации данных
                          example: 5
                        number_sub:
                          type: integer
                          description: Номер абонента для фильтрации данных
                          example: 10
                responses:
                  200:
                    description: Успешный ответ с перечислением принятых параметров
                    content:
                      application/json:
                        schema:
                          type: object
                          properties:
                            message:
                              type: string
                              description: Сообщение о принятых параметрах
                  400:
                    description: Не переданы параметры для фильтрации
                  405:
                    description: Метод не разрешен, допустим только POST-запрос
                """

            if request.method == 'POST':
                response_message = ''
                data = request.json

                if 'number_block' in data:
                    criteria_block = data['number_block']
                    server.message_queue.criteria_block = criteria_block
                    response_message += f'number_block: {criteria_block}'

                if 'number_sub' in data:
                    criteria_subscriber = data['number_sub']
                    server.message_queue.criteria_subscriber = criteria_subscriber
                    response_message += f'number_sub: {criteria_subscriber}'

                if response_message:
                    return Response(response=f'Received parameter: {response_message}\n',
                                    status=200,
                                    mimetype='text/plain')
                else:
                    return Response(response='Не переданы параметры для фильтрации\n',
                                    status=400,
                                    mimetype='text/plain')
            else:
                return Response(response='Метод не разрешен, допустим только POST-запрос\n',
                                status=405,
                                mimetype='text/plain')

        @self.app.route('/image', methods=['GET'])
        def get_image_sun():
            """
                Получить изображение стоек
                Этот ресурс возвращает изображение в формате SVG.
                ---
                responses:
                  '200':
                    description: Изображение в формате SVG
                  '404':
                    description: Файл с изображением пуст или не существует
                """

            image_path = 'resource/sub_image.svg'

            # Проверка на существование файла и его размер
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()

                # Отправка изображения в ответе
                return Response(response=image_data,
                                status=200,
                                mimetype='image/svg+xml')
            else:
                return Response(response='Файл с изображением пуст или не существует',
                                status=404)

        @self.app.route('/toggle-streaming-mode', methods=['GET'])
        def toggle_streaming_mode():
            """
               Включение/выключение режима передачи данных по WebSocket

               Этот ресурс позволяет включать или выключать режим передачи данных по WebSocket.

               ---
               responses:
                 '200':
                   description: Сообщение о текущем состоянии режима передачи данных по WebSocket.
                 default:
                   description: Произошла ошибка
               """

            global streaming_mode_enabled

            # Изменение состояния флага
            streaming_mode_enabled = not streaming_mode_enabled

            # Формирование ответа
            response_message = 'Режим передачи данных по WebSocket включен' \
                if streaming_mode_enabled \
                else 'Режим передачи данных по WebSocket выключен'

            return Response(response=response_message,
                            status=200,
                            mimetype='text/plain')

        @self.app.route('/get-streaming-mode-state', methods=['GET'])
        def get_streaming_mode_state():
            """
            Получение текущего состояния режима передачи данных по WebSocket

            Этот ресурс возвращает текущее состояние режима передачи данных по WebSocket.

            ---
            responses:
              '200':
                description: JSON объект, содержащий текущее состояние режима передачи данных по WebSocket.
              default:
                description: Произошла ошибка
            """

            global streaming_mode_enabled

            # Отправка текущего состояния флага в ответе
            return Response(response=str(streaming_mode_enabled),
                            status=200,
                            mimetype='text/plain')

        @self.app.route('/set-message-interval', methods=['POST'])
        def set_message_interval():
            """
            Установка периода между отправкой сообщений по WebSocket

            Этот ресурс позволяет устанавливать период между отправкой сообщений по WebSocket.

            ---
            parameters:
              - in: body
                name: body
                required: true
                description: Параметры установки периода между отправкой сообщений
                schema:
                  type: object
                  properties:
                    interval:
                      type: integer
                      description: Период между отправкой сообщений в секундах
                      example: 1
            responses:
              '200':
                description: Успешно установлен новый период между отправкой сообщений
              default:
                description: Произошла ошибка при установке нового периода между отправкой сообщений
            """
            global message_interval

            data = request.json
            new_interval = data.get('interval')
            if new_interval is None or not isinstance(new_interval, int) or new_interval <= 0:
                Response('Некорректный период между отправкой сообщений', status=400, mimetype='text/plain')

            message_interval = new_interval
            return Response('Новый период между отправкой сообщений установлен', status=200, mimetype='text/plain')

    def stream_data(self):
        while True:
            if streaming_mode_enabled:

                time.sleep(message_interval)

                response = Parser.map_object_to_json(self.queue.get_message())
                self.socketIO.emit('message', response)  # Отправляем ответное сообщение клиенту

    def start(self):
        self.socketIO.run(self.app, self.host, self.port, allow_unsafe_werkzeug=True)
