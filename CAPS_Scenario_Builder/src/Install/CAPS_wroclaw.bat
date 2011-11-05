@echo off

SET OSGEO4W_ROOT=C:\PROGRA~1\QUANTU~2
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
SET qgis_prefix=%OSGEO4W_ROOT%\apps\qgis

@echo off

SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins\1.8

@echo off


REM SET %PYTHONPATH%; PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin\;%OSGEO4W_ROOT%\apps\grass\grass-6.4.1\lib
start "CAPS_Scenario_Builder" /B python "c:\CAPS_Scenario_Builder\caps.py" %*
rem start "CAPS_Scenario_Builder" /B pythonw "c:\CAPS_Scenario_Builder\caps.pyw" %*
rem start "Quantum GIS" /B "%OSGEO4W_ROOT%"\apps\qgis\bin\qgis.exe %*
