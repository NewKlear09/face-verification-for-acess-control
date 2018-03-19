xterm -title "Init" -e "fuser -k 8000/tcp; fuser -k 8002/tcp; fuser -k 8003/tcp;" &
xterm -title "Verification Server" -hold -e "cd py; python verification_server.py" &
xterm -title "NFC Reader" -hold -e "cd py; python NFC_Arduino.py" &
xterm -title "Face Tracker" -hold -e "cd py; python facetracker.py DeepFace" &
xterm -title "Camera" -hold -e "cd cpp; make; sleep 5; ./webcam_acquisition" &
xterm -title "IMSHOW" -hold -e " sleep 5;cd py; python img_screen_entry.py" 
