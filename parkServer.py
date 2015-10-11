import socket
import MySQLdb
import mibanda
import time
import math
import gcm
#
#import pyttsx
import mraa
import os
import sys

breakTime=0.0

class Counter:
	count = 0;
c = Counter()
d = Counter()

def func_stop():
	while 1:
		tempT=time.time()
		if(start):
			breakTime+=time.time()-tempT
			break

def test(args):
	c.count += 1
def test2(args):
	d.count += 1

x = mraa.Gpio(7)
x.dir(mraa.DIR_IN)

y = mraa.Gpio(4)
y.dir(mraa.DIR_IN)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5001))
server_socket.listen(5)
print("wating...")
db=MySQLdb.connect('localhost','root','root','kobot')

cursor=db.cursor()
cursor.execute("USE kobot")
sd=mibanda.DiscoveryService()
device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
print (device)
device.connect()
device.setUserInfo(1563037356, True, 25, 180, 80, 1)
device.enableRealTimeSteps()
#gcm=GCM("need :api key")
#reg_id='need : regid'

# for soccer mode !!!!!!
start = 0
tmpStep1 = 0
tmpStep2 = 0
maxAvg = 0
minAvg = 0
countKim = 0
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
	buffer=client_socket.recv(1024)
	print buffer
	data2=buffer.split('.')
	Event=data2[0]
	userName=data2[1]
	#Height=data2[2]
	cursor.execute("select * from userData")
	#while True:
	#	r=cursor.fetchone()
	#	if r==None:
	#		break
	#	elif r[0]==userName:
	#		HaveData=1
	#		client_socket.send(str(HaveData))	
	#		checkHaveUserInfo=1
	#		break
	#if checkHaveUserInfo==0:
	#	client_socket.send(str(HaveData))
	#	Height=int(client_socket.recv(256))
	#	print Height
	#	cursor.execute("insert into userData values(\"%s\")"%(userName))
	#	cursor.execute("create table %s_Height(Height int(10) not null)"%(userName))
	#	cursor.execute("create table %s_marathon(sector1 float(6,2) not null, sector2 float(6,2) not null, sector3 float(6,2) not null, sector4 float(6,2) not null, sector5 float(6,2) not null, sector6 float(6,2) not null, sector7 float(6,2) not null, sector8 float(6,2) not null, sector9 float(6,2) not null, sector10 float(6,2) not null)"%(userName))
	#	cursor.execute("create table %s_record(sector1 float(6,2) not null, sector2 float(6,2) not null, sector3 float(6,2) not null, sector4 float(6,2) not null, sector5 float(6,2) not null,sector6 float(6,2) not null, sector7 float(6,2) not null, sector8 float(6,2) not null, sector9 float(6,2) not null, sector10 float(6,2) not null)"%(userName))
	#	cursor.execute("create table %s_jogging(day int(11) not null auto_increment primary key, velocity float(6,2))"%(userName))
	#	cursor.execute("insert into %s_Height values(%d)"%(userName,Height))
	#	db.commit()
	#else:
	#	cursor.execute("select * from %s_Height"%(userName))
	#	tmp=cursor.fetchall()
	#	Height=int(''.join(map(str,tmp[0])))
		
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
	#device.setCurrentSteps(0)
	#print("setCurrnetSteps=0")
	
	while 1:
		if Event == ("marathon" or Event == "Jogging") and connectEvent==0:
			device.setCurrentSteps(0)
			buffer=client_socket.recv(1024)
			data2=buffer.split('.')
			print (data2)
			TargetRange=int(data2[0])
			TargetTime=float(data2[1])#Goal
			averageRange=(Height*0.37 + Height-100)/2/100 #walk range cm->m
			connectEvent=1 
			if Event=="marathon" and checkHaveUserInfo==0: #init marathon values
				tempL=0
				while tempL==0:
					try:
						initSteps=device.getSteps()
						tmepL=1
						t=time.time()
					except RuntimeError as e:
						if str(e)=="Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
							tempL=0
						continue
				Voltage=TargetRange/TargetTime
				strl="INSERT INTO %s_marathon VALUES(%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f)" % (userName,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage)
				cursor.execute(strl)
				db.commit()
		if Event=="marathon":
			#print("testSteps=%d")%(device.getSteps())
			cursor.execute("select * from %s_marathon"%(userName))
			row=cursor.fetchall()
			record=[" "]
			timeFirst=0
			count=1
			sectorCount=0
			v=0
			print(row)
			while True:
			#	time.sleep(10)
				sector=TargetRange/10
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
						time.sleep(10)
					#	device=None
					#	device=mibanda.BandDevice("88:0f:10:96:b1:4b","MI")
					#	device.connect()
					print("run error")
					continue
				
				SectorSteps=100#NowSteps-Steps
				movement=averageRange*SectorSteps
				time1=time.time()-t
				timeT=time1-timeFirst
				print ("SectorSteps = %d") % (SectorSteps)
				if movement>sector:	#in sector
					Steps=NowSteps
					print ("time is %f") %(timeT)
					timeFirst=time1
					v=movement/timeT #sector voltage
					if row[0][sectorCount]>v:
						#data={'key1':"Your %d sector pace is slow"%(count), 'key2':"average voltage is %.2f but your volatage is %.2f"%(row[0][sectorCount],v} #dictionary
						#gcm.plainttext_request(registration_id=reg_id, data=data}
						engine.say("Your %d sector pace is slow. Average velocity is %.2f but your velocity is %.2f" %(count,row[0][sectorCount],v))
						print("slow")
					else:
						#data={'key1':"Your %d sector pace is fast"%(count), 'key2':"average voltage is %.2f, your voltage is %.2f"%(row[0][sectorCount],v)}
						#gcm.plainttext_request(registration_id=reg_id, data=data}
						engine.say("your %d sector pace is fast. Average velocity is %.2f, your velocity is %.2f" %(count,row[0][sectorCount],v))
						print("fast")
					engine.runAndWait()
					s=`count`
					s="sector"+s
					strl= "UPDATE %s_marathon SET %s = \"%f\"" % (userName,s,v)
					cursor.execute(strl)
					record.append(v)
					count=count+1
					sectorCount=sectorCount+1
					db.commit()
				elif (time.time()-t)/60>sectorCount:#300==0:			#not sector.
					engine.say("%d meter left."%(TargetRange-averageRange*nowSteps))
					if row[0][sectorCount]>v:
						#data={'key1':'Your pace is slow', 'key2':'Do up your pace'}
						#gcm.plainttext_request(registration_id=reg_id, data=data)
						engine.say("Your pace is slow. Do up your pace")
						print ("slow")
					else:
						#data={'key1':'Yout pace is fast', 'key2':'Becareful!'}
						#gcm.plainttext_request(registration_id=reg_id, data=data)
						engine.say("Your oace is fast, Becareful")
						print("fast")
					engine.runAndWait()
				if sectorCount==10:
					record.remove(" ")
					print(record)
					strl="INSERT INTO %s_record VALUES(%f,%f,%f,%f,%f,%f,%f,%f,%f,%f)" % (userName,record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],record[9])
					cursor.execute(strl)
					db.commit()
					break

				#time.sleep(10)	
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
	#cursor.execute("DELETE FROM record")
				#i think this part do graph
				if (averageList[countList-1]-averageList[0])/countList>0:
					#data={'key1':'increasing your face','key2':'good'}
					#gcm.plainttext_request(registration_id=reg_id, data=data)
					print("up ! goodboy")
				else:
					#data={'key1':'decreasing you face','key2':'bad'}
					#gcm.plainttext_request(registration_id=reg_id, data=data)
					print("badboy! down")
				if (averageList[countList-1]-averageList[countList-2])>0:
					#data={'key1':'faster than yesterday','key2':'excellent'}
					#gcm.plainttext_request(registration_id=reg_id, data=data)
					print("yesterday better")
				else:
					#data={'key1':'slower than yesterday','key2':'not good'}
					#gcm.plainttext_request(registration_id=reg_id, data=data)
					print("yesterday notgoods")

			break				
		if Event=="JOGGING":
			engine = pyttsx.init()
			insertDB=0
			#print (device.getSteps())
			#cursor.execute("select * from jogging")
			startTime=time.time()
			while 1:
				First=0
				cursor.execute("select * from %s_jogging"%(userName))
				while True:
					r=cursor.fetchone()
					if r==None:
						break;
					else:
						First=1
				firstV =  round((TargetRange / TargetTime), 2)
				x.isr(mraa.EDGE_BOTH,test,test)
				time.sleep(3)
				if c.count == 2:
					parkStart = 1
				if parkStart == 1:
					try:
						NowSteps = device.getSteps()
						print NowSteps
					except RuntimeError,e:
						print(e)
						if str(e)=="Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
						continue
				#print "Next FDSsfdsfsdfsdfsdfsdfsfdsfsfdsfsf"
				steps = 0
				dist = averageRange*(NowSteps - steps)
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
					if currentV < firstV:
					#print ("Hurry Up")
						engine.say('Hurry Up')
					elif currentV > firstV:
						#print ("Run Slow")
						engine.say('Run Slow')
					else:
						#print("Good, cheer up!!")
						engine.say('Good, cheer up!!')
					engine.runAndWait()
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
						#tmp = avg-stdDeviation
						if (avg-stdDeviation) > currentV:							
							#print("Hurry Up")
							engine.say('Hurry Up')
						elif (avg+stdDeviation) < currentV:
						#print("Run Slow")
							engine.say('Run Slow')
						else:
						#print("Good, cheer up!!")
							engine.say('Good, cheer up!!')
						engine.runAndWait()
					
				if TargetRange <= MoveOfUser:
					spendTime=time.time()-startTime-breakTime
					todayV=MoveOfUser/spendTime		
					strl=“INSERT INTO %s_jogging(velocity) VALUES(%0.2f)"%(userName,todayV)
					cursor.execute(strl)
					db.commit()
					break
			break	#finish jogging
		
		if Event == "Soccer":
			print "Soccer mode call"
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
			PY = 0
			MN = 0
			btnCommand = 0
			while True:
				if PY == 0:
					client_socket, address=server_socket.accept()
					data5 = client_socket.recv(1024)
					print data5
					tmpData5 = data5.split('.')
					btnCommand = tmpData5[0]
				if start == 0 and btnCommand == 'Player':
					PY = 1
					print "Player mode call"
					x.isr(mraa.EDGE_BOTH,test,test)
					y.isr(mraa.EDGE_BOTH,test2,test2)
					time.sleep(3)
					if c.count == 2:
						btnCommand2 = 'start'
					elif c.count == 4:
						btnCommand2 = 'end'
					#client_socket, address=server_socket.accept()
					#data6 = client_socket.recv(1024)
					#print data6
					#tmpData6 = data6.split('.')
					#btnCommand2 = tmpData7[0]
					if start == 0 and btnCommand2 == 'start': # if player press start button
						print "Start button is pressed"
						start = 1
						try:
							tmpStep1 = device.getSteps() # get initial steps
						except RuntimeError,e:
							if str(e)=="Channel or attrib not ready":
								device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
								device.connect()
								print "re connect"
						print "Get Steps from MiBand : ", tmpStep1
						continue
					elif btnCommand2 == 'end': # if player press ending button
						print "End button is pressed"
						try:
							tmpStep2 = device.getSteps()
						except RuntimeError,e: 
							if str(e)=="Channel or attrib not ready":
								device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
								device.connect()
								print "re connect"
						print "Get second Steps from MiBand : ", tmpStep2
						totalSteps = tmpStep2 - tmpStep1
						print "Total Steps : ", totalSteps
						move = ((172-100)*totalSteps)/100 # player's moving distance
						#### height extract from DB ################
						print "Move : ", move
						# save move data to soccer DB
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
						break
				if Event == "Manager-soccer":
					manTmpStep = -1
					print "Manager-soccer mode call"
					try:
						manTmpStep = device.getSteps()
					except RuntimeError,e:
						if str(e) == "Channel or attrib not ready":
							device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
							device.connect()
							print ("re connect")
					forSend = manTmpStep-tmpStep1
					forSendMove = ((172-100)*forSend)/100
					########## height later modify !! ###########
					if forSendMove < minAvg:
						print "Player's status may be normal."
						server_socket.send('Normal')
					elif minAvg <= forSendMove and forSendMove < maxAvg:
						print "Player's status may be warning."
						server_socket.send('Warning')
					elif maxAvg <= forSendMove:
						print "Player's status may be danger."
						server_socket.send('Danger') 
	break
db.close()
server_socket.close()
print("close")
