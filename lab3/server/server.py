#python server.py 10010 -v

import socket, sys, os

utf = 'utf-8'
n = 1024
host = ''
port = int(sys.argv[1])
ready = 'READY'.encode(utf)
ok = 'OK'.encode(utf)
done = 'DONE'.encode(utf)

def intToByteArray(value):
	bytes = socket.htonl(value)
	buffer = bytearray()
	buffer.append((bytes & 0xFF000000) >> 24)	
	buffer.append((bytes & 0xFF0000) >> 16)
	buffer.append((bytes & 0xFF00) >> 8) 
	buffer.append(bytes & 0xFF)
	return buffer

def byteArrayToInt(fileN):
	mask1 = 0xFF000000
	mask2 = 0xFF0000
	mask3 = 0xFF00
	mask4 = 0xFF		
	fSize = ((fileN[0] << 24) & 0xFF000000) | ((fileN[1] << 16) & 0xFF0000) | ((fileN[2] << 8) & 0xFF00) | (fileN[3] & 0xFF)	
	return socket.ntohl(fSize)

if len(sys.argv) > 2:
	v  = True
else:
	v = False
	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

if v:
	print('server waiting on port %i' % port)
conn, address = s.accept()

if (conn, address):
	if v:
		print('server connected to client at %s : %i' % (host, port))
	conn.send(ready)
	
	
	request = conn.recv(n).decode(utf)
	if v:
		print('server receiving request: %s' % request)
	request = request.split(' ')
	action = request[0]
	filename = request[1]
#______________________________GET_________________________________	
	if action == 'GET':
		try:
			f = open(filename, "rb")
		except IOError as e:
			getErr = ('ERROR: ' + filename + ' does not exist').encode(utf)
			conn.send(getErr)
		else:
			conn.send(ok)
			readyRecv = conn.recv(n)
			
			if readyRecv == ready:
				bTote = os.path.getsize(f.name)
				buffer = intToByteArray(bTote)
				conn.send(buffer)
				okRecv = conn.recv(n)
				
				if okRecv == ok:
					if v:
						print('server sending %i bytes' % bTote)
					bSent = 0
					while bSent < bTote: 
						data = f.read(min((bTote - bSent), n)) 
						s = conn.send(data) 
						bSent += s
						
					conn.send(done)
					f.close()	
					conn.close()
#_____________________________PUT_________________________________	
	elif action == 'PUT':
		try:
			f = open(filename, 'wb')
		except IOError as e:
				errPut = ('ERROR: unable to create file ' + filename).encode(utf)
				s.send(errPut)
		else:
			conn.send(ok)
			fileN = conn.recv(n)
			fSize = byteArrayToInt(fileN)			
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
			

#______________________________DEL_________________________________	
	elif action == 'DEL':
		
		if os.access(filename, os.R_OK):
			if v:
				print('server deleting file %s' % filename)
			os.remove(filename)
			conn.send(done)
		else:
			error = ('ERROR: unable to delete ' + filename).encode(utf)
			conn.send(error)
				
		
			
			