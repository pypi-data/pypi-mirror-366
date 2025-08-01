from nor1029_controller import Nor265, list_ports

port = list_ports()[0].device

import logging

logging.basicConfig(level=logging.DEBUG)

# print("Connect", port)
with Nor265(port) as nor:
	nor.start_sweep(0, 180, 10)
	# print("Start")
	# nor.rotate(100)
	#
	# print("Stop")

# import serial
# from time import sleep
# port = '/dev/cu.PL2303G-USBtoUART110'
#
# nor = serial.Serial(
#     port,
#     baudrate=9600,
#     bytesize=serial.EIGHTBITS,
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     timeout=30,
#     dsrdtr=True,
# )
#
# print(nor.read_all().decode())
#
# nor.write('FS;'.encode())
#
# sleep(1)
#
# print(nor.read_all().decode())
