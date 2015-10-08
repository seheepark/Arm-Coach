import socket
import MySQLdb
import mibanda
import mraa
import time
import os
import sys
from socket import *

#buttonSrc = os.system('python /home/edison/switch.py')

#if not buttonSrc == 0:
#	print >> sys.stderr, 'error occured : ', buttonSrc


class Counter:
	count = 0;
c = Counter()
d = Counter()

def test(args):
	c.count +=1
def test2(args):
	d.count+=1

x = mraa.Gpio(2)
x.dir(mraa.DIR_IN)

y = mraa.Gpio(4)
y.dir(mraa.DIR_IN)

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", 5001))
server_socket.listen(5)
print("wating...")

#host = '192.168.0.65'
#port = 5002 # manager port
#manageSocket = socket(AF_INET, SOCK_STREAM)
#manageAddr = (host, port)
#manageSocket.connect(manageAddr)

db=MySQLdb.connect('localhost','root','root','kim')
#connect database schema
cursor=db.cursor()
cursor.execute("USE kim")

#connect miband using bluetooth
#sd=mibanda.DiscoveryService()
#device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
#device.connect()
#print ("connect miband")

start = 0
tmpStep1 = 0
tmpStep2 = 0
maxAvg = 0
minAvg = 0
count = 0

#connect edison-android
while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	data = client_socket.recv(1024)
	print(data)
	tmpData1 = data.split('.')
	exercise = tmpData1[0]
	name = tmpData1[1]
	while 1:
		if exercise == "Player-soccer":
			print "Player-soccer mode call"
			if count == 0:
				client_socket, address=server_socket.accept()
				data2 = client_socket.recv(1024)
				print data2
				tmpData2 = data2.split('.')
				goal = tmpData2[0]
				height = tmpData2[1]
				time = tmpData2[2]
				count+=1

			client_socket, address=server_socket.accept()
			data3 = client_socket.recv(1024)
			tmpData3 = data3.split('.')
			btnCommand = tmpData3[0]		
			while True:
				x.isr(mraa.EDGE_BOTH,test,test)
				y.isr(mraa.EDGE_BOTH,test2,test2)

				if start == 0 and c.count==4: #if player press start button
					c.count=0
					sd = mibanda.DiscoveryService()
					device = mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
					device.connect()
					print ("connect miband")
	
					print "Start button is pressed"
					start = 1
					try:
						tmpStep1 = device.getSteps()
					except RuntimeError,e:
						if str(e)=="Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
							print ("re connect")
					print "Get Steps from MiBand : ", tmpStep1
					continue
				elif c.count==2: # if player press ending button
					c.count=0
					print "End button is pressed"
					try:
						tmpStep2 = device.getSteps()
					except RuntimeError,e:
						if str(e)=="Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
							print ("re connect")
					print "Get second Steps from Miband : ", tmpStep2
					totalSteps = tmpStep2 - tmpStep1
					print "Total Step : ", totalSteps
					move = ((172-100)*totalSteps)/100 # player's moving distance
					# height extract from DB - oh dae kyung
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
				time.sleep(10)

		elif exercise == 'Manager-soccer': # if it is received manager request message
			forSendTmp = -1
		
			print "Datareq data received"
			host = '192.168.0.65'
			port = 5002
			manageAddr = (host, port)
			manageSocket = socket(AF_INET, SOCK_STREAM)
			manageSocket.connect(manageAddr) # connect to manager socket
			try:
				forSendTmp = device.getSteps()
			except RuntimeError,e:
				if str(e) == "Channel or attrib not ready":
					device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
					device.connect()
					print ("re connect")
			print "Retrieve Steps for sending to Manager : ", forSendTmp
			forSend = forSendTmp-tmpStep1
			forSendMove = ((172-100)*forSend)/100
			# height. later modify!!!
			print "For sending total Move : ", forSendMove
			manageSocket.send('%d' % (forSendMove)) # send player's moving data
			print "Sending steps to manager successfully."
			manageSocket.close() # close socket
			break
db.close()
server_socket.close()
print("close")
