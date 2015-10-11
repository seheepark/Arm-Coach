#!/usr/bin/env python
import MySQLdb
import math
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("",5002))
server_socket.listen(10)
print "Waiting"
# For use DB
db=MySQLdb.connect ('localhost', 'root', 'root', 'soccer')
cursor=db.cursor()
cursor.execute("USE soccer")

def useDB():
	db = MySQLdb.connect('localhost', 'root', 'root', 'soccer')
	cursor = db.cursor()
	cursor.execute("USE soccer")

def dbStrCompare(nowMove, maxAvg, minAvg):
	selStr = "select *from value3"
	cursor.execute(selStr)
	nowMoveTmp = cursor.fetchone()
	nowMove = nowMoveTmp[0]
	print "Now move is : ", nowMove
	selMaxMinStr = "select *from value2"
	cursor.execute(selMaxMinStr)
	maxMinTmp = cursor.fetchall()
	maxAvg = maxMinTmp[0][0]
	minAvg = maxMinTmp[1][0]
	print "Max, Min Avg is : ", maxAvg, " ", minAvg

	if nowMove < minAvg:
		print "Player's status may be normal."
		client_socket.send('odk / %d / %d / %d / Normal' % (nowMove, minAvg, maxAvg))
		client_socket.close()
	elif minAvg <= nowMove and nowMove < maxAvg:
		print "Player's status may be warning."
		client_socket.send('odk / %d / %d / %d / Warning' % (nowMove, minAvg, maxAvg))
		client_socket.close()
	elif maxAvg <= nowMove:
		print "Player's status may be danger."
		client_socket.send('odk / %d / %d / %d / Danger' % (nowMove, minAvg, maxAvg))
		client_socket.close()

while 1:
	client_socket, address=server_socket.accept()
	print "Address is : ", address
	Event = client_socket.recv(5124)
	#client_socket.close()
	print Event

	useDB()

	nowMove = 0
	maxAvg = 0
	minAvg = 0

	if Event == 'manager-soccer':
		#selStr = "select *from value3"
		#cursor.execute(selStr)
		#nowMoveTmp = cursor.fetchone()
		#nowMove = nowMoveTmp[0]
		#print "Now move is : ", nowMove
		#selMaxMinStr = "select *from value2"
		#cursor.execute(selMaxMinStr)
		#maxMinTmp = cursor.fetchall()
		#maxAvg = maxMinTmp[0][0]
		#minAvg = maxMinTmp[1][0]
		#print "Max, Min Avg is : ", maxAvg, " ", minAvg
		
		dbStrCompare(nowMove, maxAvg, minAvg)

		#if nowMove < minAvg:
		#	print "Player's status may be normal."
		#	client_socket.send('Normal')
		#	client_socket.close()
		#elif minAvg <= nowMove and nowMove < maxAvg:
		#	print "Player's status may be warning."
		#	client_socket.send('Warning')
		#	client_socket.close()
		#elif maxAvg <= nowMove:
		#	print "Player's status may be danger."
		#	client_socket.send('Danger')
		#	client_socket.close()
