import os
import json
from typing import List

from .utils import (convert_packet_to_bytes_array,
                    fetch_value,
                    get_executor_path,
                    get_content_from_bundle)

class OutputFieldConf:
    __type = ''
    __name = ''
    __endian = ''
    __unit = ''
    __scaling = ''

    def __init__(self, name, field_type, endian,unit,scaling) -> None:
        self.__name = name
        self.__type = field_type
        self.__endian = endian
        self.__unit = unit
        self.__scaling = scaling
    
    @property
    def type(self)->str:
        return self.__type
    
    @property
    def name(self)->str:
        return self.__name
    
    @property
    def endian(self)->str:
        return self.__endian
    
    @property
    def unit(self)->str:
        return self.__unit
    
    @property
    def scaling(self)->str:
        return self.__scaling
    
class OutputConf:
    __name = ''
    __display = ''
    __packet = []
    __fields = None

    def __init__(self, name, display, packet, fields: List[OutputFieldConf]) -> None:
        self.__name = name
        self.__display = display
        self.__packet = packet
        self.__fields = fields

    @property
    def name(self)->str:
        return self.__name

    @property
    def display(self)->str:
        return self.__display

    @property
    def packet(self)->List[int]:
        return self.__packet
    
    @property
    def fields(self)->List[OutputFieldConf]:
        return self.__fields

class MessageProtocol:
    __outputs = []
    __scalings = {}

    def __init__(self, json_config):
        default_endian = json_config['defaults']['payloadEndian']

        for item in json_config['userMessages']['outputPackets']:
            packet_name = fetch_value(item,'name')
            packet_bytes_array = convert_packet_to_bytes_array(packet_name, fetch_value(item,'packet'))

            if packet_name not in json_config['payloads']:
                continue

            json_payload_conf = json_config['payloads'][packet_name]
            output_fields_conf = []
            for field in json_payload_conf:
                output_fields_conf.append(
                    OutputFieldConf(
                        fetch_value(field,'name'),
                        fetch_value(field,'type'),
                        fetch_value(field,'endian', default_endian),
                        fetch_value(field,'unit'),
                        fetch_value(field,'scaling')
                    )
                )
            self.__outputs.append(
                OutputConf(
                    packet_name,
                    fetch_value(item,'display'),
                    packet_bytes_array,
                    output_fields_conf
                )
            )

        self.__scalings = json_config['scaling']

    @property
    def outputs(self)->List[OutputConf]:
        return self.__outputs
    
    @property
    def scalings(self)->dict:
        return self.__scalings

def create_internel_protocol(device_type:str)->MessageProtocol:
    if device_type == 'INS502':
        # Get configure path in package path if work as a library
        # read from user's document path
        # if cannot find, extract from package path
        config_parent = 'configs'
        config_name = '{0}.json'.format(device_type)
        executor_path = get_executor_path()
        config_path = os.path.join(executor_path, config_parent, config_name)
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            content = get_content_from_bundle(config_parent, config_name)
            with open(config_path, "wb") as fw:
                fw.write(content)

        return create_protocol_from_path(config_path)
    
    raise Exception('Unsupported device type.', device_type)
    
def create_protocol_from_path(config_path)->MessageProtocol:
    with open(config_path) as f:
        config = json.load(f)
    
    return MessageProtocol(config)