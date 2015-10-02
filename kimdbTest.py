import MySQLdb

db = MySQLdb.connect ('localhost', 'root', 'root', 'kim')
cursor = db.cursor()
cursor.execute ("USE kim")

countStr = "select * from value2"
cursor.execute(countStr)
tmpCount = cursor.fetchall()
print tmpCount[1][0]
#count1d = int(''.join(map(str,tmpCount)))
db.commit()
#print count1d
#for c in count:
#	tmp = int(''.join(map(str,c)))
#	print tmp
