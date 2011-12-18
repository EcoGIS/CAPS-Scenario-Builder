<<<<<<< HEAD
This is the Beta version of CAPS_Scenario_Builder and is intended to be used by the CAPS project team members for purposes of testing and debugging, but anyone is welcome to use the program and submit issues. 
------------------------------------------------------------------------------- 
Please report any issues or bugs at.  

https://github.com/EcoGIS/CAPS-Scenario-Builder/issues/1

Please, make sure to include the Windows operating system you are using (including service pack number) and a detailed description of the issue so that I can duplicate it.

Some terminology that may make descriptions easier:

"base layer": Any layer in the base_layers folder.

"orienting base layer": USGS.SID, base_land.tif, base_streams.tif, base_traffic.tif, base_towns.shp

"scenario edit type": One of the 7 general types of edits that can be made. These are the 7 choices in the "Edit Scenario" dialog.

"editing layer": edit_scenario(points), edit_scenario(lines) or edit_scenario(polygons)

-------------------------------------------------------------------------------- 
Since there is no documentation yet, I expect that some people may be confused by some of the application's behavior. In general, only buttons that are usable in the current circumstances are active.  Buttons that cannot be used in the current circumstances are grayed out.  This serves to make it difficult for users to make mistakes that might result in submitting bad scenarios. It also serves to reduce the number of possibilities for user action and thus reduces the number of potential user errors that must be handled.
Here are a few notes that might help for folks unfamiliar with the app:
 
You can't edit rasters so no edit buttons will be active while a raster layer is selected, and since a raster doesn't have an attribute table, the "Open Vector Attribute Table" will be grayed out.

All editing actions, or changing the scenario edit type (i.e. dams, add roads etc.), require you to click the "Edit Scenario" button.

The modify features button will only be active if a point baselayer is selected. (i.e. base_culverts_bridges, base_dams, base_terrestrial_passage or base_tidal_restrictions).

To delete a feature on a point base layer or on an editing layer just select the feature and click "Delete Selected."

You must have an edit layer selected for the add points, lines or polygons buttons to be active.

All edits are stored in the three editing layers.  A red X in the edit_scenario(points) layer indicates a deleted point feature, red triangle indicates a modified point feature, and a simple point indicates a new feature.

The "Export Scenario" exports a scenario's changes in csv file format.

etc.....

Thanks,
=======
Description

The CAPS Scenario Builder will allow government officials, conservation groups 
and others to submit "scenarios" for proposed changes to land cover and 
infrastructure so that these changes can be assessed for their impact on 
ecological integrity. See the url below for more:
http://www.umass.edu/landeco/research/caps/caps.html

HOW TO INSTALL CAPS SCENARIO BUILDER

The specifications for CAPS Scenario Builder only require it to run on MS Windows. 
Because the app is written in Python, you can probably get it to run on nearly
any platform, but the instructions below are for MS Windows.

Install Requirements:  A working installation of QGIS-1.6.0
					   A copy of CAPS_Scenario_Builder.zip	

1) Download the contents of CAPS-Scenario-Builder.zip 
(from https://sourceforge.net/projects/osscripts/files/). 
 Note that this is the same code as found in the master branch at
 https://github.com/EcoGIS/CAPS-Scenario-Builder but includes
some rather large data files that are necessary to run the application. 

2) Unzip the files to C:\Caps_Scenario_Builder.  You may choose another insallation 
location, but you will need to alter the line 
"start "CAPS" /B pythonw "c:\caps\caps.pyw" 
in the file CAPS_copiapo.bat to point to your location.
   
3) If you don't have an existing installation of QGIS Copiapo,
   install using QGIS-1.6.0-Setup.exe (found at http://qgis.org/downloads/).
   
3) Make sure that the "SET OSGEO4W_ROOT=C:\PROGRA~1\QUANTU~1" line in the file 
   CAPS_copiapo.bat points to the installation folder (i.e. Quantum GIS Copiapo)
   
4) Click on CAPS_copiapo.bat to run CAPS Scenario Builder

I don't have the time right now to help with installation issues, so please don't
contact me about installation.  I will make a windows installer sometime in November
or early December, 2011 that should make the installation easy.

Thanks for your interest!
>>>>>>> refs/heads/master
Bob English
