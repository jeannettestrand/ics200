#python server.py 10010 -v

import socket, sys, os

utf = 'utf-8'
n = 1024
host = ''
port = int(sys.argv[1])
ready = 'READY'.encode(utf)
ok = 'OK'.encode(utf)
done = 'DONE'.encode(utf)


if len(sys.argv) > 2:
	v  = True
else:
	v = False
	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

if v:
	print('server waiting on port ', port)
conn, address = s.accept()

if (conn, address):
	if v:
		print('server connected to client at ', address, ' : ', port)
	conn.send(ready)
	
	
	request = conn.recv(n).decode(utf)
	if v:
		print('server receiving request: ', request)
	request = request.split(' ')
	action = request[0]
	filename = request[1]
#______________________________GET_________________________________	
	if action == 'GET':
		try:
			f = open(filename, "rb")
		except IOError as e:
			if e.errno == errno.EACCES:
				conn.send('ERROR: ', filename, ' does not exist').encode(utf)
		else:
			conn.send(ok)
			readyRecv = conn.recv(n)
			
			if readyRecv == ready:
				bTote = os.path.getsize(f.name)

				bytes = socket.htonl(bTote)
				
				buffer = bytearray()
				mask1 = 0xFF000000
				mask2 = 0xFF0000
				mask3 = 0xFF00
				mask4 = 0xFF
				buffer.append((bytes & mask1) >> 24)	
				buffer.append((bytes & mask2) >> 16)
				buffer.append((bytes & mask3) >> 8) 
				buffer.append(bytes & mask4)	
				conn.send(buffer)
				
				okRecv = conn.recv(n)
				
				if okRecv == ok:
					if v:
						print('server sending ', bTote, ' bytes')
					bSent = 0
					while bSent < bTote: 
						data = f.read(min((bTote - bSent), n)) 
						s = conn.send(data) 
						bSent += s
						
					conn.send(done)
					f.close()	
					conn.close()
# #______________________________PUT_________________________________	
	elif action == 'PUT':
		try:
			f = open(filename, 'wb')
		except IOError as e:
			if e.errno == errno.EACCES:
				s.send('ERROR: unable to create file ', filename).encode(utf)
		else:
			conn.send(ok)
			
			fileN = conn.recv(n)
				
			fSize = ((fileN[0] << 24) & 0xFF000000) | ((fileN[1] << 16) & 0xFF0000) | ((fileN[2] << 8) & 0xFF00) | (fileN[3] & 0xFF)
			
			fSize = socket.ntohl(fSize)
			print(fSize)
			conn.send(ok)
			if v:
				print('server receiving %i bytes' % fSize)
			fRec = 0
			while fRec < fSize:
				data = conn.recv(n)
				f.write(data)
				fRec += len(data)
			f.close()
			conn.recv(n)			
			conn.close()
			

# #______________________________DEL_________________________________	
	elif action == 'DEL':
		
		if os.access(filename, os.R_OK):
			if v:
				print('server deleting file ', filename)
			os.remove(filename)
			conn.send(done)
		else:
			error = ('ERROR: unable to delete ' + filename).encode(utf)
			conn.send(error)
				
		
			
			