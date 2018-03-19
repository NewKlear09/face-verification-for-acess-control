"""Program that simulates the server that receives the face descriptors sent by the face tracker and compares them to the descriptors that are in a specific folder whose name is the NFC tag value received.
This comparision will give a value: the lower the value the more likely it is the same person.
"""

import RecognitionFactory as rf
import socket
import cv2
import numpy as np
import glob
import os
import time
import send_socket as ss
from datetime import datetime

global descriptor_values
descriptor_values = []
global folder_aux
folder_aux =" "
global i
i = 0

TCP_IP = 'localhost'
TCP_PORT = 8000

file = open("../../logsverification_values.txt", "a")

##
## @brief      Function that will convert the socket received into a string.
##
## @param      sock   The socket
## @param      count  The socket size
##
## @retval	   String Socket Information
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
## @brief      Calculates a face descriptor and appends it with others already calculated into a list. 
##
## @param      img   Image
## @param      bb    Bounding box of the biggest face
##
def calc_store_face_descriptors(img, bb):
	face_descriptor1 = verificator.calc_face_descriptor_alignedImage(img, bb)
	descriptor_values.append(face_descriptor1)

##
## @brief      It will append the face descriptor received into a list. If the list is full, the 
## least recent descriptor will be deleted.
##
## @param      face_descriptor1  Face descrpitor
##
def store_face_descriptors(face_descriptor1):
	if len(descriptor_values) == 5:
		descriptor_values.pop(0)
		descriptor_values.append(face_descriptor1)
	else:
		descriptor_values.append(face_descriptor1)

##
## @brief      Stores the face descriptors received into a folder (already created or not). 5 descriptors for each person.
##
## @param      face_descriptor  The face descriptor
##
def store_face_descriptors_folder(face_descriptor, folder_name):
	global i

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
	if i == 5:
		ss.send_signal_image("1")
		i = 0
		print "Registation Done"
		
		file.write("Registration at: " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
		file.flush()
		person_register = False				

##
## @brief      It will load the descriptors that are on a specific folder into a desciptors list.
##
## @param      folder  Folder path
##
def load_descriptors_from_folder(folder):
    global folder_aux
    global descriptor_values
    decriptors_saved = []
    try:
	    for filename in os.listdir(folder):
	        descriptor = np.load(os.path.join(folder,filename))
	        if descriptor is not None:
	            decriptors_saved.append(descriptor)            
    except OSError:
    	print "There is no ticket associated to that NFC card! Pass again in order to register"

    	if folder_aux == folder:
    		for x in range(0, len(descriptor_values)):
    			store_face_descriptors_folder(descriptor_values[x], folder)		
    	folder_aux = folder
    		 
    return decriptors_saved
    

##
## @brief      Function that will check if everything is ready for the comparision process. 
## 			   It will search if there is face descriptors received by the socket function ready for the comparision.
## 			   It will also check if the directory given is valid and if there is any face descriptor avaliable for the comparision.
##
## @param      person_name  String with the name of the folder where the desciptors are.
##
## @retval	   -1 if there are no descriptors on the folder searched (database)
## @retval     0 if there are no descriptors for the comparision (received by the socket)
## @retval	   1 if the comparision was sucessfully made
## 
def load_and_compare_descriptors(person_name):
	#Find the folder and load the .npy of the 128D descriptors
	path_to_descriptors = verificator.path_to_descriptors + person_name + "/"
	descriptors_saved = load_descriptors_from_folder(path_to_descriptors)
	if len(descriptor_values) == 0:
		print "No faces avaliable for the comparision. Wait until the camera detects someone!"
		ss.send_signal_image("4")
		return 0
	
	if len(descriptors_saved) == 0:
		print "No descriptors avaliable in the database associated with that tag!"
		ss.send_signal_image("2")
		return 1
	return compare_descriptors(descriptors_saved)

##
## @brief      Function that does an average of the similarity values calculated with the face descriptors.
##
## @param      descriptors_saved  The descriptors that are stored on a given folder.
##
## @retval     0 if there was some problem with the division process
## @retval	   1 if the comparision was sucessfully made
##
def compare_descriptors(descriptors_saved):
	global verificator
	global time_NFC
	d_values = []
	
	for x in range(0, len(descriptors_saved)):
		for y in range(0, len(descriptor_values)):
			d = verificator.compare(descriptor_values[y], descriptors_saved[x])
			d_values.append(d)		
	try:					 
		d_average = sum(d_values)/len(d_values)
		if time_NFC > 0:
			time_elapsed = time.time() - time_NFC
			print "Time Elapsed in Comparision: {} seconds".format(time_elapsed)

	except ZeroDivisionError:
		print "There were no comparisions made! Try again..."
		return 0
	
	print "Comparision value: {}".format(d_average)
	
	if d_average < verificator.threshold:
		ss.send_signal_image("1")    #Welcoming Message
	else:
		ss.send_signal_image("3")    #Denying Message

	for i in range(0, len(d_values)):
		file.write(str(d_values[i]) + " ; " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")

	file.flush()	

	descriptor_values[:] = []		
	return 1



def main():
	global descriptor_values
	global bb
	global verificator
	global time_NFC
	time_NFC = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(True)

	conn, addr = s.accept()
	length = int(recvall(conn,16))
	stringData = recvall(conn, length)
	if stringData == "OpenFace":
		verificator = rf.RecognitionAlgorithm.factory("OpenFace")
	elif stringData == "DeepFace":
		verificator = rf.RecognitionAlgorithm.factory("DeepFace")
	else: 
		verificator = rf.RecognitionAlgorithm.factory("dLib")	

	while 1:
		#Read what information has in the socket
		conn, addr = s.accept()
		length = int(recvall(conn,16))
		stringData = recvall(conn, length)
		
		#Manage the information received
		if stringData[0:3] == "tim":   #time sent through socket in order to measure processing times
			time_NFC = float(stringData[3:])
		elif len(stringData) > 23:     #Descriptor values
			data = np.fromstring(stringData, dtype = 'float', sep = ' ')
			face_descriptor = np.array([float(x) for x in stringData[1:len(stringData)-1].split()])
			store_face_descriptors(face_descriptor)
		elif stringData == "10":      #Warning value to reset the array of descriptor values 
			descriptor_values[:] = []
			print "Deleting all of the reputation values..."
		elif 6 <= len(stringData) < 21 or len(stringData) == 1:      #NFC or Keyboard number
			print "Comparing to the database images..."
			load_and_compare_descriptors(stringData)
			
	s.close()
	file.close()

if __name__ == "__main__":
    main()	