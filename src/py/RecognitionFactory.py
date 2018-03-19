import dlib
import openface
import numpy as np
import cv2
from scipy.spatial import distance
import facenet
import tensorflow as tf
from scipy import misc
from os.path import join as pjoin
import os
import auxiliary as aux

dlibModelDir = '../../models/shape_predictor_68_face_landmarks.dat'
preprocessing = ""

class RecognitionAlgorithm(object):
	def factory(type):
		if type == "dLib": return dLib()
		if type == "OpenFace": return OpenFace()
		if type == "DeepFace": return DeepFace()
		assert 0, "No algorithm such as " + type
	factory = staticmethod(factory)

class dLib(RecognitionAlgorithm):
	
	def __init__(self):
		print "dlib algorithm chosen for verification."
		self.facerec = dlib.face_recognition_model_v1('../../models/dlib_face_recognition_resnet_model_v1.dat')
		self.sp = dlib.shape_predictor(dlibModelDir)
		self.path_to_descriptors = "../../database/dlib_shared" + preprocessing + "/" 

		#Create the folder to store the database descriptors
		if not os.path.exists(self.path_to_descriptors):
			os.makedirs(self.path_to_descriptors)

		self.threshold = 0.7
	
	def calc_face_descriptor(self, img, bb, landmarks):
		shape = self.sp(img, bb)
		self.alignedFace = img
		
		if preprocessing == "Gamma":
			self.alignedFace = aux.adjust_gamma(self.alignedFace, 1.5)
		if preprocessing == "CLAHE":
			self.alignedFace = aux.apply_clahe(self.alignedFace)

		face_descriptor = np.array(self.facerec.compute_face_descriptor(self.alignedFace, shape))
		return face_descriptor

	def calc_face_descriptor_alignedImage(self, img, bb):
		shape = self.sp(img, dlib.rectangle(long(bb[0]), long(bb[1]), long(bb[2]), long(bb[3])))
		face_descriptor = np.array(self.facerec.compute_face_descriptor(img, shape))
		return face_descriptor

	def compare(self, face_descriptor1, face_descriptor2):
		return np.linalg.norm(face_descriptor1 - face_descriptor2)

class OpenFace(RecognitionAlgorithm):
	def __init__(self):
		print "OpenFace algorithm chosen for verification."
		self.align = openface.AlignDlib(dlibModelDir)
		self.openfaceModelDir = '../../models/nn4.small2.v1.t7'
		self.path_to_descriptors = "../../database/openface_shared" + preprocessing + "/" 
		
		#Create the folder to store the database descriptors 
		if not os.path.exists(self.path_to_descriptors): 
			os.makedirs(self.path_to_descriptors)

		self.net = openface.TorchNeuralNet(self.openfaceModelDir, 96)
		self.threshold = 0.8
	
	def calc_face_descriptor(self, img, bb, landmarks):	
		self.alignedFace = self.align.align(96, img, bb, landmarks, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
		if preprocessing == "Gamma":
			self.alignedFace = aux.adjust_gamma(self.alignedFace, 1.5)
		if preprocessing == "CLAHE":
			self.alignedFace = aux.apply_clahe(self.alignedFace)

		rep = self.net.forward(self.alignedFace)
		return rep

	def calc_face_descriptor_alignedImage(self, alignedFace, bb):
		rep = self.net.forward(alignedFace)
		return rep	

	def compare(self, rep1, rep2):
		try:
			d = rep1 - rep2
		except ValueError:
			print "It wasn't possible to do the comparation between descriptors. Please check if the folder specified has anything other thant .npy files!"
			return 1	
		return np.dot(d, d)

class DeepFace(RecognitionAlgorithm):
	def __init__(self):
		print "DeepFace algorithm chosen for verification."
		self.modeldir = '../../models/20170511-185253.pb'
		facenet.load_model(self.modeldir) 
		self.path_to_descriptors = "../../database/DeepFace_shared" + preprocessing + "/"
		
		#Create the folder to store the database descriptors
		if not os.path.exists(self.path_to_descriptors):
			os.makedirs(self.path_to_descriptors)
		
		self.threshold = 1
		#TensorFlow initializations
		self.input_image_size = 160
		self.image_size = 182
		self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
		self.embedding_size = self.embeddings.get_shape()[1]
		self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
		self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
		gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
		self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

	def calc_face_descriptor(self, img, bb, landmarks):
		cropped = []
		scaled = []
		scaled_reshape = []
		emb_array = np.zeros((1, self.embedding_size))
		cropped.append(img[int(bb[3]):int(bb[1]), int(bb[0]):int(bb[2]), :])
		cropped[0] = facenet.flip(cropped[0], False)
		
		if preprocessing == "Gamma":
			cropped[0] = aux.adjust_gamma(cropped[0], 1.5)
		if preprocessing == "CLAHE":
			cropped[0] = aux.apply_clahe(cropped[0])

		scaled.append(misc.imresize(cropped[0], (self.image_size, self.image_size), interp='bilinear'))
		scaled[0] = cv2.resize(scaled[0], (self.input_image_size,self.input_image_size),
                                               interpolation=cv2.INTER_CUBIC)
		scaled[0] = facenet.prewhiten(scaled[0])

		scaled_reshape.append(scaled[0].reshape(-1,self.input_image_size,self.input_image_size,3))
		feed_dict = {self.images_placeholder: scaled_reshape[0], self.phase_train_placeholder: False}
		emb_array[0, :] = self.sess.run(self.embeddings, feed_dict=feed_dict)
		return emb_array[0, :]

	def calc_face_descriptor_alignedImage(self, alignedFace, bb):
		return 0

	def compare(self, rep1, rep2):
		d = np.linalg.norm(rep1 - rep2)
		return d

