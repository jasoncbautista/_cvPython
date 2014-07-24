'''


sampleCode.py 1.2 40 0 haarcascade_frontalface_default.xml
Sources:
http://opencv.willowgarage.com/documentation/python/cookbook.html
http://www.lucaamore.com/?p=638
http://fideloper.com/facial-detection
http://stackoverflow.com/questions/13211745/detect-face-then-autocrop-pictures
 '''
# http://www.cognotics.com/opencv/servo_2007_series/part_2/page_2.html

#Python 2.7.2
#Opencv 2.4.2
#PIL 1.1.7

import cv #Opencv
import Image #Image from PIL
import glob
import os
import math
import sys


har = sys.argv[4] # haarcascade_frontalface_default.xml
multiply = float(sys.argv[1])  # 1.2
yDelta1 = int(sys.argv[2])
yDelta2 = int(sys.argv[3])

missing = 0
total = 0
def DetectFace(image, faceCascade):
    # This function takes a grey scale cv image and finds
    # the patterns defined in the haarcascade function
    # modified from: http://www.lucaamore.com/?p=638

    #variables
    min_sizeVar = 30
    min_size = (30,30)
    haar_scale = 1.1
    min_neighbors = 5
    haar_flags = 0

    # Equalize the histogram
    cv.EqualizeHist(image, image)

    # Detect the faces
    faces = cv.HaarDetectObjects(
            image, faceCascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size
        )
    return faces

def pil2cvGrey(pil_im):
    # Convert a PIL image to a greyscale cv image
    # from: http://pythonpath.wordpress.com/2012/05/08/pil-to-opencv-image/
    pil_im = pil_im.convert('L')
    cv_im = cv.CreateImageHeader(pil_im.size, cv.IPL_DEPTH_8U, 1)
    cv.SetData(cv_im, pil_im.tostring(), pil_im.size[0]  )
    return cv_im

def cv2pil(cv_im):
    # Convert the cv image to a PIL image
    return Image.fromstring("L", cv.GetSize(cv_im), cv_im.tostring())

def imgCrop(image, cropBox, boxScale=1):
    # Crop a PIL image with the provided box [x(left), y(upper), w(width), h(height)]

    # Calculate scale factors
    xDelta=max(cropBox[2]*(boxScale-1),0)
    xDelta=int(math.floor(xDelta))
    yDelta=max(cropBox[3]*(boxScale-1),0)
    yDelta=int(math.floor(yDelta))

    # Convert cv box to PIL box [left, upper, right, lower]
    PIL_box=[cropBox[0]-xDelta, (cropBox[1]-yDelta) + yDelta1, cropBox[0]+cropBox[2]+xDelta, cropBox[1]+cropBox[3]+yDelta + yDelta2]

    return image.crop(PIL_box)

def faceCrop(imagePattern,boxScale=1):
    global total
    global missing
    global har
    # Select one of the haarcascade files:
    #   haarcascade_frontalface_alt.xml  <-- Best one?
    #   haarcascade_frontalface_alt2.xml
    #   haarcascade_frontalface_alt_tree.xml
    #   haarcascade_frontalface_default.xml
    #   haarcascade_profileface.xml
    faceCascade = cv.Load(har)

    imgList=glob.glob(imagePattern)
    if len(imgList)<=0:
        print 'No Images Found'
        return


    for img in imgList:
        pil_im=Image.open(img)
        cv_im=pil2cvGrey(pil_im)
        faces=DetectFace(cv_im,faceCascade)
        print "."
        total += 1
        if faces:
            n=1
            for face in faces:
                croppedImage=imgCrop(pil_im, face[0],boxScale=boxScale)
                fname,ext=os.path.splitext(img)
                croppedImage.save(fname+'_crop'+str(n)+ext)
		print "|"
                n+=1
        else:
            missing = missing + 1
            print 'Nothing found:', img

# Crop all jpegs in a folder. Note: the code uses glob which follows unix shell rules.
# Use the boxScale to scale the cropping area. 1=opencv box, 2=2x the width and height
print "Working."
faceCrop('images/*.jpg',boxScale=multiply)

print "Done."
print "Percentage: "
print float(missing)/float(total)
