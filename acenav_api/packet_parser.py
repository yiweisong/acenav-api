from typing import List
from .message_protocol import (MessageProtocol,OutputConf,CommandConf)
from .field_parser import(BASIC_DATA_TYPES, EXTEND_DATA_TYPES, PARAMETERS_DATA_TYPES, 
                          encode_field, decode_field, 
                          encode_extend_field, decode_extend_field, 
                          encode_parameters_field, decode_parameters_field)

class PacketParser:
    __device_type = ''
    __config = None
    __decoder = {}
    __encoder = {}

    def __init__(self, device_type:str, config: MessageProtocol):
        self.__device_type = device_type
        self.__config = config

    def __build_decoder(self, packet_type:str):
        exist_output = next((output for output in self.__config.outputs if output.name==packet_type), None)
        if exist_output != None:
            return self.__build_output_payload_decoder(exist_output, self.__config.scalings)
        
        #TODO: may need decoder for commands
        exist_command = next((command for command in self.__config.commands if command.name==packet_type), None)
        if exist_command != None:
            return self.__build_command_payload_decoder(exist_command)
        
        return lambda payload: payload

    def __build_output_payload_decoder(self, output: OutputConf, scalings: dict):
        def decoder(payload: bytes)->dict:
            result = {}
            start = 0
            for field in output.fields:
                value, data_len = decode_field(field.type, field.endian, payload, start)
                if field.scaling in scalings:
                    value = value * eval(scalings[field.scaling])
                result[field.name] = value
                start = start + data_len
            return result
        return decoder

    def __build_command_payload_decoder(self, command: CommandConf):
        if command.response_fields == None or len(command.response_fields) == 0:
            return lambda payload: True
        
        def decoder(payload: bytes)->dict:
            # analyze the response fields in command
            # fill the dict with the response fields
            # should check the data type in response fields
            result = {}
            start = 0
            for field in command.response_fields:
                if field.type in BASIC_DATA_TYPES:
                    value, data_len = decode_field(field.type, field.endian, payload, start)
                elif field.type in EXTEND_DATA_TYPES:
                    value, data_len = decode_extend_field(field.type, payload, start)
                elif field.type in PARAMETERS_DATA_TYPES:
                    value, data_len = decode_parameters_field(field.type, self.__config.parameters, payload, start)
                else:
                    raise ValueError('Decode failed, unknown data type {0} in command: {1}'.format(field.type, command.name))
                result[field.name] = value
                start = start + data_len
            return result
        return decoder

    def __build_encoder(self, packet_type:str):
        exist_output = next((output for output in self.__config.outputs if output.name==packet_type), None)
        if exist_output != None:
            return self.__build_output_payload_encoder(exist_output, self.__config.scalings)
        
        #TODO: may need encoder for commands
        exist_command = next((command for command in self.__config.commands if command.name==packet_type), None)
        if exist_command != None:
            return self.__build_command_payload_encoder(exist_command)
        
        return lambda payload: None

    def __build_output_payload_encoder(self, output: OutputConf, scalings: dict):
        def encoder(packet_value: List[int])->bytes:
            result = bytearray()
            packet_value_len = len(packet_value)
            for idx, field in enumerate(output.fields):
                value = 0
                if idx < packet_value_len:
                    value = packet_value[idx]
                    if field.name in scalings:
                        value = value / eval(scalings[field.scaling])
                
                result.extend(encode_field(field.type, field.endian, value))
            return bytes(result)
        return encoder

    def __build_command_payload_encoder(self, command: CommandConf):
        if command.request_fields == None or len(command.request_fields) == 0:
            return lambda args: bytes([])
        
        def encoder(args)->bytes:
            args_len = len(args)
            result = bytearray()
            # same as decoder, analyze the command fields
            # fill the bytes with the request fields
            for idx, field in enumerate(command.request_fields):
                value = 0
                if(idx < args_len):
                    value = args[idx]

                if field.type in BASIC_DATA_TYPES:
                    result.extend(encode_field(field.type, field.endian, value))
                elif field.type in EXTEND_DATA_TYPES:
                    result.extend(encode_extend_field(field.type, value))
                elif field.type in PARAMETERS_DATA_TYPES:
                    result.extend(encode_parameters_field(field.type, self.__config.parameters, value))
                else:
                    raise ValueError('Encode failed, unknown data type {0} in command: {1}'.format(field.type, command.name))
            return result
        return encoder

    @property
    def device_type(self):
        return self.__device_type
    
    @property
    def config(self):
        return self.__config

    def decode(self, packet_type:str, payload: bytes)->dict:
        if packet_type not in self.__decoder:
            decoder = self.__build_decoder(packet_type)
            if decoder == None:
                raise Exception('No decoder for packet type: ' + packet_type)
            self.__decoder[packet_type] = decoder
        else:
            decoder = self.__decoder[packet_type]

        return decoder(payload)

    def encode(self, packet_type:str, packet_value: dict)->bytes:
        if packet_type not in self.__encoder:
            encoder = self.__build_encoder(packet_type)
            if encoder == None:
                raise Exception('No encoder for packet type: ' + packet_type)
            self.__encoder[packet_type] = encoder
        else:
            encoder = self.__encoder[packet_type]
        
        return encoder(packet_value)