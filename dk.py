import mibanda
import time
sd=mibanda.DiscoveryService()
device=mibanda.BandDevice("88:0f:10:96:b1:4b", "MI")
device.connect()
device.setUserInfo(1563037356, True, 25, 180, 80, 0)
count=0
device.setCurrentSteps(0)
while count<11:
	count=count+1
	print (device.getSteps())
	time.sleep(10)
