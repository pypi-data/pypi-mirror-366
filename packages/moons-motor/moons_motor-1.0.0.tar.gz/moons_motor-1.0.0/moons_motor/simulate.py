import socketio
from moons_motor.motor import MoonsStepper
from moons_motor.observer import Observer
import time


class MoonsStepperSimulate(Observer):
    def __init__(
        self,
        moons_motor: MoonsStepper,
        universe: int = 0,
        server_address: str = "http://localhost:3001",
        log_message: bool = True,
    ):
        self.server_address = server_address
        self.universe = universe
        self.moons_motor = moons_motor
        self.io = socketio.SimpleClient()
        self.connected = False
        self.log_message = True

    def update(self, event):
        if self.log_message == False:
            return
        print(f"Simulate send: {event}")
        self.emit("motor", event)

    def connect(self):
        self.moons_motor.register(self)
        try:
            self.is_log_message = False
            self.io.connect(self.server_address)
            self.connected = True
            print(f"Socket connected to {self.server_address}[{self.io.sid}]")
            # self.rederict_thread = threading.Thread(
            #     target=self.rederict_job,
            # )
            # self.rederict_thread.daemon = True
            # self.rederict_thread.start()
        except Exception as e:
            print(f"Socket connection error: {e}")
            self.connected = False

    def rederict_job(self):
        if not self.connected:
            print("Socket not connected")
            return
        if self.moons_motor is None:
            print("Motor is None")
            return
        while True:
            # self.moons_motor.on_send_event.wait(timeout=0.5)
            if self.moons_motor.command_cache.empty():
                continue
            cmd = self.moons_motor.command_cache.get_nowait()
            # self.moons_motor.command_cache.task_done()

            self.emit("motor", f"{self.universe}-{cmd}")
            # self.moons_motor.command_cache = ""
            # self.moons_motor.on_send_event.clear()

            if not self.connected:
                break
            time.sleep(0.05)

    def disconnect(self):
        self.connected = False
        self.moons_motor.unregister(self)
        self.io.disconnect()

    def emit(self, eventName: str, data):
        if not self.connected:
            print("Socket not connected")
            return
        self.io.emit(eventName, data)
        if self.is_log_message:
            print("[bold blue]Send to socket:[/bold blue] {}\n".format(data))
