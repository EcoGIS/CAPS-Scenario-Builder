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
Bob English