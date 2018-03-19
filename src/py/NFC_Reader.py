import tty
import sys
import termios
import send_socket as ss
import time

orig_settings = termios.tcgetattr(sys.stdin)

tty.setraw(sys.stdin)
x = 0
while x != chr(27): # ESC
    x=sys.stdin.read(1)[0]
    if len(x) > 0:
    	ss.send_time(time.time())
    	ss.send_ticket_number(x)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings) 