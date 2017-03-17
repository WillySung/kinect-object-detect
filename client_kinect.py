#import the necessary modules
import freenect
import cv2
import numpy as np
import socket
import time
import threading
import Queue
import multiprocessing
import os
import sys
import pickle
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
dilate_kernel = np.ones((6, 6), np.uint8)

#address setting and socket connect
TCP_IP = '140.116.164.19'
TCP_PORT = 5001
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((TCP_IP,TCP_PORT))

# flag for termination
EXIT = False
pickle.dump(EXIT,open("exit_client.txt","w"))

#function to get mouse click and print distance
def callbackFunc(e,x,y,f,p):
    if e == cv2.EVENT_LBUTTONDOWN:
       print depth[y,x]*3

#set mouse click listener
cv2.setMouseCallback("Depth", callbackFunc, None)

#subprocess to send and show image
def show_image(frame_q,depth_q,binn_q):
    #fps count defines
    cnt = 0
    fps = 0
    
    while (True):
        #get images from queue
        frame = frame_q.get()
        depth = depth_q.get()
        binn = binn_q.get()

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
        
        #send image to PC server
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),30]
        result,imgencode = cv2.imencode('.jpg',frame,encode_param)
        data = np.array(imgencode)
        stringData_send = data.tostring()
        client.send(str(len(stringData_send)).ljust(16)) 
        client.sendto(stringData_send,(TCP_IP,TCP_PORT))
        
        # show image
        cv2.imshow('RGB',frame)
        cv2.imshow('Depth',depth)
        cv2.imshow('Threshold', binn)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            print("Exit")
            EXIT = True
            pickle.dump(EXIT, open("exit_client.txt","w"))
            os._exit(0)

#main process to do image processing
def main_process():
    frame_q = multiprocessing.Queue()
    depth_q = multiprocessing.Queue()
    binn_q = multiprocessing.Queue()
    show_process = multiprocessing.Process(target=show_image, args=(frame_q,depth_q,binn_q))
    show_process.start()
    
    while (True):
        #create a thread to receive command from PC server
        chatThread = threading.Thread(name='chat',target=ChatThread)
        chatThread.start()

        #get RGB image and depth map from kinect
        frame = get_video()
        depth = get_depth()

        #morphology
        depth = cv2.erode(depth, erode_kernel, 4)
        depth = cv2.dilate(depth, dilate_kernel , 4)

        #thresholding 
        _,binn = cv2.threshold(depth,20,255,cv2.THRESH_BINARY_INV)
        binn = cv2.dilate(binn,dilate_kernel , 4)
        binn = cv2.erode(binn, erode_kernel, 4)

        #find contour
        v1 = 37
        v2 = 43
        edges = cv2.Canny(binn, v1, v2)
        (contours, _) = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #defined points to check distance
        spac=30
        flag120=[1, 1, 1, 1]
        flag140=[1, 1, 1, 1]
        f14=0
        f12=0
        f10=0
        f8=0
        (rows,cols)=depth.shape # 480 rows and 640 cols

        for i in range(rows/spac): #every 30 to mark a point    
            for j in range(cols/spac):
                cv2.circle(depth, (spac*j,spac*i), 1, (0, 255, 0), 1)
                if (depth[spac*i,spac*j]*3 < 50):
                    f8=1
                    cv2.putText(depth,"0",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),2)
                if (depth[spac*i,spac*j]*3 < 60):
                    f10=1
                    cv2.putText(depth,"1",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),2)
                if (depth[spac*i,spac*j]*3 < 80):
                    f12=1
                    cv2.putText(depth,"2",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),2)
                    flag120 = RegionCheck(spac*j, flag120)
                if (depth[spac*i,spac*j]*3 < 120):
                    f14=1
                    cv2.putText(depth,"3",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
                    flag140 = RegionCheck(spac*j, flag140)
        
        #judge the obstacles' position to show instructions for users   
        if(flag120[1:3]==[1, 1] and f12==1):
            cv2.putText(frame," frwd",(480,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        elif(flag120[2:4]==[1, 1] and f12==1):
            cv2.putText(frame," right",(480,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        elif(flag120[0:2]==[1, 1] and f12==1):
            cv2.putText(frame," left",(480,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        elif(f12==1):
            cv2.putText(frame," back",(480,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        
        #draw rectangle and show
        for i in range(len(contours)):
            if (cv2.contourArea(contours[i])>1200):
                    x,y,w,h = cv2.boundingRect(contours[i])         
                    rect = cv2.minAreaRect(contours[i])               
                    box = cv2.cv.BoxPoints(rect)                    
                    box = np.int0(box)
                    cv2.drawContours(binn,[box],0,(0,0,255),2)
                    cv2.drawContours(frame,[box],0,(0,0,255),2)
                    
                    #compute the center of the rectangle
                    x_center = x + w/2
                    y_center = y + h/2
                    a=depth[y_center,x_center]*3
                    cv2.putText(frame,"%.1fcm" % a , (x,y) , cv2.FONT_HERSHEY_SIMPLEX , 1 , (0,0,255) , 2 )
        
        #put images into queues
        frame_q.put(frame)
        depth_q.put(depth)
        binn_q.put(binn)

        Leaving = pickle.load(open("exit_client.txt","r"))
        if Leaving:
            os._exit(0)   

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
    main_process()
    
    #clear buffer
    the_q.put(None)
    show_process.join()
    client.close()
    cv2.destroyAllWindows() 
