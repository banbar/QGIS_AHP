from PyQt5.QtWidgets import (QDialog)
from PyQt5.QtCore import QStandardPaths
import os

from ..utilities.uihelpers import get_ui_class
from ..models.project import Project
import json
from PyQt5.QtWidgets import QMessageBox

class CreateOrOpenProjectDialog(QDialog, get_ui_class('createOrOpenProjectDialog.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreateOrOpenProjectDialog, self).__init__(parent)
        self.setupUi(self)
        self.project_file_tb.setFilter("AHP Project Files (*.ahp)")
        self.connectSignalsSlots()
        self.raed_last_proj_file_path_from_cache_file()

    def connectSignalsSlots(self):
        self.createProject_btn.clicked.connect(self.createProject)
        self.openProject_btn.clicked.connect(self.openProject)

    def createProject(self):
        project_file_path = self.new_project_file_tb.filePath()
        if project_file_path is None or project_file_path == "" or not project_file_path.endswith(".ahp"):
            QMessageBox.warning(None, "Warning", "Please create a *.ahp file to save the project")
            return
        
        self.project = Project()
        self.project.project_file = project_file_path
        self.accept()
        
    def openProject(self):
        project_file_path = self.project_file_tb.filePath()
        if project_file_path is None or project_file_path == "" or not project_file_path.endswith(".ahp"):
            QMessageBox.warning(None, "Warning", "Please select a *.ahp file to open the project")
            return
        
        with open(self.project_file_tb.filePath(), "r") as file:
            json_string = file.read()
            self.project = Project(dict=json.loads(json_string),proj_file=self.project_file_tb.filePath())

        self.write_last_proj_file_path_to_cache_file(self.project_file_tb.filePath())
        
        self.accept()

    def get_cache_file_path(self, file_name):
        # Get the app-specific writable directory
        settings_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        
        # Ensure the directory exists
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
        
        # Return the full path to the cache file
        return os.path.join(settings_dir, file_name)
    
    def write_last_proj_file_path_to_cache_file(self, proj_file):
        with open(self.get_cache_file_path("cache_file"), "w") as file:
            print(f"Cache file will be saved to: {file}")
            file.write(proj_file)

    def raed_last_proj_file_path_from_cache_file(self):
        try:
            cache_file = self.get_cache_file_path("cache_file")
            if os.path.exists(cache_file):
                with open(cache_file, "r") as file:
                    path = file.readline()
                    print(path)
                    self.project_file_tb.setFilePath(path)
        finally:
            return
