#xterm -title "Init" -e "fuser -n tcp -k 8000; fuser -n tcp -k 8002; fuser -n tcp -k 8003; fuser -n tcp -k 8004;" &
fuser -n tcp -k 8003
fuser -n tcp -k 8000
fuser -n tcp -k 8002
fuser -n tcp -k 8004
sleep 5
xterm -title "Camera" -hold -e " cd cpp; make; sleep 5; ./webcam_acquisition" &
xterm -title "Store Registration Server" -hold -e "cd py; python register_server.py" &
xterm -title "Face Tracker" -hold -e " cd py; python register_facetracker.py OpenFace" &
xterm -title "NFC/KeyBoard Reader" -hold -e "cd py; python NFC_Arduino.py" &
xterm -title "IMSHOW" -hold -e " sleep 5;cd py; python img_screen.py" 
