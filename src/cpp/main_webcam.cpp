#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include "opencv2/opencv.hpp"
#include "Socket/socket_client.hpp"

using namespace cv;
using namespace std;

int main(int, char**)
{
    VideoCapture cap(0); // open the default camera
    if(!cap.isOpened())  // check if we succeeded
        return -1;
    Mat frame;
    cap >> frame; // get a new frame from camera
    
    //Socket connection
    int port = 8002;
    int rows = frame.rows;
    int cols = frame.cols;
    const char hostname[] = "localhost";
    std::unique_ptr<SocketClient> client_ptr(new SocketClient(hostname, port));
    client_ptr->ConnectToServer();
    client_ptr->SendImageDims(rows, cols);

    int i = 0; //variable used in order to skip frames
    for(;;)
    {
        cap >> frame; // get a new frame from camera
        
        if (i == 5){
            client_ptr->SendImage(frame);  //Send the image through sockets
            i = 0;
        }  
        i++;

        if(waitKey(30) >= 0) break; //Esc to quit the program

    }
    // the camera will be deinitialized automatically in VideoCapture destructor
    return 0;
}