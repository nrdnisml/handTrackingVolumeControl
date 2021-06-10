import time
import numpy as np
import cv2
import mediapipe as mp
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



class VolumeControl:

    def __init__(self):
        self.data = None
        self.prvTime = 0

    def setCamera(self):
        wCam, hCam = 1280, 720
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)

    def showFps(self, img):
        curTime = time.time()
        subTime = curTime - self.prvTime
        if subTime != 0:
            fps = 1 / subTime
            self.prvTime = curTime
            cv2.putText(img, f'FPS : {int(fps)}', (30, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)


def main():
    vc = VolumeControl()
    vc.setCamera()
    detector = htm.handDetector()

    #PYCAW VOLUME CONTROL
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # volume.GetMute()
    # volume.GetMasterVolumeLevel()

    volumeRange = volume.GetVolumeRange()
    volumeMax = volumeRange[1]
    volumeMin = volumeRange[0]
    volBar = 500
    volPercent = 0
    myPCVolume = 0

    while True:
        success, img = vc.cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0 :
            # print(lmList[4],lmList[8])
            # koordinat
            x1,y1 = lmList[4][1], lmList[4][2]
            x2,y2 = lmList[8][1], lmList[8][2]
            cx,cy = (x1+x2)//2, (y1+y2)//2

            cv2.circle(img, (x1,y1), 10, (255,0,0), cv2.FILLED)
            cv2.circle(img, (x2,y2), 10, (255,0,0), cv2.FILLED)
            cv2.line(img, (x1,y1),(x2,y2), (255,0,0),3)
            cv2.circle(img, (cx,cy), 10, (255,0,0), cv2.FILLED)

            #cari panjang line
            # panjang line 50 - 400
            lengthLine = math.hypot(x2-x1,y2-y1)

            # convert range line kedalam range volume
            myPCVolume = np.interp(lengthLine, [50, 400], [volumeMin,volumeMax])
            volBar = np.interp(lengthLine, [50,400], [500,150])
            volPercent = np.interp(lengthLine, [50,400], [0,100])
            print(lengthLine,myPCVolume)
            # set volume
            volume.SetMasterVolumeLevel(myPCVolume, None)

            if lengthLine<=50:
                cv2.circle(img, (cx,cy), 10, (0,0,255), cv2.FILLED)

        # gambar volume bar
        cv2.rectangle(img, (50,150), (85,400), (255,0,0), 3)
        cv2.rectangle(img, (50,int(volBar)), (85,400), (255,0,0), cv2.FILLED)
        cv2.putText(img, f'{int(volPercent)} %', (40,500), cv2.FONT_HERSHEY_COMPLEX, 1, (0 ,255,0), 3)

        vc.showFps(img)
        cv2.imshow("Gambar", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()
