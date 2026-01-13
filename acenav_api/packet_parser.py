from typing import List,Union,Dict,Protocol
from .message_protocol import (MessageProtocol,OutputConf,CommandConf,ScalingConf,FieldConf)
from .field_parser import(BASIC_DATA_TYPES, EXTEND_DATA_TYPES, PARAMETERS_DATA_TYPES, MANUFACTORY_DATA_TYPES, 
                          encode_field, decode_field, 
                          encode_extend_field, decode_extend_field, 
                          encode_parameters_field, decode_parameters_field,build_random_value,build_random_bits,
                          encode_manfuactory_field, decode_manfuactory_field,
                          encode_bits_field, decode_bits_field)

def get_data_type_size(data_type: str) -> int:
    if data_type in ['uint8', 'int8']: return 1
    if data_type in ['uint16', 'int16']: return 2
    if data_type in ['uint32', 'int32', 'float']: return 4
    if data_type in ['uint64', 'int64', 'double']: return 8
    return 0

class PacketParserProtocol(Protocol):
    device_type: str
    config: MessageProtocol

    def decode(self, packet_type:str, payload: bytes)->dict:
        ...

    def encode(self, packet_type:str, *args)->bytes:
        ...


class PacketParser(PacketParserProtocol):
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

        exist_command = next((command for command in self.__config.commands if command.name==packet_type), None)
        if exist_command != None:
            return self.__build_command_payload_decoder(exist_command, self.__config.scalings)
        
        return lambda payload: payload

    def __build_output_payload_decoder(self, output: OutputConf, scalings: Dict[str, ScalingConf]):
        if hasattr(self, output.name):
            return lambda payload: getattr(self, output.name)(output.fields, payload)
        
        def decoder(payload: bytes)->dict:
            result = {}
            current_bit_pos = 0

            for field in output.fields:
                if hasattr(field.context, 'start') and field.context.get('start') is not None:
                    start_bit = field.context.get('start')
                else:
                    start_bit = current_bit_pos
                
                value = 0
                field_bit_len = 0

                if field.type == 'bits':
                    value = decode_bits_field(payload, start_bit, field.context.get('length'))
                    field_bit_len = field.context.get('length')
                elif field.type in BASIC_DATA_TYPES:
                    byte_start = start_bit // 8
                    value, data_len = decode_field(field.type, field.endian, payload, byte_start, field.precision)
                    field_bit_len = data_len * 8
                elif field.type in EXTEND_DATA_TYPES:
                    byte_start = start_bit // 8
                    value, data_len = decode_extend_field(field.type, payload, byte_start)
                    field_bit_len = data_len * 8
                else:
                    raise ValueError('Decode output failed, unknown data type {0} in output: {1}'.format(field.type, output.name))
                
                current_bit_pos = start_bit + field_bit_len
                
                if field.scaling in scalings:
                    value = value * scalings.get(field.scaling).scale + scalings.get(field.scaling).offset
                    if field.precision > 0 :
                        try:
                            value = float(round(value, field.precision))
                        except:
                            value = 0
                result[field.name] = value
                start_bit = start_bit + field_bit_len
            return result
        return decoder

    def __build_command_payload_decoder(self, command: CommandConf, scalings: Dict[str, ScalingConf]):
        custom_handler_name = '{0}_RESP'.format(command.name)
        
        if hasattr(self, custom_handler_name):
            return lambda payload: getattr(self, custom_handler_name)(command.response_fields, payload)
        
        if command.response_fields == None or len(command.response_fields) == 0:
            return lambda payload: payload
        
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
                elif field.type in MANUFACTORY_DATA_TYPES:
                    value, data_len = decode_manfuactory_field(field.type, self.__config.manufactory, payload, start)
                else:
                    raise ValueError('Decode command failed, unknown data type {0} in command: {1}'.format(field.type, command.name))
                
                if field.scaling in scalings:
                    value = value * scalings.get(field.scaling).scale + scalings.get(field.scaling).offset

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
            return self.__build_command_payload_encoder(exist_command, self.__config.scalings)
        
        return lambda payload: None

    def __build_output_payload_encoder(self, output: OutputConf, scalings: dict):
        def encoder(packet_value: List[int])->bytes:
            is_bit_mode = any(f.type == 'bits' for f in output.fields)
            
            if is_bit_mode:
                total_int = 0
                current_bit_pos = 0
                packet_value_len = len(packet_value)
                for idx, field in enumerate(output.fields):
                    value = 0
                    if idx < packet_value_len:
                        value = packet_value[idx]
                        if field.scaling in scalings:
                            value = int((value - scalings.get(field.scaling).offset) / scalings.get(field.scaling).scale)
                    
                    if hasattr(field.context, 'start') and field.context.get('start') is not None:
                        start_bit = field.context.get('start')
                    else:
                        start_bit = current_bit_pos
                    
                    if field.type == 'bits':
                        total_int = encode_bits_field(total_int, value, start_bit, field.context.get('length'))
                        current_bit_pos = start_bit + field.context.get('length')
                    elif field.type in BASIC_DATA_TYPES:
                        field_size = get_data_type_size(field.type)
                        total_int = total_int | (value << current_bit_pos)
                        current_bit_pos = current_bit_pos + field_size * 8
                    else:
                        raise ValueError('Encode output failed in bit mode, unknown data type {0} in output: {1}'.format(field.type, output.name))
                    
                return total_int.to_bytes(8, byteorder='little') # Assuming lsb
            else:
                result = bytearray()
                packet_value_len = len(packet_value)
                for idx, field in enumerate(output.fields):
                    value = 0
                    if idx < packet_value_len:
                        value = packet_value[idx]
                        if field.name in scalings:
                            value = int((value - scalings.get(field.scaling).offset) / scalings.get(field.scaling).scale)
                    
                    if field.type in BASIC_DATA_TYPES:
                        result.extend(encode_field(field.type, field.endian, value))
                    elif field.type in EXTEND_DATA_TYPES:
                        result.extend(encode_extend_field(field.type, value))
                    else:
                        raise ValueError('Encode output failed, unknown data type {0} in output: {1}'.format(field.type, output.name))
                return bytes(result)
        return encoder

    def __build_command_payload_encoder(self, command: CommandConf, scalings: dict):
        custom_handler_name = '{0}_REQ'.format(command.name)
        
        if hasattr(self, custom_handler_name):
            return lambda *args: getattr(self, custom_handler_name)(command.request_fields, *args)
        
        if command.request_fields == None or len(command.request_fields) == 0:
            return lambda *args: bytes([])
        
        def encoder(*args)->bytes:
            args_len = len(args)
            result = bytearray()
            # same as decoder, analyze the command fields
            # fill the bytes with the request fields
            for idx, field in enumerate(command.request_fields):
                value = 0
                if(idx < args_len):
                    value = args[idx]
                    if field.scaling in scalings:
                        value = int((value - scalings.get(field.scaling).offset) / scalings.get(field.scaling).scale)

                if field.type in BASIC_DATA_TYPES:
                    result.extend(encode_field(field.type, field.endian, value))
                elif field.type in EXTEND_DATA_TYPES:
                    result.extend(encode_extend_field(field.type, value))
                elif field.type in PARAMETERS_DATA_TYPES:
                    result.extend(encode_parameters_field(field.type, self.__config.parameters, value))
                elif field.type in MANUFACTORY_DATA_TYPES:
                    result.extend(encode_manfuactory_field(field.type, self.__config.manufactory, value))
                else:
                    raise ValueError('Encode command failed, unknown data type {0} in command: {1}'.format(field.type, command.name))
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

    def encode(self, packet_type:str, *args)->bytes:
        if packet_type not in self.__encoder:
            encoder = self.__build_encoder(packet_type)
            if encoder == None:
                raise Exception('No encoder for packet type: ' + packet_type)
            self.__encoder[packet_type] = encoder
        else:
            encoder = self.__encoder[packet_type]

        return encoder(*args)
    
    def build_random_data(self, packet_type:str)->List[Union[int,float]]:
        # read payload define from the config, build a random data for the packet type
        exist_output = next((output for output in self.__config.outputs if output.name==packet_type), None)
        if exist_output == None:
            return None
        
        is_bit_mode = any(f.type == 'bits' for f in exist_output.fields)
        if is_bit_mode:
            # for bit mode, return a list with single integer value
            result = []
            for field in exist_output.fields:
                random_value = build_random_bits(field.context.get('length'))
                result.append(random_value)
            return result
        else:
            result = []
            for field in exist_output.fields:
                random_value = build_random_value(field.type)
                result.append(random_value)
            return result


class IMUUartPacketParser(PacketParser):
    def __init__(self, config: MessageProtocol):
        super().__init__('IMU_UART', config)

    def _generate_address_sequence(self, address) -> List[int]:
        if isinstance(address, int):
            return [address]
        if isinstance(address, list):
            return address
        return []
    
    def WF_REQ(self, fieldConfs: List[FieldConf], *args) -> bytes:
        return self.SF_REQ(fieldConfs, *args)
    
    def WF_RESP(self, fieldConfs: List[FieldConf], payload: bytes) -> bool:
        return self.SF_RESP(fieldConfs, payload)
    
    def SF_REQ(self, fieldConfs: List[FieldConf], *args) -> bytes:
        message_body = bytearray()
        valid_param_count = 0
        
        if not args or len(args) == 0:
            return bytes([0])

        parameters = args[0] # Expect list of {paramId, value}

        for parameter in parameters:
            param_id = parameter.get('paramId')
            value = parameter.get('value')

            param_item = next((p for p in self.config.parameters if p.param_id == param_id), None)
            if not param_item:
                continue

            value_buffer = encode_field(param_item.type, param_item.endian, value)
            
            if hasattr(param_item, 'address') and param_item.address:
                sequence = self._generate_address_sequence(param_item.address)
                if not sequence:
                    continue
                
                for index, field_address in enumerate(sequence):
                    message_body.extend(encode_field('uint16', param_item.endian, field_address))
                    start = 2 * index
                    end = 2 * index + 2
                    if start < len(value_buffer):
                        chunk = value_buffer[start:end]
                        # Ensure chunk is 2 bytes if needed? TS slice just takes what is there.
                        message_body.extend(chunk)
                valid_param_count += len(sequence)
            else:
                message_body.extend(encode_field('uint16', param_item.endian, param_item.param_id))
                message_body.extend(value_buffer)
                valid_param_count += 1
        
        return bytes([valid_param_count]) + message_body
    
    def SF_RESP(self, fieldConfs: List[FieldConf], payload: bytes) -> bool:
        if not payload:
            return False
        updated_count = payload[0]
        return updated_count > 0
    
    def RF_REQ(self, fieldConfs: List[FieldConf], *args) -> bytes:
        return self.GF_REQ(fieldConfs, *args)
    
    def RF_RESP(self, fieldConfs: List[FieldConf], payload: bytes) -> dict:
        return self.GF_RESP(fieldConfs, payload)
    
    def GF_REQ(self, fieldConfs: List[FieldConf], *args) -> bytes:
        message_body = bytearray()
        fields_count = 0
        ids = args[0] if args and len(args) > 0 else []

        if ids:
            fields = [p for p in self.config.parameters if p.param_id in ids]
        else:
            fields = self.config.parameters
        
        for field in fields:
            if hasattr(field, 'address') and field.address:
                sequence = self._generate_address_sequence(field.address)
                if not sequence:
                    # console.log('Cannot generate address sequence...')
                    break

                for item in sequence:
                    message_body.extend(encode_field('uint16', field.endian, item))
                fields_count += len(sequence)
            else:
                message_body.extend(encode_field('uint16', field.endian, field.param_id))
                fields_count += 1
        
        return bytes([fields_count]) + message_body
    
    def GF_RESP(self, fieldConfs: List[FieldConf], payload: bytes) -> dict:
        if not payload:
            return []

        data = []
        fields_count = payload[0]
        fields_collection = []

        # 1. build a field list
        for i in range(fields_count):
            current_index = 4 * i + 1
            value_index = current_index + 2
            
            if current_index + 2 > len(payload):
                break
            
            try:
                # TS uses readUint16BE for address in GF_RESP
                address, _ = decode_field('uint16', 'big', payload, current_index // 2 if False else current_index) 
                # decode_field expects byte_start for types size > 1? 
                # No, decode_field(type, endian, payload, start_byte, precision). start_byte is byte index.
                # My previous check: "start_bit // 8" in PacketParser. But generic decode_field takes byte index? 
                # Let's check usages in PacketParser:
                # value, data_len = decode_field(field.type, field.endian, payload, start)
                # So start is byte index.
                
                value = payload[value_index : value_index + 2]
                fields_collection.append({'address': address, 'value': value})
            except:
                continue

        # 2. map field to parameter, do decode
        for parameter_conf in self.config.parameters:
            filter_fields = []
            
            if hasattr(parameter_conf, 'address') and parameter_conf.address:
                address_list = self._generate_address_sequence(parameter_conf.address)
                if not address_list:
                    continue
                
                filter_fields = [f for f in fields_collection if f['address'] in address_list]
                
                # Simple check for completeness. 
                # Assuming address_list elements are unique.
                # To match TS logic: filterFields.length !== addressList.length
                filtered_addresses = [f['address'] for f in filter_fields]
                # Note: This logic assumes we received all parts for the parameter.
                unique_found = len(set(filtered_addresses))
                if unique_found != len(address_list):
                    continue
                    
                # Sort filter_fields to match address_list order? 
                # TS: filterFields.filter(field => addressList.indexOf(field.address) > -1)
                # TS filter preserves order of original array (fieldsCollection).
                # fieldsCollection is ordered by payload order.
                # If the device returns fields in requested order, AND we requested in addressList order...
                # TS GF_REQ concat sequence.map. So we request in order.
                # So response should be in order.
                # However, cleaner to sort by index in address_list
                filter_fields.sort(key=lambda x: address_list.index(x['address']))

            else:
                filter_fields = [f for f in fields_collection if f['address'] == parameter_conf.param_id]
            
            if not filter_fields:
                continue

            need_decode_payload = bytearray()
            for f in filter_fields:
                need_decode_payload.extend(f['value'])
            
            # decode_field returns (value, length)
            # We treat the concatenated bytes as the payload.
            val, _ = decode_field(parameter_conf.type, parameter_conf.endian, need_decode_payload, 0)
            
            data.append({
                'paramId': parameter_conf.param_id,
                'name': parameter_conf.name,
                'value': val
            })
            
        return data
    
    def SR_REQ(self, fieldConfs: List[FieldConf], *args) -> bytes:
        return bytes([])
    
    def SR_RESP(self, fieldConfs: List[FieldConf], payload: bytes) -> bool:
        return len(payload) == 0