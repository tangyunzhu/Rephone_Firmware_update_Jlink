import subprocess
import datetime
import shlex
import serial
import os
import signal
import sys
import threading
from serial.tools import list_ports
from time import sleep

Tcount_ok=0
Tcount_ng=0

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def WriteCount(count_ok,count_ng):
	file=open("../count/count.txt",'r+')
	count=str(count_ok)+'\n'+str(count_ng)
	file.write(str(count))
	file.close()

				
def target_flash_start():

	file=open("../count/count.txt",'r+')
	count_ok=file.readline()
	count_ng=file.readline()
	count_ok=int(count_ok)
	count_ng=int(count_ng)
	file.close()
	sleep(1)
	child1=subprocess.Popen(["../tool/JLink.exe","-CommanderScript","flash_nrf.jlink"],stdout=subprocess.PIPE)
	out=child1.communicate()
#	print out[0]
	print("**************************")
	print("")
	if "Writing target memory failed" in out[0]:
		print "       flash error    "
		serial.write('Error\r\n')
		count_ng=count_ng+1
	elif "O.K." in out[0]:
		print("       flash ok       ")
		serial.write('OK\r\n')
		count_ok=count_ok+1
	else:
		print"Didn't flash any chip"

	WriteCount(count_ok,count_ng)
	print("%d/%d"%(count_ok,count_ng))
	print("**************************")
	target_flash_start_event.set()

def target_flash_end():
	print("end....")
	print("end....")
	print("end....")
	print("end....")
	target_flash_start_event.set()
	target_flash_end_event.set()
	line_received_event.set()
	stop_event.set()
	sys.exit(0)


def require(message,timeout=1):
	try:
		print('tx:'+message)
		line_received_event.clear()
		serial.write(message+'\r\n')
	except IOError as e:
		print(e)
		serial.close()
		stop_event.set()
	if not line_received_event.wait(timeout):
		print('no response')
		return None
	return serial_received_line

def receive(count_ok,count_ng):
	print("ready to receive command...")
	while not stop_event.is_set():
		try:
			line=serial.readline()
			if line:
				print("rx: "+line)
			if line.startswith('start'):
				target_flash_start()
			if line.startswith('end'):
				target_flash_end()
			else:
				serial_received_line=line
				line_received_event.set()

		except IOError as e:
			print(e)
			serial.close()
			stop_event.set()


error_message='Writing target memory failed'
target_flash_start_event=threading.Event()
target_flash_end_event=threading.Event()
stop_event = threading.Event()
line_received_event = threading.Event()


if os.path.isfile('../count/count.txt'):
	file=open("../count/count.txt",'r+')
	count_ok=file.readline()
	count_ng=file.readline()
	count_ok=int(count_ok)
	count_ng=int(count_ng)
	file.close()
else:
	file=open("../count/count.txt",'w')
	file.write(str(0)+'\n'+str(0))
	Tcount_ok=0
	Tcount_ng=0
	file.close()


os.chdir("../firmware")
#os.system("dir")

for p in list_ports.comports():
	print p[0],p[1],p[2]
	if p[2].upper().startswith('FTDIBUS\\VID_0403+PID_6001') or p[2].upper().startswith('USB VID:PID=0403:6001'):
		print("find seeeduino mega!")
		port=p[0]
		serial=serial.Serial(port=port,baudrate=115200,bytesize=8,stopbits=1,timeout=1)
		serial_thread = threading.Thread(target=receive(Tcount_ok,Tcount_ng))
		serial_thread.start()
if not serial:
	print("*******************************")
	print("")
	print("		please connect USB!!")
	print("")
	print("*******************************")

#serial=serial.Serial(port='COM212',baudrate=115200,bytesize=8,stopbits=1,timeout=1)
#serial_thread = threading.Thread(target=receive(Tcount_ok,Tcount_ng))
#serial_thread.start()

#while(1):
#	child1=subprocess.Popen(["../tool/JLink.exe","-CommanderScript","flash_nrf.jlink"],stdout=subprocess.PIPE)
#	out=child1.communicate()
#	print("**************************")
#	print("")
#	if "Writing target memory failed" in out[0]:
#		print "       flash error    "
#		count_ng=count_ng+1
#	else:
#		print("       flash ok       ")
#		count_ok=count_ok+1
#	WriteCount(count_ok,count_ng)
#	print("%d/%d"%(count_ok,count_ng))
#	print("**************************")
#	key=raw_input("Press any key to continue....")






