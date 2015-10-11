#!/usr/bin/env python
import socket
import MySQLdb
import mibanda
import time
import math
import gcm
#import pyttsx
import mraa
import os
import sys

breakTime=0.0
stopSteps=0
restartSteps=0
breakSteps=0
class Counter:
	count = 0;
c = Counter()
d = Counter()

def func_stop():
	print("stop")
	while 1:
		try:
			stopSteps=device.getSteps()
			break
		except RuntimeError as e:
			if str(e)=="Channel or attrib not ready":
				device=mibanda.BandDevice("88:0f:10:96:b1:4b","MI")
				device.connect()
			continue
	while 1:
		x.isr(mraa.EDGE_BOTH,test,test)
		time.sleep(3)
		tempT=time.time()
		if c.count==2:
			print "start"
			while 1:
				try:
					restartSteps=deivce.getSteps()
					break
				except RuntimeError as e:
					if str(e)=="Channel or attrib not ready":
						device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
						device.connect()
					continue
			breakTime=breakTime+time.time()-tempT
			breakSteps=breakSteps+restartSteps-stopSteps
			break
def compareVelocity1(a,b):
	#if a < b:
	#	engine.say("Hurry up")
	#elif a > b:
	#	engine.say("Run Slow")
	#else:
	#	engine.say("Good, Cheer up")
	#engine.runAndWait()
	print "compare1"
def compareVelocity2(a,b,c):
	#if (a-b) > c:
	#	engine.say("Hurry UP")
	#elif (a+b) < c:
	#	engine.say("Run Slow")
	#else:
	#	engine.say("Good, Cheer Up")
	#engine.runAndWait()
	print "compare2"
def alaramDistance(a):
	#engine.say("%f meters Left"%(a))
	#engine.runAndWait()
	print "alarm"
def test(args):
	c.count += 1
def test2(args):
	d.count += 1

x = mraa.Gpio(4)
x.dir(mraa.DIR_IN)

y = mraa.Gpio(2)
y.dir(mraa.DIR_IN)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5001))
server_socket.listen(10)
print("wating...")
db=MySQLdb.connect('localhost','root','root','kobot')

cursor=db.cursor()
cursor.execute("USE kobot")
sd=mibanda.DiscoveryService()
device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
print (device)
device.connect()
#device.setUserInfo(1563037356, True, 25, 180, 80, 1)
#device.enableRealTimeSteps()

# for soccer mode !!!!!!
start = 0
tmpStep1 = 0
tmpStep2 = 0
maxAvg = 0
minAvg = 0
countKim = 0
btnCommand = 0
Event=""
userName=""
Height=0
print ("connect miband")

#button = os.system('python /home/edison/server/button.py')

while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	checkHaveUserInfo=0
	connectEvent=0
	countLoop=0
	HaveData=0
	buffer=client_socket.recv(5124)
	print buffer
	data2=buffer.split('.')
	Event=data2[0]
	userName=data2[1]
	cursor.execute("select * from userData")
	if Event != "manager-soccer":
		while True:
			r=cursor.fetchone()
			if r==None:
				break
			elif r[0]==userName:
				HaveData=1
				client_socket.send(str(HaveData))	
				checkHaveUserInfo=1
				break
		if checkHaveUserInfo==0:
			client_socket.send("new")
			client_socket.close()
			client_socket, address=server_socket.accept()
			print "not have height"
			tmpHeight = client_socket.recv(256)
			Height = int(tmpHeight)
			#Height=int(client_socket.recv(256))
			print Height
			cursor.execute("insert into userData values(\"%s\")"%(userName))
			cursor.execute("create table %s_Height(Height int(10) not null)"%(userName))
			cursor.execute("create table %s_marathon(sector1 float(6,2) not null, sector2 float(6,2) not null, sector3 float(6,2) not null, sector4 float(6,2) not null, sector5 float(6,2) not null, sector6 float(6,2) not null, sector7 float(6,2) not null, sector8 float(6,2) not null, sector9 float(6,2) not null, sector10 float(6,2) not null)"%(userName))
			cursor.execute("create table %s_record(sector1 float(6,2) not null, sector2 float(6,2) not null, sector3 float(6,2) not null, sector4 float(6,2) not null, sector5 float(6,2) not null,sector6 float(6,2) not null, sector7 float(6,2) not null, sector8 float(6,2) not null, sector9 float(6,2) not null, sector10 float(6,2) not null)"%(userName))
			cursor.execute("create table %s_jogging(day int(11) not null auto_increment primary key, velocity float(6,2))"%(userName))
			cursor.execute("insert into %s_Height values(%d)"%(userName,Height))
			db.commit()
		else:
			client_socket.send("old")
			client_socket.close()
			cursor.execute("select * from %s_Height"%(userName))
			tmp=cursor.fetchall()
			Height=int(''.join(map(str,tmp[0])))
		
	countTime=0
	NowStep=0
	Steps=0
	movement=0.1
	timeFirst=0
	initSteps=0
	TargetRange=0
	TargetTime=0.0
	averageRange=0.0
	t=time.time()

	
	while 1:
		if (Event == "marathon" or Event == "jogging") and connectEvent==0:
			#device.setCurrentSteps(0)
			client_socket, address=server_socket.accept()
			buffer=client_socket.recv(1024)
			data2=buffer.split('.')
			print (data2)
			TargetRange=int(data2[0])
			TargetTime=float(data2[1])#Goal
			averageRange=(Height*0.37 + Height-100)/2/100 #walk range cm->m
			connectEvent=1 
			#engine=pyttsx.init()
			while 1:
				try:
					initSteps=device.getSteps()
					print "init Steps %d"%(initSteps)
					break
				except RuntimeError,e:
					print(e)
					if str(e)=="Channel or attrib not ready":
						device=mibanda.BandDevice("88:0f:10:96:b1:4b","MI")
						device.connet()
					continue
			if Event=="marathon" and checkHaveUserInfo==0: #init marathon value
				Voltage=TargetRange/TargetTime
				strl="INSERT INTO %s_marathon VALUES(%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f)" % (userName,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage)
				cursor.execute(strl)
				db.commit()
			
			t=time.time()
		if Event=="marathon":
			cursor.execute("select * from %s_marathon"%(userName))
			row=cursor.fetchall()
			record=[" "]
			timeFirst=0
			count=1
			sectorCount=0
			v=0
			print(row)
			while True:
 				try:
					NowSteps=device.getSteps()-initSteps
					print ("NowSteps=%d")%(NowSteps)
				except RuntimeError as e:
					print(e)
					if str(e)=="Channel or attrib not ready":
						device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
						device.connect()
						print("connect miband")
					else:
						time.sleep(5)
					print("run error")
					continue
				sector=TargetRange/10
				SectorSteps=NowSteps-Steps
				movement=averageRange*SectorSteps
				time1=time.time()-t
				timeT=time1-timeFirst
				print ("SectorSteps = %d") % (SectorSteps)
				#engine=pyttsx.init()
				if movement>sector:	#in sector
					Steps=NowSteps
					print ("time is %f") %(timeT)
					timeFirst=time1
					v=movement/timeT #sector voltage
					if row[0][sectorCount]>v:
				#		engine.say("Your %d sector pace is slow. Average velocity is %.2f but your velocity is %.2f" %(count,row[0][sectorCount],v))
						print("slow")
					else:
				#		engine.say("your %d sector pace is fast. Average velocity is %.2f, your velocity is %.2f" %(count,row[0][sectorCount],v))
						print("fast")
				#	engine.runAndWait()
					s=`count`
					s="sector"+s
					strl= "UPDATE %s_marathon SET %s = \"%f\"" % (userName,s,v)
					cursor.execute(strl)
					record.append(v)
					count=count+1
					sectorCount=sectorCount+1
					db.commit()
				elif int(time.time()-t)%300==0:#300==0:			#not sector.
				#	engine.say("%d meter left."%(TargetRange-averageRange*nowSteps))
					if row[0][sectorCount]>v:
				#		engine.say("Your pace is slow. Do up your pace")
						print ("slow")
					else:
				#		engine.say("Your oace is fast, Becareful")
						print("fast")
				#	engine.runAndWait()
				if sectorCount==10:
					record.remove(" ")
					print(record)
					strl="INSERT INTO %s_record VALUES(%f,%f,%f,%f,%f,%f,%f,%f,%f,%f)" % (userName,record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],record[9])
					cursor.execute(strl)
					db.commit()
					break
#finish marathon
			averageList=[" "]
			countList=0
			cursor.execute("select * from %s_record"%(userName))
			while True:
				r=cursor.fetchone()
				if r==None:
					break;
				else:
					average=r[0]+r[1]+r[2]+r[3]+r[4]+r[5]+r[6]+r[7]+r[8]+r[9]
					averageList.append(average)
					countList=countList+1
			averageList.remove(" ")
			if countList!=0 or countList!=1:
				sumOfV=0
				for a in range(1,countList-1):
					sumOfV=sumOfVsumOfVaverageList[a]-averageList[a-1]
				if sumOfV>0:
				#	engine.say("upgrading")
					print ("upgrade")
				else :
				#	engine.say("downgrading")
					print ("downgrade")
				if (averageList[countList-1]-averageList[countList-2])>0:
				#	engine.say("better than yesterday")
					print("better than yesterday")
				else:
				#	engine.say("worse than yesterday")
					print("worse than yesterday")
				#engine.runAndWait()

			#break				
		if Event=="jogging":
			#engine = pyttsx.init()
			insertDB=0
			isStart=0
			isOut=0
			x.isr(mraa.EDGE_BOTH,test,test)
			time.sleep(3)
			if c.count==2:
				print "Start button is pressed"
				isStart=1
				startTime=time.time()
			while isStart==1:
				First=0
				cursor.execute("select * from %s_jogging"%(userName))
				while True:
					r=cursor.fetchone()
					if r==None:
						break;
					else:
						First=1
				firstV =  round((TargetRange / TargetTime), 2)
				while 1:
					try:
						NowSteps = device.getSteps()-breakSteps-initSteps
						print NowSteps
						break
					except RuntimeError,e:
						print(e)
						if str(e)=="Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
						continue
				
				dist = averageRange*(NowSteps)
				spendTime = time.time()-startTime-breakTime
				currentV = round((dist/spendTime), 2)
				MoveOfUser=averageRange*NowSteps #movement total
				#left movement == TartgetRange-MoveOfUser
				if First==0:
					if insertDB==0:
						strl="TRUNCATE %s_jogging"%(userName)
						cursor.execute(strl)
						db.commit()
						strl="INSERT INTO %s_jogging(velocity) VALUES(%0.2f)" % (userName,firstV)
 						cursor.execute(strl)
						db.commit()
						strl="INSERT INTO %s_jogging(velocity) VALUES(%0.2f)" % (userName,currentV)
						cursor.execute(strl)
						db.commit()
						insertDB=1
					x.isr(mraa.EDGE_BOTH,test,test)
					time.sleep(3)
					if c.count==1:
						print "Stop button is pressed"
						func_stop()
					elif c.count==4:
						print "End button is pressed"
						isOut=1
						break
					elif d.count==2: 
						compareVelocity(currentV,firstV)
					elif d.count==4:
						alaramDistance(TargetRange-MoveOfUser)
				else:
					strl="SELECT * FROM %s_jogging ORDER BY day"%(userName)
					cursor.execute(strl)
					result=cursor.fetchall()
					total = cursor.rowcount #total=len(result[1])
					strl="SELECT AVG(velocity) FROM %s_jogging"%(userName)
					avg = cursor.execute(strl)
					currentV = round(dist/spendTime, 2)
					sum = 0									
					stdDeviation = 0	
		
					dayVelocity = {}
		
					if total < 1:
						print ("No daliy velocity entries!")
					else:
						for i in range(total):
							dayVelocity[i] = result[i][1] #velocity	
							sum += pow(abs(avg-dayVelocity[i]), 2)
							stdDeviation = round(math.sqrt(sum/total), 2)
					x.isr(mraa.EDGE_BOTH,test,test)
					time.sleep(3)
					if c.count==1:
						fuc_stop()
					elif c.count==4:
						isOut=1
						break
					elif d.count==2: 
						compareVelocity2(avg,stdDeviation,currentV)
					elif d.count==4:
						alaramDistance(TargetRange-MoveOfUser)
				if TargetRange <= MoveOfUser or isOut==1:
					spendTime=time.time()-startTime-breakTime
					todayV=MoveOfUser/spendTime		
					strl="INSERT INTO %s_jogging(velocity) VALUES(%0.2f)"%(userName,todayV)
					cursor.execute(strl)
					db.commit()
					print "jogging finish"
					break
#			break	#finish jogging
		
		if Event == "player-soccer":
			print "player-soccer mode call"
			# Use soccer DB
			db2 = MySQLdb.connect('localhost', 'root', 'root', 'soccer')
			cursor2 = db2.cursor()
			cursor2.execute("USE soccer")

			#if countKim == 0:
			#	client_socket, address=server_socket.accept()
			#	data2 = client_socket.recv(1024)
			#	print data2
			#	tmpData2 = data2.split('.')
			#	goal = tmpData2[0]
			#	height = tmpData2[1]
			#	time = tmpData2[2]
			#	countKim+=1
			#while True:
			#	x.isr(mraa.EDGE_BOTH,test,test)
			#	y.isr(mraa.EDGE_BOTH,test2,test2)
			#	time.sleep(3)
			#	if c.count == 2:
			#		break
			#	elif c.count == 4:
			#		break
			#if c.count == 2:
			#	btnCommand = 'start'
			#	c.count = 0
			#elif c.count == 4:
			#	btnCommand = 'end'
			#	c.count = 0
			#client_socket, address=server_socket.accept()
			#data3 = client_socket.recv(1024)
			#tmpData3 = data3.split('.')
			#btnCommand = tmpData3[0]
			client_socket, address=server_socket.accept()
			mode = client_socket.recv(5000)
			#client_socket.close()
			print "Mode is : ", mode
			while True:
				x.isr(mraa.EDGE_BOTH,test,test)
				#y.isr(mraa.EDGE_BOTH,test2,test2)
				time.sleep(3)
				if c.count == 2:
					btnCommand = 'start'
					c.count = 0
				elif c.count == 4:
					btnCommand = 'end'
					c.count = 0
				#client_socket, address=server_socket.accept()
				#data6 = client_socket.recv(1024)
				#print data6
				#tmpData6 = data6.split('.')
				#btnCommand2 = tmpData7[0]
				if start == 0 and btnCommand == 'start': # if player press start button
					print "Start button is pressed"
					start = 1
					while 1:
						try:
							tmpStep1 = device.getSteps() # get initial steps
							break
						except RuntimeError,e:
							if str(e)=="Channel or attrib not ready":
								device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
								device.connect()
								print "re connect"
							print(e)
							continue
					print "Get Steps from MiBand : ", tmpStep1
				elif mode == 'Real' and start == 1 and btnCommand == 'start':
					forSaveTmpStep = 0
					print "Save Player's moving data to DB"
					while 1:
						try:
							forSaveTmpStep = device.getSteps()
							break
						except RuntimeError,e:
							if str(e)=="Channel or attrib not ready":
								device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
								device.connect()
								print "reconnect"
							print(e)
							continue
					#print "Get Steps from MiBand for Save : ", forSaveTmpStep
					forSaveSteps = forSaveTmpStep-tmpStep1
					forSaveMove = ((Height-100)*forSaveSteps)/100
					print "For save moving data : ", forSaveMove
					# Renew DB
					delingStr = "delete from value3"
					cursor2.execute(delingStr)
					db2.commit()
					insertingStr = "INSERT INTO value3 VALUES (%d)" % (forSaveMove)	
					cursor2.execute(insertingStr)
					db2.commit()				
				elif btnCommand == 'end': # if player press ending button
					print "End button is pressed"
					while 1:
						try:
							tmpStep2 = device.getSteps()
							break;
						except RuntimeError,e: 
							if str(e)=="Channel or attrib not ready":
								device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
								device.connect()
								print "re connect"
							print(e)
							continue
					print "Get second Steps from MiBand : ", tmpStep2
					totalSteps = tmpStep2 - tmpStep1
					print "Total Steps : ", totalSteps
					move = ((Height-100)*totalSteps)/100 # player's moving distance
					print "Move : ", move
					# save move data to soccer DB
					#db2 = MySQLdb.connect ('localhost', 'root', 'root', 'kim')
					#cursor2 = db2.cursor()
					#cursor2.execute("USE kim")
		
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
						insertMoveStr = "INSERT INTO value1 VALUES (%d)" % (move)
						cursor2.execute(insertMoveStr)
						db2.commit()
					else: # not initial case
						avgStr = "select * from value2"
						cursor2.execute(avgStr)
						tmpAvg = cursor2.fetchall()
						maxAvg = tmpAvg[0][0]
						minAvg = tmpAvg[1][0]
						# calculates player's max, min conditions and compare recent moving data
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
					# renew val2's max, min avg
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
					if val1Count == 4: # if table full
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
					start = 0
					countKim = 0
					btnCommand = 0
					break
			break
		#if Event == "Manager-soccer":
		#	manTmpStep = -1
		#	print "Manager-soccer mode call"
		#	try:
		#		manTmpStep = device.getSteps()
		#	except RuntimeError,e:
		#		if str(e) == "Channel or attrib not ready":
		#			device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
		#			device.connect()
		#			print ("re connect")
		#	forSend = manTmpStep-tmpStep1
		#	forSendMove = ((172-100)*forSend)/100
			########## height later modify !! ###########
		#	if forSendMove < minAvg:
		#		print "Player's status may be normal."
		#		server_socket.send('Normal')
		#	elif minAvg <= forSendMove and forSendMove < maxAvg:
		#		print "Player's status may be warning."
		#		server_socket.send('Warning')
		#	elif maxAvg <= forSendMove:
		#		print "Player's status may be danger."
		#		server_socket.send('Danger') 
	break
db.close()
server_socket.close()
print("close")
