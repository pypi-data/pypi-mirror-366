from abc import ABC, abstractmethod


@abstractmethod
class Observer(ABC):
    def update(self, event):
        pass
