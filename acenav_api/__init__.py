#__all__ = ['create_parser', 'PacketParser']

from .packet_parser import PacketParser
from .message_protocol import (create_internel_protocol,create_protocol_from_path)

def create_parser(device_type:str, config_path=None)->PacketParser:
    if config_path == None:
        protocol = create_internel_protocol(device_type)
        parser = PacketParser(device_type, protocol)
    else:
        protocol = create_protocol_from_path(config_path)
        parser = PacketParser(device_type, protocol)
    return parser