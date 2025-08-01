from abc import ABC, abstractmethod


@abstractmethod
class Observer(ABC):
    @abstractmethod
    async def update(self, event):
        pass
