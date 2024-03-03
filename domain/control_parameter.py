class ControlParameter:

    def __init__(self, value: int, number_cp: int, number_sub: int, number_block: int):
        self.value = value
        self.number = number_cp
        self.number_sub = number_sub
        self.number_block = number_block

    def self_check(self, function, x, y) -> bool:
        return function(self.value, x, y)

    @staticmethod
    def convert_to_dict(self):
        return self.__dict__
