import time
import numpy as np
import cv2
import HandTrackingModule as htm
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
    volBar = 350
    volPercent = 0
    colorVolume = (255,0,0)
    while True:
        success, img = vc.cap.read()
        # deteksi tangan pada camera
        img = detector.findHands(img)
        lmList,bounding_box = detector.findPosition(img, draw=True)
        if len(lmList) != 0 :

            #Convert ukuran tangan ke bounding box
            luas_bounding_box = (bounding_box[2]-bounding_box[0]) * (bounding_box[3]-bounding_box[1])//1000

            if 70<luas_bounding_box<300:
                #Jarak antara jempol dan telunjuk
                lengthLine, img, lengtInfo= detector.findDistance(4,8,img)
                print(lengthLine)

                #convert volume
                volBar = np.interp(lengthLine, [50, 350], [350, 150])
                volPercent = np.interp(lengthLine, [50, 350], [0, 100])


                #Kurangi resolusi agar lebih smooth
                smoothness = 5
                volPercent = smoothness * round(volPercent/smoothness)

                #Cek jari lain up untuk set volume
                fingers = detector.fingersUp()
                if fingers[4] :
                    # set volume
                    colorVolume = (0, 0, 255)
                    volume.SetMasterVolumeLevelScalar(volPercent / 100, None)
                    cv2.circle(img, (lengtInfo[4], lengtInfo[5]), 10, (0, 0, 255), cv2.FILLED)
                else :
                    colorVolume = (255, 0, 0)

        # gambar volume bar
        cv2.rectangle(img, (50,150), (85,350), (255,0,0), 3)
        cv2.rectangle(img, (50,int(volBar)), (85,350), (255,0,0), cv2.FILLED)
        cv2.putText(img, f'{int(volPercent)} %', (40,400), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 3)
        currentVolume = volume.GetMasterVolumeLevelScalar()*100
        cv2.putText(img, f'Vol Set: {int(currentVolume)}', (600,70), cv2.FONT_HERSHEY_COMPLEX, 1, colorVolume, 3)

        vc.showFps(img)
        cv2.imshow("Gambar", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()
