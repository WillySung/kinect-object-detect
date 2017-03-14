#import the necessary modules
import freenect
import cv2
import numpy as np
import socket
import time
import threading
from functions import *

#set up the windows to show images
cv2.namedWindow("RGB")
cv2.namedWindow("Depth")
cv2.namedWindow('Threshold')
cv2.moveWindow('RGB',5,5)
cv2.moveWindow('Depth',600,5)
cv2.moveWindow('Threshold',1200,5)

#thresholding global defines
erode_kernel = np.ones((3, 3), np.uint8)
dilate_kernel = np.ones((3, 3), np.uint8)

#fps count global defines
cnt = 0
fps = 0

#address setting and socket connect
TCP_IP = '140.116.164.19'
TCP_PORT1 = 5001
TCP_PORT2 = 5002
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((TCP_IP,TCP_PORT1))

#set mouse click listener
cv2.setMouseCallback("Depth", callbackFunc, None)

#function to receive the message from server
def ChatThread():
    buf = client.recv(16)
    if(buf=='F'):
        print 'F'
    elif(buf=='B'):
        print 'B'
    elif(buf=='R'):
        print 'R'
    elif(buf=='L'):
        print 'L'
    else:
        print 'wrong'

if __name__ == '__main__':
  while 1:
    #get a frame from RGB camera
    frame = get_video()
    
    #compute fps
    cnt += 1
    if cnt == 1:
        start = time.time()
    if cnt == 10:
        end = time.time()
        second = (end - start)
        fps = 10/second
        cnt = 0
    cv2.putText(frame,"FPS : %.2f"%fps , (0,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    
    #get a frame from depth sensor
    depth = get_depth()
    depth = cv2.erode(depth, erode_kernel, 4)
    depth = cv2.dilate(depth, dilate_kernel , 4)

    #thresholding 
    _,binn = cv2.threshold(depth,20,255,cv2.THRESH_BINARY_INV)
    binn = cv2.erode(binn, erode_kernel, 4)
    binn = cv2.dilate(binn,dilate_kernel , 4)

    #find contour
    v1 = 37
    v2 = 43
    edges = cv2.Canny(binn, v1, v2)
    (contours, _) = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #find center of mass
    '''cx=0
    cy=0
    try:
        for i in range(len(contours)):
            M = cv2.moments(contours[i])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(frame, (cx, cy), 6, (0, 255, 0), 3)
        cx = cx/len(contours)
        cy = cy/len(contours)
    except:
        pass'''
    
    #draw rectangle and show
    for i in range(len(contours)):
        if (cv2.contourArea(contours[i])>500):
                x,y,w,h = cv2.boundingRect(contours[i])         
                #cv2.rectangle(binn,(x,y),(x+w,y+h),(0,0,255),2)
                #cv2.circle(binn, (x+w/2,y+h/2), 1, (0, 255, 0), 3)

                rect = cv2.minAreaRect(contours[i])               
                box = cv2.cv.BoxPoints(rect)                    
                box = np.int0(box)
                cv2.drawContours(binn,[box],0,(0,0,255),2)

                #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                cv2.drawContours(frame,[box],0,(0,0,255),2)
                
                #compute the center of the rectangle
                x_center = x + w/2
                y_center = y + h/2
                a=depth[y_center,x_center]*3
                cv2.putText(frame,"%.1fcm" % a , (x,y) , cv2.FONT_HERSHEY_SIMPLEX , 1 , (0,0,255) , 2 )   
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),30]
    result,imgencode = cv2.imencode('.jpg',frame,encode_param)
    data = np.array(imgencode)
    stringData_send = data.tostring()
    client.send(str(len(stringData_send)).ljust(16))
    #print len(stringData_send)  
    client.sendto(stringData_send,(TCP_IP,TCP_PORT1))
    cv2.waitKey(10)

    chatThread = threading.Thread(name='chat',target=ChatThread)
    chatThread.start()
     
    #display RGB image
    cv2.imshow('RGB',frame)
    #display depth image
    cv2.imshow('Depth',depth)
    #display threshold image
    cv2.imshow('Threshold', binn)

    # quit program when 'esc' key is pressed
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
client.close()
cv2.destroyAllWindows()        

