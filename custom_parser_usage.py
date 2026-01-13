from acenav_api.command_builder import CommandBuilder
from acenav_api.packet_parser import IMUUartPacketParser
from acenav_api.message_protocol import create_protocol_from_path

#region Generate data parser
message_protocol = create_protocol_from_path('./configs/MTLT335D-uart.json')
parser = IMUUartPacketParser(message_protocol)
#endregion

#region Generate command builder   
command_builder = CommandBuilder(parser)
#endregion

#region Command Demo
command_definitions = [
    ['SF', [{'paramId':1, 'value':12}, {'paramId':2, 'value':34}], bytes([0x01, 0x00, 0x00])],
    ['WF', [{'paramId':1, 'value':12}, {'paramId':2, 'value':34}], bytes([0x01, 0x00, 0x00])],
    ['GF', [1,2], bytes([0x02, 0x00, 0x01, 0x00,0x02, 0x00,0x02, 0x00,0x03])],
    ['RF', [3,4], bytes([0x02, 0x00, 0x01, 0x00,0x02, 0x00,0x02, 0x00,0x03])],
]

def command_demo():
    print('Command Demo:')
    print('--------------------------\r\n')
    for command in command_definitions:
        cmd = command[0]
        if isinstance(command[1], tuple):
            data = command_builder.create(cmd, *command[1])
        else:
            data = command_builder.create(cmd, command[1])
        command_response = parser.decode(cmd, command[2])
        print_command((cmd, data, command_response))

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

#endregion

#region Data Parser Demo
def data_parser_demo():
    print('Data Parser Demo:')
    print('--------------------------\r\n')
    output_packet_types = ['S1','A2','FM', 'SM', 'ID', 'VR']
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

#endregion

if __name__ == '__main__':
    command_demo()
    data_parser_demo()