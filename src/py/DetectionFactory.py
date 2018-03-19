"""Script that implements the face detection algorithms in a factory method for the encapsulating of object creation.
If a new algorithm is found, just add to the factory and there will be no need of change the code that it is on a higher level.
Algorithms implemented: Dlib, MTCNN.
"""

import cv2
import openface
import numpy as np
from scipy.spatial import distance
import tensorflow as tf
import detect_face


class DetectionAlgorithm(object):
	def factory(type):
		if type == "MTCNN": return MTCNN()
		if type == "dLib": return dLib()
		assert 0, "No algorithm such as " + type
	factory = staticmethod(factory)

class dLib(DetectionAlgorithm):

	def __init__(self):
		print "dlib algorithm chosen for detection"
		dlibModelDir = '../../models/shape_predictor_68_face_landmarks.dat'
		self.align = openface.AlignDlib(dlibModelDir)

		#Define which of the 68 points represents what
		self.EYE_TIPNOSE_EYE = [0, 27, 16]
		self.LEFT_EYE = [36, 37, 38, 39, 40, 41]
		self.RIGHT_EYE = [42, 43, 44, 45, 46, 47]

	##
	## @brief      It will select if the face image is 
	## suitable or not to be sent to the verification system according to the yaw movement of the head towards the camera.
	## 
	## @param      img   Image acquired by the camera
	## @param      bb    Bounding box that delineates the biggest face found on the image
	##
	## @retval     True if the face image is suitable to be sent
	## @retval	   False if not
	##
	def yaw_movement(self, img, bb):
		self.landmarks = self.align.findLandmarks(img, bb)
		self.npLandmarks_YAW = np.float32(self.landmarks)

		#Get the landmarks coordinates of the eyes and tip of the nose to calculate yaw  
		npLandmark_YAW_Indices = np.array(self.EYE_TIPNOSE_EYE)
		left_ear = self.npLandmarks_YAW[npLandmark_YAW_Indices][0]
		tip_nose = self.npLandmarks_YAW[npLandmark_YAW_Indices][1]
		right_ear = self.npLandmarks_YAW[npLandmark_YAW_Indices][2]

		#Distance relation between the two lines drawn
		distance1 = distance.euclidean(left_ear, tip_nose)
		distance2 = distance.euclidean(right_ear, tip_nose)
		distance_relation = distance1/distance2
		
		if 0.8 < distance_relation < 1.2:
			return True
		else:
			return False

	##
	## @brief      It will select if the face image is 
	## suitable or not to be sent to the verification system according to the eyes of the person.
	## If the person has his/her eyes closed then the image will not be used for the verification system.
	## 
	## @param      img   Image acquired by the camera
	## @param      bb    Bounding box that delineates the biggest face found on the image
	##
	## @retval     True if the face image is suitable to be sent
	## @retval	   False if not
	##
	def blink_eyes(self, img, bb):
		npLm = self.npLandmarks_YAW
		npLm_eye_left = np.array(self.LEFT_EYE)
		npLm_eye_right = np.array(self.RIGHT_EYE)

		d1_left = distance.euclidean(npLm[npLm_eye_left][1], npLm[npLm_eye_left][5])
		d2_left = distance.euclidean(npLm[npLm_eye_left][2], npLm[npLm_eye_left][4])
		d3_left = distance.euclidean(npLm[npLm_eye_left][0], npLm[npLm_eye_left][3])

		d1_right = distance.euclidean(npLm[npLm_eye_right][1], npLm[npLm_eye_right][5])
		d2_right = distance.euclidean(npLm[npLm_eye_right][2], npLm[npLm_eye_right][4])
		d3_right = distance.euclidean(npLm[npLm_eye_right][0], npLm[npLm_eye_right][3])

		ear_left = (d1_left + d2_left) / (2.0 * d3_left)
		ear_right = (d1_right + d2_right) / (2.0 * d3_right)

		ear = (ear_left + ear_right) / 2.0

		if ear > 0.20:
			return True
		else:
			return False

	##
	## @brief      It will search for the biggest face on the image using dlib's face detection
	##
	## @param      img   Image acquired by the camera
	##
	## @retval     True if there is a face detected
	## @retval	   False if not
	##
	def face_detection(self, img):
		self.img2 = None #This variable will be used on the main program (facetracker) as it is the reshaped image
		self.cc  = {} #Where the coordinates of the bounding box of the face are be stored in the reshaped image
		if img.shape[1] > 1000 and img.shape[0] > 1000:
			shape_factor = 4
		else:
			shape_factor = 2

		self.img2 = cv2.resize(img, (img.shape[1]/shape_factor, img.shape[0]/shape_factor), interpolation = cv2.INTER_AREA)
		img2_gray = cv2.cvtColor(self.img2, cv2.COLOR_BGR2GRAY)
		cv2.equalizeHist(img2_gray, img2_gray)	
		self.bb = self.align.getLargestFaceBoundingBox(img2_gray)

		if self.bb is not None:
			self.cc[0] = self.bb.left()*shape_factor
			self.cc[1] = self.bb.top()*shape_factor
			self.cc[2] = self.bb.right()*shape_factor
			self.cc[3] = self.bb.bottom()*shape_factor	

		#Sometimes the face is partially out of the image acquired. This detections are discarded.
		if self.bb is not None and self.bb.top()>0 and self.bb.right()<self.img2.shape[1] and self.bb.bottom()<self.img2.shape[0] and self.bb.left()>0:
			return 1
		else:
			return 0

class MTCNN(DetectionAlgorithm):

	def __init__(self):
		print "MTCNN algorithm chosen for detection"
		#Define the GPU options for the TensorFlow and load the networks
		with tf.Graph().as_default():
			gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
			sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
			with sess.as_default():
				self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(sess, '../../models/')

		self.minsize = 20  # minimum size of face
		self.threshold = [0.6, 0.7, 0.7]  # three steps's threshold
		self.factor = 0.709  # scale factor
		self.margin = 44
		self.image_size = 182

	##
	## @brief      It will select if the face image is 
	## suitable or not to be sent to the verification system according to the yaw movement of the head towards the camera.
	## 
	## @param      img   Image acquired by the camera
	## @param      bb    Bounding box that delineates the biggest face found on the image
	##
	## @retval     True if the face image is suitable to be sent
	## @retval	   False if not
	##
	def yaw_movement(self, img, bb):
		left_eye = []
		right_eye = []
		tip_nose = []

		left_eye.append((self.landmarks[0], self.landmarks[5]))
		right_eye.append((self.landmarks[1], self.landmarks[6]))
		tip_nose.append((self.landmarks[2], self.landmarks[7]))
		distance1 = distance.euclidean(left_eye, tip_nose)
		distance2 = distance.euclidean(right_eye, tip_nose)
		distance_relation = distance1/distance2
		if 0.6 < distance_relation < 1.4:
			return True
		else:
			return False


	##
	## @brief      It will select if the face image is 
	## suitable or not to be sent to the verification system according to the eyes of the person.
	## If the person has his/her eyes closed then the image will not be used for the verification system. IT DOES NOT WORK WITH MTCNN!
	## 
	## @param      img   Image acquired by the camera
	## @param      bb    Bounding box that delineates the biggest face found on the image
	##
	## @retval     True if the face image is suitable to be sent
	## @retval	   False if not
	##
	def blink_eyes(self, img, bb):
		return True

	##
	## @brief      It will search for the biggest face on the image using MTCNN's face detection.
	##
	## @param      img   Image acquired by the camera
	##
	## @retval     True if there is a face detected
	## @retval	   False if not
	##
	def face_detection(self, img):
		self.img2 = None
		self.cc  = {}
		self.landmarks = []
		all_landmarks = []
		if img.shape[1] > 1000 and img.shape[0] > 1000:
			shape_factor = 4
		else:
			shape_factor = 2

		self.img2 = cv2.resize(img, (img.shape[1]/shape_factor, img.shape[0]/shape_factor))
		self.img2 = self.img2[:, :, 0:3]
		self.bb, all_landmarks = detect_face.detect_face(self.img2, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
		#print all_landmarks
		nrof_faces = self.bb.shape[0]
		if nrof_faces > 0:
			det = self.bb[:, 0:4]
			if nrof_faces > 1:   #Choose the biggest face detected in the image
				bounding_box_size = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
				for n in range(len(bounding_box_size)):
					if bounding_box_size[n] == max(bounding_box_size):
						self.cc[0] = int(det[n, 0]*shape_factor)
						self.cc[1] = int(det[n, 3]*shape_factor)
						self.cc[2] = int(det[n, 2]*shape_factor)
						self.cc[3] = int(det[n, 1]*shape_factor)
						self.landmarks = all_landmarks[:, n]
			else:
				self.landmarks = all_landmarks
				self.cc[0] = int(det[0, 0]*shape_factor)
				self.cc[1] = int(det[0, 3]*shape_factor)
				self.cc[2] = int(det[0, 2]*shape_factor)
				self.cc[3] = int(det[0, 1]*shape_factor)
		else:
			return 0

		self.bb = {}
		self.bb[0] = int(det[0, 0])
		self.bb[1] = int(det[0, 3])
		self.bb[2] = int(det[0, 2])
		self.bb[3] = int(det[0, 1])

		#Sometimes the face is partially out of the image acquired. This detections are discarded.
		if self.cc is not None and self.cc[1]>0 and 0<self.cc[2]<img.shape[1] and 0<self.cc[3]<img.shape[0] and self.cc[0]>0:
			return 1
		else:
			return 0								             										