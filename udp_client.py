import socket
import cv2
import numpy
import freenect

UDP_IP = '140.116.164.19'
UDP_PORT = 5001

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.connect((UDP_IP,UDP_PORT))

#capture = cv2.VideoCapture(0)

def get_video():
    video = freenect.sync_get_video()[0]
    video = cv2.cvtColor(video,cv2.COLOR_RGB2BGR)
    return video

while (True):
    frame = get_video()
    
    #ret,frame = capture.read()
    '''encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    result,imgencode = cv2.imencode('.jpg',frame,encode_param)
    data = numpy.array(imgencode)
    stringData_send = data.tostring()'''

    frame = frame.flatten()
    stringData = frame.tostring()
    
    for i in xrange(40):
        client.sendto(stringData[i*23040:(i+1)*23040],(UDP_IP,UDP_PORT))
    #client.sendto(str(len(stringData_send)).ljust(16),(UDP_IP,UDP_PORT))
    #print(len(stringData_send))  
    #client.sendto(stringData_send,(UDP_IP,UDP_PORT))
    #print(len(stringData_send))

    cv2.waitKey(10)
      
client.close()
cv2.destroyAllWindows()
