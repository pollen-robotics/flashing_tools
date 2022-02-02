from subprocess import CalledProcessError, check_output, Popen, PIPE
from pathlib import Path

import sys
from glob import glob
import time
import yaml
import numpy as np
from pypot.dynamixel import DxlIO, Dxl320IO
from pypot.dynamixel.io.abstract_io import DxlTimeoutError, DxlCommunicationError


LUOSFLASH = 'dfu-util -d 0483:df11 -a 0 -s 0x08000000 -D'
BIN_PATH = Path.home() / 'dev' / 'binaries'
CONFIG_PATH = Path.home() / 'dev' / 'reachy_pyluos_hal' / 'reachy_pyluos_hal' / 'config'


robot_part_to_real_name = {
    'bras gauche': 'left_arm_advanced',
    'bras droit': 'right_arm_advanced',
    'tête': 'head',
}

french_motor_name_to_english = {
    'épaule droite 10': 'r_shoulder_pitch',
    'épaule droite 11': 'r_shoulder_roll', 
    'biceps droit 12': 'r_arm_yaw',
    'coude droit 13': 'r_elbow_pitch', 
    'avant-bras droit 14': 'r_forearm_yaw',
    'poignet droit 15': 'r_wrist_pitch',
    'poignet droit 16': 'r_wrist_roll',
    'pince droite 17': 'r_gripper',
    'épaule gauche 20': 'l_shoulder_pitch',
    'épaule gauche 21': 'l_shoulder_roll', 
    'biceps gauche 22': 'l_arm_yaw',
    'coude gauche 23': 'l_elbow_pitch', 
    'avant-bras gauche 24': 'l_forearm_yaw',
    'poignet gauche 25': 'l_wrist_pitch',
    'poignet gauche 26': 'l_wrist_roll',
    'pince gauche 27': 'l_gripper',
    'antenne gauche 30': 'l_antenna',
    'antenne droite 31': 'r_antenna',
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

    motor_conf = part_conf[real_robot_part][french_motor_name_to_english[motor_name]]['dxl_motor']

    config['id'] = motor_conf['id']
    config['limit_angle'] = (int(np.rad2deg(motor_conf['cw_angle_limit'])),
                             int(np.rad2deg(motor_conf['ccw_angle_limit'])))
    config['baudrate'] = default_baudrate
    config['temperature_limit'] = default_max_temperature
    config['delay_time'] = default_return_delay_time
    return config


def get_usb2ax_port():
    if sys.platform == 'linux':
        port_template = '/dev/ttyACM*'
    elif sys.platform == 'darwin':
        port_template = '/dev/tty.usbmodem*'

    try:
        port = glob(port_template)[0]
    except IndexError:
        port = ''
    return port


def flash_motor(robot_part, motor_name, motor_type = 'dxl'):
    config = get_motor_config(robot_part, motor_name)

    port = get_usb2ax_port()

    if port == '':
        return 'USB non détecté.'

    if motor_type == 'dxl320':
        dxl = Dxl320IO(port=port)

    else:
        dxl = DxlIO(port=port, baudrate=57600)

    try:
        dxl_scanned = dxl.scan(range(40))
    except DxlCommunicationError:
        return "Moteur mal détecté. \n Assurez vous que l'alimentation est branchée."

    if not dxl_scanned and motor_type=='dxl':
        dxl.close()
        dxl = DxlIO(port=get_usb2ax_port(), baudrate=1000000)

    dxl_scanned = dxl.scan(range(40))

    if not dxl_scanned:
        dxl.close()
        return 'Pas de moteur détecté. \n Assurez-vous que le moteur est correctement branché.'

    if len(dxl_scanned) > 1:
        dxl.close()
        return 'Plusieurs moteurs détectés. \n Rééssayez avec seulement un moteur branché.'

    new_id = config['id']

    if dxl_scanned[0] != new_id:
        dxl.change_id({dxl_scanned[0]: new_id})

    try:
        dxl.set_angle_limit({new_id: config['limit_angle']})
        time.sleep(0.01)
        dxl.set_return_delay_time({new_id: config['delay_time']}, convert=False)
        time.sleep(0.01)
        dxl.set_highest_temperature_limit({new_id: config['temperature_limit']})
        time.sleep(0.01)
        dxl.change_baudrate({new_id: 1000000})
        time.sleep(0.01)

    except DxlTimeoutError:
        return 'Un problème est survenu, veuillez rééssayer.'

    dxl.close()
    return 'Moteur configuré.'
