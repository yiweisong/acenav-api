# A library to decode and encode data packet for Aceinna Devices

## Usage
```python
from acenav_api import create_parser
    
parser = create_parser('IN502')
decode_payload = parser.decode('S2', bytes([0x0,0x1,0x2])) # return a dict object
binary_bytes = parser.encode('S2', [1,2,3]) # return as bytes
```

It also supports to pass a configuration file to the parser, the configuration file contains payload definition and the parser will generate the parser based on the configuration file.

```python
from acenav_api import create_parser

parser = create_parser('IN502-custom', 'path/to/config.json')
# support custom packet type
decode_payload = parser.decode('S2', bytes([0x0,0x1,0x2])) # return a dict object
binary_bytes = parser.encode('S2',[0,1,2]) # return as bytes
```

## How it work
The libary predefined configurations for each device, the configuration file is a json file that contains the payload definition for each packet type. It will decode or encode the data based on the configuration file.

User also could pass a custom configuration file to the parser to generate the parser. It is allowed to update the payload definition in the configuration file. It could be useful if the output format is modified or the payload is changed.