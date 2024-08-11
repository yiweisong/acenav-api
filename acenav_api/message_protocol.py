import os
import json
from typing import List,Union

from .utils import (convert_packet_to_bytes_array,
                    fetch_value,
                    get_executor_path,
                    get_content_from_bundle)

ALREADY_SUPPORTED = ['INS502']

class ParameterConf:
    __name = ''
    __param_id = 0
    __type = ''
    __endian = ''
    __precision = 0
    __address_range = '' #prepare for IMU330RA
    
    def __init__(self, name, type, param_id, endian, precision) -> None:
        self.__name = name
        self.__type = type
        self.__param_id = int(param_id)
        self.__endian = endian
        self.__precision = precision
        
    @property
    def name(self)->str:
        return self.__name
    
    @property
    def param_id(self)->int:
        return self.__param_id
    
    @property
    def type(self)->str:
        return self.__type
    
    @property
    def endian(self)->str:
        return self.__endian
    
    @property
    def precision(self)->int:
        return self.__precision

class CommandFieldConf:
    __type = ''
    __name = ''
    
    def __init__(self, name, field_type) -> None:
        self.__type = field_type
        self.__name = name
        
    @property
    def type(self)->str:
        return self.__type
    
    @property
    def name(self)->str:
        return self.__name
    
    @property
    def endian(self)->str:
        return 'lsb'

class CommandConf:
    __name = ''
    __packet = []
    __request_fields = None
    __response_fields = None
    __format = ''
    
    def __init__(self, name:str, packet:List[int], format:str, request_fields:List[CommandFieldConf], response_fields:List[CommandFieldConf]) -> None:
        self.__name = name
        self.__packet = packet
        self.__request_fields = request_fields
        self.__response_fields = response_fields
        self.__format = format
        
    @property
    def name(self)->str:
        return self.__name
    
    @property
    def packet(self)->List[int]:
        return self.__packet
    
    @property
    def request_fields(self)->List[CommandFieldConf]:
        return self.__request_fields
    
    @property
    def response_fields(self)->List[CommandFieldConf]:
        return self.__response_fields
    
    @property
    def format(self)->str:
        return self.__format

class OutputFieldConf:
    __type = ''
    __name = ''
    __endian = ''
    __unit = ''
    __scaling = ''
    __precision = 0

    def __init__(self, name, field_type, endian,unit,scaling,precision) -> None:
        self.__name = name
        self.__type = field_type
        self.__endian = endian
        self.__unit = unit
        self.__scaling = scaling
        self.__precision = precision
    
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
    
    @property
    def precision(self)->int:
        return self.__precision
    
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
    __manufactory = []
    __parameters = []
    __commands = []
    __outputs = []
    __scalings = {}
    
    def __init__(self, json_config):
        default_format = json_config['defaults']['format']
        default_endian = json_config['defaults']['payloadEndian']
        
        # fill manufacturer
        for item in json_config['manufactory']:
            self.__manufactory.append(
                ParameterConf(
                    fetch_value(item,'name'),
                    fetch_value(item,'type'),
                    fetch_value(item,'contentId'),
                    fetch_value(item,'endian',default_endian),
                    fetch_value(item,'precision',4)
                )
            )

        # fill parameters
        for item in json_config['userConfiguration']:
            self.__parameters.append(
                ParameterConf(
                    fetch_value(item,'name'),
                    fetch_value(item,'type'),
                    fetch_value(item,'paramId'),
                    fetch_value(item,'endian',default_endian),
                    fetch_value(item,'precision',4)
                )
            )

        # fill outputs
        for item in json_config['userMessages']['outputPackets']:
            output_packet_dict = convert_to_packet_dict(item)
            
            packet_name = fetch_value(output_packet_dict,'name')
            packet_bytes_array = convert_packet_to_bytes_array(packet_name, fetch_value(output_packet_dict,'packet'))

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
                        fetch_value(field,'scaling'),
                        fetch_value(field,'precision',6)
                    )
                )
            self.__outputs.append(
                OutputConf(
                    packet_name,
                    fetch_value(output_packet_dict,'display'),
                    packet_bytes_array,
                    output_fields_conf
                )
            )

        # fill commands
        for item in json_config['userMessages']['inputPackets']:
            input_packet_dict = convert_to_packet_dict(item)
            
            packet_name = fetch_value(input_packet_dict,'name')
            packet_bytes_array = convert_packet_to_bytes_array(packet_name, fetch_value(input_packet_dict,'packet'))
            message_format = fetch_value(input_packet_dict,'format',default_format)

            request_fields_conf = []
            response_fields_conf = []
            if packet_name+'_REQ' in json_config['payloads']:
                json_request_conf = json_config['payloads'][packet_name+'_REQ']
            else:
                json_request_conf = []
            
            if packet_name+'_RESP' in json_config['payloads']:
                json_response_conf = json_config['payloads'][packet_name+'_RESP']
            else:
                json_response_conf = []

            for field in json_request_conf:
                request_fields_conf.append(
                    CommandFieldConf(
                        fetch_value(field,'name'),
                        fetch_value(field,'type')
                    )
                )
            
            for field in json_response_conf:
                response_fields_conf.append(
                    CommandFieldConf(
                        fetch_value(field,'name'),
                        fetch_value(field,'type')
                    )
                )

            self.__commands.append(
                CommandConf(
                    packet_name,
                    packet_bytes_array,
                    message_format,
                    request_fields_conf,
                    response_fields_conf
                )
            )
        self.__scalings = json_config['scaling']

    @property
    def outputs(self)->List[OutputConf]:
        return self.__outputs
    
    @property
    def scalings(self)->dict:
        return self.__scalings
    
    @property
    def commands(self)->List[CommandConf]:
        return self.__commands
    
    @property
    def parameters(self)->List[ParameterConf]:
        return self.__parameters
    
    @property
    def manufactory(self)->List[ParameterConf]:
        return self.__manufactory

def convert_to_packet_dict(packet_conf: Union[str,dict])->dict:
    if isinstance(packet_conf, str):
        return { 'name': packet_conf }
    
    return packet_conf

def create_internel_protocol(device_type:str)->MessageProtocol:
    if device_type.upper() in ALREADY_SUPPORTED:
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
