# face-verification-for-acess-control



## Getting Started

Face verification system using several opensource and state of the art algorithms. This project is meant to be used for access control in real time. For that, the whole system is divided into smaller scripts that are communicating between sockets thus simulating a server and its several requests.

First, there are acquired images from the webcam and the facetracker is done if a face is detected. This facetracker is the comparision of the output of the neural network of the recognition algorithm when the input is a face image. These outputs (called face descriptors) will be sent to the server to be stored and, if requested, comapared to the descriptors that are on the database (verification process).
If the system is in a registration stage, these descriptors will be stored according to the input read by the NFC Reader or the keyboard.

For more information please look the guide.pdf that is in this repository. 

Algorithms implemented for face detection:
* [MTCNN](https://kpzhang93.github.io/MTCNN_face_detection_alignment/index.html)
* [Histogram of Oriented Gradients (HOG)](http://dlib.net/face_detector.py.html)

Algorithms implemented for face verification:
* [OpenFace](https://cmusatyalab.github.io/openface/)
* [Deep Metric Learning](http://blog.dlib.net/2017/02/high-quality-face-recognition-with-deep.html)
* [FaceNet](https://github.com/davidsandberg/facenet)



### Prerequisites
Project tested on machines running Ubuntu 16.04

In order to test this project, you need to install the following:

* [Python 2.7](https://www.python.org/downloads/)
* [OpenCV](https://docs.opencv.org/3.0-beta/doc/tutorials/introduction/linux_install/linux_install.html)
* [Dlib](https://pypi.python.org/pypi/dlib)
* [imutils](https://github.com/jrosebr1/imutils)
* [OpenFace](https://cmusatyalab.github.io/openface/setup/) (I've installed by hand)
* [Tensorflow 1.2.1 - GPU](https://www.tensorflow.org/install/install_linux)
* [Caffe](http://caffe.berkeleyvision.org/install_apt.html)

Then, please download and paste into the folder models/ the following models for the algorithms:
DeepFace:
* [20170511-185253.pb](https://drive.google.com/file/d/0B5MzpY9kBtDVOTVnU3NIaUdySFE/edit)

MTCNN
* [det1.npy, det2.npy, and det3.npy](https://github.com/davidsandberg/facenet/tree/master/src/align)

OpenFace
* [nn4.small2.v1](https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7)

Dlib (don't forget to extract)
* [dlib_face_recognition_resnet_model_v1.dat.bz2, shape_predictor_68_face_landmarks.dat.bz2 and shape_predictor_5_face_landmarks.dat.bz2](https://github.com/davisking/dlib-models)

Also, the ARDUINO connected with the RFID-RC522 is advisable as it turns closer to the real experience of accessing control. However, this can be simulated by the keys pressed in the keyboard.

## How to Run

In a first step you need to do the registration:

```
cd src
start_registration.sh
```

Once registred:

```
cd src
start_verification.sh
```

Make sure that if you're pressing a key on the keyboard you are on the tab of the NFC/KeyBoard Reader.

If you want to test other verification algorithms open the .sh files and change the following line:
```
xterm -title "Face Tracker" -hold -e " cd py; python register_facetracker.py <\Algorithm/>"
```

and replace <\Algorithm/> by "OpenFace", "dLib" or "DeepFace".

for more insight on each function just open the Doxygen documentation:
```
cd src
documentation.sh
```

### Software Structure

![Alt text](./display images/BehaviorDiagram.png?raw=true "Behaviour Diagram")


## Contributing

If you have any suggestion feel free to contact us. This is an early work and it has a lot of room to improve.


## Authors

* **Daniel Lopes**
* **Ricardo Ribeiro** 

## License

This project has not yet a license. 

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
