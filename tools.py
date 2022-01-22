from subprocess import CalledProcessError, check_output, Popen, PIPE
from pathlib import Path

import sys
from glob import glob
import time
import yaml
import numpy as np
from pypot.dynamixel import DxlIO, Dxl320IO

LUOSFLASH = 'dfu-util -d 0483:df11 -a 0 -s 0x08000000 -D'
BIN_PATH = Path.home() / 'dev' / 'binaries'
CONFIG_PATH = Path.home() / 'dev' / 'reachy_pyluos_hal' / 'reachy_pyluos_hal' / 'config'


robot_part_to_real_name = {
    'left arm': 'left_arm_advanced',
    'right arm': 'right_arm_advanced',
    'head': 'head',
}


def flash_module(module: str):
    try:
        cmd = LUOSFLASH.split() + [str(BIN_PATH / f'{module}-firmware.bin')]
        check_output(cmd)
    except CalledProcessError:
        return -1
    return 0


def get_motor_config(robot_part, motor_name):
    config = {}
    default_baudrate = 1000000
    default_max_temperature = 55
    default_return_delay_time = 20

    real_robot_part = robot_part_to_real_name[robot_part]
    with open(str(CONFIG_PATH / f'{real_robot_part}.yaml')) as f:
        part_conf = yaml.load(f, Loader=yaml.FullLoader)

    motor_conf = part_conf[real_robot_part][motor_name]['dxl_motor']

    config['id'] = motor_conf['id']
    config['limit_angle'] = (int(np.rad2deg(motor_conf['cw_angle_limit'])),
                             int(np.rad2deg(motor_conf['ccw_angle_limit'])))
    config['baudrate'] = default_baudrate
    config['temperature_limit'] = default_max_temperature
    config['delay_time'] = default_return_delay_time
    return config


def get_usb2ax_port():
    if sys.platform == 'linux':
        port_template = '/dev/ttyUSB*'
    elif sys.platform == 'darwin':
        port_template = '/dev/tty.usbmodem*'
        return glob(port_template)[0]


def flash_motor(robot_part, motor_name):
    config = get_motor_config(robot_part, motor_name)

    dxl = DxlIO(port=get_usb2ax_port(), baudrate=57600)

    if not dxl.scan(range(40)):
        dxl.close()
        dxl = DxlIO(port=get_usb2ax_port(), baudrate=1000000)

    dxl_scanned = dxl.scan(range(40))

    if not dxl_scanned:
        dxl.close()
        return -1  # No motor detected

    if len(dxl_scanned) > 1:
        dxl.close()
        return -1  # Multiple motors detected

    new_id = config['id']

    if dxl_scanned[0] != new_id:
        dxl.change_id({dxl_scanned[0] : new_id})

    dxl.change_baudrate({new_id: 1000000})
    time.sleep(0.01)
    dxl.set_angle_limit({new_id: config['limit_angle']})
    time.sleep(0.01)
    dxl.set_return_delay_time({new_id: config['delay_time']}, convert=False)
    time.sleep(0.01)
    dxl.set_highest_temperature_limit({new_id: config['temperature_limit']})
    time.sleep(0.01)
    dxl.close()
    return 0
