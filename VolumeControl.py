import time
import numpy as np
import cv2
import mediapipe as mp
import HandTrackingModule as htm


class VolumeControl:

    def __init__(self):
        self.data = None
        self.prvTime = 0

    def setCamera(self):
        wCam, hCam = 1280/3, 720/3
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
    while True:
        success, img = vc.cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=True)

        print(lmList)
        vc.showFps(img)
        cv2.imshow("Gambar", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()
