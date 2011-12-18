@echo off

SET OSGEO4W_ROOT=C:\PROGRA~1\QUANTU~1
SET qgis_prefix=%OSGEO4W_ROOT%\apps\qgis
PATH=%OSGEO4W_ROOT%\bin;%OSGEO4W_ROOT%\apps\qgis\bin\;%PATH%
call "%OSGEO4W_ROOT%"\etc\ini\gdal.bat
call "%OSGEO4W_ROOT%"\etc\ini\libgeotiff.bat
call "%OSGEO4W_ROOT%"\etc\ini\proj.bat
call "%OSGEO4W_ROOT%"\etc\ini\python.bat

@echo off

call "%OSGEO4W_ROOT%"\bin\gdal17.bat
SET PYTHONPATH=%OSGEO4W_ROOT%\bin;%OSGEO4W_ROOT%\apps\qgis\python;%OSGEO4W_ROOT%\apps\Python25\Lib\site-packages;%PYTHONPATH%
start "CAPS_Scenario_Builder" /B pythonw "c:\CAPS_Scenario_Builder\caps.pyw"

@echo off
