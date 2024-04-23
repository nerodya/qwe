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
message_interval = 0.2  # Интервал отправки сообщений в секундах


def reset_settings_translation():
    global message_interval, streaming_mode_enabled
    message_interval = 1
    server.message_queue.criteria_block = None
    server.message_queue.criteria_subscriber = None
    streaming_mode_enabled = False


class FlaskApp:

    def __init__(self, queue: QueueMessage):
        config.load()

        self.host = config.web_socket.deliver.host
        self.port = config.web_socket.deliver.port

        self.app = Flask(__name__)
        self.socketIO = SocketIO(self.app, cors_allowed_origins="*")
        self.swagger = Swagger(self.app)

        self.app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

        self.queue = queue

        self.thread = None

        @self.socketIO.on('connect')
        def connection():
            reset_settings_translation()
            # Thread(target=self.stream_data, daemon=True).start()
            print('connecting client')
            self.socketIO.emit('connection', 'connection')

        @self.socketIO.on('disconnect')
        def disconnection():
            print('disconnect client')
            self.socketIO.emit('disconnection', 'disconnection')
            reset_settings_translation()

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

                if 'number_sub' in data:
                    criteria_subscriber = data['number_sub']
                    server.message_queue.criteria_subscriber = criteria_subscriber
                    response_message += f'number_sub: {criteria_subscriber}'
                    image_path = ''
                    if criteria_subscriber % 2 == 0:
                        image_path = 'resource/student_AFAR_Stoiki_new.svg'
                    else:
                        image_path = 'resource/sub_image.svg'

                    # Проверка на существование файла и его размер
                    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                        with open(image_path, 'rb') as image_file:
                            image_data = image_file.read()

                        # Отправка изображения в ответе
                        return Response(response=image_data,
                                        status=200,
                                        mimetype='application/xml')
                    else:
                        return Response(status=400)

                if 'number_block' in data:
                    criteria_block = data['number_block']
                    server.message_queue.criteria_block = criteria_block
                    response_message += f'number_block: {criteria_block}'

                if response_message == '':
                    return Response(response='Не переданы параметры для фильтрации\n',
                                    status=400,
                                    mimetype='text/plain')
                else:
                    return Response(status=200)
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

            if streaming_mode_enabled is True:
                if self.thread is None:
                    self.thread = Thread(target=self.stream_data, daemon=True)
                self.thread.start()
            else:
                self.thread = None


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

        @self.app.route('/reset-criteria', methods=['POST'])
        def reset_criteria():
            """
            Сброс критерий для выборки КП.

            Этот ресурс позволяет сбросить критерии выборки КП.

            ---
            responses:
              '200':
                description: Критерии выборки КП сброшены
            """
            server.message_queue.criteria_subscriber = None
            server.message_queue.criteria_block = None

            return Response('Критерии выборки КП сброшены', status=200, mimetype='text/plain')

        @self.app.route('/image-code', methods=['GET'])
        def get_image_code():
            """
            Получить изображение стоек
            Этот ресурс возвращает изображение в формате xml.
            ---
            responses:
              '200':
                description: Изображение в формате xml
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
                                mimetype='application/xml')
            else:
                return Response(response='Файл с изображением пуст или не существует',
                                status=404)

        @self.app.route('/log', methods=['GET'])
        def get_file_log():
            """
            Получить файл логов
            Этот ресурс позволяет получить филы логов по номерам агента и блоков.
            ---
            responses:
              '200':
                description: Файл application/octet-stream
              '404':
                description: Файла не существует
            """
            # Отправка изображения в ответе
            return Response(response="qwe",
                            status=200,
                            mimetype='application/octet-stream')

        @self.app.route('/cp', methods=['GET'])
        def get_last_cp():
            """
            Получить последние полученные контрольные параметры
            Этот ресурс позволяет последние полученные контрольные параметры.
            ---
            responses:
              '200':
                description: JSON-сообщение application/json
            """
            get_last_cp_ws(None)
            return Response(status=200)


        @self.socketIO.on('last_cp')
        def get_last_cp_ws(data):
            data = self.queue.get_message()
            if data is not None or data == '{"message": []}':
                response = Parser.map_object_to_json(data)
                self.socketIO.emit('last_cp', response)

    def stream_data(self):
        while True:
            if streaming_mode_enabled:
                time.sleep(message_interval)
                data = self.queue.get_message()
                if data is not None or data == '{"message": []}':
                    response = Parser.map_object_to_json(data)
                    self.socketIO.emit('message', response)  # Отправляем ответное сообщение клиенту
            else:
                return


    def start(self):
        self.socketIO.run(self.app, self.host, self.port, allow_unsafe_werkzeug=True)
