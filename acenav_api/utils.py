import pkgutil
import struct
import os
import sys
from typing import List,Union
from .package import PACKAGE_NAME

def convert_packet_to_bytes_array(name:str, packet:Union[None, str, List[int]])->List[int]:
    if packet == None:
        return [ord(c) for c in name]

    if isinstance(packet, str):
        try:
            packet_number = int(packet, 16)
            return list(struct.pack('<H', packet_number))
        except:
            raise Exception('Invalid value in packet raw data: ' + packet)
    
    return packet

def fetch_value(field:dict, key:str, default=None)->Union[None, str, int, float]:
    if key in field:
        return field[key]
    return default

def is_dev_mode():
    return hasattr(sys, '__dev__') and getattr(sys, '__dev__')

def get_executor_path():
    if is_dev_mode():  # if start from main.py
        path = os.getcwd()
    else:
        path = os.path.join(os.path.expanduser('~'), PACKAGE_NAME)
        if not os.path.isdir(path):
            os.makedirs(path,exist_ok=True)
    return path

def get_content_from_bundle(package, path):
    return pkgutil.get_data(PACKAGE_NAME, os.path.join(package, path))

def calc_crc(payload):
    '''
    Calculates 16-bit CRC-CCITT FALSE
    '''
    crc = 0x1D0F
    for bytedata in payload:
        crc = crc ^ (bytedata << 8)
        i = 0
        while i < 8:
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            i += 1
        crc = crc & 0xffff
    crc_msb = ((crc >> 8) & 0xFF)
    crc_lsb = (crc & 0xFF)
    return [crc_msb, crc_lsb]