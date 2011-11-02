'''
Created on Jul 20, 2011

@author: urbanec
'''
# from qgis/python/plugins/mapserver_export

project = QgsProject.instance()
    # question: save project on loading export dialog?
    if project.isDirty():
      msg = "Save project to \"" + project.fileName() + "\" before exporting?\nOnly the last saved version of your project will be exported."
      if project.fileName()=="":
        msg = "Please save project before exporting.\nOnly saved projects can be exported."
      if forUnload:
        msg = "Save project first?\nAfter saving, this project will be unloaded."
      shouldSave = QMessageBox.question(self.dlg, "Save?", msg,
                    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
      if shouldSave == QMessageBox.Yes:
        if project.fileName().size() == 0:
          # project has not yet been saved:
          saveAsFileName = QFileDialog.getSaveFileName(self.dlg,
                      "Save QGIS Project file as...", ".",
                      "QGIS Project Files (*.qgs)", "Filter list for selecting files from a dialog box")
          # Check that a file was selected
          if saveAsFileName.size() == 0:
            QMessageBox.warning(self.dlg, "Not saved!", "QGis project file not saved because no file name was given.")
            # fall back to using current project if available
            self.dlg.ui.txtQgisFilePath.setText(project.fileName())
          else:
            if not saveAsFileName.trimmed().endsWith('.qgs'):
              saveAsFileName += '.qgs'
            self.dlg.ui.txtQgisFilePath.setText(saveAsFileName)
            project.setFileName(saveAsFileName)
            project.write()
        else:
          project.write()
        #project ok now
        return True
      elif shouldSave == QMessageBox.No and forUnload:
        # unloading a non saved project: just leave ...
        return True
      elif shouldSave == QMessageBox.No:
        # users does not want to save project, but has to because only saved projects can be exported
        return False
      elif shouldSave == QMessageBox.Cancel:
        # user cancelled
        return False
    else: 
      # project saved and not dirty
      return True