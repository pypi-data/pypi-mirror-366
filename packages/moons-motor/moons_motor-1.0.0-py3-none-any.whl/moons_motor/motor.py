import serial
import serial.rs485
from serial.tools import list_ports
import re
import asyncio
import serial_asyncio
from rich import print
from rich.console import Console
from rich.panel import Panel
from moons_motor.subject import Subject
import time

from dataclasses import dataclass

import logging


class ColoredFormatter(logging.Formatter):
    # Define ANSI escape codes for colors and reset
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    bold_yellow = "\x1b[33;1m"
    bold_green = "\x1b[32;1m"
    bold_blue = "\x1b[34;1m"
    bold_cyan = "\x1b[36;1m"
    bold_magenta = "\x1b[35;1m"
    reset = "\x1b[0m"

    # Define the base format string
    format_time = "%(asctime)s"
    format_header = " [%(levelname)s]"
    format_base = " %(message)s"

    # Map log levels to colored format strings
    FORMATS = {
        logging.DEBUG: format_time
        + bold_cyan
        + format_header
        + reset
        + format_base
        + reset,
        logging.INFO: format_time
        + bold_green
        + format_header
        + reset
        + format_base
        + reset,
        logging.WARNING: format_time
        + bold_yellow
        + format_header
        + reset
        + format_base
        + reset,
        logging.ERROR: format_time
        + bold_red
        + format_header
        + reset
        + format_base
        + reset,
        logging.CRITICAL: format_time
        + bold_magenta
        + format_header
        + reset
        + format_base
        + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class StepperModules:
    STM17S_3RN = "STM17S-3RN"


@dataclass(frozen=True)
class StepperCommand:
    JOG: str = "CJ"  # Start jogging
    JOG_SPEED: str = "JS"  # Jogging speed (Need to set before start jogging)
    JOG_ACCELERATION: str = (
        "JA"  # Jogging acceleration (Need to set before start jogging)
    )
    CHANGE_JOG_SPEED: str = "CS"  # Change jogging speed while jogging
    STOP_JOG: str = "SJ"  # Stop jogging with deceleration
    STOP: str = "ST"  # Stop immediately (No deceleration)
    STOP_DECEL: str = "STD"  # Stop with deceleration
    STOP_KILL: str = (
        "SK"  # Stop with deceleration(Control by AM) and kill all unexecuted commands
    )
    STOP_KILL_DECEL: str = (
        "SKD"  # Stop and kill all unexecuted commands with deceleration(Control by DE)
    )
    ENABLE: str = "ME"  # Enable motor
    DISABLE: str = "MD"  # Disable motor
    MOVE_ABSOLUTE: str = "FP"  # Move to absolute position
    MOVE_FIXED_DISTANCE: str = "FL"  # Move to fixed distance
    POSITION: str = "IP"  # Motor absolute position(Calculated trajectory position)
    TEMPERATURE: str = "IT"  # Motor temperature
    VOLTAGE: str = "IU"  # Motor voltage

    ENCODER_POSITION: str = "EP"  # Encoder position
    SET_POSITION: str = "SP"  # Set encoder position

    HOME: str = "SH"  # Home position
    VELOCITY: str = "VE"  # Set velocity

    ALARM_RESET: str = "AR"  # Reset alarm

    SET_RETURN_FORMAT_DECIMAL: str = "IFD"  # Set return format to decimal
    SET_RETURN_FORMAT_HEXADECIMAL: str = "IFH"  # Set return format to hexadecimal

    SET_TRANSMIT_DELAY: str = "TD"  # Set transmit delay
    REQUEST_STATUS: str = "RS"  # Request status


class MoonsStepper(Subject):
    motorAdress = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
        ":",
        ";",
        "<",
        "=",
        ">",
        "?",
        "@",
    ]
    # Configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter())
    logger.addHandler(ch)

    def __init__(
        self,
        model: StepperModules,
        VID,
        PID,
        SERIAL_NUM,
        only_simlate=False,
        universe=0,
    ):
        super().__init__()
        self.universe = universe
        self.model = model  # Motor model
        self.only_simulate = only_simlate
        self.device = ""  # COM port description
        self.VID = VID
        self.PID = PID
        self.SERIAL_NUM = SERIAL_NUM  # ID for determent the deivice had same VID and PID, can be config using chips manufacturer tool

        self.is_connected = False
        self.ser_reader = None
        self.ser_writer = None
        self.send_queue = asyncio.Queue()
        self.recv_queue = asyncio.Queue()
        self.pending_futures = {}
        self._io_tasks = []
        self.readBuffer = ""

        self.console = Console()

        self.is_log_message = True

        self.microstep = {
            0: 200,
            1: 400,
            3: 2000,
            4: 5000,
            5: 10000,
            6: 12800,
            7: 18000,
            8: 20000,
            9: 21600,
            10: 25000,
            11: 25400,
            12: 25600,
            13: 36000,
            14: 50000,
            15: 50800,
        }

    # region connection & main functions
    @staticmethod
    def list_all_ports():
        ports = list(list_ports.comports())
        simple_ports = []
        port_info = ""
        for p in ports:
            port_info += f"■ {p.device} {p.description} [blue]{p.usb_info()}[/blue]"
            if p != ports[-1]:
                port_info += "\n"
            simple_ports.append(p.description)
        print(Panel(port_info, title="All COMPorts"))
        return simple_ports

    @staticmethod
    def process_response(response):
        equal_sign_index = response.index("=")
        address = response[0]
        command = response[1:equal_sign_index]
        value = response[equal_sign_index + 1 :]

        if command == "IT" or command == "IU":
            # Handle temperature response
            value = int(value) / 10.0
        return {
            "address": address,
            "command": command,
            "value": value,
        }

    async def connect(self, COM=None, baudrate=9600, callback=None):
        # Simulate mode
        if self.only_simulate:
            self.is_connected = True
            self.device = f"Simulate-{self.universe}"
            MoonsStepper.logger.info(f"{self.device} connected")
            if callback:
                callback(self.device, self.is_connected)
            return

        # Find port
        ports = list(list_ports.comports())
        found_port = None
        if COM is not None:
            for p in ports:
                if p.device == COM:
                    found_port = p
                    self.device = p.description
                    break
            if not found_port:
                MoonsStepper.logger.error(f"Specified COM port {COM} not found.")
                if callback:
                    callback(self.device, False)
                return
        else:
            # Auto-detect port by VID/PID
            for p in ports:
                m = re.match(
                    r"USB\s*VID:PID=(\w+):(\w+)\s*SER=([A-Za-z0-9]*)", p.usb_info()
                )
                if (
                    m
                    and m.group(1) == self.VID
                    and m.group(2) == self.PID
                    and (m.group(3) == self.SERIAL_NUM or self.SERIAL_NUM == "")
                ):
                    MoonsStepper.logger.info(
                        f"Device found: {p.description} | VID: {m.group(1)} | PID: {m.group(2)} | SER: {m.group(3)}"
                    )
                    self.device = p.description
                    found_port = p
                    break

        if not found_port:
            MoonsStepper.logger.error(
                f"Device with VID={self.VID}, PID={self.PID} not found."
            )
            if callback:
                callback(self.device, self.is_connected)
            return

        # Attempt to connect
        try:
            # --- THIS IS THE CRITICAL RS485 PART ---
            rs485_settings = serial.rs485.RS485Settings(
                rts_level_for_tx=True,
                rts_level_for_rx=False,
                loopback=False,
                delay_before_tx=0.02,
                delay_before_rx=0.02,
            )
            self.ser_reader, self.ser_writer = (
                await serial_asyncio.open_serial_connection(
                    url=found_port.device,
                    baudrate=baudrate,
                    # rs485_mode=rs485_settings,  # Pass the settings here
                )
            )
            # ----------------------------------------

            self.is_connected = True
            MoonsStepper.logger.info(f"Device connected: {self.device}")

            # Start I/O handlers
            read_task = asyncio.create_task(self._read_handler())
            write_task = asyncio.create_task(self._write_handler())
            self._io_tasks = [read_task, write_task]

        except Exception as e:
            MoonsStepper.logger.error(f"Device connection error: {e}")
            self.is_connected = False

        await asyncio.sleep(0.1)

        if callback:
            callback(self.device, self.is_connected)

    async def _read_handler(self):
        MoonsStepper.logger.info("Read handler started.")
        while self.is_connected:
            try:
                response_bytes = await self.ser_reader.readuntil(b"\r")
                response = response_bytes.decode("ascii", errors="ignore").strip()
                if response:
                    self.handle_recv(response)
            except asyncio.CancelledError:
                MoonsStepper.logger.info("Read handler cancelled.")
                break
            except Exception as e:
                MoonsStepper.logger.error(f"Read error: {e}")
                self.is_connected = False
                break

    async def _write_handler(self):
        MoonsStepper.logger.info("Write handler started.")
        while self.is_connected:
            try:
                command = await self.send_queue.get()

                full_command = (command + "\r").encode("ascii")
                self.ser_writer.write(full_command)
                await self.ser_writer.drain()

                if self.is_log_message:
                    MoonsStepper.logger.debug(f"Sent to {self.device}: {command}")

                self.send_queue.task_done()
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                MoonsStepper.logger.info("Write handler cancelled.")
                break
            except Exception as e:
                MoonsStepper.logger.error(f"Write error: {e}")
                self.is_connected = False
                break

    async def disconnect(self):
        if not self.is_connected and not self.only_simulate:
            return

        # For simulation
        if self.only_simulate:
            self.is_connected = False
            MoonsStepper.logger.info(f"Simulate-{self.universe} disconnected")
            return

        # Stop I/O tasks
        self.is_connected = False
        for task in self._io_tasks:
            task.cancel()

        # Wait for tasks to finish cancellation
        await asyncio.gather(*self._io_tasks, return_exceptions=True)

        # Clear queues
        while not self.send_queue.empty():
            self.send_queue.get_nowait()
        while not self.recv_queue.empty():
            self.recv_queue.get_nowait()

        # Close serial connection
        if self.ser_writer:
            self.ser_writer.close()
            await self.ser_writer.wait_closed()

        MoonsStepper.logger.info(f"Device disconnected: {self.device}")

    async def send_command(self, address="", command="", value=None):
        if not self.is_connected and not self.only_simulate:
            MoonsStepper.logger.warning("Not connected. Cannot send command.")
            return

        if command == "":
            MoonsStepper.logger.warning("Command can't be empty")
            return

        if value is not None:
            command_str = self.addressed_cmd(address, command + str(value))
        else:
            command_str = self.addressed_cmd(address, command)

        await self.send_queue.put(command_str)
        await super().notify_observers(f"{self.universe}-{command_str}")

    def handle_recv(self, response):
        # First, process the response to extract key information
        try:
            processed = MoonsStepper.process_response(response)
            address = processed.get("address")
            command = processed.get("command")
            # Create a unique key for the request-response pair
            future_key = (address, command)

            # Check if a future is waiting for this specific response
            if future_key in self.pending_futures:
                future = self.pending_futures.pop(future_key)
                future.set_result(processed) # Set the future's result
                MoonsStepper.logger.debug(f"Future for {future_key} resolved.")
                return # Stop further processing

        except Exception as e:
            # This can happen for simple ACK/NACK responses that don't have an '='
            MoonsStepper.logger.debug(f"Received non-standard response: {response}. Error: {e}")

        # Handle general ACKs or unexpected messages
        if "*" in response:
            MoonsStepper.logger.info(f"(o)buffered_ack")
        elif "%" in response:
            MoonsStepper.logger.info(f"(v)success_ack")
        elif "?" in response:
            MoonsStepper.logger.info(f"(x)fail_ack")
        else:
            MoonsStepper.logger.info(f"Received unhandled message from {self.device}: {response}")
            # Optionally, put unhandled messages into the general queue
            self.recv_queue.put_nowait(response)

    # endregion

    # region motor motion functions

    # def setup_motor(self, motor_address="", kill=False):
    #     if kill:
    #         self.stop_and_kill(motor_address)
    #     self.set_transmit_delay(motor_address, 25)
    #     self.set_return_format_dexcimal(motor_address)

    async def home(self, motor_address="", speed=0.3):
        # Send initial homing commands
        await self.send_command(
            address=motor_address, command=StepperCommand.VELOCITY, value=speed
        )
        await self.send_command(
            address=motor_address, command=StepperCommand.HOME, value="3F"
        )
        await self.send_command(
            address=motor_address, command=StepperCommand.ENCODER_POSITION, value=0
        )
        await self.send_command(
            address=motor_address, command=StepperCommand.SET_POSITION, value=0
        )

        MoonsStepper.logger.info(f"Homing command sent to address {motor_address}. Polling for completion...")

        # Loop until the motor is no longer in the homing state
        while self.is_connected:
            result = await self.get_status(
                motor_address=motor_address,
                command=StepperCommand.REQUEST_STATUS,
            )

            if result and "H" not in result.get("value", ""):
                MoonsStepper.logger.info(f"Motor at address {motor_address} is homed.")
                return # Homing is complete
            
            MoonsStepper.logger.info(f"Motor at address {motor_address} is not homed yet. Waiting...")
            # Wait a bit before polling again
            await asyncio.sleep(0.5)

    # endregion
    async def get_status(self, motor_address, command: StepperCommand):
        future = asyncio.get_running_loop().create_future()
        future_key = (motor_address, command)
        self.pending_futures[future_key] = future

        await self.send_command(motor_address, command)

        try:
            # Wait for the future to be resolved by handle_recv
            result = await asyncio.wait_for(future, timeout=2.0) # 2-second timeout
            return result
        except asyncio.TimeoutError:
            MoonsStepper.logger.error(f"Timeout waiting for response for {future_key}")
            # Clean up the pending future on timeout
            self.pending_futures.pop(future_key, None)
            return None

    def decode_status(status_code):
        """
        Decode the status code from the motor.
        """
        status = {
            "A": "An Alarm code is present (use AL command to see code, AR command to clear code)",
            "D": "Disabled (the drive is disabled)",
            "E": "Drive Fault (drive must be reset by AR command to clear this fault)",
            "F": "Motor moving",
            "H": "Homing (SH in progress)",
            "J": "Jogging (CJ in progress)",
            "M": "Motion in progress (Feed & Jog Commands)",
            "P": "In position",
            "R": "Ready (Drive is enabled and ready)",
            "S": "Stopping a motion (ST or SK command executing)",
            "T": "Wait Time (WT command executing)",
            "W": "Wait Input (WI command executing)",
        }
        status_string = ""
        for char in status_code:
            if char in status:
                status_string += status[char]
                status_string += "\n"
            else:
                status_string += f"Unknown status code: {char}"
        return status_string

    # endregion

    # region utility functions

    def addressed_cmd(self, motor_address, command):
        return f"{motor_address}{command}"


# endregion

# SERIAL => 上次已知父系(尾巴+A) 或是事件分頁
# reg USB\s*VID:PID=(\w+):(\w+)\s*SER=([A-Za-z0-9]+)


# serial_num  裝置例項路徑
# TD(Tramsmit Delay) = 15
