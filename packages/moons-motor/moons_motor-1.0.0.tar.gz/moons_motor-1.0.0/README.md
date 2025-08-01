# Moons Motor

This is a python library for control moons motor through serial port.

## Compatibility

Now only support Windows.

## Installing

Install through `pip`

```bash
python -m pip install moons_motor

```

## Usage

```python
from motor import MoonsStepper, StepperModules, StepperCommand
import simulate
from time import sleep

motor = MoonsStepper(StepperModules.STM17S_3RN, "0403", "6001", "TESTA")

MoonsStepper.list_all_ports()
motor.connect()

motor.send_command(address="@", command=StepperCommand.JOG)
sleep(5)
motor.send_command(address="@", command=StepperCommand.STOP_JOG)

```

## Tested Motor

1. STM17S-3RN

## Reference
