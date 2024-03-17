import time
import random
from util.parser import Parser
from domain.subscriber import Subscriber
from websockets.sync.client import connect
from domain.function_block import FunctionBlock
from domain.control_parameter import ControlParameter
from domain.message_aboat_cp import MessageFromSystemAgent


def generate_random_message(num_subscribers: int, max_blocks_per_subscriber: int, max_parameters_per_block: int):
    message = MessageFromSystemAgent()
    for i in range(num_subscribers):
        subscriber = Subscriber(i)  # Генерация случайного номера подписчика
        for j in range(random.randint(1, max_blocks_per_subscriber)):
            function_block = FunctionBlock(j)  # Генерация случайного номера блока функций
            for k in range(random.randint(1, max_parameters_per_block)):
                control_parameter = ControlParameter(random.randint(1, 100),
                                                     k,
                                                     subscriber.number,
                                                     function_block.number)  # Генерация случайных значений параметров
                function_block.add_control_parameter(control_parameter)
            subscriber.add_function_block(function_block)
        message.add_subscriber(subscriber)
    return message


if __name__ == '__main__':
    with connect("ws://localhost:8080") as websocket:
        while True:
            time.sleep(1)
            print(1)
            data = generate_random_message(12, 8, 12)
            message = Parser.map_object_to_json(data)
            print(message)
            websocket.send(message)
