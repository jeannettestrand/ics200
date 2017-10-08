# python client.py localhost 10010 GET mytest.txt


import sys, socket, os

utf = 'UTF-8'
n = 1024
bytes = None
ready = 'READY'.encode(utf)
ok = 'OK'.encode(utf)
done = 'DONE'.encode(utf)

def errMsg(msg):
	err = 'ERROR: '
	i = msg.find(err) + len(err)
	return msg[i:]

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
		okConf = s.recv(n)
		if okConf != ok:
			errMsg = errMsg(okConf.decode(utf))
			print('server error: %s' % errMsg)
		else:	
			s.send(ready)
			
			nTot = s.recv(n)
			
			nTot = byteArrayToInt(nTot)
			try:
				f = open(filename, "wb")
			except IOError as e:
				print('client error: unable to create file %s' % filename)
			else:
				print('client receiving file %s (%i bytes)' % (filename, nTot))
				s.send(ok)
				fRecv = 0
				while fRecv < nTot: 
					data = s.recv(min((nTot - fRecv), n))
					f.write(data)
					fRecv += len(data)
				doneConf = s.recv(n)
				if doneConf == done:
					print('Complete')
						
#QUESTION: with the other relays of ok, done, ready etc what sort of error handling should be implemented?
			
#______________________________PUT_________________________________#	
	
	elif action == 'PUT':
		request =( action + ' ' + filename).encode(utf)
		s.send(request)
		okConf = s.recv(n)
		
		if okConf != ok:
			errPut = errMsg(okConf.decode(utf))
			print('server error: %s' % errPut)
		else:
			try:
				f = open(filename, 'rb')
			except IOError as e:
				print('unable to create file %s' % filename)
			else: 
				bTot = os.path.getsize(f.name)
				
				s.send(intToByteArray(bTot))	
				
				okConf = s.recv(n)
				if okConf == ok:
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
				
		doneConf = s.recv(n)
		if doneConf == done:
			print('Complete')
		else:
			errMsg = errMsg(doneConf.decode(utf))
			print('server error: %s' % errMsg)
		s.close()
		