import socket
import MySQLdb
import mibanda
import time
import os
import sys
from socket import *

#buttonSrc = os.system('python /home/edison/switch.py')

#if not buttonSrc == 0:
#	print >> sys.stderr, 'error occured : ', buttonSrc

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5001))
server_socket.listen(5)
print("wating...")

manageSocket = socket(AF_INET, SOCK_STREAM)
host = '192.168.0.65'
port = 5002 # manager port
manageAddr = (host, port)

db=MySQLdb.connect('localhost','root','root','kim')
#connect database schema
cursor=db.cursor()
cursor.execute("USE kim")

#connect miband using bluetooth
sd=mibanda.DiscoveryService()

device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
device.connect()
print ("connect miband")

start = 0
tmpStep1 = 0
tmpStep2 = 0

#connect edison-android
while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	data=client_socket.recv(1024)
	print(data)
	data2=data.split('.')
	btnCommand = data2[0]
			
	if start == 0 and btnCommand == 'start': #if player press start button
		print "Start button is pressed"
		start = 1
		tmpStep1 = device.getSteps()
		print "Get Steps from MiBand : ", tmpStep1
	elif btnCommand == 'end': # if player press ending button
		print "End button is pressed"

		tmpStep2 = device.getSteps()
		print "Get second Steps from Miband : ", tmpStep2
		totalSteps = tmpStep2 - tmpStep1
		print "Total Step : ", totalSteps
		move = ((Height-100)*totalSteps)/100 # player's moving distance
		print "Move : ", move
		# save move data to kim DB
		db2 = MySQLdb.connect ('localhost', 'root', 'root', 'kim')
		cursor2 = db2.cursor()
		cursor2.execute("USE kim")

		countStr = "select Count(move) from value1"
		cursor2.execute(countStr)
		val1CountTmp = cursor2.fetchone()
		val1Count = int(''.join(map(str,val1CountTmp))) 
		# calculate player's table size
		# first, compare max, min <-> move data
		avgCountStr = "select Count(avg) from value2" # calculate value2's size
		cursor2.execute(avgCountStr)
		avgCountTmp = cursor2.fetchone()
		avgCount = int(''.join(map(str,avgCountTmp)))

		if avgCount == 0: # if no data in value2's avg columm / initial case
			insertMaxAvgStr = "INSERT INTO value2 VALUES (%d)" % (move)
			cursor2.execute(insertMaxAvgStr)
			db2.commit()
			insertMinAvgStr = "INSERT INTO value2 VALUES (%d)" % (move)
			cursor2.execute(insertMinAvgStr)
			db2.commit()
			insertMoveStr = "INSERT INTO (value1) VALUES (%d)" % (move)
			cursor2.execute(insertMoveStr)
			db2.commit()
		else: # not initial case
			avgStr = "select * from value2"
			cursor2.execute(avgStr)
			tmpAvg = cursor2.fetchall()
			maxAvg = tmpAvg[0][0]
			minAvg = tmpAvg[1][0]
			# calculate player's max, min conditions and compare recent move data
			if move > maxAvg:
				maxAvg = (move+maxAvg)/2
			elif move < minAvg:
				minAvg = (move+minAvg)/2
			else:
				tmpMaxMove = maxAvg-move
				tmpMinMove = move-minAvg
				if tmpMaxMove > tmpMinMove:
					minAvg = (move+minAvg)/2
				elif tmpMaxMove < tmpMinMove:
					maxAvg = (move+maxAvg)/2
		# renew val2's max,min avg
		delVal2Str = "delete from value2"
		cursor2.execute(delVal2Str)
		db2.commit()
		insertMaxAvgStr = "INSERT INTO value2 VALUES (%d)" % (maxAvg)
		cursor2.execute(insertMaxAvgStr)
		db2.commit()
		insertMinAvgStr = "INSERT INTO value2 VALUES (%d)" % (minAvg)
		cursor2.execute(insertMinAvgStr)
		db2.commit()
		# insert now move value to val1 table
		if val1Count == 4:
			delVal1Str = "delete from value1"
			cursor2.execute(delVal1Str)
			db2.commit()
			insertMoveStr = "INSERT INTO value1 VALUES (%d)" % (move)
			cursor2.execute(insertMoveStr)
			db2.commit()
		else:
			insertMoveStr = "INSERT INTO value1 VALUES (%d)" % (move)
			cursor2.execute(insertMoveStr)
			db2.commit()
		break
	elif btnCommand == 'dataReq': # if it is received manager request message
		manageSocket.connect(manageAddr) # connect to manager socket
		forSendTmp = device.getSteps()
		forSend = forSendTmp-tmpStep1
		manageSocket.send(forSend) # send player's moving data
		manageSocket.close() # close socket
db.close()
server_socket.close()
print("close")
