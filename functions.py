import cv2
import numpy as np
import freenect

#function to get RGB image from kinect
def get_video():
    video = freenect.sync_get_video()[0]
    video = cv2.cvtColor(video,cv2.COLOR_RGB2BGR)
    return video

#function to filter noise with a mask
def filter_noise(depth_array, mask, masked_array, row, col):
    row_ratio = 480/row
    column_ratio = 640/col
    temp_y = 0
    for i in xrange(col):
        temp_x = 0
        for j in xrange(row):
            area = masked_array[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1]
            mask[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1] *= area.mean()
            depth_array[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1] += mask[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1]
            temp_x = temp_x + row_ratio
        temp_y = temp_y + column_ratio
    return depth_array

#function to smooth depth map by bilateral filter
def filter_smooth(depth_array):
    ret, mask = cv2.threshold(depth_array, 10, 255, cv2.THRESH_BINARY_INV)
    mask_1 = mask/255
    masked_array = depth_array + mask
    blur = filter_noise(depth_array, mask_1, masked_array, 1, 1)
    blur = cv2.bilateralFilter(blur, 5, 50, 100)
    return blur
 
#function to get depth image from kinect
def get_depth():
    depth = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    depth = depth/30.0
    depth = depth.astype(np.uint8)
    depth = filter_smooth(depth)
    depth[0:479, 630:639] = depth[0:479, 620:629]
    return depth

def RegionCheck(foo, ListPath):#foo defines x-coordinate of point

    if (foo <= 130) and (ListPath[0] is not 0):
        ListPath[0] = 0
    if (foo > 130) and (foo <= 320) and (ListPath[1] is not 0):
        ListPath[1] = 0
    if (foo > 320) and (foo <= 510) and (ListPath[2] is not 0):
        ListPath[2] = 0
    if (foo > 510) and (ListPath[3] is not 0):
        ListPath[3] = 0

    return ListPath
