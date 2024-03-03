from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Receive(DataClassJsonMixin):
    host: str = None
    port: int = None


@dataclass
class Deliver(DataClassJsonMixin):
    host: str = None
    port: int = None


@dataclass
class WebSocket(DataClassJsonMixin):
    receive: Receive = None
    deliver: Deliver = None
    logs_folder: str = None


@dataclass
class LogFolder(DataClassJsonMixin):
    logs_folder: str = None


@dataclass
class Log(DataClassJsonMixin):
    logs_folder: LogFolder = None


@dataclass
class Config(YamlDataClassConfig):
    web_socket: WebSocket = None
    # log: Log = None


config = Config()
