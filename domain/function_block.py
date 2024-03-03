from domain.control_parameter import ControlParameter


class FunctionBlock:

    def __init__(self, number_block: int):
        self.number = number_block
        self.control_parameters = list()

    def add_control_parameter(self, cp: ControlParameter):
        if cp is not None:
            self.control_parameters.append(cp)
        else:
            raise ZeroDivisionError

    def get_parameter(self, index: int) -> ControlParameter:
        return self.control_parameters[index]
