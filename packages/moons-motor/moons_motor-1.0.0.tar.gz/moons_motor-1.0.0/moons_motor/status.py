class MoonsStepperStatus:
    def __init__(self, address=""):

        # info
        self.address = ""
        self.position = 0  # IP
        self.temperature = 0  # IT
        self.sensor_status = 0  # IS
        self.voltage = 0  # IU
        self.acceleration = 0  # AC
        self.deceleration = 0  # DE
        self.velocity = 0  # VE
        self.distance = 0  # DI
        self.jog_speed = 0  # JS

        # status
        self.status_string = ""
        self.alarm = False
        self.disabled = False
        self.drive_fault = False
        self.moving = False
        self.homing = False
        self.jogging = False
        self.motion_in_progess = False
        self.ready = False
        self.stoping = False
        self.waiting = False

    def update_info(self, info: dict) -> bool:
        if info is None or len(info) < 1:
            print("Update failed: input is None")
            return False
        self.position = info["pos"]
        self.temperature = info["temp"]
        self.sensor_status = info["sensor"]
        self.voltage = info["vol"]
        self.acceleration = info["accel"]
        self.deceleration = info["decel"]
        self.velocity = info["vel"]
        self.distance = info["dis"]
        self.jog_speed = info["jogsp"]
        return True

    def update_status(self, status_string) -> bool:
        if status_string == None and status_string == "":
            print("Update failed: input is empty or None")
            return False
        self.status_string = status_string
        self.alarm = "A" in status_string
        self.disabled = "D" in status_string
        self.drive_fault = "E" in status_string
        self.moving = "F" in status_string
        self.homing = "H" in status_string
        self.jogging = "J" in status_string
        self.motion_in_progess = "M" in status_string
        self.ready = "R" in status_string
        self.stoping = "S" in status_string
        self.waiting = "T" in status_string
        return True

    def get_info(self) -> str:
        return f"""
        Position: {self.position}
        Temperature: {self.temperature}
        Sensor Status: {self.sensor_status}
        Voltage: {self.voltage}
        Acceleration: {self.acceleration}
        Deceleration: {self.deceleration}
        Velocity: {self.velocity}
        Distance: {self.distance}
        Jog Speed: {self.jog_speed}"""

    def get_status(self) -> str:
        return f"""
        Alarm: {self.alarm}
        Disabled: {self.disabled}
        Drive Fault: {self.drive_fault}
        Moving: {self.moving}
        Homing: {self.homing}
        Jogging: {self.jogging}
        Motion in Progress: {self.motion_in_progess}
        Ready: {self.ready}
        Stoping: {self.stoping}
        Waiting: {self.waiting}"""
