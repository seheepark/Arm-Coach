import socket
import MySQLdb
import mibanda
import time
import math
import pyttsx

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5006))
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
print ("connect miband")

while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	connectEvent=0
	countLoop=0
	buffer=client_socket.recv(1024)
	countTime=0
	NowStep=0
	Steps=0
	movement=0.1
	timeFirst=0
	device.setCurrentSteps(0)
#	time.sleep(10)
	print("setCurrnetSteps=0")
	#time.sleep(10)
	while 1:
		if connectEvent==0:
			#device.setCurrentSteps(0)
			data2=buffer.split('.')
			print (data2)
			Event=data2[0]
			UserName=data2[1]
			TargetRange=int(data2[2])
			Gender=data2[3]
			Age=int(data2[4])
			Height=int(data2[5])
			Weight=int(data2[6])#Goal
			TargetTime=float(data2[7])#Goal
			First=int(data2[8])#first run or second,third....
			averageRange=(Height*0.37 + Height-100)/2/100 #walk range cm->m
			connectEvent=1 
			t=time.time()
			if Event=="marathon" and First==0: #init marathon values
				Voltage=TargetRange/TargetTime
				strl="INSERT INTO marathon VALUES(%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f)" % (Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage,Voltage)
				cursor.execute(strl)
				db.commit()
		if Event=="marathon":
			#print("testSteps=%d")%(device.getSteps())
			cursor.execute("select * from marathon")
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
					NowSteps=device.getSteps()
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
					strl= "UPDATE marathon SET %s = \"%f\"" % (s,v)
					cursor.execute(strl)
					record.append(v)
					count=count+1
					sectorCount=sectorCount+1
					db.commit()
				elif (time.time()-t)/60>sectorCount:#300==0:			#not sector.
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
					strl="INSERT INTO record VALUES(%f,%f,%f,%f,%f,%f,%f,%f,%f,%f)" % (record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],record[9])
					cursor.execute(strl)
					db.commit()
					break

				#time.sleep(10)	
#finish marathon
			averageList=[" "]
			countList=0
			cursor.execute("select * from record")
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
		
	break
db.close()
server_socket.close()
print("close")
