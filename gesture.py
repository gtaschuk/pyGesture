#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np
import matplotlib.pyplot as plt

# Gesture tracker object
class GestureClassifier(object):
  line_thresh = 4000
  rel_rad = .8

  def __init__(self):
    self.minpoints = 10
    self.maxpoints = 15
    self.points = []
    self.pattern_points = []
    self.classification = ""
    self.running_len = 0

    # we want to notify the parent when the gesture changes
    # so we track responders
    self._responders = []

    # the bounding box
    self.b_box = False

    self.recording = False
    self.current_pattern = False 

  ####################################################
  # HELPLERS
  ####################################################
  def plot(self):
    plt.plot(self.x_points(),self.y_points(),'ro')
    plt.axis([0,640,0,480])
    plt.show()
    return

  def print_on(self,img,color):
    for p in self.points:
	cv.Circle(img, (p[0],p[1]), 4,color,5)


  def __str__(self):
    string = "Gest: %s" % self.classification
    if self.classification == "C":
      return string + " - " + str(self.circ_guess)
    return string

  def x_points(self):
    return [a[0] for a in self.points]

  def y_points(self):
    return [a[1] for a in self.points]

  def xy_points(self):
    return [(a[0],a[1]) for a in self.points]


  def dist(start,fin):
    return (start[0] - fin[0])**2 + (start[1] - fin[1])**2
  
  # returns index of closest point
  def closest(point,points):
    closest = -1
    mindist = 1000000
    for i,p in enumerate(points):
      if dist(p,point) < dist:
	closest = i
	mindist = dist(p,point)
    return closest
  
  ####################################################
  # HELPER METHODS
  ####################################################

  def attach(self,obs):
    if not obs in self._responders:
      self._responders.append(obs)

  def detach(self,obs):
    try:
      self._responders.remove(obs)
    except ValueError:
      pass

  # check if there are enough points to work with
  def ready_to_classify(self):
    return len(self.points) > self.minpoints

  def notify(self,classification):
    for resp in self._responders:
      resp.process_gesture(classification)

  def enqueue(self,point):
    # get bounding box
    if len(self.points) > 1:
      self.b_box = self.bounding_box()

    self.points.append(point)
    
    if self.ready_to_classify():
      self.classify()

    if len(self.points) > self.maxpoints:
      self.points.pop(0)
      

  def reset():
    return

  # We only want to notify when something changes
  def detect(self,classification):
    if classification == "":
      # no longer is sending an event
      self.reset()
      return
    if self.classification == classification:
      self.running_len += 1
      print self.running_len
    else:
      # new gesture
      self.classification = classification
      self.running_len = 0
    # otherwise, we should notify all subscribers
    #if classification in ["L","R"]:
    #  self.clear()
    self.notify(classification)

  def classify(self):
     return


  #############################################
  # METHODS RELATING TO THE WINDOW OF POINTS
  #############################################
  def respond_to_key(self,k):
    if k == 'r':
      print "RESETTING"
      self.reset()
      # otherwise its a gesture-mode specific key
    return

  def clear(self):
    self.points = []
    return

  def total_offset(self):
    first = np.array(self.points[0])
    last = np.array(self.points[-1])
    return np.linalg.norm(last - first) 

  # measures the displacement over the last n points
  def displacement(self):
    first = np.array(self.points[0])
    last = np.array(self.points[-1])
    return last - first

  def bounding_box(self):
    min_x = min(self.x_points())
    min_y = min(self.y_points())
    max_x = max(self.x_points())
    max_y = max(self.y_points()) 
    first = np.array((min_x,min_y))
    last = np.array((max_x,max_y))
    return [first,last]
