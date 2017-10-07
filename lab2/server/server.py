import socket
import sys
import math

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
		
		#server’s return datagram must be exactly 4 bytes
		
		r = socket.htonl(r & 0xFFFFFFFF)
		
		buffer = bytearray()
		mask1 = 0xFF000000
		mask2 = 0xFF0000
		mask3 = 0xFF00
		mask4 = 0xFF
		
		#"network order", which is big-endian
		#first byte must be the MOST SIGNIFICANT byte of the return result
		buffer.append((r & mask1) >> 24)
		buffer.append((r & mask2) >> 16)
		buffer.append((r & mask3) >> 8) 
		#fourth byte must be the LEAST SIGNIFICANT byte of the return result
		buffer.append(r & mask4)

		s.sendto(buffer, address)
		
s.close()		