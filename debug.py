import cv
import frame_convert

# Utility function - checks for non-zero rectangle
def is_rect_nonzero(r):
      (_,_,w,h) = r
      return (w > 0) and (h > 0)
	
class Debug:
  def __init__(self,name,parent,shift_left=False):
    # Create window and event callbacks
    self.name = name
    self.parent = parent
    cv.NamedWindow(self.name)
    if shift_left:
      cv.MoveWindow(self.name,480,0)
    cv.SetMouseCallback( self.name, self.on_mouse)
    
    # We want to track the location and area of drags
    # Set to (x,y) when mouse starts drag
    self.drag_start = None      
    # Set to rect when the mouse drag finishes
    self.selection = None
    self.parent = parent
    
    self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, .5, .5, 0, 3, 8) 
    #Creates a font
    self.mess_ll = "BEGAN"

  # if not returns false
  # Draws a box if in the process of selecting
  # Returns a selection if the selection is nonzero 
  def check_for_selection(self,track_window,track_box):
    # if complete selection, recompute the histogram
    if self.drag_start and is_rect_nonzero(self.selection):
      return self.selection
    # If mouse is pressed, highlight the current selected rectangle
    elif track_window and is_rect_nonzero(track_window):
      # draws box to img
      cv.EllipseBox(self.img, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )

    return False

  def on_mouse(self, event, x, y, flags, param):
      if event == cv.CV_EVENT_LBUTTONDOWN:
	  self.drag_start = (x, y)
      if event == cv.CV_EVENT_LBUTTONUP:
	  self.drag_start = None
	  self.parent.track_window = self.selection
      if self.drag_start:
	  xmin = min(x, self.drag_start[0])
	  ymin = min(y, self.drag_start[1])
	  xmax = max(x, self.drag_start[0])
	  ymax = max(y, self.drag_start[1])
	  self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)
	  
  # Color by classification
  # default color = grey
  def get_classification_color(self,gesture):
    cl = gesture.classification
    color = cv.RGB(127,127,127) 
    if cl == "C":
      color = cv.RGB(255,0,0)
    elif cl == "L":
      color = cv.RGB(0,0,127)
    elif cl == "R":
      color = cv.RGB(0,127,0)
    elif cl == "U":
      color = cv.RGB(0,127,127)
    elif cl == "D":
      color = cv.RGB(127,127,0)
    return color

  def add_box(self,rect):
      color = cv.RGB(127,127,0)
      cv.Rectangle(self.img, 
	  (rect[0],rect[1]), 
	  (rect[0]+rect[2],rect[1]+rect[3]),
	  color,
	  thickness=2) 
	  

  def put_messages(self):
    color = cv.RGB(255,255,255) 
    if self.mess_ll: 
      cv.PutText(self.img,self.mess_ll,(20,450),self.font,color)
    if self.mess_lr: 
      cv.PutText(self.img,self.mess_lr,(300,450),self.font,color)

  # Takes base img
  # adds gesture classification
  # draws circle if applicable 
  def update(self,img):
    # load image into frame
    self.img = img
    detected = []
    for gest_t in self.parent.classifiers:
      self.print_gesture(gest_t)
      detected.append(gest_t.classification)
 
    self.mess_ll = ",".join(detected)
    #gest_t.classification
    #self.mess_lr = 'Circ: {0} Line: {1}'.format(gest_t.circ_error,gest_t.line_error)
    self.mess_lr = ''
    self.put_messages()
    #self.render()
    # just for convention

  def print_gesture(self,gest_t):
    color = self.get_classification_color(gest_t)
   
    # print the points seen thusfar
    gest_t.print_on(self.img,color)

    # print the pattern we're comparing it against
    if len(gest_t.pattern_points) > 1:
      #gest_t.current_pattern.print_on(self.img,color)
      p = gest_t.pattern_points[0]
      col = cv.RGB(255,127,0)
      cv.Circle(self.img, (p[0],p[1]), 4,col,4)

      col = cv.RGB(127,127,0)
      for p in gest_t.pattern_points[1:]:
	cv.Circle(self.img, (p[0],p[1]), 4,col,4)

    # Draw the circle regression 
    if gest_t.classification == "C": 
      circ = gest_t.circ_guess
      # Center (x,y) Radius (r)
      cv.Circle(self.img, (circ[0],circ[1]), circ[2],color,4)
    return True
     
  def render(self):
    #cv.Circle(img, xy, 10,color,5)
    cv.ShowImage(self.name, self.img)

