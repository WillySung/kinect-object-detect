import socket
import cv2
import numpy
import freenect
import cv2.cv as cv

TCP_IP = '140.116.164.19'
TCP_PORT = 5001

client = socket.socket()
client.connect((TCP_IP,TCP_PORT))

#capture = cv2.VideoCapture(0)

def get_video():
    video = freenect.sync_get_video()[0]
    video = cv2.cvtColor(video,cv2.COLOR_RGB2BGR)
    return video

while (True):
    frame = get_video()
    
    #ret,frame = capture.read()
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),50]
    result,imgencode = cv2.imencode('.jpg',frame,encode_param)
    data = numpy.array(imgencode)
    stringData_send = data.tostring()

    client.send(str(len(stringData_send)).ljust(16))
    print len(stringData_send)  
    client.send(stringData_send)
    cv2.waitKey(10)
    
client.close()
cv2.destroyAllWindows()
