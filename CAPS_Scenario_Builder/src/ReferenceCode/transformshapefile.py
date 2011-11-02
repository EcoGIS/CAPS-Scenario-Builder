"""
Convert one shapefile type to another 
"""

import shapefile


# Create a line and a multi-point 
# and single point version of
# a polygon shapefile

# The shapefile type we are converting to
newType = shapefile.POLYLINE

# This is the shapefile we are trying
# to convert. In this case it's a
# state boundary polygon file for 
# Mississippi with one polygon and
# one dbf record.
r = shapefile.Reader("data/basedata2/towns")

## POLYLINE version
w = shapefile.Writer(newType)
w._shapes.extend(r.shapes())
# You must explicity set the shapeType of each record.
# Eventually the library will set them to the same
# as the file shape type automatically.
for s in w.shapes():
  s.shapeType = newType
w.fields = list(r.fields)
w.records.extend(r.records())
w.save("base_towns")
'''
## MULTIPOINT version
newType = shapefile.MULTIPOINT

w = shapefile.Writer(newType)
w._shapes.extend(r.shapes())
for s in w.shapes():
  s.shapeType = newType
w.fields = list(r.fields)
w.records.extend(r.records())
w.save("Miss_MPoint")

## POINT version
newType = shapefile.POINT

w = shapefile.Writer(newType)
# For a single point shapefile
# from another type we
# "flatten" each shape
# so each point is a new record.
# This means we must also assign
# each point a record which means
# records are usually duplicated.
for s in r.shapeRecords():
  for p in s.shape.points:
    w.point(*p)
    w.records.append(s.record)  
w.fields = list(r.fields)
w.save("Miss_Point")'''
