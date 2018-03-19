"""Program that simulates the server that receives the face descriptors sent by the face tracker and stores them into a folder according to the NFC tag value received.
"""

import RecognitionFactory as rf
import socket
import cv2
import numpy as np
import glob
import os
import time
import shutil
import send_socket as ss
from datetime import datetime

TCP_IP = 'localhost'
TCP_PORT = 8000

file = open("../../logs/registartion_values.txt", "a")

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

##
## @brief      Stores the face descriptors received into a folder (already created or not).
##
## @param      face_descriptor  The face descriptor
##
def store_face_descriptors(face_descriptor):
	global i
	global folder_name
	global ticket_name
	global person_register

	if i == 0:
		try:
			os.makedirs(folder_name)
		except OSError:
			pass	
		filename_rep = folder_name + "descriptor" + str(i)
		try: 
			np.save(filename_rep, face_descriptor)
		except IOError:
			print "Could not save the descriptors! Check if you are connected to the database servers and try again!"	
	else:
		filename_rep = folder_name + "descriptor" + str(i) 
		try: 
			np.save(filename_rep, face_descriptor)
		except IOError:
			print "Could not save the descriptors! Check if you are connected to the database servers and try again!"
					
	i += 1
	ss.send_signal_image("0")
	if i == 10:
		ss.send_signal_image("1")
		i = 0
		print "Registation Done"
		
		file.write("Registration at: " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
		file.flush()
		person_register = False	


def main():
	global folder_name
	global ticket_name
	global i
	global person_register
	person_register = False
	i = 0
	ticket_name = ""
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(True)

	conn, addr = s.accept()
	length = int(recvall(conn,16))
	algorithm = recvall(conn, length)
	
	#Verificator is created in order to get the path where the descriptors will be stored
	verificator = rf.RecognitionAlgorithm.factory(algorithm)		

	while 1:
		#Read what information has in the socket
		conn, addr = s.accept()
		length = int(recvall(conn,16))
		stringData = recvall(conn, length)

		#Manage the information received
		if stringData[0:3] == "tim":  #time sent through socket in order to measure processing times
			pass
		if len(stringData) > 23 and person_register is True:     #Descriptor values
			data = np.fromstring(stringData, dtype = 'float', sep = ' ')
			face_descriptor = np.array([float(x) for x in stringData[1:len(stringData)-1].split()])
			print "Storing Face Descriptors..."
			store_face_descriptors(face_descriptor)
		if stringData == "10":     #Warning value to stop storing face descriptors
			folder_name = None
			i = 0
			person_register = False
			print "Ticket Number is None"
		if 6 <= len(stringData) < 21 or len(stringData) == 1:     #NFC or Keyboard number
			print "Ticket Number Saved"
			if stringData == ticket_name:
				i = 0
				if folder_name is not None:
					try:
						shutil.rmtree(folder_name)
						print "Replacing the old descriptors with new ones..."
					except OSError:
						print "Couldn't remove the old descriptors!"	
				
			ticket_name = stringData
			folder_name = verificator.path_to_descriptors + ticket_name + "/"
			person_register = True	 #This flag will tell to store the descriptors in the NFC number read previously
			
	s.close()

if __name__ == "__main__":
    main()	