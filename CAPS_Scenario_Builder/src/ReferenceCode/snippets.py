'''
Created on Jun 2, 2011

@author: urbanec
'''
import sys
from PyQt4 import QtCore, QtGui 
from qgis.core import *
from qgis.gui import *



                

self = "some class"
parent = "some widget's parent"

#    THE BELOW CRASHES THE APP
#self.info = QtCore.QFileInfo(QtCore.QString(self.mainwindow.scenarioFilePath))
#self.mainwindow.legend.removeAll()
# remove all layers from the registry
#QgsMapLayerRegistry.instance().removeAllMapLayers()
#scenario = QgsProject.instance()
#scenario.write(self.info)
#scenario.read(self.info)

# Try closing and reloading the scenario after adding features in order
# to update extents
#self.mainwindow


# the below crashed the app when trying to update extentnts.
# Try closing and reloading the layer after adding features in order
        # to update extents
        vfilePath = self.activeVLayer.source()
        vfileID = self.activeVLayer.getLayerID()
        print "vfileID is " + str(vfileID)
        self.mainwindow.activeVLayer = None
        QgsMapLayerRegistry.instance().removeMapLayer(vfileID)


# the below doesn't work
# make the files in the ./data/baselayer directory read only
'''directoryFileList = os.listdir(self.baseLayersPath)
for file in directoryFileList:
    path = self.baseLayersPath + file
    print "current file is: " + file
    print "current path is: " + path
    os.chmod(path, stat.S_IWRITE)'''


''' Field names corresponding to user input fields only 
# If you add a new label above, you must add the new field name here.
# You must also add the new field name to the corresponding 
#self.fieldValues list below 
self.userInputFieldNames0 = self.fieldNames0 = ['aqua_score', 'terr_score'] 
self.userInputFieldNames1 =self.fieldNames1 = ['aqua_score']
self.userInputFieldNames2 =self.fieldNames2 = ['terr_score']
self.userInputFieldNames3 =self.fieldNames3 = ['r_severity']
self.userInputFieldNames4 =self.fieldNames4 = ['newrd_rate', 'newrd_clas']
self.userInputFieldNames5 =self.fieldNames5 = ['modrd_rate', 'modrd_cls']
self.userInputFieldNames6 =self.fieldNames6 = ['ldcvr_cls']'''

# change directory permissions
    import os
    import stat
     
    try:
    # create a folder with mode 777 (octal)
    os.mkdir("montypython")
    # change mode to 577
    os.chmod("montypython", 0577) # don't forget the 0
    # get the current mode and print it
    print stat.S_IMODE(os.stat("montypython")[stat.ST_MODE])
    finally:
    # in any case, attempt to remove directory
    try:
    os.rmdir("montypython")
    except OSError:
    pass


# code to chang file permissions on windows
from win32api import MoveFileEx, GetUserName
 
from win32file import (
    MOVEFILE_COPY_ALLOWED,
    MOVEFILE_REPLACE_EXISTING,
    MOVEFILE_WRITE_THROUGH
)
from win32security import (
    LookupAccountName,
    GetFileSecurity,
    SetFileSecurity,
    ACL,
    DACL_SECURITY_INFORMATION,
    ACL_REVISION
)
from ntsecuritycon import (
    FILE_ALL_ACCESS,
    FILE_GENERIC_EXECUTE,
    FILE_GENERIC_READ,
    FILE_GENERIC_WRITE,
    FILE_LIST_DIRECTORY
)
 
EVERYONE_GROUP = 'Everyone'
ADMINISTRATORS_GROUP = 'Administrators'
 
def _get_group_sid(group_name):
    """Return the SID for a group with the given name."""
    return LookupAccountName('', group_name)[0]
 
 
def _set_file_attributes(path, groups):
    """Set file attributes using the wind32api."""
    security_descriptor = GetFileSecurity(path, DACL_SECURITY_INFORMATION)
    dacl = ACL()
    for group_name in groups:
        # set the attributes of the group only if not null
        if groups[group_name]:
            group_sid = _get_group_sid(group_name)
            dacl.AddAccessAllowedAce(ACL_REVISION, groups[group_name],
                group_sid)
    # the dacl has all the info of the dff groups passed in the parameters
    security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
    SetFileSecurity(path, DACL_SECURITY_INFORMATION, security_descriptor)
 
def set_file_readonly(path):
    """Change path permissions to readonly in a file."""
    # we use the win32 api because chmod just sets the readonly flag and
    # we want to have imore control over the permissions
    groups = {}
    groups[EVERYONE_GROUP] = FILE_GENERIC_READ
    groups[ADMINISTRATORS_GROUP] = FILE_GENERIC_READ
    groups[GetUserName()] = FILE_GENERIC_READ
    # the above equals more or less to 0444
    _set_file_attributes(path, groups)

'''Martin Dobias raster transparency
This way you can access current list of transparency values:

>>> rt=l.rasterTransparency()

>>> lst = rt.transparentSingleValuePixelList()

>>> for item in lst: print item.pixelValue, item.percentTransparent

...

-9999.0 100.0

0.0 50.0

To set a list with just one value:

>>> x = QgsRasterTransparency.TransparentSingleValuePixel()

>>> x.pixelValue = 123

>>> x.transparencyPercent = 50

>>> rt.setTransparentSingleValuePixelList( [ x ] )


The above examples suppose that you use single band raster. In case of RGB
image the steps are similar, just instead of "SingleValue" methods you would
use "ThreeValue" methods and instead of "pixelValue" attribute there are
"red", "green", "blue" attributes.'''

# obsolete code.  Use legend.findItems().  much easier
def oldarrangeOrientingLayers(self):
        # debugging
        print "arrangeOrientingLayers()"
        
        legend = self.legend
        legendLayers = legend.getLayerSet()
        numLegendLayers = len(legendLayers)
        oRLayers = self.orientingRasterLayers
        oVLayers = self.orientingVectorLayers
        rcount = 0
        vcount = 0
        
        print "numLegendLayers is " + str(numLegendLayers)
        
        for (counter, legendLayer) in enumerate(legendLayers):
            legendLayerName = legendLayer.layer().name()
            print "legendLayerName is " + legendLayerName
            print "r counter is " + str(counter)
            for orientingLayer in oRLayers:
                info = QtCore.QFileInfo(orientingLayer)
                orientingLayerName = info.completeBaseName()
                print "orientingLayerName is " + orientingLayerName
                if legendLayerName == orientingLayerName:
                    print "orientingLayerName inside is " + orientingLayerName
                    itemToMove = legend.topLevelItem(counter)
                    print "itemToMove is " + itemToMove.canvasLayer.layer().name()
                    position = numLegendLayers - oRLayers.index(orientingLayer) # itemToMove is the base layer
                    print "r position is " + str(position)
                    print type(position), position
                    itemToMove.storeAppearanceSettings() # Store settings 
                    self.legend.takeTopLevelItem(counter)
                    legend.insertTopLevelItem(1, itemToMove)
                    rcount += 1
                    print "ending rcount is " + str(rcount)
                    if rcount == len(oRLayers):
                        break
                    else: continue
            
        # debugging
        print "rcount is " + str(rcount)
       
        for (counter, legendLayer) in enumerate(legendLayers):
            legendLayerName = legendLayer.layer().name()
            print "legendLayerName is " + legendLayerName
            print "r counter is " + str(counter)   
            for orientingLayer in oVLayers:
                info = QtCore.QFileInfo(orientingLayer)
                orientingLayerName = info.completeBaseName()
                print "orientingLayerName is " + orientingLayerName
                if legendLayerName == orientingLayerName:
                    itemToMove = legend.topLevelItem(counter)
                    print "itemToMove is " + itemToMove.canvasLayer.layer().name()                    
                    position = numLegendLayers - (oVLayers.index(orientingLayer) + (rcount)) # itemToMove is the base layer 
                    print "v position is " + str(position)
                    print type(position), position
                    itemToMove.storeAppearanceSettings() # Store settings 
                    self.legend.takeTopLevelItem(counter)
                    legend.insertTopLevelItem(0, itemToMove)
                    vcount += 1
                    print "ending vcount is " + str(vcount)
                    if vcount == len(oVLayers):
                        break
                    else: continue

# Martin Dobias reading project properties

'''The QgsProject class offers a similar interface to QSettings for
access to properties. The example is mostly self-explanatory except
for the "[0]" at the end of the readNumEntry lines. This function in
python returns a tuple: first value is the number, second value is a
boolean whether the conversion to number went fine - for simplicity we
ignore that flag here.'''

prj = QgsProject.instance()
r = prj.readNumEntry("Gui", "/SelectionColorRedPart", 255)[0]
g = prj.readNumEntry("Gui", "/SelectionColorGreenPart", 255)[0]
b = prj.readNumEntry("Gui", "/SelectionColorBluePart", 0)[0]
a = prj.readNumEntry("Gui", "/SelectionColorAlphaPart", 255)[0]
clr = QColor(r,g,b,a)



# unneeded code because edit layers must be open if they exist in the scenario directory
def openEditLayer(self):
            # edit file directory has same name as the scenario file (*.caps)
            info = self.mainwindow.info
            directoryName = info.completeBaseName()
            editFilePath = unicode(info.path() + "/" + directoryName + "/" + self.editLayer + ".shp")
            
            # debugging
            print "the directory name is " + directoryName
            print "the editFilePath is " + editFilePath
            
            # if the file exists, open it (automatically goes to the top of the layer panel)
            editFile = QtCore.QFile(editFilePath)
            if editFile.exists():
                self.mainwindow.openVectorLayer(editFilePath)                 



# unneeded orienting layer code
def openOrientingBaseLayers(self, layers):
        ''' Open needed orienting layers and arrange '''
        legendLayers = layers
        orientingVlayers = self.mainwindow.orientingVectorLayers
        orientingRlayers = self.mainwindow.orientingRasterLayers
        path = self.mainwindow.baseLayerPath
        
        # Check for open and open if not
        for legendLayer in legendLayers:
            legendLayerName = layer.layer().name()
            for orientingLayer in orientingVlayers:
                info = QFileInfo(orientingLayer)
                orientingLayerName = info.completeBaseName()
                if legendLayerName == orientingLayerName: 
                    orientingVlayers.remove(orientingLayer)
                    continue
            for orientingLayer in orientingRlayers:
                info = QFileInfo(orientingLayer)
                orientingLayerName = info.completeBaseName()
                if legendLayerName == orientingLayerName: 
                    orientingVlayers.remove(orientingLayer)
                    continue




#open a file with QFile
editFile = QtCore.QFile(editFilePath)
        
try:
    editFile.open(QtCore.QIODevice.ReadWrite)
except (IOError, OSError), e:
    error = unicode(e)
if error:
    print e
    QtGui.QMessageBox.warning(self, "File error:", "The scenario editing layer "\
+ editLayer + " failed to open. Could it have been damaged somehow?")   


# code for empty extents
extent = self.canvas.extent()
if str(extent.xMinimum()) == "-1.#IND":                                                            
    extent = QgsRectangle(32000, 780000, 330000, 965000) # MA state extents   

# code used to save file name to open file dialog to last directory
dir = os.path.dirname(self.rfilename) \
                if self.rfilename is not None else "./data/Base_layers"    

# a slick way to make a list of 3 zeros 
groups = [0]*3
for i in xrange(3):
    groups[i] = self.getGroup(selected, header + i)

or more "Pythonically":

groups = [self.getGroup(selected, header + i) for i in xrange(3)]

# code for opening a console and finding and killing a process
# but only for UNIX!!
#!/usr/bin/env python
import os
import signal
 
# Change this to your process name
processname = 'aterm'
 
for line in os.popen("ps xa"):
    fields  = line.split()
    pid     = fields[0]
    process = fields[4]
 
    if process.find(processname) > 0:
        # Kill the Process. Change signal.SIGHUP to signal.SIGKILL if you like
        os.kill(int(pid), signal.SIGHUP)
 
        # Do something else here
        print "Doing something else here"
 
        # Restart the process
        os.system(processname)
 
        # Hop out of loop
        break

# This is my last hope for finding out if QGIS is running:
import win32com.client

def find_process(name):
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(".", "root\cimv2")
    colItems = objSWbemServices.ExecQuery(
         "Select * from Win32_Process where Caption = '{0}'".format(name))
    return len(colItems)

print find_process("SciTE.exe")



''' clear the python interpreter '''
import os

def clear():
    if os.name == 'posix':
        os.system('clear')

    elif os.name == ('ce', 'nt', 'dos'):
        os.system('cls')


clear()

# using the lockfile module
lock = LockFile(vfile)
                #lock.acquire(0)
                lock.break_lock()
                lock.acquire()
            
                #debugging
                print "type vfile = " + str(type(vfile))
                print vfile
                print "is locked? " + str(lock.is_locked())
                print "is CAPS locking? " + str(lock.i_am_locking())

try: 
                    lock.acquire(timeout=0)
                    print "I locked ", lock.path 
                except AlreadyLocked:
                    QtGui.QMessageBox.warning(self, "Failed to save:", "Please check if this \
vector layer is open in another program." + error)
                    lock.break_lock()
                except LockFailed:
                    QtGui.QMessageBox.warning(self, "Failed to save:", "Please check if this \
vector layer is open in another program." + error)
                    lock.break_lock()   
                    return

try: 
                    self.provider.deleteFeatures( pyList )
                except (WindowsError, OSError, IOError):
                    QtGui.QMessageBox.warning(self, "Failed to save:", "Please check if this \
vector layer is open in another program." + error)
                    return


try:
                    f = open(vfile, 'rb')
                    f.close()
                except IOError, e:
                    error = unicode(e)

lockFile = vfile + ".lckchk"
                error = None
                if(os.path.exists(lockFile)):
                    os.remove(lockFile)
                try:
                    os.rename(vfile, lockFile)
                    time.sleep(1)
                    os.rename(lockFile, vfile)
                except WindowsError, e:
                    error = unicode(e)
                    QtGui.QMessageBox.warning(self, "Failed to save:", "Please check if this \
vector layer is open in another program." + error)
                    return

try: # open file and read
            scenario.read(self.info)
        except (IOError, OSError), e:
            error = unicode (e)
        finally:
            if scenarioFilePath:
                scenario = None
            if error:
                QtGui.QMessageBox.warning(self, "File Error", error)

    def updateStatusBar(self):
        capture_string = QtCore.QString(self.scenarioFileName)
        self.statusBar.showMessage(capture_string, 8000)
''' save as dialog code '''
qd = QtGui.QFileDialog()
        filter_str = QtCore.QString("CAPS Scenario*.cap *.cap)\nAll Files(*)")
        # get the path to the directory for the saved file Python
        dir = os.path.dirname("./data/Scenarios/") \
        # change the QString to unicode so that Python can slice it for the directory name 
        scenarioFileName = unicode(qd.getSaveFileName(self, QtCore.QString("New Scenario"),
                                            dir, filter_str))
        # Check for cancel
        if len(scenarioFileName) == 0:
            return
        
        # remember the opened filename (Python unicode)
        self.scenarioFileName = scenarioFileName
        # add filename to statusbar with 8 sec. timeout
        capture_string = QtCore.QString(scenarioFileName)
        self.statusBar.showMessage(capture_string, 8000)
        self.info = QtCore.QFileInfo(QtCore.QString(scenarioFileName))
        # write the project information to a file using QgsProject
        self.scenario = QgsProject.instance()
        self.scenario.write(self.info)
        # create an associated directory to store the scenario's editing files
        directoryName = self.info.completeBaseName()
        QtCore.QDir().mkdir("./data/Scenarios/" + directoryName)

identify tool
res, ident = rlayer.identify(QgsPoint(15.30,40.98))
for (k,v) in ident.iteritems():
  print str(k),":",str(v)



extent = self.activeVLayer.extent()
extent.scale(1.05)
self.canvas.setExtent(extent)


>>> x = [1, 2, 3, 4, 5, 6, 7, 8]
>>> y = [4, 7, 9]
>>> list(set(x) - set(y))
[1, 2, 3, 5, 6, 8]


self.chkEditMode(callingAction)
if self.appStateChanged("startingEditing") == "Cancel":.destroy(True, True)

        
 # this block of code will only handle toggle type tools 
        # that are part of the "toolGroup." The "editingStopped"
        # callingAction gets handled below.
        #(select features, add points, add lines, add polygons)
        '''toolAction = None
        if not self.toolGroup.checkedAction() == None:
            print "setting toolGroup.checkedAction name"
            toolAction = self.toolGroup.checkedAction().objectName()
        print "toolAction = " + str(toolAction)'''
        
        if toolAction == "mpActionSelectFeatures":
            # The line of code below is for the bizarre situation where all tool group actions been
            # set to unchecked when a raster was loaded but the "self.toolGroup.checked()" 
            # Qt method still has the value "mpActionSelectFeatures" !!! really bizarre!
            # If we are loading a raster or we have and activeRLayer or the VLayer = None
            # then chkSelectState has already been called by either 
            # removeCurrentLayer, legendMousePress, addVector or addRaster.
            # So, no need to call chkSelectState again just return.
            if self.layerType == 1 or self.activeRLayer or self.activeVLayer == None:
                return
            # So, we must be working with a vector layer
            print "length of selected features " + str(len(self.activeVLayer.selectedFeatures()))
            # if there are no selected features, no need to prompt the user.
            if len(self.activeVLayer.selectedFeatures()) == 0:
                return
            elif self.chkSelectState(callingAction) == "Cancel":
                return "Cancel"
        elif toolAction == "mpActionAddPoints":
            # this is for the bizarre situation where the tool button has been
            # set to unchecked when the raster was loaded but "self.toolGroup.checked 
            # action still has the value "mpActionAddPoints" !!! really bizarre!
            if self.layerType == 1 or self.activeRLayer or self.activeVLayer == None:
                            elif self.editDirty == False:
                return
            elif self.toolAddPoints.numberFeaturesAdded() == 0:
                return
            elif self.chkAddPointsState(callingAction) == "Cancel":
                return "Cancel"
        
        
      
        
        
        self.legend.blockSignals(True)
        provider.reloadData()
        self.activeVLayer.removeSelection(False)
        ''' Add the new feature and display '''
        provider.reloadData
        provider = self.vlayer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(self.qgsPoint))
        feat.setAttributeMap(attributes)
        # the 0 and 1 represent the field numbers
        feat.setAttributeMap({0 : QtCore.QVariant(5), 1 : QtCore.QVariant("test")})
        this actually writes the added point to disk
        provider.addFeatures([ feat ])

'''old restoreLegendState code and my first attempts at model view'''
print type(self.legend.selectionModel())
        self.oldSelection is a QModelIndex 
        legend.selectionModel() returns a QItemSelectionModel class'''
        '''indexes = self.legend.selectionModel().selectedIndexes()
        for ind in indexes:
        text = QtCore.QString("(%1,%2)").arg(ind.row()).arg(ind.column())
        print QtCore.QString("(%1,%2)").arg(ind.row()).arg(ind.column())
        self.legend.model().setData(ind, text)
        indexMaker = QtGui.QStandardItemModel.index()
        topLeft = indexMaker.createIndex(0,0)
        selection = QtGui.QItemSelection(topLeft, oldSelection)
        self.legend.selectionModel().select(selection, QtGui.QItemSelectionModel.Select)
        self.legend.repaint()
        self.legend.selectionModel().clearSelection()

'''Check what type of symbol renderer the vector layer is using'''
if self.vlayer.isUsingRendererV2():
    # new symbology - subclass of QgsFeatureRendererV2 class
    #rendererV2 = self.vlayer.rendererV2()
    print "V2"
else:
    # old symbology - subclass of QgsRenderer class
    #self.vlayer = self.vlayer.renderer()
    print "V1"

'''some work on writing shapfiles to disk'''
print " Write shapefile to disk "
crs = self.provider.crs()
fields = self.provider.fields()
writer = QgsVectorFileWriter("test_points.shp", "UTF-8", fields, QGis.WKBPoint, crs)
if writer.hasError() != QgsVectorFileWriter.NoError:
    print "Error when creating shapefile: ", writer.hasError()
print writer.hasError()

'''example of QgsVertexMarker'''
def markPoint(self, point):
        # display the clicked point on the screen
        marker = QgsVertexMarker(self.canvas)
        transform = self.canvas.getCoordinateTransform()
        self.qgspoint = transform.toMapCoordinates(point.x(), point.y())
        marker.setPenWidth(2)
        marker.setCenter(self.qgspoint)

'''example of intersects'''
def __getIdFeaturesIntersect(self, rect, lyr):
    prov = lyr.dataProvider()
    allAttrs = prov.attributeIndexes()
    prov.select(allAttrs, core.QgsRectangle())
    idInSpatialIndex = self.__createIndex(prov).intersects(rect)
    prov.rewind()
    ids = []
    feat = core.QgsFeature()
    for id in idInSpatialIndex:
      prov.featureAtId(int(id), feat, True)
      if feat.geometry().intersects(rect):
        ids.append(int(id)) 
    return ids

''' cursor '''
self.canvas.setCursor(cursor)
self.canvas.unsetCursor(cursor)

'''make circle ??'''
self.center = self.toMapCoordinates(e.pos())
self.rb=QgsRubberBand(self.canvas,True)
rbcircle(self.rb,self.center,self.center,40)


'''both of these worked in selectfeatures.py
 when mainwindow had a variable self.test'''

print  parent.test
print  self.mainwindow.test

'''Add Path to system path''' 
sys.path.insert(0, "path")

'''Return prefixPath'''
QgsApplication.prefixPath()

'''Exit QGis'''
QgsApplication.exitQgis()

'''get the extent as QgsRectangle'''
layer = "some layer"
layerExtent = layer.extent()
# extends a little bit the layer extent to be sure to get all features ( as point in the frontier)
layerExtent.scale(1.1, layerExtent.center())
# select the features in this rectangle ie all features
layer.select(layerExtent, True)
        
'''generic message box'''
self.mb = QtGui.QMessageBox()
title = QtCore.QString("Error")
self.mb.setWindowTitle(title)
txt = QtCore.QString("You can only select features from a vector layer.\
Please select a vector layer in the layer panel and click 'Select Features' again.")
self.mb.setText(txt)
self.mb.exec_()