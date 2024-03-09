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
    for _ in range(num_subscribers):
        subscriber = Subscriber(random.randint(1, num_subscribers + 1))  # Генерация случайного номера подписчика
        for _ in range(random.randint(1, max_blocks_per_subscriber)):
            function_block = FunctionBlock(random.randint(1, max_blocks_per_subscriber + 1))  # Генерация случайного номера блока функций
            for _ in range(random.randint(1, max_parameters_per_block)):
                control_parameter = ControlParameter(random.randint(1, 100),
                                                     random.randint(1, 100),
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
            websocket.send(Parser.map_object_to_json(data))
