import socket
import MySQLdb
import mibanda
import time
import os
import sys
from socket import *

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
reqSocket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", 5002)) # manager port
server_socket.listen(5)
print("wating...")
db=MySQLdb.connect('localhost','root','root','kim')
#connect database schema
cursor=db.cursor()
cursor.execute("USE kim")

start = 0
maxAvg = 0
minAvg = 0
data = -1

host = '192.168.0.65'
port = 5001 # player source code's port
reqAddr = (host, port)
reqSocket.connect(reqAddr)

#connect edison-android
while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
			
	if start == 0: # for retrieve max, min avg value in first time
		retStr = "select * from value2"
		cursor.execute(retStr)
		tmpVal = cursor.fetchall()
		maxAvg = tmpVal[0][0]
		minAvg = tmpVal[1][0]
		print "Retrieved max, min value is : ", maxAvg, " ", minAvg
		start = 1
	else:
		# request player's move value every 10 seconds	
		reqSocket.send("dataReq.")
		while data == -1:
			data = reqSocket.recv(1024)
			print "Waiting for player's moving data from miband"
		print "Player's moving data is received : ", data
		print "Modify and Sending to Android"
		# compare, and sending to android
		if minAvg <= data and data < maxAvg:
			print "Player's status may be warning."
			server_socket.send('warning')
		elif maxAvg <= data:
			print "player's status may be danger."
			server_socket.send('danger')
		time.sleep(10)
		
server_socket.close()
print("close")
