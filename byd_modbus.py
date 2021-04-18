#!/usr/bin/env python3

# Fork of https://github.com/christianh17/ioBroker.bydhvs/blob/master/main.js
# but converted into some kind of modbus RTU via TCP socket operation


# Run with byd_modbus.py -h to see all available commandline options

import socket

import time
import argparse

# Currently only used for CRC16 calculation. Need to extent to work with Modbus RTU via TCP socket
import minimalmodbus


class BatteryHVS:
    def __init__(self, ipaddr, debug=False):
        self.ipaddr = ipaddr
        self.port = 8080
        self.debug = debug
        
        self.registers = {
            # name : register, type, multiplier
            'soc' : [ 0, 'uint16', 1 ],
            'soh' : [ 3, 'uint16', 1 ],
            'current' : [ 4, 'sint16',  0.1 ],
            'voltage' : [ 5, 'uint16',  0.01 ],
            'cell_min_voltage' : [ 2,'uint16', 0.01 ],
            'cell_max_voltage' : [ 1, 'uint16', 0.01 ],
            'cell_min_temperature' : [ 7 ,'uint16', 1 ],
            'cell_max_temperature' : [ 6 , 'uint16', 1 ],
            'cell_avg_temperature' : [ 8 , 'uint16', 1 ],
            }
        
    def get_response(self, request):
        BUFFER_SIZE = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ipaddr, self.port))
        s.send(request)
        response = s.recv(BUFFER_SIZE)
        s.close()

        return response
    
    
    def read_holding_registers(self, register, length=1):
        request = b'\x01\x03'
        request += register.to_bytes(2, byteorder='big')
        request += length.to_bytes(2, byteorder='big')  # Len=1
        
        crc = minimalmodbus._calculate_crc_string(request.decode('latin1'))
        request += crc.encode('latin1')

        if self.debug:
            print('Sending {0}'.format(request))
        response = self.get_response(request)

        if self.debug:
            print("received data: {0}".format(response))
            print(bytes(response).hex())

            for i in range(len(response)):
                print('{} -  0x{:02x}'.format(i,response[i]))
            
        crc = minimalmodbus._calculate_crc_string(response[0:5].decode('latin1'))

        if crc.encode('latin1') == response[5:7]:
            if self.debug:
                print('CRC ok')
            return [ int.from_bytes(response[3:5], 'big') ]
        else:
            return False
            
    def read_uint16(self, addr):
        regs = self.read_holding_registers(addr + 1280, 1)
        if regs:
            return int(regs[0])
        else:
            print("read_uint16() - error")
            return False    

    def read_sint16(self, addr):
        value = self.read_uint16(addr)
        if value:
            if value > 32767:
                return int(value)-65535
            else:
                return int(value)
        else:
            print("read_sint16() - error")
            return False    

    def read_data(self, parameter):
        [register, datatype, multiplier] = self.registers[parameter]
        
        if datatype == "float":
            return False
#            return self.read_float(register)
#        elif datatype == "uint32":
#            return self.read_uint32(register)
        elif datatype == "sint16":
            return self.read_sint16(register) * multiplier
        elif datatype == "uint16":
            return self.read_uint16(register) * multiplier
        else:
            return False
        
    def print_all(self):
        print("Dump all registers:")
        for name, params in self.registers.items():
            value = self.read_data(name)
            if type(params[0]) is list:
                print("{0:d}: {1:s} - {2:2.1f}".format(params[0][0], name, value))
            else:
                print("{0:d}: {1:s} - {2:2.1f}".format(params[0], name, value))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--ipaddr", help="IP Address", 
                           default='192.168.16.254', action='store')
    argparser.add_argument("--debug", help="Enable debug output for Modbus RTU",
                           action='store_true')
    argparser.add_argument("-a", "--dump_all", help="Dump all registers",
                           action='store_true')
    argparser.add_argument("-t", "--test", help="Enable Test functions",
                           action='store_true')
    args = argparser.parse_args()
    
    battery = BatteryHVS(args.ipaddr, debug=args.debug)

    if args.dump_all:
        battery.print_all()
        
    if args.test:
        # print(battery.read_uint16(3))
        print(battery.read_data('soc'))
        # battery.print_all()



