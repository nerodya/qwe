import queue
import time
from queue import Queue
from threading import Thread
from threading import Lock
from util.log import CustomLogger
from domain.message_aboat_cp import MessageFromSystemAgent

n = 0
t = 0


class QueueMessage:

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
                    message = self.message_queue.get_nowait()
                except queue.Empty:
                    raise ValueError('Result queue is empty')
                return message

    # todo Тут добавить обработку хводящих КП
    def add_message(self, message: MessageFromSystemAgent):
        with self.look:
            if message is not None:
                self.check_cp(message)
                self.message_queue.put(message)
            else:
                raise ValueError('Value is None')

    def check_cp(self, data: MessageFromSystemAgent):
        start_time = time.time()
        for i in range(len(data.subscribers)):
            sub = data.get_subscribers(i)
            for j in range(len(sub.function_blocks)):
                block = sub.get_function_blocks(j)
                for k in range(len(block.control_parameters)):
                    cp = block.get_parameter(k)
                    flag = cp.self_check(function=lambda value_cp, x, y: x < value_cp < y, x=10, y=85)
                    # flag = True
                    # if cp.value < 10 or cp.value > 85:
                    #     flag = False
                    if flag is False:
                        self.log.info(cp)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Время выполнения: {execution_time} секунд")
