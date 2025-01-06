from .addOrEditCriterionDialog import AddOrEditCriterionDialog
from .addOrEditGroupDialog import AddOrEditGroupDialog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ..utilities.uihelpers import get_ui_class

class CriteriaDefinitionWidget(QtWidgets.QWidget, get_ui_class('criteriaDefinition.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(CriteriaDefinitionWidget, self).__init__(parent)
        self.setupUi(self)
        self.relatedLabel = parent.criteria_lbl
        self.project = parent.project
        self.load_project()
        self.connect_signals_slots()

    def stylize_table(self):
        self.criteria_tbl.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Criteria Name"))
        self.criteria_tbl.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Is Group"))
        self.criteria_tbl.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Parent Group"))
        self.criteria_tbl.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Data Type"))
        self.criteria_tbl.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("File Name"))
        self.criteria_tbl.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem("Algorithm"))
        self.criteria_tbl.resizeColumnsToContents()
        self.criteria_tbl.horizontalHeader().setSectionResizeMode(4, 1)
        self.edit_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)

    def load_project(self):
        if self.project is not None:
            self.update_criteria_table()
    
    def connect_signals_slots(self):
        self.add_btn.clicked.connect(self.open_add_criteria_dialog)
        self.add_group_btn.clicked.connect(self.open_add_group_dialog)
        self.edit_btn.clicked.connect(self.open_edit_criteria_dialog)        
        self.remove_btn.clicked.connect(self.remove_criterion)
        self.criteria_tbl.itemSelectionChanged.connect(self.criteria_tbl_selection_changed)

    def open_add_criteria_dialog(self):
        """Opens a blocking dialog to create a new criterion"""
        dialog = AddOrEditCriterionDialog(self.project)
        if dialog.exec():
            if(dialog.criterion is not None):
                print("criterion created")
                self.project.criteria_definitions.append(dialog.criterion)
                self.update_criteria_table()

                return
            else:
                print("dialog returned null")
        else:
            print("dialog rejected")
            
    def open_add_group_dialog(self):
        """Opens a blocking dialog to create a new group"""
        dialog = AddOrEditGroupDialog(self.project)
        if dialog.exec():
            if(dialog.criterion is not None):
                self.project.criteria_definitions.append(dialog.criterion)
                self.update_criteria_table()

                return
            else:
                print("group dialog returned null")
        else:
            print("group dialog rejected")

    def open_edit_criteria_dialog(self):
        """Opens a blocking dialog to edit a criterion"""
        selected_index = self.get_selected_index_of_criterion()
        criteria_to_edit = self.project.criteria_definitions[selected_index]

        dialog = AddOrEditGroupDialog(self.project, self) if criteria_to_edit.is_group else AddOrEditCriterionDialog(self.project, self) 
        dialog.edit_criterion(criteria_to_edit)
        if dialog.exec():
            if(dialog.criterion is not None):
                print("criterion created")
                old_criterion_name = self.project.criteria_definitions[selected_index].criterion_name
                self.project.criteria_definitions[selected_index] = dialog.criterion
                self.project.update_pairwise_comparisons(old_criterion_name, dialog.criterion.criterion_name)
                self.update_criteria_table()

                return
            else:
                print("dialog returned null")
        else:
            print("dialog rejected")

    def remove_criterion(self):
        selected_index = self.get_selected_index_of_criterion()
        if self.project.remove_criterion(selected_index):
            self.update_criteria_table()
        else:
            QMessageBox.warning(None, "Warning", "You need to remove the subcriteria from the group first.")
    
    def update_criteria_table(self):
        # display whole table instead of adding one line
        self.criteria_tbl.clear()
        row_index = 0
        for criterion in self.project.criteria_definitions:
            # do not show Main group in the table
            if criterion.criterion_name == "Main":
                continue
            self.criteria_tbl.setRowCount(row_index + 1)
            self.criteria_tbl.setItem(row_index, 0, QtWidgets.QTableWidgetItem(criterion.criterion_name))
            self.criteria_tbl.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(criterion.is_group)))
            self.criteria_tbl.setItem(row_index, 2, QtWidgets.QTableWidgetItem(criterion.parent_group))
            if not criterion.is_group:
                self.criteria_tbl.setItem(row_index, 3, QtWidgets.QTableWidgetItem(criterion.data_type.value))
                self.criteria_tbl.setItem(row_index, 4, QtWidgets.QTableWidgetItem(criterion.input_file))
                self.criteria_tbl.setItem(row_index, 5, QtWidgets.QTableWidgetItem(criterion.algorithm.value))
            row_index += 1

        self.stylize_table()
        self.project.save_to_file()
        
    def criteria_tbl_selection_changed(self):
        if self.criteria_tbl.selectedIndexes().__len__() == 0:
            self.edit_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
        else:
            self.edit_btn.setEnabled(True)
            self.remove_btn.setEnabled(True)

    def get_selected_index_of_criterion(self):
        return self.criteria_tbl.selectedIndexes()[0].row() + 1