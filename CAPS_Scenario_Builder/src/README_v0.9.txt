This is the Beta version 0.9 of CAPS_Scenario_Builder and is intended to be used by the CAPS project team members for purposes of testing and debugging, but anyone is welcome to use the program and submit issues. 

For those users who have a version that exposes config.py, that file can be found in install directory/CAPS Scenario Builder/lib/shardlib.  Please note that shardlib is a zip archive and must be opened with a zip utility.  After editing config.py, you must replace the old version in the shardlib zip archive with the edited version.
 
-------------------------------------------------------------------------------
 
Please report any issues or bugs at.  

https://github.com/EcoGIS/CAPS-Scenario-Builder/issues/1

Please, make sure to include the Windows operating system you are using (including service pack number) and a detailed description of the issue.  If a bug does occur, please copy the log files from install directory/log and then close the application. Please send the log files to bobengl@gmail.com along with the issue number from github.

Some terminology that may make descriptions easier:

"base layer": Any layer in the base_layers folder.

"orienting base layer": USGS.SID, base_land.tif, base_streams.tif, base_traffic.tif, base_towns.shp

"scenario edit type": One of the 7 general types of edits that can be made. These are the 7 choices in the "Edit Scenario" dialog.

"editing layer": edit_scenario(points), edit_scenario(lines) or edit_scenario(polygons)

-------------------------------------------------------------------------------- 

Please see the CAPS Scenario Builder Users Manual.pdf at github in the git root for more information.

Thanks,
Bob English