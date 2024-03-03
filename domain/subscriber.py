from domain.function_block import FunctionBlock


class Subscriber:

    def __init__(self, number_sub):
        self.description = None
        self.number = number_sub
        self.function_blocks = list()

    def set_description(self, description):
        self.description = description

    def add_function_block(self, function_block: FunctionBlock):
        self.function_blocks.append(function_block)

    def get_function_blocks(self, index: int) -> FunctionBlock:
        return self.function_blocks[index]
