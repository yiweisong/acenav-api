import struct

def build_fmt(fmt:str, endian:str)->str:
    if endian == 'lsb':
        return '<'+fmt
    else:
        return '>'+fmt

def decode_field(data_type:str, endian:str, payload:bytes, start:int):
    result = None
    if data_type == 'uint64':
        result = (struct.unpack(build_fmt('Q',endian), payload[start:start+8])[0],8)
    elif data_type == 'int64':
        result = (struct.unpack(build_fmt('q',endian), payload[start:start+8])[0],8)
    elif data_type == 'double':
        result = (struct.unpack(build_fmt('d',endian), payload[start:start+8])[0],8)
    elif data_type == 'uint32':
        result = (struct.unpack(build_fmt('I',endian), payload[start:start+4])[0],4)
    elif data_type == 'int32':
        result = (struct.unpack(build_fmt('i',endian), payload[start:start+4])[0],4)
    elif data_type == 'float':
        result = (struct.unpack(build_fmt('f',endian), payload[start:start+4])[0],4)    
    elif data_type == 'uint16':
        result = (struct.unpack(build_fmt('H',endian), payload[start:start+2])[0],2)
    elif data_type == 'int16':
        result = (struct.unpack(build_fmt('h',endian), payload[start:start+2])[0],2)
    elif data_type == 'uint8':
        result = (struct.unpack('B', payload[start:start+1])[0],1)
    elif data_type == 'int8':
        result = (struct.unpack('b', payload[start:start+1])[0],1)
    else:
        raise ValueError('Decode failed, unknown data type: {0}'.format(data_type))

    return result

def encode_field(data_type:str, endian:str, value:int)->bytes:
    payload = bytearray()

    if data_type == 'uint64':
        payload = struct.pack(build_fmt('Q',endian), value)
    elif data_type == 'int64':
        payload = struct.pack(build_fmt('q',endian), value)
    elif data_type == 'double':
        payload = struct.pack(build_fmt('d',endian), value)
    elif data_type == 'uint32':
        payload = struct.pack(build_fmt('I',endian), value)
    elif data_type == 'int32':
        payload = struct.pack(build_fmt('i',endian), value)
    elif data_type == 'float':
        payload = struct.pack(build_fmt('f',endian), value)
    elif data_type == 'uint16':
        payload = struct.pack(build_fmt('H',endian), value)
    elif data_type == 'int16':
        payload = struct.pack(build_fmt('h',endian), value)
    elif data_type == 'uint8':
        payload = struct.pack(build_fmt('B',endian), value)
    elif data_type == 'int8':
        payload = struct.pack(build_fmt('b',endian), value)
    else:
        raise ValueError('Encode failed, unknown data type: {0}'.format(data_type))
    return payload
    