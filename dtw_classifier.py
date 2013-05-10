import cv
from gesture import GestureClassifier
from pattern import Pattern
from dtw.dtw2d import dtw
import numpy as np

class DTWClassifier(GestureClassifier):
  error_thresh = 10000000

  def __init__(self):
    GestureClassifier.__init__(self)
    self.maxpoints = 100
    # mode 0 is normal mode
    # mode 1 is recording mode
    #self.pattern = [(412,278),(357,332),(228,279),(227,277),(221,257),(220,233),(221,225),(227,202),(404,186),(405,188)]
    self.pattern_points = []
    self.patterns = []
    print "INITIALIZED WARPGESTURE"

  def respond_to_key(self,k):
    GestureClassifier.respond_to_key(self,k)
    if k == 'w':
      if self.recording:
        self.recording = False

	print "STOPPED RECORDING"
	name = raw_input("Enter a name for this gesture: ")
	self.patterns.append(Pattern(name,self.pattern_points))
	#print self.patterns[-1].normalize()
	self.reset()
      else:
	print "STARTED RECORDING"
	self.recording = True
	self.reset()
    elif k == 's':
      if len(self.patterns) > 0:
	self.write_to_file()
    return
 
  def write_to_file(self):
    # TODO file
    patterns = {}
    for pat in self.patterns:
      patterns[pat.name] = pat.points

    np.savez('patterns.npz', patterns)
    return

  def load_patterns(self,outfile):
    #outfile.seek(0) # Only needed here to simulate closing & reopening file
    npzfile = np.load(outfile)
    for k,v in npzfile.iteritems():
      self.patterns.append(Pattern(k,v))
    return

  def reset(self):
    self.points = []
    self.pattern_points = []
    self.classification = ""
    self.running_len = 0


  def classify(self):
    point_window = self.xy_points()
    res = np.array([pat.test_against(point_window) for pat in self.patterns])
    min_idx = np.argmin(res)

    if res[min_idx] < DTWClassifier.error_thresh:
      name = self.patterns[min_idx].name
      #print "%10s - Error %d" % (name,res[min_idx]) 
      #print name
      self.detect(name)

    #print self.current_pattern.test_against(point_window)

    # endix is the closest point on the circle to
    # the first observed point
    #begindex = closest(xys[0],self.circle)
    # begin is the closest point to the first point
    #begin = (0,begindex)
    #endex = closest(xys[0],self.circle)
    # end is the closest point to the last seen point 
    #end = (self.maxpoints,endex) 

    #if dtt2[0] < 1000000:
    #  print "LOW ERROR"
    #else:
    #  print "HIGH ERROR"
    #self.reset()

  def enqueue(self,point):
    super(DTWClassifier,self).enqueue(point)
    if self.recording:
      #self.current_pattern.add_point((point[0],point[1]))
      self.pattern_points.append((point[0],point[1]))
      #print "RECORDING"

  # checks if there are enough points and a current_pattern
  def ready_to_classify(self):
    a = len(self.points) > self.minpoints
    b = a and len(self.patterns) > 0
    return b
