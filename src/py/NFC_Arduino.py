"""Program that it is used for read an Arduino connected on ttyUSB0 port which consequently has a RC522 NFC Reader connected to it.
Once a NFC value is read, it will send the hexadecimal value associated to the NFC Tag via socket.
"""

import serial
import send_socket as ss
from datetime import datetime
import time
import tty
import sys
import termios

try:
	ser = serial.Serial('/dev/ttyUSB0', 9600)
except serial.SerialException:
	print "Arduino with RFID reader not connected!\n If you want to register/compare please use the keyboard. Each character will correspond to a person."
file = open("../../logs/logins.txt", "a")


orig_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)
x = None

while True:
	try:
		stra = ser.readline()[1:-2]
		ss.send_time(time.time())
		ss.send_ticket_number(stra)
		print stra + " ID card read"
		file.write(stra + " ; " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
		file.flush()
	except (serial.SerialException, OSError):
		print "Did not sent any NFC number through socket!"
		stra = None
	except NameError:
		pass

	x=sys.stdin.read(1)[0]
	if len(x) > 0:
		ss.send_time(time.time())
		ss.send_ticket_number(x)
		file.write(x + " ; " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
		file.flush()

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings) 	
file.close()	
