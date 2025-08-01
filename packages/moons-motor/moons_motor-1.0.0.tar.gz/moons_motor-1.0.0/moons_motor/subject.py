import asyncio

class Subject:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify_observers(self, event):
        tasks = [observer.update(event) for observer in self._observers]
        await asyncio.gather(*tasks)
