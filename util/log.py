import os
import zlib
import logging
from logging import Logger
from datetime import datetime
from application_property import config
from logging.handlers import RotatingFileHandler
from domain.control_parameter import ControlParameter

base_logs_folder = ''


class CustomLogger:

    def __init__(self):
        self.loggers = {}

        global base_logs_folder
        config.load()
        base_logs_folder = config.web_socket.logs_folder

    def info(self, control_parameter: ControlParameter):
        logger = self.get_logger(int(control_parameter.number_sub), int(control_parameter.number_block))
        logger.info(f'Number: {control_parameter.number}.'
                    f' Value: {control_parameter.value}.')

    def get_logger(self, number_sub: int, number_block: int) -> Logger:

        key = zlib.crc32(bytes([number_block])) * 31 + zlib.crc32(bytes([number_sub])) * 13

        try:
            logger = self.loggers.get(key)
        except IndexError:
            # Обработка ошибки, если индексы выходят за границы списка
            logger = None

        if logger is None:
            logger = self.init_logger(number_sub, number_block, str(key))

            self.loggers[key] = logger

        return logger

    @staticmethod
    def init_logger(number_sub: int, number_block: int, hash_log: str) -> Logger:

        log_folder = base_logs_folder + '/sub_' + str(number_sub) + '/block_' + str(number_block)
        logger_name = datetime.today().strftime('%Y-%m-%d') + '_' + hash_log

        # Проверяем, существует ли каталог, и создаем его, если нет
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Создаем RotatingFileHandler
        log_file = os.path.join(log_folder, f"{logger_name}.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)

        # Настройка формата
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Создаем логгер
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        return logger
