import cv2
import mediapipe as mp
import time
import math

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bounding_box = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 6, (255, 0, 0), cv2.FILLED)
            xMin, xMax = min(xList), max(xList)
            yMin, yMax = min(yList), max(yList)
            bounding_box = xMin, yMin, xMax, yMax
            if draw:
                cv2.rectangle(img,(bounding_box[0]-20, bounding_box[1]-20),(bounding_box[2]+20, bounding_box[3]+20),(0,255,0), 2)
        return self.lmList,bounding_box

    def fingersUp(self):
        fingers = []
        #jempol
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else :
            fingers.append(0)
        #4 Fingers
        for id in range(1,5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self,point1, point2, img, draw=True ):
        # koordinat antara telunjuk dan jempol
        x1, y1 = self.lmList[point1][1], self.lmList[point1][2]
        x2, y2 = self.lmList[point2][1], self.lmList[point2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if draw:
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

        # cari panjang line
        # panjang line 50 - 400
        lengthLine = math.hypot(x2 - x1, y2 - y1)
        return lengthLine, img, [x1,y1,x2,y2,cx,cy]

# def main():
#     pTime = 0
#     cTime = 0
#     cap = cv2.VideoCapture(0)
#     detector = handDetector()
#     while True:
#         success, img = cap.read()
#         img = detector.findHands(img)
#         lmList = detector.findPosition(img)
#         if len(lmList) != 0:
#             print(lmList[4])
#
#         cTime = time.time()
#         subTime = cTime - pTime
#         if subTime != 0:
#             fps = 1 / subTime
#             pTime = cTime
#
#         cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
#                     (255, 0, 255), 3)
#
#         cv2.imshow("Image", img)
#         cv2.waitKey(1)
#
#
# if __name__ == "__main__":
#     main()