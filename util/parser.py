import json
from domain.function_block import FunctionBlock
from domain.control_parameter import ControlParameter
from domain.subscriber import Subscriber
from domain.message_aboat_cp import MessageFromSystemAgent


# TODO - сделать нормальную обработку ошибок

class Encoder(json.JSONEncoder):
    def __init__(self, default=None, *args, **kwargs):
        super().__init__(default=self.default, *args, **kwargs)

    def default(self, obj):
        try:
            if isinstance(obj, ControlParameter):
                return {
                    "value": obj.value,
                    "number": obj.number,
                    "min_value": obj.min_value,
                    "max_value": obj.max_value
                }
            elif isinstance(obj, FunctionBlock):
                return {
                    "number_block": obj.number,
                    "control_parameters": obj.control_parameters
                }
            elif isinstance(obj, Subscriber):
                return {
                    "number_sub": obj.number,
                    "function_blocks": obj.function_blocks,
                    "description": obj.description
                }
            elif isinstance(obj, MessageFromSystemAgent):
                return {
                    "message": obj.subscribers
                }
        except:
            print('Произошла ошибка при преобразовании объекта в json-строку')
        else:
            return super().default(obj)


class Decoder(json.JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(json_dict):
        try:
            if 'message' in json_dict:
                message = MessageFromSystemAgent()
                for subscriber_data in json_dict['message']:
                    subscriber = Subscriber(number_sub=subscriber_data['number_sub'])
                    subscriber.description = subscriber_data['description']

                    for function_block_data in subscriber_data['function_blocks']:
                        function_block = FunctionBlock(number_block=function_block_data['number_block'])

                        for control_parameters_data in function_block_data['control_parameters']:
                            control_parameters = ControlParameter(
                                min_value=control_parameters_data['min_value'],
                                max_value=control_parameters_data['max_value'],
                                value=control_parameters_data['value'],
                                number_cp=control_parameters_data['number'],
                                number_sub=subscriber.number,
                                number_block=function_block.number
                            )
                            function_block.control_parameters.append(control_parameters)

                        subscriber.function_blocks.append(function_block)

                    message.subscribers.append(subscriber)

                return message
        except:
            print('Произошла ошибка при преобразовании json-строки в объект')
        else:
            return json_dict


class Parser:

    @staticmethod
    def map_json_to_object(json_data: str) -> MessageFromSystemAgent:
        res = json.loads(json_data, cls=Decoder)
        return res

    @staticmethod
    def map_object_to_json(obj):
        res = json.dumps(obj, cls=Encoder)
        return res


if __name__ == '__main__':
    m = MessageFromSystemAgent()
    s = Subscriber(1)
    f = FunctionBlock(1)
    f1 = FunctionBlock(11)
    c = ControlParameter(1, 2)
    c1 = ControlParameter(1, 2)
    c2 = ControlParameter(1, 2)
    f.add_control_parameter(2, 1)
    f.add_control_parameter(2, 1)
    f1.add_control_parameter(2, 1)
    f1.add_control_parameter(2, 1)
    s.add_function_block(f)
    s.add_function_block(f1)
    m.add_subscriber(s)

    print(Parser.map_object_to_json(m))
