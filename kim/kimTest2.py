import socket
import MySQLdb
import mibanda
import time
import os
import sys

#buttonSrc = os.system('python /home/edison/switch.py')

#if not buttonSrc == 0:
#	print >> sys.stderr, 'error occured : ', buttonSrc

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5000))
server_socket.listen(5)
print("wating...")
db=MySQLdb.connect('localhost','root','root','kim')
#connect database schema
cursor=db.cursor()
cursor.execute("USE kim")

#connect miband using bluetooth
#sd=mibanda.DiscoveryService()

#device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
#device.connect()
#print ("connect miband")

#connect edison-android
while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	connectEvent=0
	countLoop=0
	data=client_socket.recv(1024)
	countTime=0
	print(data)
	
	while 1:
		if connectEvent==0:
			data2=data.split('.')
			Event = data2[0]
			UserName=data2[1]
			TargetRange=int(data2[2])
			Gender=data2[3]
			Age=int(data2[4])
			Height=int(data2[5])
			Weight=int(data2[6])
			TargetTime=int(data2[7])#Goal
			#First=int(data2[8])#first run or second,third....
			averageRange=(Height*0.37 + Height-100)/2 #walk range
			connectEvent=1 
			
			if Event=="Player-soccer": # if edison received Plater-soccer signal from android
				print "Player-soccer mode Call"
				soccerPlayer = os.system('python /home/edison/kimTest.py') # show that mode
			elif Event=="Manager-soccer":
				print "Manager-soccer mode Call"
				soccerManager = os.system('python /home/edison/manager.py')
print("close")
