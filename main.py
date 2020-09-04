import numpy as np 
import cv2
import os


class OpenCvTests:

  def __init__(self):
      pass
      
  
  

  
  def showContours(self): 
    img = np.zeros((200,200),dtype=np.uint8) 
    squareWidth = 100
    x,y = 50,50
    img[x:x+squareWidth,y:y+squareWidth] = 255
    img[10:25,10:25] = 255 
    _ , thresh = cv2.threshold(img,127,255,0)
    contours , hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contourColor = (0,255,0)
    contourSize = 3
    contourIdx = -1
    colorImg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    cv2.drawContours(colorImg,contours,contourIdx,contourColor,contourSize) 
    cv2.imshow('Contor the square ',colorImg)
    cv2.waitKey()
    cv2.destroyAllWindows()        

  def convertPhoto(self,source_file_name : str,dest_file_name : str):
    img = cv2.imread(source_file_name)
    cv2.imwrite(dest_file_name,img)
    
  def captureVideoCamera(self,seconds : int, file_name : str):
    camCapture = cv2.VideoCapture(0)
    fps = 30
    size = (int(camCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    videoWriter = cv2.VideoWriter(file_name,
                                   cv2.VideoWriter_fourcc('I','4','2','0'),
                                  fps,size)
    success,frame = camCapture.read()
    numFramesRemaining = seconds * fps - 1 
    while success and (numFramesRemaining>0):
        videoWriter.write(frame)
        success,frame = camCapture.read()
        numFramesRemaining -= 1
        
  def displayImageOnWindow(self, img):
     cv2.imshow('',img)
     cv2.waitKey()
     cv2.destroyAllWindows()
     
  def roundingCircles(self, file_name : str): 
     planets = cv2.imread(file_name)
     grayedImg = cv2.cvtColor(planets, cv2.COLOR_BGR2GRAY)
     grayedImg = cv2.medianBlur(grayedImg,5)
     circles = cv2.HoughCircles(grayedImg,cv2.HOUGH_GRADIENT, 1,120,param1=100,param2=30,minRadius=0,maxRadius=0)
     circles = np.uint16(np.around(circles))
     for elem in circles[0,:]: 
        cv2.circle(planets,(elem[0],elem[1]),elem[2],(0,255,0),2)
        cv2.circle(planets,(elem[0],elem[1]),2,(0,0,255),3)
     cv2.imshow('Hough circles',planets)
     cv2.waitKey()
     cv2.destroyAllWindows()     
  


  def removingBackgroundWathershed(self, file_name : str): 
    img = cv2.pyrDown(  cv2.imread(file_name) )
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret , thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    #remove the noise 
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations=2)
    #find the background
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
    #find the foreground
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret , sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(),255,0)
    sure_fg = sure_fg.astype(np.uint8)
    #find the unknown region
    unknown = cv2.subtract(sure_bg,sure_fg)
    ret,markers = cv2.connectedComponents(sure_fg)
    markers += 1
    markers[unknown==255]=0
    markers = cv2.watershed(img,markers)
    img[markers==-1]=[255,0,0]
    cv2.imshow(file_name , img)   
    cv2.waitKey()
    cv2.destroyAllWindows()
      
  def detectingFaces(self): 
    classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    cam= cv2.VideoCapture(0)
    while (cv2.waitKey(1)==-1):
        success ,frame = cam.read()
        if success:    
           grayed = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
           faces = classifier.detectMultiScale(grayed,1.08,5,minSize=(100,100),maxSize=(300,300))    
           for (x,y,w,h) in faces: 
              frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
           cv2.imshow('',frame)    
    cv2.destroyAllWindows()   
  def HarrisFeatureDetection(self,file_name : str):
    img = cv2.pyrDown( cv2.imread(file_name) )
    grayed = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grayed = np.float32(grayed)
    dest = cv2.cornerHarris(grayed,5,3,0.04)
    img[dest>0.01*dest.max()]=[0,255,0]
    cv2.imshow(file_name,img)
    cv2.waitKey()
    cv2.destroyAllWindows()

  def trackObject(self):
    
    capture = cv2.VideoCapture(0)
    for i in range(10):
      captured,frame = capture.read()
    frame_h, frame_w = frame.shape[:2]

    w = frame_w//2
    h = frame_h//2
    x = frame_w//2 - w//2
    y = frame_h//2 - h//2
    track_window = (x,y,w,h)
    roi = frame[y:y+h,x:x+w]
    hsv_roi = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)) ) #works well for faces only
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    captured,frame = capture.read()
    while(True):
      if not captured:
        break
      hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
      dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
      rotated_rect, track_window = cv2.CamShift(dst, track_window, term_crit)
      if not rotated_rect:
        break
      box_points = cv2.boxPoints(rotated_rect)
      box_points = np.int0(box_points)
      cv2.polylines(frame,[box_points],True,(0,255,0),2)
      cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
      cv2.imshow('cam shift',frame)
      k = cv2.waitKey(1)
      if k == 27:
        break
      captured,frame = capture.read()  
    cv2.destroyAllWindows()
    capture.release()

  def backgroundSubtractor(self):
    capture = cv2.VideoCapture(0)
    bkSubtractor = cv2.createBackgroundSubtractorKNN(detectShadows=False)
    erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,5))
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,11))
    captured,frame = capture.read()
    while(captured):
      fgmsk = bkSubtractor.apply(frame)
      _,thresh = cv2.threshold(fgmsk,244,255,cv2.THRESH_BINARY)
      cv2.erode(thresh, erode_kernel,thresh,iterations=2)
      cv2.dilate(thresh, dilate_kernel,thresh,iterations=2)
      contours, hierarchy = cv2.findContours(thresh , cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_SIMPLE)
      if(len(contours)>0):  
        biggest_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour) > cv2.contourArea(biggest_contour):
                biggest_contour = contour
      x,y,w,h = cv2.boundingRect(biggest_contour)
      cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
      cv2.imshow('MOG BGR Subtractor',frame)
      k = cv2.waitKey(30)
      if k == 27:
        break
      captured,frame = capture.read()
    capture.release()
    cv2.destroyAllWindows()



  def mouse_move(self,event,x,y,flags,param):
      measure = np.array([[x],[y]],np.float32)
      if self.last_measure is None:
        self.kalman.statePre = np.array([[x],[y],[0],[0]],np.float32)
        self.kalman.statePost = np.array([[x],[y],[0],[0]],np.float32)
        prediction = measure
      else:
        self.kalman.correct(measure)  
        prediction = self.kalman.predict()
        cv2.line(self.img, (int(self.last_measure[0]), int(self.last_measure[1])),
         (int(measure[0]), int(measure[1])), (0, 255, 0))
        cv2.line(self.img, (int(self.last_prediction[0]), int(self.last_prediction[1])),
        (int(prediction[0]), int(prediction[1])), (0, 0, 255))   
      self.last_prediction = prediction.copy()
      self.last_measure = measure

  def trackingMouseWithKalman(self):
    self.img = np.zeros((800, 800, 3), np.uint8) 
    self.kalman = cv2.KalmanFilter(4,2)
    self.kalman.measurementMatrix = np.array(
                                        [[1, 0, 0, 0],
                                        [0, 1, 0, 0]], np.float32)
    self.kalman.transitionMatrix = np.array(
                                        [[1, 0, 1, 0],
                                        [0, 1, 0, 1],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]], np.float32)
    self.kalman.processNoiseCov = np.array(
                                        [[1, 0, 0, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]], np.float32) * 0.03 

    self.last_measure = None 
    self.last_prediction = None 
    name = 'kalman_tracker'
    cv2.namedWindow(name)
    cv2.setMouseCallback(name,self.mouse_move)
    while(True):
      cv2.imshow(name,self.img)
      k = cv2.waitKey(1)
      if k == 27:
        break 
    cv2.destroyAllWindows()
  
 
  def img_optimized(self,img_ : np.ndarray):
    img = img_.copy()
    img = cv2.resize(img,(100,100))
    h,w = img.shape[:2]
    x = 20
    y = h//2 - 15
    w = w //2
    h = h//2 - 10
    self.removingBackground(img,(x,y,w,h),[0,0,0],True)
    roi = img[y:y+h,x:x+w]
    resized_roi = cv2.resize(roi,(100,100))
    return resized_roi

  def mouse_move_interative_grabcut(self,event,x,y,flags,param):
     
      if self.end_draw:
        return
      if event == cv2.EVENT_LBUTTONDOWN:
        if self.begin_pos is None:
          self.begin_pos = (x,y)
        else:
          self.end_draw = True
          return
          
      if self.begin_pos is not None:
         _x,_y = self.begin_pos
         self.img = self.default_img.copy()#reset image
         w = (x-_x)
         h = (y-_y)
         cv2.rectangle(self.img,(_x,_y),
                       (_x+w,_y+h),(0,255,0),1)
         self.roi_rect = (_x,_y,w,h)
        
      
  
  def interativeGrabCut(self, img : np.ndarray, path : str):
    self.begin_pos = None
    self.end_draw = False
    self.roi_rect = None
    self.img = img
    self.default_img = self.img.copy()
    name = 'interative grabcut'
    cv2.namedWindow(name)
    cv2.setMouseCallback(name,self.mouse_move_interative_grabcut)
    while(True):
      cv2.imshow(name,self.img)
      k = cv2.waitKey(1)
      if k == 27:
        self.img = self.default_img.copy()
        self.begin_pos = None
        self.end_draw = False
        self.roi_rect = None
      if k == ord('q'):   
        break
      if k == ord('g'):
        if self.roi_rect is not None:
         cutted_img = self.default_img.copy()
         self.removingBackground(cutted_img,self.roi_rect,[0,0,0])
         self.img = cutted_img.copy()
      if k == ord('s'):
        cv2.imwrite(path,self.img)
    cv2.destroyAllWindows()
  def matchKeypoints(self,path1 : str , path2 : str, pyrDownCount=0):
      img1 = cv2.imread(path1,cv2.IMREAD_GRAYSCALE)
      img2 = cv2.imread(path2,cv2.IMREAD_GRAYSCALE)
      for i in range(0,pyrDownCount):
        img2 = cv2.pyrDown(img2)
      sift = cv2.xfeatures2d.SIFT_create()
      kp1,des1 = sift.detectAndCompute(img1,None)
      kp2,des2 = sift.detectAndCompute(img2,None)
      FLANN_IDX_KDTREE = 1
      idx_params = dict(algorithm=FLANN_IDX_KDTREE, trees = 5)
      search_params = dict(checks=5)
      flann = cv2.FlannBasedMatcher(idx_params,search_params)
      matches = flann.knnMatch(des1,des2,k=2)
      matchesMask = [[0,0] for i in range(len(matches))]
      for i,(m,n) in enumerate(matches):
        if m.distance <0.7 * n.distance:
          matchesMask[i]=[1,0]
      draw_params = dict(matchColor=(0,255,0),
                         singlePointColor=(255,0,0),
                         matchesMask=matchesMask,
                         flags=cv2.DrawMatchesFlags_DEFAULT)
      img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)
      return img3
  def resizeImgRoi(self,frame : np.ndarray,size=(100,100)) -> np.ndarray:
      img = frame
      converted = False
      if (len(img.shape)>2):
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        converted = True
      contours, hierarchy = cv2.findContours(img , cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_SIMPLE)
      if(len(contours)>0):  
        biggest_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour) > cv2.contourArea(biggest_contour):
                biggest_contour = contour
        x,y,w,h = cv2.boundingRect(biggest_contour)
        roi = frame[y:y+h,x:x+w]
        return cv2.resize(roi,size,interpolation=cv2.INTER_AREA)
      return frame  
  def getBiggestContourRect(self,img_ : np.ndarray):
    img = img_.copy()
    if (len(img.shape)>2):
      img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img = cv2.bilateralFilter(img,9,75,75) 
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,5))
    cv2.erode(img, erode_kernel,img,iterations=2)
    contours, hierarchy = cv2.findContours(img , cv2.RETR_TREE,
                                             cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours)>0):  
      biggest_contour = None
      for contour in contours:
        if (biggest_contour is None):
          area = 0
        else:
          area = cv2.contourArea(biggest_contour)
        if (cv2.contourArea(contour) > area):
            x,y,w,h = cv2.boundingRect(contour)
            if((x != 0) and (y!=0)):
              biggest_contour = contour
      x,y,w,h = cv2.boundingRect(biggest_contour)
      return (x,y,w,h)
      #print('%d %d %d %d' % (x,y,x+w,y+h))
      #cv2.rectangle(img_,(x,y),(x+w,y+h),(0,255,0),2)
    #cv2.drawContours(img_,contours,-1,(0,255,0),2)
    #self.displayImageOnWindow(img_)
  def removingBackground(self,img : np.ndarray,rect,backgroundColor,draw_rect = False):   
    x,y,w,h = rect
    rect = (x,y,x+w,y+h)
        
    if draw_rect:
     cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
     return
    mask = np.zeros(img.shape[:2],np.uint8)
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    for (i,j),value in np.ndenumerate(mask):
       if ((i > (x+w)) and (j > (y+h))): #out of roi rect
         mask[i,j] = cv2.GC_BGD
    #cv2.grabCut(img,mask,None,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_MASK)
    img[ (mask == cv2.GC_BGD) | ( mask == cv2.GC_PR_BGD) ] = backgroundColor  
def main():

   openCv = OpenCvTests()
   path = r'C:\Users\Ivo Ribeiro\Documents\open-cv\datasets\originals\IMG_20200831_080644.jpg'
   img = cv2.pyrDown(cv2.imread(path))
   img = cv2.pyrDown(img)
   x,y,w,h = openCv.getBiggestContourRect(img)
   
   openCv.removingBackground(img,(x,y,w,h),[0,0,0])
   cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
   #roi = img[x:x+w,y:y+h]
   #resized = cv2.resize(roi,(100,100),interpolation=cv2.INTER_AREA)
   openCv.displayImageOnWindow(img)

   
if __name__ == '__main__':
    main()

