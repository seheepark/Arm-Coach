import mraa
import time

class Counter:
	count =0;
c = Counter()
d = Counter()
e = Counter()

def test(args):
	c.count+=1

def test2(args):
	d.count+=1

def test3(args):
	e.count+=1

x = mraa.Gpio(2)
x.dir(mraa.DIR_IN)
#x.isr(mraa.EDGE_BOTH,test,test)

y = mraa.Gpio(4)
y.dir(mraa.DIR_IN)
#y.isr(mraa.EDGE_BOTH,test2,test2)

z = mraa.Gpio(7)
z.dir(mraa.DIR_IN)
#z.isr(mraa.EDGE_BOTH,test3,test3)
while True:
	x.isr(mraa.EDGE_BOTH,test,test)
	y.isr(mraa.ERGE_BOTH,test2,test2)
	z.isr(mraa,ERGE_BOTH,test3,test3)

	if c.count ==4:
		print("end")
		c.count =0
		#tcpClientSocket.send("end.")
	elif c.count ==2:
		print("start")
		c.count=0
		#tcpClientSocket.send("start.")
	elif c.count ==1:
		print("stop")
		c.count=0
		#tcpClientSocket.send("stop")

	if d.count == 4:
		print "cheer up"
		d.count=0
	#tcpClientSocket.send("end.")
	elif d.count ==2:
		print "compare"
		d.count=0
	#tcpClientSocket.send("start.")



