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
import os, shutil

setupPath = "C:/beta"
workPath = "C:\egit_repositories\CAPS-Scenario-Builder\CAPS_Scenario_Builder\src"
workPathMain = workPath + "\Main"
workPathTools = workPath + "\Tools"
# miscFiles = ["caps_setupexe.py", "CAPS_splash.png", "config.py", "make_setupexe.py", "resources_rc.py", "setup_program_icon.ico"]
# To expose config.py, comment out the miscFiles above and use the one below.
miscFiles = ["caps_setupexe_config.py", "CAPS_splash.png", "config.py", "make_setupexe_config.py", "resources_rc.py", "setup_program_icon.ico"]

def getFilePathsInDirectory(path):
    list = os.listdir(path)
    newList = []
    for name in list:
        if ".pyc" not in name:
            os.path.join(path, name)
            newList.append(os.path.join(path, name))
    return newList        
    
mainFiles = getFilePathsInDirectory(workPathMain)
toolsFiles = getFilePathsInDirectory(workPathTools)

os.mkdir(setupPath)
dstMain = setupPath + "\Main"
os.mkdir(dstMain)
dstTools = setupPath + "\Tools"
os.mkdir(dstTools)

for name in miscFiles:
    src = os.path.join(workPath, name)
    if name == 'caps_setupexe.py' or name == 'caps_setupexe_config.py':
        name = 'caps.py'
    dst = os.path.join(setupPath, name)
    print "misc src path is " + src
    print "misc dst path is " + dst
    shutil.copyfile(src, dst)

for path in mainFiles:
    dst = os.path.join(dstMain, os.path.basename(path))
    print "Main src is " + path
    print "Main dst is " + dst
    shutil.copyfile(path, dst)

for path in toolsFiles: shutil.copyfile(path, os.path.join(dstTools, os.path.basename(path)))
