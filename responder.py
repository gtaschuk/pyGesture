from regresture import RegressionClassifier
from dtw_classifier import DTWClassifier
from hand_tracker import HandTracker

# Responder is a base class any program can extend to track gestures
class Responder:
  def __init__(self):
    self.classifiers = []
    self.bound_methods = {}
    print( "Keys:\n"
             "    k - kill the program\n"
	     "    r - reset the gesture classification\n"
	     "    w - start/stop recording current pattern\n" 
	     "    s - save the patterns\n"
	     #"    b - switch to/from backprojection view\n"
             "To initialize tracking, drag across the object with the mouse\n" )

  def process_gesture(self,gest_name):
    if gest_name in self.bound_methods:
      self.bound_methods[gest_name]()
    return 

  # adds a new classifier that will handle points
  def add_classifier(self,classifier):
    classifier.attach(self)
    self.classifiers.append(classifier)
    return

  # starts the filtering loop  
  def start(self):
    self.tracker = HandTracker(self.classifiers,debug=True) 
    self.tracker.start()

if __name__ == '__main__':
  r = Responder()
  classifier = DTWClassifier() 
  r.add_classifier(classifier)
  r.start()
