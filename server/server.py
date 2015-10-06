import socket
import MySQLdb
import mibanda
import time
import math

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
#device.pair()
device.connect()
device.setUserInfo(1563037356, True, 25, 180, 80, 1)
#device.enableRealTimeSteps()
print ("connect miband")
while 1:
	client_socket, address=server_socket.accept()
	print ("connect from" ,address)
	connectEvent=0
	countLoop=0
	data=client_socket.recv(1024)
	countTime=0
	NowStep=1
	Steps=0
	device.setCurrentSteps(0)
#	time.sleep(10)
	print("setCurrnetSteps=0")
	#time.sleep(10)
	while 1:
		if connectEvent==0:
			#device.setCurrentSteps(0)
			data2=data.split('.')
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
			v=0
			print(row)
			while True:
			#	time.sleep(10)
				sector=TargetRange/10
 				try:
					NowSteps=device.getSteps()
					print ("NowSteps=%d")%(NowSteps)
				except RuntimeError as e:
					#if e=="Channel or attrib not ready":
					#device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
					#device.connect()
					#print ("connect miband")
					print(e)
					
					if str(e)=="Channel or attrib not ready":
						device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
						device.connect()
						print("connect miband")
					#else:
						#print("sleep 10sec")
						#time.sleep(10)
					print("run error")
					continue
				SectorSteps=NowSteps-Steps
				print "step is %d"%(SectorSteps)###########
				Steps=NowSteps
				movement=averageRange*SectorSteps
				if movement>sector:	#in sector
					time1=time.time()-t #time
					timeT=time1-timeFirst #
					print "time is %f" %(timeT)#########################
					timeFirst=time1
					v=movement/timeT #sector voltage
					if row[0][count]>v:
						print ("slow")
					else:
						print("fast")

					s=`count`
					s="sector"+s
					strl="UPDATE marathon SET %s = \"%f\"" % (s,v)
					cursor.execute(strl)
					record.append(v)
					count=count+1
					db.commit()
				else: #(time.time()-t)%3!=0:#300==0:			#not sector.
					if row[0][count]>v:
						print ("slow")
					else:
						print("fast")

				if count==10:
					record.remove(" ")
					strl="INSERT INTO record VALUES(%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f)" % (record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[8],record[9])
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
				if (averageList[countList]-averageList[0])/countList>0:
					print("up ! goodboy")
				else:
					print("badboy! down")
				if (averageList[countList]-averageList[countList])>0:
					print("yesterday better")
				else:
					print("yesterday notgoods")

		#break				
		if Event=="JOGGING":
			#print (device.getSteps())
			#cursor.execute("select * from jogging")
			firstV =  round((TargetRange / TargetTime), 2)
			try:
				NowSteps = device.getSteps()
			except RuntimeError,e:
				print(e)
				if str(e)=="Channel or attrib not ready":
					device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
					device.connect()
				continue
			steps = 0
			dist = averageRange*(NowSteps - steps)
			spendTime = time.time()-t
			currentV = round((dist/spendTime), 2)
	
			if First==1:
				strl="TRUNCATE jogging"
				cursor.execute(strl)
				db.commit()
				strl="INSERT INTO jogging(velocity) VALUES(%0.2f)" % (firstV)
 				cursor.execute(strl)
				db.commit()
				strl="INSERT INTO jogging(velocity) VALUES(%0.2f)" % (currentV)
				cursor.execute(strl)
				db.commit()
				


				if currentV < firstV:
					print ("Hurry Up")
				elif currentV > firstV:
					print ("Run Slow")
				else:
					print("Good, cheer up!!")
			else:
				strl="SELECT * FROM jogging ORDER BY day"
				cursor.execute(strl)
				result=cursor.fetchall()
				total = cursor.rowcount #total=len(result[1])
				strl="SELECT AVG(velocity) FROM jogging"
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
						print("Hurry Up")
					elif (avg+stdDeviation) < currentV:
						print("Run Slow")
					else:
						print("Good, cheer up!!")
				strl="INSERT INTO jogging(velocity) VALUES(%0.2f)" % (currentV)
				cursor.execute(strl)
				db.commit()			
		break	
		
	break
db.close()
server_socket.close()
print("close")
