from socket import *
import sys
import re

if len(sys.argv) <= 1:
        print 'Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server'
        sys.exit(2)

tcpSerPort = 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

tcpSerSock.bind(("",tcpSerPort)) #listening port 
tcpSerSock.listen(1)

while 1:
        
        print 'Ready to serve...'
        tcpCliSock, addr = tcpSerSock.accept()
        print 'Received a connection from:', addr
        message = tcpCliSock.recv(1024) # added code
        print message
        
        print message.split()[1]
        requestType = message.split()[0]
        filename = message.split()[1].partition("/")[2]
        print filename
        fileExist = "false"
        filetouse = "/" + filename
        print filetouse

        try: # Check whether the file exist in the cache
                f = open(filetouse[1:], "r")
                outputdata = f.readlines()
                fileExist = "true"
                # ProxyServer finds a cache hit and generates a response message
                tcpCliSock.send("HTTP/1.0 200 OK\r\n")
                tcpCliSock.send("Content-Type:text/html\r\n")
                
                for data in outputdata:
                        tcpCliSock.send(data)
                
                print 'Read from cache'
                continue
        # Error handling for file not found in cache
        except IOError:
           # if fileExist == "false":
                print "Cache file does not exist"
        # Create a socket on the proxyserver
        
        c = socket(AF_INET, SOCK_STREAM)
        
        hostn = filename.replace("www.","",1).partition("/")[0]
        print 'going to connect to: ', hostn
        try:
            # Connect to the socket to port 80
            
            c.connect((hostn,80))
            
            # Create a temporary file on this socket and ask port 80
            #for the file requested by the client
            fileobj = c.makefile('r', 0)
            subfile = filename.partition("/")[2]
            if requestType == 'GET':
                fileobj.write("GET "+"http://" + hostn + "/" + subfile + " HTTP/1.0\n\n")
            else:
                fileobj.write("POST "+"http://" + filename + " HTTP/1.0\n\n")
                msg_body = re.split("\r\n",message, maxsplit=1)[1]
                fileobj.write(msg_body)
            # Read the response into buffer
            
            tmpBuffer = fileobj.readlines()
            
            # Create a new file in the cache for the requested file.
            # Also send the response in the buffer to client socket
            # and the corresponding file in the cache
            tmpFile = open("./" + filename,"wb")
            # 
            for data in tmpBuffer:
                    tmpFile.write(data)
                    tcpCliSock.send(data)
            tmpFile.close()
        
        except IOError as e:
            print ""
        # HTTP response message for file not found
        
        try:    
            print 'Server Response:',tmpBuffer[0].split("\n", 1)[0]
            tmpBuffer = ""
        except Exception as e:
            print " "
            
            # Close the client and the server sockets
        tcpCliSock.close()
        
        c.close()
        
