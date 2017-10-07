# python client.py localhost 10010 GET mytest.txt


import sys, socket, os

utf = 'UTF-8'
n = 1024
bytes = None
ready = 'READY'.encode(utf)
ok = 'OK'.encode(utf)
done = 'DONE'.encode(utf)


host = sys.argv[1]
port = sys.argv[2]
action = sys.argv[3]
filename = sys.argv[4]
request = (action + ' ' + filename).encode(utf)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, int(port)))			
readyRecv = s.recv(n).decode(utf)

if readyRecv == 'READY':		

#______________________________GET_________________________________#	
	
	if action == 'GET':
		s.send(request)
		okRecv = s.recv(n)
		if okRecv == ok:
			s.send(ready)
					
			fileN = s.recv(n)
			mask1 = 0xFF000000
			mask2 = 0xFF0000
			mask3 = 0xFF00
			mask4 = 0xFF		
		
			n = ((fileN[0] << 24) & mask1) | ((fileN[1] << 16) & mask2) | ((fileN[2] << 8) & mask3) | (fileN[3] & mask4)
			nTot = socket.ntohl(n)
			
			try:
				f = open(filename, "wb")
			except IOError as e:
				print('client error: unable to create file %s' % (filename))
			else:
				print('client receiving file %s ( %i bytes)' % (filename, nTot))
				
				s.send(ok)
				print('nTot: %i' % nTot)
				fRecv = 0
				while fRecv < nTot: 
					data = s.recv(min((nTot - fRecv), n))
					f.write(data)
					fRecv += len(data)
					print('fRecv %i' % fRecv)
				doneRecv = s.recv(n)
				if doneRecv == done:
					print('Complete')
						
			
# #______________________________PUT_________________________________#	
	
	elif action == 'PUT':
		request =( action + ' ' + filename).encode(utf)
		s.send(request)
		okRecv = s.recv(n)
					
		if okRecv == ok:
			try:
				f = open(filename, 'rb')
			except IOError as e:
				print('client error: %s does not exist' % filename)
			else: 
				bTot = os.path.getsize(f.name)
				bytes = socket.htonl(bTot)
				
				buffer = bytearray()
				buffer.append((bytes & 0xFF000000) >> 24)	
				buffer.append((bytes & 0xFF0000) >> 16)
				buffer.append((bytes & 0xFF00) >> 8) 
				buffer.append(bytes & 0xFF)
				s.send(buffer)
				
				okRecv = s.recv(n)
				if okRecv == ok:
					print('client sending file %s (%i bytes)' % (filename, bTot))
					bSent = 0
					while bSent < bTot:
						data = f.read(min((bTot - bSent), n))
						sent = s.send(data)
						bSent += sent 
					s.send(done)
					print('Complete')
			
# #______________________________DEL_________________________________#

					
	elif action == 'DEL':
		print('client deleting file ', filename)
		request = (action + ' ' + filename).encode(utf)
		s.send(request)
				
		doneRecv = s.recv(n)
		if doneRecv == done:
			print('Complete')
		else:
			print('server error: ', doneRecv.decode(utf)) #remove the server"error" prefix
		s.close()
		