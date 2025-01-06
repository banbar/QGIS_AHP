from ..models.enums.dataType import DataType
from ..models.enums.reclassificationMethod import ReclassificationMethod
from ..models.enums.rasterAlgorithm import RasterAlgorithm
from ..models.enums.vectorAlgorithm import VectorAlgorithm

from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.QtWidgets import QMessageBox

from .addSuitabilityRangeDialog import AddSuitabilityRangeDialog
from ..utilities.uihelpers import get_ui_class
from ..utilities.enumhelpers import enum_index_of
from ..models.criterion import Criterion
import copy

class AddOrEditCriterionDialog(QDialog, get_ui_class('addOrEditCriterionDialog.ui')):
    def __init__(self, project, parent=None):
        """Constructor."""
        super(AddOrEditCriterionDialog, self).__init__(parent)
        self.setupUi(self)
        self.criterion = Criterion()
        self.project = project
        self.populate_comboboxes()
        self.stylize_table()
        self.connect_signals_slots()
        self.edit_mode = False
        self.criterion_name_updated = False
        self.original_criterion_name = ""
        
    def populate_comboboxes(self):
        for member in DataType:
            self.data_type_cb.addItem(member.value, member.name)
        for member in ReclassificationMethod:
            self.reclass_method_cb.addItem(member.value, member.name)
        
        index_of_none = enum_index_of(ReclassificationMethod.NONE, ReclassificationMethod)
        self.reclass_method_cb.model().item(index_of_none).setEnabled(False)
        self.populate_algorithms_cb(self.criterion.data_type)
        self.populate_parent_group_cb()
                
    def connect_signals_slots(self):
        self.create_criterion_btn.clicked.connect(self.create_criterion)
        self.criterion_name_tb.textEdited.connect(self.criterion_name_changed)
        self.input_file_tb.fileChanged.connect(self.input_file_changed)
        self.data_type_cb.currentTextChanged.connect(self.data_type_changed)
        self.algorithm_cb.currentTextChanged.connect(self.algorithm_changed)
        self.reclass_method_cb.currentTextChanged.connect(self.reclass_method_changed)
        self.add_suitability_range_btn.clicked.connect(self.add_suitability_range)
        self.remove_suitability_range_btn.clicked.connect(self.remove_suitability_range)
        self.suitability_class_ranges_tbl.itemSelectionChanged.connect(self.suitability_class_ranges_tbl_selection_changed)
        self.parent_group_cb.currentTextChanged.connect(self.parent_group_changed)

    def edit_criterion(self, criterion:Criterion):
        """updates the ui with the given criterion"""
        self.criterion = copy.deepcopy(criterion)
        algorithm = criterion.algorithm
        self.criterion_name_tb.setText(criterion.criterion_name)
        self.parent_group_cb.setCurrentIndex(self.project.get_criteria_group_names().index(criterion.parent_group))
        self.input_file_tb.setFilePath(criterion.input_file)
        self.data_type_cb.setCurrentIndex(enum_index_of(criterion.data_type, DataType))
        criterion.algorithm = algorithm
        if criterion.data_type == DataType.RASTER:
            self.algorithm_cb.setCurrentIndex(enum_index_of(criterion.algorithm, RasterAlgorithm))
        elif criterion.data_type == DataType.VECTOR:
            self.algorithm_cb.setCurrentIndex(enum_index_of(criterion.algorithm, VectorAlgorithm))
        self.reclass_method_cb.setCurrentIndex(enum_index_of(criterion.reclassification_method, ReclassificationMethod))
        self.update_suitability_table()
        self.setWindowTitle("Update Criterion")
        self.create_criterion_btn.setText("Update Criterion")
        self.edit_mode = True
        self.original_criterion_name = self.criterion.criterion_name        
        self.criterion_name_tb.setEnabled(False)

    def criterion_name_changed(self, criterion_name):
        """set the selected value to Criterion object"""
        self.criterion.criterion_name = criterion_name
        self.criterion_name_updated = criterion_name != self.original_criterion_name

    def parent_group_changed(self, parent_group_name):
        """set the selected value to Criterion object"""
        self.criterion.parent_group = parent_group_name

    def input_file_changed(self, input_file):
        """set the selected value to Criterion object"""
        self.criterion.input_file = input_file

    def data_type_changed(self, data_type):
        """Different data type dictates different algorithms and file types to be selected. This function handles those"""
        
        # set the selected value to Criterion object
        self.criterion.data_type = DataType(data_type)
        self.populate_algorithms_cb(data_type)

    def populate_parent_group_cb(self):
        for group in self.project.get_criteria_group_names():
            self.parent_group_cb.addItem(group, group)

    def populate_algorithms_cb(self, data_type):
        # set allowed algorithms
        self.algorithm_cb.clear()
        if data_type == DataType.RASTER.value:
            for member in RasterAlgorithm:
                self.algorithm_cb.addItem(member.value, member.name)
            self.input_file_tb.setFilter("Raster Files (*.tif;*.tiff;*.jpeg;*.jpg;*.png;*.gif)")
        elif data_type == DataType.VECTOR.value:
            for member in VectorAlgorithm:
                self.algorithm_cb.addItem(member.value, member.name)
            self.input_file_tb.setFilter("Vector Files (*.shp)")
                
    def algorithm_changed(self, algorithm):
        """set the selected value to Criterion object"""
        if(algorithm == ""):
            return
        default_reclass_method_for_algo = ReclassificationMethod.MANUAL
        if self.criterion.data_type == DataType.RASTER:
            self.criterion.set_algorithm(RasterAlgorithm(algorithm))
        elif self.criterion.data_type == DataType.VECTOR:
            self.criterion.set_algorithm(VectorAlgorithm(algorithm))
            if self.criterion.algorithm == VectorAlgorithm.RESTRICT:
                default_reclass_method_for_algo = ReclassificationMethod.NONE
        self.update_reclass_method(default_reclass_method_for_algo)

    def update_reclass_method(self, reclassification_method):
        self.reclass_method_cb.setCurrentIndex(enum_index_of(reclassification_method, ReclassificationMethod))
        self.reclass_method_cb.setEnabled(reclassification_method != ReclassificationMethod.NONE)

    def reclass_method_changed(self, reclassification_method):
        """Only show the Suitability Class table if MANUAL is selected"""
        # set the selected value to Criterion object
        self.criterion.reclassification_method = ReclassificationMethod(reclassification_method)

        if reclassification_method == ReclassificationMethod.MANUAL.value:
            self.suitability_input_section.show()
        else:
            self.suitability_input_section.hide()

    def stylize_table(self):
        self.suitability_class_ranges_tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Min"))
        self.suitability_class_ranges_tbl.setHorizontalHeaderItem(1, QTableWidgetItem("Max"))
        self.suitability_class_ranges_tbl.setHorizontalHeaderItem(2, QTableWidgetItem("Value"))
        self.remove_suitability_range_btn.setEnabled(False)

    def add_suitability_range(self):
        dialog = AddSuitabilityRangeDialog()
        if dialog.exec():
            if(dialog.suitability_class_range is not None):
                print("suitability_class_range created")
                self.criterion.add_suitability_class_range(dialog.suitability_class_range)
                self.update_suitability_table()

                return
            else:
                print("dialog returned null")
        else:
            print("dialog rejected")

    def remove_suitability_range(self):
        selected_index = self.suitability_class_ranges_tbl.selectedIndexes()[0].row()
        self.criterion.remove_suitability_class_range(selected_index)
        self.update_suitability_table()
    
    def update_suitability_table(self):
        # display whole table instead of adding one line
        self.suitability_class_ranges_tbl.clear()
        row_index = 0
        for class_range in self.criterion.suitability_class_ranges:
            self.suitability_class_ranges_tbl.setRowCount(row_index + 1)
            self.suitability_class_ranges_tbl.setItem(row_index, 0, QTableWidgetItem(str(class_range.min_value)))
            self.suitability_class_ranges_tbl.setItem(row_index, 1, QTableWidgetItem(str(class_range.max_value)))
            self.suitability_class_ranges_tbl.setItem(row_index, 2, QTableWidgetItem(str(class_range.suitability_class.name)))
            row_index += 1
            
        self.stylize_table()

    def suitability_class_ranges_tbl_selection_changed(self):
        if self.suitability_class_ranges_tbl.selectedIndexes().__len__() == 0:
            self.remove_suitability_range_btn.setEnabled(False)
        else:
            self.remove_suitability_range_btn.setEnabled(True)

    def create_criterion(self):
        """Closes the dialog as the criterion is all set"""
        
        number_of_same_name_criteria = 0
        for criterion in self.project.criteria_definitions:
            if criterion.criterion_name == self.criterion.criterion_name:                        
                number_of_same_name_criteria += 1
        
        if self.edit_mode and self.criterion_name_updated and number_of_same_name_criteria > 0:
            QMessageBox.warning(None, "Warning", "There is another criterion with the same name.")
            return
        
        if not self.edit_mode and number_of_same_name_criteria > 0:
            QMessageBox.warning(None, "Warning", "There is another criterion with the same name.")
            return
        
        self.accept()