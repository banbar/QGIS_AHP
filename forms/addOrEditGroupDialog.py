from PyQt5.QtWidgets import (QDialog)
from PyQt5.QtWidgets import QMessageBox

from ..utilities.uihelpers import get_ui_class
from ..models.criterion import Criterion
import copy

class AddOrEditGroupDialog(QDialog, get_ui_class('addOrEditGroupDialog.ui')):
    def __init__(self, project, parent=None):
        """Constructor."""
        super(AddOrEditGroupDialog, self).__init__(parent)
        self.setupUi(self)
        self.criterion = Criterion()
        self.criterion.is_group = True
        self.project = project
        self.populate_comboboxes()
        self.connect_signals_slots()
        
    def populate_comboboxes(self):
        self.populate_parent_group_cb()
                
    def connect_signals_slots(self):
        self.create_group_btn.clicked.connect(self.create_group)
        self.criterion_name_tb.textEdited.connect(self.criterion_name_changed)
        self.parent_group_cb.currentTextChanged.connect(self.parent_group_changed)

    def edit_criterion(self, criterion:Criterion):
        """updates the ui with the given criterion"""
        self.criterion = copy.deepcopy(criterion)
        self.criterion_name_tb.setText(criterion.criterion_name)
        self.parent_group_cb.setCurrentIndex(self.project.get_criteria_group_names().index(criterion.parent_group))
        self.create_group_btn.setText("Update Group")
        self.setWindowTitle("Update Group")     
        self.criterion_name_tb.setEnabled(False)

    def criterion_name_changed(self, criterion_name):
        """set the selected value to Criterion object"""
        self.criterion.criterion_name = criterion_name

    def parent_group_changed(self, parent_group_name):
        """set the selected value to Criterion object"""
        self.criterion.parent_group = parent_group_name

    def populate_parent_group_cb(self):
        for group in self.project.get_criteria_group_names():
            self.parent_group_cb.addItem(group, group)

    def create_group(self):
        """Closes the dialog as the criterion is all set"""
        
        for criterion in self.project.criteria_definitions:
            if criterion.criterion_name == self.criterion.criterion_name:                        
                QMessageBox.warning(None, "Warning", "There is another criterion with the same name")
                return
            
        self.accept()