import dtw1d 
import dtw2d 

a = [0,0,0,0,1,1,2,2,3,2,1,1,0,0,0,0]
b = [0,0,1,1,2,2,3,3,3,3,2,2,1,1,0,0]

a2 = [(0,1),(0,2),(0,2),(0,1),(1,2),(1,2),(2,2),(2,1),
      (3,1),(2,2),(1,2),(1,1),(0,0),(0,0),(0,1),(0,2)]
b2 = [(0,1),(0,1),(1,2),(1,1),(2,2),(2,2),(3,1),(3,0),
      (3,0),(3,1),(2,2),(2,1),(1,0),(1,0),(0,1),(0,1)]

a3 = [(0,1),(0,2),(0,2),(0,1),(1,2),(1,2),(2,2),(2,1)]
b3 = [(0,1),(0,1),(1,2),(1,1),(2,2),(2,2),(3,1),(3,0)]

begin = (0,0)
end = (len(b)-1,len(a)-1)

print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
print "SQUARE 1D VECTORS"
print dtw1d.dtw(a,b,begin,end)

end = (len(b)-3,len(a)-1)
print "Rectangular 1D VECTORS"
print dtw1d.dtw(a,b[:-2],begin,end)

print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
begin = ((0),(0))

end = (len(b3)-1,len(a3)-1)

print "SQUARE 2D VECTORS"
dtt2 = dtw2d.dtw(a3,b3)
print "ERROR: %f\nPATH: %s" % dtt2

end = (len(b3)-3,len(a3)-1)
print "RECTANGULAR 2D VECTORS"
dtt2 = dtw2d.dtw(a3,b3[:-2])
print "ERROR: %f\nPATH: %s" % dtt2
