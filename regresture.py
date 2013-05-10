from gesture import GestureClassifier
import numpy as np
from scipy.optimize import fmin
import itertools
import math


class RegressionClassifier(GestureClassifier):
  line_thresh = 4000
  rel_rad = .7

  def __init__(self):
    GestureClassifier.__init__(self)
    self.circ_error = 10000
    self.line_error = 10000
    self.reset_circle()

  # call after classifications are no longer being sent
  # clears state
  def reset(self):
    self.circ_error = 10000
    self.line_error = 10000

  # It helps for the regression to start at the center
  # when it doesn't have a last-circle to work from
  def reset_circle(self):
    self.circ_guess = np.array([320,240,100])

  # determine if we have a wide swath of points
  def sufficient_circle_coverage(self):
    cx,cy,radius = self.circ_guess

    xys = (self.x_points(),self.y_points())
    # Average points
    avg_x = sum(xys[0])/len(xys[0])
    avg_y = sum(xys[1])/len(xys[1])

    # calc Euclidian distance
    dist_sq = (cx - avg_x)**2 + (cy - avg_y)**2

    return dist_sq < GestureClassifier.rel_rad*radius**2

  def errfunc(self,params):
    nx = self.x_points()
    ny = self.y_points()
    tcx,tcy,tr = params
    return (((nx-tcx)**2 + (ny-tcy)**2 - tr**2)**2).sum()

  def is_circle(self):
    # Guess params
      params = fmin(
	  self.errfunc, 
	  self.circ_guess,
	  disp=False,
	  maxiter=20)
      self.circ_error = self.errfunc(params)
      px,py,pr = params
      if self.running_len > 0:
	if (pr < 300) and (pr > 40) and (self.circ_error/math.pow(pr,2) < 3400):
	  self.circ_guess = np.array([px, py, pr]).astype(int)
	  return self.sufficient_circle_coverage()
      else:
	if (pr < 250) and (pr > 60) and (self.circ_error/math.pow(pr,2) < 2000):
	  self.circ_guess = np.array([px, py, pr]).astype(int)
	  return self.sufficient_circle_coverage()
      return False
  
  def is_horiz_line(self):
    x_dpl = abs(self.b_box[0][0] - self.b_box[1][0])
    if x_dpl > 150:
	x_pts = self.x_points()
	y_pts = self.y_points()
	A = np.vstack([x_pts,np.ones(len(x_pts))]).T
	line = np.linalg.lstsq(A,y_pts)[0]
	residuals = np.linalg.lstsq(A,y_pts)[1]
	#print line
	#print residuals
	self.line_error = residuals[0]
	return (residuals < GestureClassifier.line_thresh)
    else:
	return False

  def is_vert_line(self):
    y_dpl = abs(self.b_box[0][1] - self.b_box[1][1])
    if y_dpl > 120:
      x_pts = self.x_points()
      y_pts = self.y_points()
      A = np.vstack([y_pts,np.ones(len(y_pts))]).T
      line = np.linalg.lstsq(A,x_pts)[0]
      residuals = np.linalg.lstsq(A,x_pts)[1]
      self.line_error = residuals[0]
      return (residuals < GestureClassifier.line_thresh)
    else:
      return False

  def sequential(self,the_list):
    it = iter(the_list)
    it.next()
    # Track how many were in order and grab direction
    # if x values are constantly increasing
    less_thans = sum([b <= a for a,b in itertools.izip(the_list, it)])
    #print less_thans
    return less_thans

  def classify(self):
    if len(self.points) < self.maxpoints:
      return
    if self.is_horiz_line():
      self.reset_circle()
      less_thans = self.sequential(self.x_points()) 
      if less_thans < 3:
	self.detect("R")
      elif less_thans > self.maxpoints - 3:
	self.detect("L")
      return
    elif self.is_vert_line():
      self.reset_circle()
      less_thans = self.sequential(self.y_points())
      if less_thans < 3:
	self.detect("D")
      elif less_thans > self.maxpoints - 3:
	self.detect("U")
      return
    elif self.is_circle():
      self.detect("C") 
      return
    else:
      # Nothing was detected
      self.detect("")
      #self.reset_circle()
      return
