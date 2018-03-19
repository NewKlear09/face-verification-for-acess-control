import cv2
import numpy as np
import send_socket as ss

global i
i = 0

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def apply_clahe(image):
	clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(4,4))
	lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

	lab_planes = cv2.split(lab)
	lab_planes[0] = clahe.apply(lab_planes[0])

	lab = cv2.merge(lab_planes)
	image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
	return image

##
## @brief      In construction phase.
## 
def send_descriptors_socket(descriptor, person_change):
	global i
	ss.send_descriptors(descriptor)
	if i <= 5:
		pass
		i += 1		
	if i == 5:
		print "Faces Saved for registration"	
	if person_change is True:
		i = 0

##
## @brief      In construction phase.
## 
def send_descriptors_socket2(descriptor, person_change):
	global i
	ss.send_descriptors(descriptor)
	if i <= 5:
		#ss.send_descriptors(descriptor)
		i += 1		
	if i == 5:
		print "Faces Saved for registration"	
	if person_change is True:
		i = 0		