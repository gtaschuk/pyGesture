#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy
import itertools
from debug import Debug, is_rect_nonzero
import argparse

# Hand Tracker manages getting data from the kinect and dispatching tracked
# points to the classifiers
class HandTracker:
  k_dim = (640,480)

  def __init__(self,classifiers,regression=False,debug=False):
      self.classifiers = classifiers
      self.curr_classifier_idx = -1
      self.threshold = 150
      self.current_depth = 350
      self.follow_point = 0 
      self.keep_running = True

      # the window where we're tracking color
      self.track_window = None    
      self.track_box = None    
     
      # if in debug mode, we feed it to a simple request handler
      # and make debug windows etc
      self.debug = debug
      
      if self.debug:
	self.dbg_depth = Debug("DEPTH",self)
        self.dbg_rgb = Debug("RGB",self,True)

      # histogram for finding FLESH
      self.hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )

  # Sets the histogram to match the selection
  def set_hist(self,frame,selection):
	sub = cv.GetSubRect(frame, selection)
	save = cv.CloneMat(sub)

	cv.ConvertScale(frame, frame, 0.5)
	cv.Copy(save, sub)
	x,y,w,h = selection

        # rectangular piece of frame
	cv.Rectangle(frame, (x,y), (x+w,y+h), (255,255,255))

	sel = cv.GetSubRect(self.hue,selection )
	cv.CalcArrHist([sel], self.hist, 0)
        
        # get the most prevalent color in the histogram
	(_, max_val, _, _) = cv.GetMinMaxHistValue(self.hist)
        
	if max_val != 0:
	    cv.ConvertScale(self.hist.bins, self.hist.bins, 255. / max_val)
	    print "Val set to " + str(max_val)

  def change_threshold(self,value):
      self.threshold = value

  def change_depth(self,value):
      self.current_depth = value

  def toXY(self,pointidx):
      return pointidx%HandTracker.k_dim[0], pointidx/HandTracker.k_dim[0]

  def toXYZ(self,pointidx,z):
      return pointidx%HandTracker.k_dim[0], pointidx/HandTracker.k_dim[0], z
 
  def is_outstanding(self,fp,data,radius):
      xy_center = self.toXY(fp)
      x = xy_center[0] - radius 
      if x < 0: x = 0

      y = xy_center[1] - radius 
      if y < 0: y = 0
	   
	   
      x_end = x+2*radius 
      if x_end > 639: x_end = 639
      y_end = y+2*radius 
      if y_end > 479: y_end = 479
     
      #print x,x_end,y,y_end
      subrect = data[x:x_end, y:y_end]
      #print subrect
      sub_avg = numpy.average(subrect)

      # if the average value of the points in some window are
      # significantly different
      closest_distance = data[fp/640,fp%480]
      
      #print closest_distance
      return ((sub_avg - closest_distance) > 50)
 

  # Finds the point most likely to be the point of gesture
  def find_pointer(self,data):
      # nd is the minimum depth
      nd = numpy.min(data)
      # np is the location of the point with minimum depth
      fp = numpy.argmin(data)
      # check neighborhood
      if self.is_outstanding(fp,data,8):
	#print sub_avg - nd
	self.follow_point = fp 
	self.nd = data[fp/640,fp%480]
	#print self.nd
	xyz = self.toXYZ(self.follow_point,self.nd)
	#print xyz
	for classifier in self.classifiers:
	  classifier.enqueue(xyz)
	return True
      return False

  # data is a [480][640] numpy
  # Triggered whenever we get new depth data from the Kinect
  def process_depth_info(self,dev, data, timestamp):
      #global keep_running
      self.find_pointer(data)
      # pass off to debug to update window
      if self.debug:
        img = frame_convert.pretty_depth_cv(data)
	self.dbg_depth.update(img)
        self.dbg_depth.render()
     
  # Triggered whenever we get new data from the Kinect
  # working on camshift
  def process_rgb(self,dev, data, timestamp):
      #global keep_running
      # get an opencv version of video_cv data
      frame = frame_convert.video_cv(data)
      frame_size = cv.GetSize(frame)

      # Convert to HSV and keep the hue
      hsv = cv.CreateImage(frame_size, 8, 3)
      cv.CvtColor(frame, hsv, cv.CV_BGR2HSV)
      self.hue = cv.CreateImage(frame_size, 8, 1)

      # split the image into different hues
      cv.Split(hsv, self.hue, None, None, None)

      # Compute back projection
      # Run the cam-shift
      backproject = cv.CreateImage(frame_size, 8, 1)
      cv.CalcArrBackProject( [self.hue], backproject, self.hist )

      # if we have a tracking window... shift it
      # Track_window => (rectangle of approx hue)
      if self.track_window and is_rect_nonzero(self.track_window):
        # set criteria for backproject iter
	# compute back projections - shifting rectangle in
	# appropriate direction
	crit = (cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1) 
	(iters, (area, value, rect), self.track_box) = cv.CamShift(backproject, self.track_window, crit)
	# set track_window to the newly selected rectangle 
	self.track_window = rect 

      # if a section is being selected - set the histogram 
      if self.debug:
	sel = self.dbg_rgb.check_for_selection(
	    self.track_window,
	    self.track_box)

	# sets the histogram if there is a selection
	if sel: self.set_hist(frame,sel)
	
	self.dbg_rgb.update(frame)
	#if self.track_window:
	#  self.dbg_rgb.add_box(self.track_box)
	  
        self.dbg_rgb.render()

      # Bail out if ESC is pushed
      key = cv.WaitKey(3)
      char = chr(key & 255)
      
      # k is for KILL
      if char == 'k':
	self.keep_running = False
      else:
	self.curr_classifier().respond_to_key(char)
	 
  def curr_classifier(self):
    return self.classifiers[self.curr_classifier_idx]

  def body(self,*args):
      if not self.keep_running:
	  raise freenect.Kill

  def start(self):
    # Asynchronously loads data from kinect
    # self.body just kills when it gets ESC
    freenect.runloop(
	depth=self.process_depth_info,
	video=self.process_rgb,
	body=self.body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test pyGesture')
    parser.add_argument('--regression', 
    action='store_true',
    help='use regression based classification')



    args = parser.parse_args()
    t = HandTracker(debug=True)
    t.start()
