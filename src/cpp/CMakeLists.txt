# cmake needs this line
cmake_minimum_required(VERSION 2.8)
set (CMAKE_CXX_STANDARD 11)

# Define project name
project(WebCam)

find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS} "/usr/local/include" ${CMAKE_CURRENT_SOURCE_DIR})
link_directories(${OpenCV_LIBRARY_DIRS} "/usr/local/lib")


# Declare the executable target built from your sources

add_executable(webcam_acquisition main_webcam.cpp Socket/socket_client.cpp Socket/socket_client.hpp)

# Link your application with OpenCV libraries
target_link_libraries(webcam_acquisition ${OpenCV_LIBS})
