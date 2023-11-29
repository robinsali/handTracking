import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

##########################
wCam, hCam = 640, 480
##########################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
volBar = 400
vol = 0
volPer = 0
brightness = 0
bgBar = 400

detector = htm.handDetector(detectionCon=0.8, trackCon=0.8)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volumeRange = volume.GetVolumeRange()

minVol = volumeRange[0]
maxVol = volumeRange[1]

while True:
    success, imgflip = cap.read()
    img = cv2.flip(imgflip, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    handLabel = detector.detectHandIndex(img)
    if len(lmList) != 0 and handLabel == 'Left':
        # print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1,y1), 7, (255, 0, 0),cv2.FILLED)
        cv2.circle(img, (x2,y2), 7, (255, 0, 0),cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (0,255,255), 3)
        cv2.circle(img, (cx,cy), 7, (255, 0, 0),cv2.FILLED)

        length = math.hypot((x1 - x2),(y1 - y2))
        # print(length)

        # Hand Range = 20 - 200
        # Volumne Range = -74 - 0

        vol = np.interp(length, [20, 200], [minVol, maxVol])
        volBar = np.interp(length, [20, 200], [400, 150])
        volPer = np.interp(length, [20, 200], [0, 100])
        # print(vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length < 20:
            cv2.circle(img, (cx,cy), 7, (0, 255, 0),cv2.FILLED)

        

    
    elif len(lmList) != 0 and handLabel == 'Right':
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1,y1), 7, (255, 0, 0),cv2.FILLED)
        cv2.circle(img, (x2,y2), 7, (255, 0, 0),cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (0,255,255), 3)
        cv2.circle(img, (cx,cy), 7, (255, 0, 0),cv2.FILLED)

        length = math.hypot((x1 - x2),(y1 - y2))
        # print(length)

        # Hand Range = 20 - 200
        # Volumne Range = -74 - 0

        brightness = np.interp(length, [20, 200], [0, 100])
        bgBar = np.interp(length, [20, 200], [400, 150])
        #set brightness to 0%
        sbc.set_brightness(int(brightness), force=True)
        # print(bgBar)

        if length < 30:
            cv2.circle(img, (cx,cy), 7, (0, 255, 0),cv2.FILLED)


# for lefthand volume
    cv2.rectangle(img, (50,150), (85,400), (180, 255, 0), 3)
    cv2.rectangle(img, (50,int(volBar)), (85,400), (180, 255, 0), cv2.FILLED)
    cv2.putText(img, f'vol {int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 1, (180, 255, 0), 2)

# for righthand brightness
    cv2.rectangle(img, ((wCam-50),150), ((wCam-85),400), (180, 255, 0), 3)
    cv2.rectangle(img, ((wCam-50),int(bgBar)), ((wCam-85),400), (180, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Bg {int(brightness)} %', ((wCam-170), 450), cv2.FONT_HERSHEY_PLAIN, 1, (180, 255, 0), 2)
    

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (180, 255, 0), 2)



    cv2.imshow("Image" ,img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break