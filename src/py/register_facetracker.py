"""Program that tracks the face of the subject that appears on the camera for the registration process (ticketline simulation). 
It will also calulate the descriptors that define the face presented and, if needed, it will send such descriptors to the verification server.
Finally, the program will send a signal to the camera acquisition program if the person changes for a further calibration. 
"""

import sys
import auxiliary as aux
import RecognitionFactory as rf
import DetectionFactory as df
import cv2
import sys
import send_socket as ss
import time
import socket
import struct
import numpy as np
from datetime import datetime

font = cv2.FONT_HERSHEY_SIMPLEX 

TCP_IP = 'localhost'
TCP_PORT = 8002

file = open("../../logs/registration_values.txt", "a")

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

def nothing(x):
    pass

def main():
	global out, out2
	global c
	global r
	try:
		algorithm = sys.argv[1]
	except IndexError:
		print "Please Choose one of the two algorithms avaliable! (dlib or OpenFace)"
		print "OpenFace will be choose on default..."
		algorithm = "OpenFace"

	verificator = rf.RecognitionAlgorithm.factory(algorithm)

	if algorithm == "DeepFace":
		detector = df.DetectionAlgorithm.factory("MTCNN")    #At this moment MTCNN only works with DeepFace
	else:
		detector = df.DetectionAlgorithm.factory("dLib")	

	ss.send_algorithm(algorithm) #send the type of algorithm to the verification_server

	end_text = 0
	start_text = 0
	person_change = False
	rep2 = None
	start_face = 0
	end_face = 0
	d = 0
	flag_2sec = False
	person_register = True

	#Socket Connection - Port 8002
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(True)
	conn, addr = s.accept()

	rows = recvall(conn,4)
  	cols = recvall(conn,4)

  	r = struct.unpack("i", rows)[0]
  	c = struct.unpack("i", cols)[0]

	ss.send_warning() 	
	
	cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
	cv2.resizeWindow('Frame', 427,342)

		
	while (cv2.waitKey(20)):
		# Capture frame-by-frame
		frame = np.zeros((r, c, 3), np.uint8)
	  	image_size = frame.size * frame.itemsize

	  	stringData = recvall(conn,image_size)
	  	data = np.fromstring(stringData, dtype='uint8')
	  	frame = data.reshape(r,c,3)					

	  	
		if frame is not None: #Frame is avaliable
			if detector.face_detection(frame) == 1:
				cv2.putText(frame,'Person Detected',(10,10), font, 0.4,(0,255,255),2)				
  				cv2.rectangle(frame, (detector.cc[0], detector.cc[1]), (detector.cc[2], detector.cc[3]), (0,0,255), 3) #Draw Bounding Box in red
  				if detector.yaw_movement(detector.img2, detector.bb) is True:
  					cv2.rectangle(frame, (detector.cc[0], detector.cc[1]), (detector.cc[2], detector.cc[3]), (0,255,255), 3) #Draw Bounding Box in yellow
  					rep1 = verificator.calc_face_descriptor(detector.img2, detector.bb, detector.landmarks)
  					if rep2 is not None:
  						d = verificator.compare(rep1, rep2)
  						print d
  						start_face = time.time() #if there isn't a face image suitable for the comparision for more than 2 seconds, ss.send_warning()
  						flag_2sec = True
  						if d > verificator.threshold:
  							person_change = True
  							ss.send_warning()
  							start_text = time.time()				  			
						if person_register is True and detector.blink_eyes(detector.img2, detector.bb) is True:
							cv2.rectangle(frame, (detector.cc[0], detector.cc[1]), (detector.cc[2], detector.cc[3]), (0,255,0), 3) #Draw Bounding Box in green
						aux.send_descriptors_socket(rep1, person_change)		
  					rep2 = rep1
	  		else:
				end_face = time.time()
			
	  		if end_face - start_face > 5 and flag_2sec is True:
	  			print "Look at the camera please!"
	  			flag_2sec = False
	  			ss.send_warning()
	  			
	  		if person_change is True and end_text - start_text < 2:     #Print on screen that person changed
				cv2.putText(frame,'Person May Have Changed!',(100,100), font, 1,(0,255,255),2)
				end_text = time.time()
				person_register = False

			if end_text - start_text > 2:	#Stop the above printing after 2 sec
				person_change = False
				person_register = True

			end_text = time.time()			

			#Display the resulting frame
			cv2.imshow('Frame',frame)

			# Press Q on keyboard to  exit
			if cv2.waitKey(1) & 0xFF == ord('q'):
				out.release()
				break

	# Closes all the frames
	cv2.destroyAllWindows()
	out.release()
	#out2.release()
		

if __name__ == "__main__":
    main()		
