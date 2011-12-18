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
Bob English