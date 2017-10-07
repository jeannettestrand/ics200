import socket
import sys

input = sys.argv #python client.py localhost 12345 - 13 5 2 4

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
				#last byte, if there is only one 4-bit integer remaining, will put the integer in the MOST SIGNIFICANT bits, and pad the LEAST SIGNIFICANT bits with all zeros
				lastbyte = (values[len-1] << 4 | 0xFF)
				len -= 1
					
			packet.append((values[i]<<4) | values[i+1])	#Each byte will hold two 4-bit integers
			i += 2
			
		if lastbyte:
			packet.append(lastbyte)

		s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s1.connect((host, int(port)))
		conf = s1.send(packet)
		buffer = s1.recv(10)
		
		mask1 = 0xFF000000
		mask2 = 0xFF0000
		mask3 = 0xFF00
		mask4 = 0xFF		
		
		result = ((buffer[0] << 24) & mask1) | ((buffer[1] << 16) & mask2) | ((buffer[2] << 8) & mask3) | (buffer[3] & mask4)
		result = socket.ntohl(result)
		if result > 2 ** 31:
			result -= (2 ** 32)
		
		print(result,'\n')