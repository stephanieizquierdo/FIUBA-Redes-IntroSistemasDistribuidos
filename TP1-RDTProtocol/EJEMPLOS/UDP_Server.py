from socket import *
#Defino Port
serverPort = 12000
#Defino IP4v y UDP
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")
while True:
  message, clientAddress = serverSocket.recvfrom(2048)
  # Tomo Client Address, vean que Port imprime:
  print ("Client Address: ", clientAddress)
  modifiedMessage = message.decode().upper()
  serverSocket.sendto(modifiedMessage.encode(), clientAddress)
  print ("Message sent")

