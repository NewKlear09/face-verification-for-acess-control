# face-verification-for-acess-control



## Getting Started

Face verification system using several opensource and state of the art algorithms. This project is meant to be used for access control in real time. For that, the whole system is divided into smaller scripts that are communicating between sockets thus simulating a server and its several requests.

First, it is acquired images from the webcam and the facetracker is done if a face is detected. This facetracker is the comparision of the output of the neural networ of the recognition algorithm when the input is a face image. These outputs (called face descriptors) will be sent to the server to be stored and, if requested, comapared to the descriptors that are on the database (verification process).
If the system is in a registration stage, these descriptors will be stored according to the input read by the NFC Reader or the keyboard.

For more information please look the guide.pdf that is in this repository. 

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

Also, the ARDUINO connected with the RFID-RC522 is advisable as it turns closer to the real experience of accessing control. However, this can be simulated by the keys pressed in the keyboard.

## Running the tests

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

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Use the .sh that are on the /src/ folder

## Built With

* [OpenFace](https://github.com/cmusatyalab/openface)
* [DeepFace](https://github.com/RiweiChen/DeepFace)
* [Dlib](http://dlib.net/)

## Contributing

If you have any suggestion feel free to contact us. This is a early work and it has a lot of room to improve.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Daniel Lopes**
* **Ricardo Ribeiro** 

## License

This project has not yet a license. 

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
