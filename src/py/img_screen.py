"""Program that will present a full-screen image according to the signal received by the verification server.
"""

import socket
import cv2
import time

TCP_IP = 'localhost'
TCP_PORT = 8004

##
## @brief      Function that will convert the socket received into a string.
##
## @param      sock   The socket
## @param      count  The socket size
##
## @recval	   String Socket Information
##
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def main():
	start_green = 0
	end_green = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(True)

	img =  cv2.imread('../../display images/red.png')
	cv2.namedWindow("Interactive Display", cv2.WINDOW_NORMAL)
	cv2.resizeWindow('Interactive Display', 640,512)
	cv2.imshow("Interactive Display",img)
	cv2.waitKey(1)

	while 1:
		conn, addr = s.accept()
		length = int(recvall(conn,16))
		stringData = recvall(conn, length)

		if stringData == "1":
			img =  cv2.imread('../../display images/green.png')
			cv2.imshow("Interactive Display",img)
			cv2.waitKey(2000)
			stringData = "2" 
			
		elif stringData == "0":
			img =  cv2.imread('../../display images/yellow.png')
		else:
			img =  cv2.imread('../../display images/red.png')

		if stringData == "2":
			img =  cv2.imread('../../display images/red.png')	

		cv2.imshow("Interactive Display",img)
		cv2.waitKey(1)	

		
	s.close()

if __name__ == "__main__":
    main()	        		


