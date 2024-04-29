import queue
import time
from queue import Queue
from threading import Lock

from domain.message_aboat_cp import MessageFromExternalDataSource
from domain.subscriber import Subscriber
from util.log import CustomLogger

criteria_block = None
criteria_subscriber = None


def get_filter(message) -> MessageFromExternalDataSource or None:
    global criteria_block
    global criteria_subscriber

    response = MessageFromExternalDataSource()

    for i in range(len(message.subscribers)):
        sub = message.get_subscribers(i)
        if criteria_subscriber is None or sub.number == criteria_subscriber:
            response_sub = Subscriber(sub.number)
            for j in range(len(sub.function_blocks)):
                block = sub.get_function_blocks(j)
                if criteria_block is None or block.number == criteria_block:
                    response_sub.add_function_block(block)
            response.add_subscriber(response_sub)
            if len(response_sub.function_blocks) == 0:
                return None
    return response


class IncomingMessageHandler:

    def __init__(self):
        # Создаем очередь для обмена данными между потоками
        self.message_queue = Queue()
        self.look = Lock()

        self.log = CustomLogger()

    # todo обработать исключение. скорее всего вернуть на фронт сообщение о пустоте
    def get_message(self):
        with self.look:

            if self.message_queue.empty():
                return None
            else:
                try:
                    message = get_filter(self.message_queue.get_nowait())
                except queue.Empty:
                    raise ValueError('Result queue is empty')
                return message

    # todo Тут добавить обработку хводящих КП
    def add_message(self, message: MessageFromExternalDataSource):
        with self.look:
            if message is not None:
                self.check_cp(message)
                self.message_queue.put(message)
            else:
                raise ValueError('Value is None')

    def check_cp(self, data: MessageFromExternalDataSource):
        start_time = time.time()
        for i in range(len(data.subscribers)):
            sub = data.get_subscribers(i)
            for j in range(len(sub.function_blocks)):
                block = sub.get_function_blocks(j)
                for k in range(len(block.control_parameters)):
                    cp = block.get_parameter(k)
                    flag = cp.self_check(function=lambda value_cp, x, y: x < value_cp < y, x=cp.min_value, y=cp.max_value)
                    if flag is False:
                        self.log.info(cp)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Время выполнения: {execution_time} секунд")
