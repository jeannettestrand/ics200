import socket
import sys

def intToByteArray(int):
	int = socket.htonl(int)
	bytes = bytearray()
	bytes.append((int & 0xFF000000) >> 24)	
	bytes.append((int & 0xFF0000) >> 16)
	bytes.append((int & 0xFF00) >> 8) 
	bytes.append(int & 0xFF)
	return bytes

def byteArrayToInt(bytes):
	int = ((bytes[0] << 24) & 0xFF000000) | ((bytes[1] << 16) & 0xFF0000) | ((bytes[2] << 8) & 0xFF00) | (bytes[3] & 0xFF)
	int = socket.ntohl(int)
	return int


input = sys.argv #python client.py localhost 10010 - 13 5 2 4

host = input[1]
port = input[2]




packet = bytearray()

op = input[3]
if op not in ('+', '-', '*'):
	print("invalid operator, please try again")
else:
	if op == '+':
		byte1 = 1	
	elif op == '-':
		byte1 = 2
	else:
		byte1 = 4	
	packet.append(byte1)

	if len(input) <= 5:
		print("please enter more than 1 operand")
	else:
		values = bytearray()
		for i in range(4, len(input)):
			values.append(int(input[i]))

		len = len(values)
		packet.append(len)
		
		#create a datagram packet  
		lastbyte = None 
		i = 0
		while i < len:
			if len % 2 != 0:
				lastbyte = (values[len-1] << 4 | 0xFF)
				len -= 1
			packet.append((values[i]<<4) | values[i+1])
			i += 2	
		if lastbyte:
			packet.append(lastbyte)

		s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s1.connect((host, int(port)))
		conf = s1.send(packet)
		buffer = s1.recv(1024)
		
		result = byteArrayToInt(buffer)

		if result > 2 ** 31:
			result -= (2 ** 32)
		
		print(result,'\n')