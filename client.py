# TCP client example
import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.0.65", 5006))
data = "JOGGING.kim.100.Men.12.170.168.60.0"
client_socket.send(data)
client_socket.close()
print ("socket colsed... END.")
