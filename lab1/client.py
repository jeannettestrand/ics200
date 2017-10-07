import socket
import sys

utf = 'UTF-8'
buff = 1024
sTag = '<HTML'

eTag = '</HTML>'

input = sys.argv[1].split('/')
webHost = input[2]
if len(input) == 3:
	resource = '/'
else:
	i = 3
	resource = ''
	while i < len(input):
		resource += '/' + input[i]
		i += 1
#python client.py http://rtvm.cs.camosun.bc.ca/ics200/lab1test1.html
request = 'GET ' + resource + ' HTTP/1.1\nhost: ' + webHost + '\r\n\r\n'	
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect((webHost, 80))
recvd = s1.send(request.encode(utf))	

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('rtvm.cs.camosun.bc.ca', 10010))
conf = s2.recv(buff)


state = 1
while state != 4:
	if state == 1:
		b = ''
		while sTag not in (b.upper()):
			b = s1.recv(buff).decode(utf)
		if eTag in b1:
			s = s2.send(b1[:(b1.find(eTag) + len(eTag))].encode(utf))
			state = 3
		else:
			b1 = b[(b.find(sTag)):] 	
			state = 2
		
	if state == 2:			
		b2 = s1.recv(buff).decode(utf)

		while eTag not in (b1 + b2).upper():
			s = s2.send(b1.encode(utf))
			b1 = b2
			b2 = s1.recv(buff).decode(utf)
		s = s2.send((b1 + b2)[:((b1 + b2).find(eTag) + len(eTag))].encode(utf))
		
		state = 3
		
	if state == 3:
		comp = 'ICS 200 HTML CONVERT COMPLETE'
		
		b1 = s2.recv(buff).decode(utf)
		b2 = s2.recv(buff).decode(utf)

		while comp not in (b1 + b2).upper():
			print(b1, end='')
			b1 = b2
			b2 = s2.recv(buff).decode(utf)

		print((b1+b2)[:((b1 + b2).find(comp))])

		state = 4
		
s1.close()
s2.close()







