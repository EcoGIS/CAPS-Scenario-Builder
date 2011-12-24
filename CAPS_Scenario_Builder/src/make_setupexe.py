# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# Original sources:
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
# Modified for CAPS Scenario Builder:
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPLv3
# 
# This file is part of CAPS.

# CAPS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CAPS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with CAPS.  If not, see <http://www.gnu.org/licenses/>..
# 
#---------------------------------------------------------------------

''' 
    A setup script showing how to extend py2exe.

    In this case, the py2exe command is subclassed to create an installation
    script for InnoSetup, which can be compiled with the InnoSetup compiler
    to a single file windows installer.

    By default, the installer will be created as dist\Output\setup.exe.
    
'''

from distutils.core import setup
import py2exe
import os

# Build tree of data_files of the form [dir, [py2exe data_files]], which is what distutils.setup() requires.
# The parameter "src" is the full path to the data files, and "base" is the part of the path that will
# be stripped off to leave only the directory names you want to see in the program installation directory.
# Modified from http://osdir.com/ml/python.py2exe/2006-02/msg00085.html and OpenOceanMap
def tree(base, src):
    #path = os.path.basename(src)
    list = [(root, map(lambda f: os.path.join(root, f), files)) for (root, dirs, files) in os.walk(os.path.normpath(src))]
    new_list = []
    for (root, files) in list:
    #print "%s , %s" % (root,files)
        #print "%s" % root
        #if len(files) > 0: #and file.count('.gitignore') == 0:
        new_files = []
        for file in files:
            if file.count('.gitignore') == 0 and file.count('test') == 0:
                new_files.append(file)    
        root = root[len(base):]
        new_list.append((root, new_files))
    return new_list
    
################################################################

class InnoScript:
    def __init__(self,
                 name,
                 lib_dir,
                 dist_dir,
                 windows_exe_files = [],
                 lib_files = [],
                 version = 0.8):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname="dist\\CAPSScenarioBuilder.iss"):
        self.pathname = pathname
        rootPath = "C:\Git_CAPS_Scenario_Builder\CAPS_Scenario_Builder\src"
        ofi = self.file = open(pathname, "w")
        
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi, r"VersionInfoVersion=%s" % self.version
        print >> ofi, r"VersionInfoCompany=University of Massachusetts: CAPS"
        print >> ofi, r"VersionInfoDescription=CAPS: Conservation Assessment and Prioritization System"
        print >> ofi, r"VersionInfoCopyright=University of Massachusetts: CAPS"
        print >> ofi, r"AppCopyright=Daystar Computing: Robert English"
        print >> ofi, r"InfoAfterFile=" + rootPath + r"\README.TXT"
        print >> ofi, r"LicenseFile=" + rootPath + r"\LICENSE.TXT"
        print >> ofi, r"WizardImageBackColor=clBlack"
        print >> ofi, r"WizardImageFile=" + rootPath + r"\images\setup_wizard_vert.bmp"
        print >> ofi, r"WizardSmallImageFile=" + rootPath + r"\images\setup_wizard_icon.bmp"
        print >> ofi, r"SetupIconFile=" + rootPath + r"\setup_program_icon.ico"
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi, r'Source: lib\QtSvg4.dll; DestDir: {app}\lib; Flags: ignoreversion'
        print >> ofi, r'Source: "' + rootPath + r'\README.TXT"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\copy.txt"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\RasterCategoryTable.htm"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\setup_program_icon.ico"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\CAPS_splash.png"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\vcredist_2005English_x86.exe"; DestDir: "{app}"'
        print >> ofi, r'Source: "' + rootPath + r'\vcredist_2008_x86.exe"; DestDir: "{app}"'
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"; WorkingDir: {app}; IconFilename: "{app}\setup_program_icon.ico"' % \
                  (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name
        print >> ofi
          
        print >> ofi, r"[Dirs]"
        print >> ofi, r'Name: "{app}\Scenarios"'
        print >> ofi, r'Name: "{app}\Exported Scenarios"'
        print >> ofi
        
        print >> ofi, r"[Run]"
        print >> ofi, r'Filename: "{app}\vcredist_2005English_x86.exe"; Description: "Install required system files"; Parameters: "/q:a /c:""VCREDI~3.EXE /q:a /c:""""msiexec /i vcredist.msi /qn"""" """'
        print >> ofi, r'Filename: "{app}\vcredist_2008_x86.exe"; Description: "Install required system files"; Parameters: "/q:a /c:""VCREDI~1.EXE /q:a /c:""""msiexec /i vcredist.msi /qn"""" """'
        
    def compile(self):
        try:
            import ctypes2
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################

from py2exe.build_exe import py2exe

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do its work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript("CAPS Scenario Builder",
                            lib_dir,
                            dist_dir,
                            self.windows_exe_files,
                            self.lib_files)
        print "*** creating the inno setup script***"
        script.create()
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

######################## py2exe setup options ########################################

zipfile = r"lib\shardlib"
#"excludes": ['backend_gtkagg', 'backend_wxagg'],
options = {"py2exe": {"compressed": 1, "optimize": 2, "includes": ['sip'], "dll_excludes": ['POWRPROF.dll'], 
          "excludes": ['backend_gtkagg', 'backend_wxagg'], "packages": ["qgis", "PyQt4"], "dist_dir": "dist"}}

# Note that I had to paste the file 'C:\Program Files\Quantum GIS Wroclaw\bin\lti_dsk.dll' into 
# the "C:\Program Files\Quantum GIS Wroclaw\apps\qgis\plugins" directory to get MrSID support to work.  py2exe 
# apparently missed that dll?
data_files = (tree("C:/Git_CAPS_Scenario_Builder/CAPS_Scenario_Builder/src/", "C:/Git_CAPS_Scenario_Builder/CAPS_Scenario_Builder/src/base_layers") + 
              tree('C:/Program Files/Quantum GIS Wroclaw/apps/qgis/', 'C:/Program Files/Quantum GIS Wroclaw/apps/qgis/plugins') + 
              tree('C:/Program Files/Quantum GIS Wroclaw/apps/qgis/', 'C:/Program Files/Quantum GIS Wroclaw/apps/qgis/resources') +
              tree('C:/Program Files/Quantum GIS Wroclaw/bin/', 'C:/Program Files/Quantum GIS Wroclaw/bin/gdalplugins/1.8') +
              tree('C:/Program Files/Quantum GIS Wroclaw/share/', 'C:/Program Files/Quantum GIS Wroclaw/share/gdal'))

              
setup(options = options, zipfile = zipfile, windows=[{"script": "caps.py", "icon_resources": [(1, "setup_program_icon.ico")]}],
    # 'cmdclass=' says to use the build_installer class, which is a subclassed py2exe build command
    cmdclass = {"py2exe": build_installer}, data_files = data_files)
