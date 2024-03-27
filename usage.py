import sys
from acenav_api import create_parser

setattr(sys, '__dev__', True)
parser = create_parser('INS502')

decode_result = parser.decode('S2', b'\x08\xbf\x00\x06\xf8\xba<#\xd7\n<#\xd7\n<#\xd7\n?\x80\x00\x00@\x00\x00\x00@@\x00\x00B\x0c\x00\x00\x00\x00\x00\x00')
print('S2 decoded as:', decode_result)

encode_result = parser.encode('S2', [2239,456890,0.01,0.01,0.01,1,2,3,35,0,0])
print('S2 encoded as:', encode_result)