import cv2
import numpy as np
import pytesseract
import os

per = 25
pixelThreshold = 150
roi = [[(28, 320), (220, 350), 'text', 'Name'],
       [(238, 318), (426, 348), 'text', 'Phone'],
       [(26, 378), (40, 392), 'box', 'Sign'],
       [(238, 376), (254, 390), 'box', 'Allergic'],
       [(32, 458), (222, 494), 'text', 'Email'],
       [(236, 458), (428, 494), 'text', 'ID'],
       [(30, 514), (218, 550), 'text', 'City'],
       [(240, 514), (430, 550), 'text', 'Country']]


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

imgQ = cv2.imread('Query1.png')
h, w, c = imgQ.shape
orb = cv2.ORB_create(1000)
kp1, des1 = orb.detectAndCompute(imgQ, None)
#impkp1 = cv2.drawKeypoints(imgQ,kp1,None)

path = 'UserForms'
myPicList = os.listdir(path)
print(myPicList)

for j, y in enumerate(myPicList):
    img = cv2.imread(path + "/" + y)
    #img = cv2.resize(img, (w//3, h//3))
    #cv2.imshow(y, img)
    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des2, des1)
    matches = sorted(matches, key=lambda x: x.distance)
    good = matches[:int(len(matches)*(per/100))]
    imgMatch = cv2.drawMatches(img, kp2, imgQ, kp1, good[:100], None, flags=2)
    #imgMatch = cv2.resize(imgMatch, (w//2, h//2))
    #cv2.imshow(y, imgMatch)
    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ =cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)
    imgScan = cv2.warpPerspective(img, M, (w, h))
    #imgScan = cv2.resize(imgScan, (w//2, h//2))
    cv2.imshow(y, imgScan)

    imgShow = imgScan.copy()
    imgMask = np.zeros_like(imgShow)

    myData = []
    print(f'#################Extracting Data from Form {j}###########')
    for x, r in enumerate(roi):
        cv2.rectangle(imgMask, ((r[0][0]), r[0][1]), ((r[1][0]), r[1][1]), (0, 255, 0), cv2.FILLED)
        imgShow = cv2.addWeighted(imgShow, 0.99, imgMask, 0.1, 0)

        imgCrop = imgScan[r[0][1]:r[1][1], r[0][0]:r[1][0]]
        cv2.imshow(str(x), imgCrop)

        if r[2] == 'text':

            print('{}:{}'.format(r[3], pytesseract.image_to_string(imgCrop)))
            myData.append(pytesseract.image_to_string(imgCrop))

        if r[2] == 'box':
            imgGray = cv2.cvtColor(imgCrop, cv2.COLOR_BGRA2GRAY)
            imgThresh = cv2.threshold(imgGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
            totalPixels = cv2.countNonZero(imgThresh)
            if totalPixels > pixelThreshold : totalPixels = 1;
            else:totalPixels = 0
            print(f'{r[3]}:{totalPixels}')
            myData.append(totalPixels)
        cv2.putText(imgShow, str(myData[x]), (r[0][0], r[0][1]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    with open('DataOutput.csv', 'a+') as f:
        for data in myData:
            f.write((str(data)+','))
        f.write('\n')

    cv2.imshow(y , imgShow)


#cv2.imshow("output",imgQ)
#cv2.imshow("keypoints",impkp1)

cv2.waitKey(0)



