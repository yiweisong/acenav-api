import sys
from acenav_api import create_parser, create_command_builder
setattr(sys, '__dev__', True)

# Generate command builder
command_builder = create_command_builder('INS502')
# Generate data parser
parser = create_parser('INS502')

#region Command Demo

def command_demo():
    print('Command Demo:')
    print('--------------------------\r\n')
    command_list = ['iR','cA','iO','gM','wS','gE',
                    'hV','sV','aV','gB','uB','sC',
                    'rD','rG','sR','lO','sO','cO',
                    'wA_start','wA_data','oT']
    for command in command_list:
        print_output(eval(f'{command}()'))

def iR():
    cmd = 'iR'
    command_bytes = command_builder.create(cmd, bytes([0x01, 0x02, 0x03, 0x04]))
    command_response = parser.decode(cmd, b'\x01\x02\x03\x04')
    return cmd, command_bytes, command_response

def cA():
    cmd = 'cA'
    command_bytes = command_builder.create(cmd, 50.5)
    command_response = parser.decode(cmd, b'no more response')
    return cmd, command_bytes, command_response

def iO():
    cmd = 'iO'
    command_bytes = command_builder.create(cmd, 0,0x18ff5164,bytes([0x01, 0x02, 0x03, 0x04,0x05,0x06,0x07,0x08]))
    command_response = parser.decode(cmd, b'no more response')
    return cmd, command_bytes, command_response

def gM():
    cmd = 'gM'
    command_bytes = command_builder.create(cmd)
    command_response = parser.decode(cmd, bytes([0x01, 0x02, 0x03, 0x04,0x05,0x06,0x07,0x08]))
    return cmd, command_bytes, command_response

def wS():
    cmd = 'wS'
    command_bytes = command_builder.create(cmd,0, 2024032818)
    command_response = parser.decode(cmd, bytes([0x00]))
    return cmd, command_bytes, command_response

def gE():
    cmd = 'gE'
    command_bytes = command_builder.create(cmd,1, 1)
    command_response = parser.decode(cmd, bytes([0x01,0x02,0x03]))
    return cmd, command_bytes, command_response

def hV():
    cmd = 'hV'
    command_bytes = command_builder.create(cmd,0)
    command_response = parser.decode(cmd, b'\x00INS50X 5020-4007-01 21790xxxxx, Hardware v1.0')
    return cmd, command_bytes, command_response

def sV():
    cmd = 'sV'
    command_bytes = command_builder.create(cmd,0)
    command_response = parser.decode(cmd, b'\x00v31.00.01')
    return cmd, command_bytes, command_response

def aV():
    cmd = 'aV'
    command_bytes = command_builder.create(cmd)
    command_response = parser.decode(cmd, b'INSLIB_1.0.0, RECEIVER_1.0.0')
    return cmd, command_bytes, command_response

def gB():
    cmd = 'gB'
    command_bytes = command_builder.create(cmd, 5, [1,2,3,4,5])

    gB_response_bytes = bytes([0x02, 0x01, 0x04, 0x10,0x06,0x9e,0x3f, 0x02, 0x04, 0xa8,0x35,0x3f,0x40 ])
    command_response = parser.decode(cmd, gB_response_bytes)
    return cmd, command_bytes, command_response
    
def uB():
    cmd = 'uB'
    command_bytes = command_builder.create(cmd, 2, [
        {'param_id':1, 'value':1.45672},
        {'param_id':2, 'value':2.98761},
    ])
    uB_response_bytes = bytes([0x02, 0x01,0x00,0x03,0x01])
    command_response = parser.decode(cmd, uB_response_bytes)
    return cmd, command_bytes, command_response

def sC():
    cmd = 'sC'
    command_bytes = command_builder.create(cmd)
    command_response = parser.decode(cmd, b'no more response')
    return cmd, command_bytes, command_response

def rD():
    cmd = 'rD'
    command_bytes = command_builder.create(cmd)
    command_response = parser.decode(cmd, b'no more response')
    return cmd, command_bytes, command_response

def rG():
    cmd = 'rG'
    command_bytes = command_builder.create(cmd, 0x01, 0x00, 0x00,0x00)
    command_response = parser.decode(cmd, b'2J\xa4x')
    return cmd, command_bytes, command_response

def sR():
    cmd = 'sR'
    command_bytes = command_builder.create(cmd)
    command_response = parser.decode(cmd, b'no more response')
    return cmd, command_bytes, command_response

def lO():
    cmd = 'lO'
    command_bytes = command_builder.create(cmd,1)
    command_response = parser.decode(cmd, bytes([0x02,0x53,0x32,0x80,0x47,0x4e,0x01]))
    return cmd, command_bytes, command_response

def sO():
    cmd = 'sO'
    command_bytes = command_builder.create(cmd,4, [
        {'packet_type':0x3253,'interface_type':0, 'odr':100}, #S2
        {'packet_type':0x4e47,'interface_type':2, 'odr':1}, #GN
        {'packet_type':0x6449,'interface_type':3, 'odr':100}, #IN
        {'packet_type':0x314f,'interface_type':255, 'odr':100}, #O1
    ])
    command_response = parser.decode(cmd, bytes([0x02,0x53,0x32,0x01,0x00,0x47,0x4e,0x01,0x00]))
    return cmd, command_bytes, command_response

def cO():
    cmd = 'cO'
    command_bytes = command_builder.create(cmd,1)
    command_response = parser.decode(cmd, b'\x00')
    return cmd, command_bytes, command_response

def wA_start():
    cmd = 'wA_start'
    command_bytes = command_builder.create(cmd, 0x0a, 30, 30*1024)
    command_response = parser.decode(cmd, bytes([0x0a,0x00,0x00]))
    return cmd, command_bytes, command_response

def wA_data():
    cmd = 'wA_data'
    command_bytes = command_builder.create(cmd,0x0b, 0x01, bytes([0x01,0x02,0x03,0x04]))
    command_response = parser.decode(cmd, bytes([0x0b,0x01,0x00,0x00]))
    return cmd, command_bytes, command_response

def oT():
    cmd = 'oT'
    command_bytes = command_builder.create(cmd,1)
    command_response = parser.decode(cmd, bytes([0x01, 0x00, 0x00]))
    return cmd, command_bytes, command_response

def print_command(args):
    if args == None or len(args) != 3:
        return
    cmd = args[0]
    request = args[1]
    response = args[2]
    print('Command:',cmd)
    print('\r')
    print('Request:', request) #['{:X}'.format(x) for x in request])
    #print('\r')
    print('Response:', response)
    print('\r\n--------------------------\r\n')

#endregion Command Demo

#region Data Parser Demo

def data_parser_demo():
    print('Data Parser Demo:')
    print('--------------------------\r\n')
    output_packet_types = ['IN','S2','GN','RR','ODO',
                           'T1','T2','GI','II','IR',
                           'MB','HS','DIAGNOSTIC','RT','SV']
    for packet_type in output_packet_types:
        print_output(build_output_demo(packet_type))
    
def build_output_demo(packet_type:str):
    random_data = parser.build_random_data(packet_type)
    if random_data is None:
        return None

    encode_result = parser.encode(packet_type, random_data)    
    decode_result = parser.decode(packet_type, encode_result)
    return packet_type, encode_result, decode_result

def print_output(args):
    if args == None or len(args) != 3:
        return
    packet_type = args[0]
    encode_result = args[1]
    decode_result = args[2]
    print('Packet Type:',packet_type)
    print('\r')
    print('Encoded:', encode_result)
    print('\r')
    print('Decoded:', decode_result) #['{:X}'.format(x) for x in encode_result])
    print('\r\n--------------------------\r\n')

#endregion Data Parser Demo

if __name__ == '__main__':
    command_demo()
    data_parser_demo()
    
