import sys
from acenav_api import create_parser, create_command_builder
setattr(sys, '__dev__', True)

# Generate command builder
command_builder = create_command_builder('INS502')
# Generate data parser
parser = create_parser('INS502')

def command_demo():
    cmd, request, response = iR()
    print_command(cmd, request, response)
    cmd, request, response = cA()
    print_command(cmd, request, response)
    cmd, request, response = iO()
    print_command(cmd, request, response)
    cmd, request, response = gM()
    print_command(cmd, request, response)
    cmd, request, response = wS()
    print_command(cmd, request, response)
    cmd, request, response = gE()
    print_command(cmd, request, response)
    cmd, request, response = hV()
    print_command(cmd, request, response)
    cmd, request, response = sV()
    print_command(cmd, request, response)
    cmd, request, response = aV()
    print_command(cmd, request, response)
    cmd, request, response = gB()
    print_command(cmd, request, response)
    cmd, request, response = uB()
    print_command(cmd, request, response)
    cmd, request, response = sC()
    print_command(cmd, request, response)
    cmd, request, response = rD()
    print_command(cmd, request, response)
    cmd, request, response = rG()
    print_command(cmd, request, response)
    cmd, request, response = sR()
    print_command(cmd, request, response)
    cmd, request, response = lO()
    print_command(cmd, request, response)
    cmd, request, response = sO()
    print_command(cmd, request, response)
    cmd, request, response = cO()
    print_command(cmd, request, response)
    cmd, request, response = wA_start()
    print_command(cmd, request, response)
    cmd, request, response = wA_data()
    print_command(cmd, request, response)
    cmd, request, response = oT()
    print_command(cmd, request, response)

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

    gB_response_bytes = bytes([0x02, 0x01, 0x04, 0x00,0x00,0x00,0x00, 0x02, 0x04, 0x00,0x00,0x00,0x00 ])
    command_response = parser.decode(cmd, gB_response_bytes)
    return cmd, command_bytes, command_response
    
def uB():
    cmd = 'uB'
    command_bytes = command_builder.create(cmd, 2, [
        {'param_id':1, 'value':1},
        {'param_id':2, 'value':2},
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
    command_response = parser.decode(cmd, bytes([0x53,0x32,0x80,0x47,0x4e,0x01]))
    return cmd, command_bytes, command_response

def sO():
    cmd = 'sO'
    command_bytes = command_builder.create(cmd,[
        {'packet_type':0x3253,'interface_type':0, 'odr':100}, #S2
        {'packet_type':0x4e47,'interface_type':2, 'odr':1}, #GN
        {'packet_type':0x6449,'interface_type':3, 'odr':100}, #IN
        {'packet_type':0x314f,'interface_type':255, 'odr':100}, #O1
    ])
    command_response = parser.decode(cmd, b'\x00')
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


def data_parser_demo():
    parser = create_parser('INS502')
    decode_result = parser.decode('S2', b'\x08\xbf\x00\x06\xf8\xba<#\xd7\n<#\xd7\n<#\xd7\n?\x80\x00\x00@\x00\x00\x00@@\x00\x00B\x0c\x00\x00\x00\x00\x00\x00')
    print('S2 decoded as:', decode_result)
    encode_result = parser.encode('S2', [2239,456890,0.01,0.01,0.01,1,2,3,35,0,0])
    print('S2 encoded as:', encode_result)

def print_command(cmd, request, response):
    print(cmd, 'Request:', ['{:X}'.format(x) for x in request])
    print(cmd, 'Response:', response)
    print('\r')

if __name__ == '__main__':
    command_demo()
    data_parser_demo()
    
