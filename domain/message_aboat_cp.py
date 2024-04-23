from domain.subscriber import Subscriber


class MessageFromExternalDataSource:

    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, sub: Subscriber):
        self.subscribers.append(sub)

    def get_subscribers(self, index: int) -> Subscriber:
        return self.subscribers[index]
