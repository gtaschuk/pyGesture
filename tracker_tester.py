from hand_tracker import HandTracker
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin
import math
from gesture import GestureTracker

from time import sleep

keep_running = True

def circle(cx,cy,r,num_points=8):
  theta = np.random.rand(num_points)*2*math.pi

  #cx = 2.3
  #cy = 0.5
  #r = 2

  x = cx + r*np.cos(theta)
  y = cy + r*np.sin(theta)

  nx = x + np.random.normal(loc=0, scale=0.2, size=num_points)
  ny = y + np.random.normal(loc=0, scale=0.2, size=num_points)
  nz = [100]*num_points
  
  return zip(nx,ny,nz)

def line(m,b,x_range,num_points=8):
  def y(m,x,b):
    return m*x+b

  x_vals = np.random.rand(num_points)*x_range
  x_vals.sort()
  #print x_vals
  y_vals = [y(m,x,b) for x in x_vals]
  z_vals = [100]*num_points
  
  return zip(x_vals,y_vals,z_vals)


# A toy class that lets us monitor the classifications
# of the gesture classifier
class GestResponder:
  def process_gesture(self,gest):
      print "Received %s" % gest
      return

class HandTest(HandTracker):
  def __init__(self):
      self.threshold = 150
      self.current_depth = 350
      
      self.responder = GestResponder()
      self.gesture = GestureTracker()
      self.gesture.attach(self.responder)

  # Shouldn't actually be necessary to override this
  # but what the hell
  def process_depth_info(self,dev, data, timestamp):
    return

  def start(self):
    # instead of a runloop we need a for loop which
    # fakes runloop
    return

  def runtest(self,fname):
    self.testcircle()
    self.testline()

  def passgesture(self,arr):
    for xyz in arr:
      self.gesture.enqueue(xyz)
    #print self.gesture.points
    self.gesture.plot()

  def testcircle(self):
    c = circle(150,200,150,15)
    self.passgesture(c)
    
  def testline(self):
    l = line(.2,200,150,15)
    self.passgesture(l)
    
if __name__ == '__main__':
  t = HandTest()
  #t.runtest(sys.argv[0])
  #t.testcircle()
  t.testline()
  #t.testcircle()
