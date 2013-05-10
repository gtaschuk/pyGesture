import matplotlib.pyplot as pyplot
import matplotlib.cm as cm
import numpy as np



"""
Takes two point vectors

Returns
Min Distance of warp path
Accumulated cost matrix
Path (tuple of 1d arrays)

.. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
.. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In First SIAM International Conference on Data Mining, 2001.
 
"""

"""
HELPER FUNCTION
finds legal successors of a point
in the grid
"""
def successors(p,dimx,dimy):
  suc = []
  
  if p[0] + 1 < dimx:
    suc.append((p[0]+1,p[1])) # x+1,y
    if p[1] + 1 < dimy:
      suc.append((p[0],p[1] + 1)) # x,y+1
      suc.append((p[0]+1,p[1] + 1)) # x+1,y+1

  # if only within y bounds
  elif p[1] + 1 < dimy:
    suc.append((p[0],p[1] + 1)) # x,y+1

  return suc

"""
Dijkstras
given cost matrix and begin,end points

finds all the predecessors and the distances 
"""
def dijk(cost,begin,end):
  dist = 0
 
  #print cost
  # now we traverse it
  ##############################################
  # DIJKSTRAS
  ##############################################
  dist = {}
  pred = {}
  queue = {}

  queue[begin] = 0
  # for each vertex in the queue
  # sorted by min distance
  while len(queue) > 0:
    # remove it and record the distance to it as it's
    # predecessor
    v = min(queue,key=queue.get)
    
    max_y,max_x = (len(cost),len(cost[0]))
    #dist[v] = queue[v]
    dist[v] = queue.pop(v)
    
    if v == end: 
      break  

    #print "SUCCESSORS" 
    #print successors(v,len(a),len(b))
    # for each possible successor w, of a point v
    for w in successors(v,max_x,max_y):
      # the length is the length sofar + the new weight
      #print w
      newLen = dist[v] + cost[(w[1],w[0])]
      
      # if we've already seen the point, compare its
      # new length, it should be less
      #print "NEWLEN"
      #print newLen
      #print "QUEUE"
      #print queue
      #print "W"
      #print w
      if w in dist:
        if newLen < dist[w]:
          raise ValueError, \
          "Dijkstra: found better path to already-final vertex"
      # if its not in queue or its a better path, enqueue it
      elif w not in queue or newLen < queue[w]:
        queue[w] = newLen
        pred[w] = v
      
	
  return (dist,pred)
  
  #return dist, cost, path

def cost_matrix(a,b):
  cost_matrix = np.empty(shape=(len(a),len(b)))
  # Calc cost matrix
  # B is on the y axis
  # A is on the x axis
  #print "max 1st index"
  #print len(cost_matrix)-1
  #print "max 2nd index"
  #print len(cost_matrix[0]) -1 
  for i in range(len(a)):
    for j in range(len(b)):
      cost_matrix[i][j] = (b[j][0]-a[i][0])**2 + (b[j][1]-a[i][1])**2

  #print "COST MATRIX"
  #print cost_matrix
  return cost_matrix

def dtw(a,b):
  begin = ((0),(0))

  end = (len(b)-1,len(a)-1)

  trail = []
  error = 0
  curr = end
  dist, pred = dijk(cost_matrix(a,b),begin,end)

  #print curr
  while curr is not begin:
    trail.append(curr)
    curr = pred[curr] 
    error = error + dist[curr] 
  trail.append(begin)

  return error,trail
