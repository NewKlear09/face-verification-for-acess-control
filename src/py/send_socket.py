"""Functions that are used to communicate between programs using sockets.
This sockets are used to send images, descriptors arrays, and signals from one program to another. 
"""

#!/usr/bin/python
import socket
import cv2
import numpy

TCP_IP = 'localhost'
TCP_PORT = 8000
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

TCP_PORT2 = 8003
TCP_PORT3 = 8004

##
## @brief      Sends a signal through a socket according to the current state of the system.
##
## @param      stringData  Signal
##
def send_signal_image(stringData):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT3))
	sock.send( str(len(stringData)).ljust(16));
	sock.send( stringData );
	sock.close()

##
## @brief      Connects the socket that connects the face_tracker (client) and the camera program (server).
##
def connect():
	sock2 = socket.socket()
	sock2.connect((TCP_IP, TCP_PORT2))
	return sock2

def close(sock2):
	sock2.close()

##
## @brief      Sends a warning to the camera. 1 if the person detected changes and 0 if not.
##
## @param      sock2       Socket
## @param      stringData  "1" or "0"
##
##
def send_warning_camera(sock2, stringData):
	sock2.send( stringData )
	#print(stringData)

##
## @brief      Sends the time.time() when the NFC is passed.
##
## @param      time  time.time()
##
def send_time(time):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	Stringtime = "tim" + str(time)
	sock.send( str(len(Stringtime)).ljust(16));
	sock.send( Stringtime );
	sock.close()

##
## @brief      Sends a string in order to the server knows what algorithm will be used.
##
## @param      algorithm  "OpenFace" or "dLib"
##
def send_algorithm(algorithm):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	sock.send( str(len(algorithm)).ljust(16));
	sock.send( algorithm );
	sock.close()
	
##
## @brief      Sends an image through a socket
##
## @param      face_img  The face image
##
def send_images(face_img):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	result, imgencode = cv2.imencode('.jpg', face_img, encode_param)
	data = numpy.array(imgencode)
	stringData = data.tostring()
	sock.send( str(len(stringData)).ljust(16));
	sock.send( stringData );
	sock.close()

##
## @brief      Sends a face descriptor through socket.
##
## @param      face_descriptor  The face descriptor
##
def send_descriptors(face_descriptor):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	stringData = numpy.array2string(face_descriptor, separator = ' ')
	sock.send( str(len(stringData)).ljust(16));
	sock.send( stringData );
	sock.close()

##
## @brief      Sends the bounding box of the detected person.
##
## @param      bb    Bounding box
##
def send_bb(bb):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	stringData = str(bb.left()) + " " + str(bb.top()) + " " + str(bb.right()) + " " + str(bb.bottom())
	sock.send( str(len(stringData)).ljust(16));
	sock.send( stringData );
	sock.close()	

##
## @brief      Sends a signal to the server.
##
def send_warning():
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	stringData = "10"
	sock.send( str(len(stringData)).ljust(16));
	sock.send( stringData );
	sock.close()

##
## @brief      Sends the ticket number via socket.
##
## @param      name  Ticket number
##
def send_ticket_number(name):
	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	sock.send( str(len(name)).ljust(16));
	sock.send( name );
	sock.close()

