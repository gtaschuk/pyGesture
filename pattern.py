import cv
from dtw.dtw2d import dtw
import numpy as np

class Pattern:
  def __init__(self,name="",points=[],skip_normalization=False):
    if skip_normalization:
      self.points = points
    else:
      self.points = self.normalize(points)
    self.name = name
    return

  def add_point(self,point):
    self.points.append(point)
    return

  # does dtw against the sequence of points given
  def test_against(self,sequence):
    #print self.normalize(sequence)
    dtt2 = dtw(self.points,self.normalize(sequence))

    return dtt2[0]

  def print_on(self,img,color):
    # print first point in another color
    p = self.points[0]
    col = cv.RGB(255,127,0)
    cv.Circle(img, (p[0],p[1]), 4,col,4)

    col = cv.RGB(127,127,0)
    for p in self.points[1:]:
      cv.Circle(img, (p[0],p[1]), 4,col,4)

    #print len(self.points)

  # this fits the gesture to a 640x480 grid
  def normalize(self,points,x_dim=640,y_dim=480):
    bounds = self.bounds(points)
    size = [abs(bounds[0][0] - bounds[1][0]),
	    abs(bounds[0][1] - bounds[1][1])]
    # multiplier 

    r = min([x_dim/float(size[0]), y_dim/float(size[1])])
    #print r
    normalized = [
	((p[0] - bounds[0][0])*r,
	  (p[1] - bounds[0][1])*r) for p in points]
    return normalized 
  
  def bounds(self,xy_points):
    min_x = min(p[0] for p in xy_points)
    min_y = min(p[1] for p in xy_points)
    max_x = max(p[0] for p in xy_points)
    max_y = max(p[1] for p in xy_points)
    first = np.array((min_x,min_y))
    last = np.array((max_x,max_y))
    return [first,last]
