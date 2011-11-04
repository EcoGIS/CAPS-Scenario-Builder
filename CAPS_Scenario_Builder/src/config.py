# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
#
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPLv3
# 
# This file is part of CAPS.

#CAPS is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#CAPS is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with CAPS.  If not, see <http://www.gnu.org/licenses/>..
#-----------------------------------------------------------------------
from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem

############################################################################################
''' APPLICATION CONFIGURATION '''
############################################################################################
''' 
The following are variables that might change over time.
They can be edited by changing values here.
Changing field labels, field values and field names will be reflected in 
the "Add Attributes" dialog and the editing shapefiles created for the 
various scenario change types.
''' 
   
# Paths to important files.  These cannot change without altering
# the application installer.
dataDirectoryPath = u"./data/"
baseLayersPath = u"./data/base_layers/"
scenariosPath = u"./scenarios/"
scenarioExportsPath = u"./Exported Scenarios/"

# MA State Plane coordinate system used by MassGIS
crs = QgsCoordinateReferenceSystem(26986, QgsCoordinateReferenceSystem.EpsgCrsId)
rectExtentMA = QgsRectangle(32000, 780000, 330000, 965000)



''' Labels for the combo boxes in the "Add Attributes" dialog '''
# If you add a new field label here, it will create a corresponding combo box
# in the "Add Attributes" dialog for the corresponding scenarioType. A new "field values" 
# list for the new combo box's drop down list must also be added below. In addition, 
# you must add a new field name to the fieldNames list below, so the field will be 
# added to the editing layer attribute table when it is created on the fly. 
# Finally, you need to add the values to be entered in the attribute table to the valuesDictionaryList 
# THE ORDER WITHIN THE LISTS IS CRITICAL, SINCE THEY ARE LOOPED THROUGH AND MATCHED
# Of course, any old scenarios the user has stored that use the editing layer that 
# has been modified will become obsolete.  The users would need to be notified of this.
fieldLabels0 = ['Aquatic crossing score:']
fieldLabels1 = ['Aquatic crossing score:']
fieldLabels2 = ['Terrestrial crossing score:']
fieldLabels3 = ['Tidal Restriction severity:']
fieldLabels4 = ['New road traffic rate:'] 
fieldLabels5 = ['Modified road traffic rate:']
fieldLabels6 = ['Land cover class:']

''' Field values for the comboBox dropdown lists '''
# If a fieldLabel is added above, a python list [] of field values for the
# new combobox must be added, in the proper position, to the corresponding 
# "list of lists" here.
fieldValues0 = [['', 'Full passage', 'Minor barrier', 'Moderate barrier', 'Significant barrier', 
                 'Severe barrier']]
fieldValues1 = [['', 'Complete removal/full passage', 'Fishway/breached dam', 'Eel passage only',
                  'Full barrier']]
fieldValues2 = [['', 'Full passage (bear, moose)', 'Large animals (fox, coyote, fisher, bobcat, otter)', 
'Medium animals (rabbit, skunk, mink, opossum, raccoon)', 
'Small animals (amphibians, reptiles, mice, voles, chipmunk, weasel)', 'No passage structure']]
fieldValues3 = [['', 'No restriction', 'Minor restriction', 'Moderate restriction', 'Severe restriction']]
fieldValues4 = [['','none(closed road; 0 cars/day)', 'very low(tiny road; 100 cars/day)',
    'low(minor road; 800 cars/day)', 'medium(collector; 2500 cars/day)',
    'medium-high(secondary highway; 5000 cars/day)', 'high(primary highway; 10,000 cars/day)', 
    'extreme(expressway; >40,000 cars/day)'], ['', '4tc1', 'tc2']] 
fieldValues5 = [['','none(closed road; 0 cars/day)', 'very low(tiny road; 100 cars/day)',
    'low(minor road; 800 cars/day)', 'medium(collector; 2500 cars/day)',
    'medium-high(secondary highway; 5000 cars/day)', 'high(primary highway; 10,000 cars/day)', 
    'extreme(expressway; >40,000 cars/day)'], ['5mc1', 'mc2']]
fieldValues6 = [['', 'Commercial', 'Industrial', 'Residential', 'Cropland', 'Water']]

# These are lists of dictionaries that contain the values for the various "fieldValues" displayed
# in the combo box widgets. 
valuesDictionaryList0 = [{'': 'empty', 'Full passage': '1.0', 'Minor barrier': '0.8', 
                          'Moderate barrier': '0.6',
                           'Significant barrier': '0.4', 'Severe barrier': '0.2'}]
valuesDictionaryList1 = [{'': 'empty', 'Complete removal/full passage': '1.0', 
                          'Fishway/breached dam': '0.6', 'Eel passage only': '0.2',
                         'Full barrier': '0.0'}]
valuesDictionaryList2 = [{'': 'empty', 'Full passage (bear, moose)': '1.0', 
                          'Large animals (fox, coyote, fisher, bobcat, otter)': '0.75', 
                          'Medium animals (rabbit, skunk, mink, opossum, raccoon)': '0.5', 
                          'Small animals (amphibians, reptiles, mice, voles, chipmunk, weasel)': 
                          '0.2', 'No passage structure': '0.0'}]
valuesDictionaryList3 = [{'': 'empty', 'No restriction': '0 m', 'Minor restriction': '0.5 m', 
                          'Moderate restriction': '1.0 m', 'Severe restriction': '2.0 m'}]
valuesDictionaryList4 = [{u'': 'empty', u'none(closed road; 0 cars/day)': '0.0', 
                          u'very low(tiny road; 100 cars/day)': '0.025', u'low(minor road; 800 cars/day)': 
                          '0.2', u'medium(collector; 2500 cars/day)': '0.5', 
                          u'medium-high(secondary highway; 5000 cars/day)': '0.75',     
                          u'high(primary highway; 10,000 cars/day)': '0.94',
                            u'extreme(expressway; >40,000 cars/day)': '1.0'}]
valuesDictionaryList5 = [{'': 'empty', 'none(closed road; 0 cars/day)': '0.0', 
                          'very low(tiny road; 100 cars/day)': '0.025', 'low(minor road; 800 cars/day)': 
                          '0.2', 'medium(collector; 2500 cars/day)': '0.5', 
                          'medium-high(secondary highway; 5000 cars/day)': '0.75', 
                          'high(primary highway; 10,000 cars/day)': '0.94', 
                           'extreme(expressway; >40,000 cars/day)': '1.0'}]
valuesDictionaryList6 = [{'': 'empty', 'Commercial': '1', 'Industrial': '2', 'Residential': '10', 
                          'Cropland': '30', 'Water': '50'}]

''' Field names, which appear in the editing layer attribute table,
    for each scenario change type.
'''     
# If a new label, combo box and list of field values has been created above, 
# a new field name must be added, in the correct position, in the corresponding 
# list here. Please note that you MUST NOT delete or change the list position of the id, 
# altered, deleted or description field names. The values for these fields are added 
# programmatically and depend on their positions in the list.

inputFieldNames0 = ['cross_id', 'c_altered', 'c_deleted', 'c_aqua_scr', 'c_describe'] 
inputFieldNames1 = ['dam_id', 'd_altered', 'd_deleted', 'd_aqua_scr', 'd_describe']
inputFieldNames2 = ['wildlf_id', 'w_altered', 'w_deleted', 'terr_scr', 'w_describe']
inputFieldNames3 = ['restr_id', 'r_altered', 'r_deleted', 'r_rest_scr', 'r_describe']
inputFieldNames4 = ['newrd_id', 'newrd_rate', 'nrd_descr']
inputFieldNames5 = ['modrd_id', 'modrd_rate', 'mrd_descr']
inputFieldNames6 = ['ldcvr_id', 'ldcvr_cls', 'l_describe']

''' The fields lists for the editing shapefiles '''
# no changes should be made to the code under this heading
editPointsFields = (inputFieldNames0 + inputFieldNames1
                         + inputFieldNames2 + inputFieldNames3) # 21 fields
editLinesFields = inputFieldNames4 # 4 fields
editPolygonsFields = inputFieldNames5 + inputFieldNames6 # 7 fields

# The list of scenario change types for populating the "Edit Scenario" dialog.
# Changing these values will only change the names shown in the "Scenario Types" dialog
# Adding a value here will NOT create a new scenario type complete with base layers
# and an editing shapefile.
scenarioTypesList = ["Road stream crossing (points)", "Dams (points)",  
                          "Wildlife crossing (points)", "Tidal restriction (points)",
                          "Add roads (lines)", "Modify roads (polygons)",        
                          "Land cover change (polygons)"]

# The below are used in varios places to check that correct layers are active for editing operations.
# The spelling of these names can be changed, but not the number of them.
pointBaseLayers = ["base_crossings", "base_dams", "base_wildlife",
                             "base_tidal_restrictions"]

slowLoadingLayers = ["base_crossings"]

lineBaseLayersBaseNames = ["base_traffic"]
polygonBaseLayersBaseNames = ["base_traffic", "base_land"]

# names of just the editing layers (used in Main.legend.removeCurrentLayer()
# and Main.mainwindow.deleteFeatures()).  These should not be changed unless
# major changes are made to the application.
editLayersBaseNames = ["edit_scenario(points)", "edit_scenario(lines)",
                       "edit_scenario(polygons)"]

# These are the lists of layers that open when the app is first opened
# or when the "New Scenario" action is clicked.  The orienting layers that
# open can be changed by changing the lists below, assuming they exist in the 
# config.baseLayersPath folder. Layers open in the order they appear in the lists.
# Raster layers open before vector layers, and the layers will be stacked in 
# the opening order with the first layer opened on the bottom in the layer panel 
# (i.e. legend).
orientingRasterLayers = ["USGS.SID", "base_land.tif", "base_streams.tif", "base_traffic.tif"]
orientingVectorLayers = ["base_towns.shp"]
allOrientingLayers = orientingRasterLayers + orientingVectorLayers

# Orienting base layer names can be added here to make them visible (i.e. checked)
baseLayersChecked = ["base_towns"]

# A list of the non-orienting base layers and editing layers. 
# Main.dlgscenariotypes.hideEditBaseLayers() uses this list to hide (uncheck) unneeded layers.
# Adding a name to this list will hide (uncheck) that layer if not needed when opening a
# new scenario edit type. 
hideEditLayers = ["edit_scenario(points)", "edit_scenario(lines)",
                       "edit_scenario(polygons)", "base_crossings", "base_dams",
                        "base_wildlife", "base_tidal_restrictions", "base_traffic"]

############################################################################################
