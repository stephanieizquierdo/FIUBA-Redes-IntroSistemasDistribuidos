from socket import *
serverName = '10.71.103.223'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = ' '
while message != 'FIN' :
 message = input("Input lowercase sentence:")
 clientSocket.sendto(message.encode(),(serverName, serverPort))
 modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
 print(modifiedMessage.decode())
clientSocket.close()


