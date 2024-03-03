import server.flask_app
from server.flask_app import FlaskApp
from server.web_socket_receiver import WebSocketReceiver
from server.message_queue import QueueMessage

if __name__ == '__main__':

    # Общая для двух потоков очередь сообщений
    queue = QueueMessage()

    # Запуск web-socket для входящих сообщений
    WebSocketReceiver(queue).start()

    # Запуск Flask-приложения
    FlaskApp(queue).start()
