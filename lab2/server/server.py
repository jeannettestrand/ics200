import socket
import sys
import math

def intToByteArray(int):
	int = socket.htonl(int)
	bytes = bytearray()
	bytes.append((int & 0xFF000000) >> 24)	
	bytes.append((int & 0xFF0000) >> 16)
	bytes.append((int & 0xFF00) >> 8) 
	bytes.append(int & 0xFF)
	return bytes

port = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', int(port)))


while True:
	data, address = s.recvfrom(1024)
	if (data, address):
	
		op = data[0]
		numValues = data[1]
		
		littleMask = 15	
		bigMask = 240
		
		values = bytearray()
		lastValue = None
		i = 2
		n = 0
		while n < numValues:
			if numValues % 2 != 0:
				lastValue = (data[len(data)-1] >> 4)
				numValues -= 1
			values.append((data[i] & bigMask)>>4)
			values.append((data[i] & littleMask))
			i += 1
			n += 2
		if lastValue:
			values.append(lastValue)	
		
		r = values[0]
		p = 1
		m = 2
		ml = 4

		if op & p == p:
			for i in range(1, len(values)):
				r += values[i]
		elif op & m == m:	
			for i in range(1, len(values)):
				r -= values[i]
		elif op & ml == ml:
			for i in range(1, len(values)):
				r *= values[i]
		print(r)
		
		buffer = intToByteArray(r & 0xFFFFFFFF)
		s.sendto(buffer, address)
		
s.close()		