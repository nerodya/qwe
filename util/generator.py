import time
import random
from util.parser import Parser
from domain.subscriber import Subscriber
from websockets.sync.client import connect
from domain.function_block import FunctionBlock
from domain.control_parameter import ControlParameter
from domain.message_aboat_cp import MessageFromExternalDataSource

number_block_ch = [54, 110, 111, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 112, 113, 114, 115, 116, 117, 130,
                   131, 132, 133, 134, 135, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 136, 137, 109]

number_block_noch = [141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160,
                     161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176]


def generate_random_message(num_subscribers: int, max_parameters_per_block: int):
    message = MessageFromExternalDataSource()
    for i in range(num_subscribers):
        i = i + 1
        subscriber = Subscriber(i)  # Генерация случайного номера подписчика
        max_blocks_per_subscriber = len(number_block_noch) if i % 2 == 0 else len(number_block_ch)
        for j in range(1, max_blocks_per_subscriber):
            function_block = FunctionBlock(
                number_block_noch[j] if i % 2 == 0 else number_block_ch[j])  # Генерация случайного номера блока функций
            for k in range(1, max_parameters_per_block):
                control_parameter = ControlParameter(random.randint(1, 100),
                                                     k,
                                                     subscriber.number,
                                                     function_block.number,
                                                     min_value=random.randint(1, 30),
                                                     max_value=random.randint(71,
                                                                              100))  # Генерация случайных значений параметров
                function_block.add_control_parameter(control_parameter)
            subscriber.add_function_block(function_block)
        message.add_subscriber(subscriber)
    return message


if __name__ == '__main__':
    with connect("ws://localhost:8080") as websocket:
        while True:
            time.sleep(1)
            data = generate_random_message(num_subscribers=7, max_parameters_per_block=12)
            message = Parser.map_object_to_json(data)
            print(message)
            websocket.send(message)
