from PyQt5 import QtWidgets
from ..models.enums.vectorAlgorithm import VectorAlgorithm
from ..utilities.uihelpers import get_ui_class
import traceback

class SummaryWidget(QtWidgets.QWidget, get_ui_class('summary.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(SummaryWidget, self).__init__(parent)
        self.setupUi(self)
        self.relatedLabel = parent.summary_lbl
        self.project = parent.project
        self.load_project()

    def stylize_table(self):
        self.summary_tbl.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Criteria Name"))
        self.summary_tbl.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Is Group"))
        self.summary_tbl.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Parent Group"))
        self.summary_tbl.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Data Type"))
        self.summary_tbl.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("File Name"))
        self.summary_tbl.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem("Algorithm"))
        self.summary_tbl.setHorizontalHeaderItem(6, QtWidgets.QTableWidgetItem("Groupwise Weight"))
        self.summary_tbl.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem("Weight"))
        self.summary_tbl.resizeColumnsToContents()
        self.summary_tbl.horizontalHeader().setSectionResizeMode(4, 1)
        
    def load_project(self):
        if self.project is None:
            return
        
        self.update_criteria_table()
        self.project_name_lbl.setText(self.project.project_name)
        self.output_file_lbl.setText(self.project.output_file)

    def update_criteria_table(self):
        # display whole table instead of adding one line
        self.summary_tbl.clear()
        row_index = 0

        sorted_criteria = sorted(self.project.criteria_definitions, key=lambda x: (
            0 if x.weight == "NA" else x.weight, 
            0 if x.groupwise_weight == "NA" else x.groupwise_weight), reverse=True)

        for criterion in sorted_criteria:
            if criterion.is_group and criterion.criterion_name == "Main":
                continue
            self.summary_tbl.setRowCount(row_index + 1)
            self.summary_tbl.setItem(row_index, 0, QtWidgets.QTableWidgetItem(criterion.criterion_name))
            self.summary_tbl.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(criterion.is_group)))
            if criterion.algorithm != VectorAlgorithm.RESTRICT:
                self.summary_tbl.setItem(row_index, 2, QtWidgets.QTableWidgetItem(criterion.parent_group))
            if not criterion.is_group:
                self.summary_tbl.setItem(row_index, 3, QtWidgets.QTableWidgetItem(criterion.data_type.value))
                self.summary_tbl.setItem(row_index, 4, QtWidgets.QTableWidgetItem(criterion.input_file))
                self.summary_tbl.setItem(row_index, 5, QtWidgets.QTableWidgetItem(criterion.algorithm.value))
            self.summary_tbl.setItem(row_index, 6, QtWidgets.QTableWidgetItem(show_percentage(criterion.groupwise_weight)))
            self.summary_tbl.setItem(row_index, 7, QtWidgets.QTableWidgetItem(show_percentage(criterion.weight)))
            row_index += 1

        self.stylize_table()
        
def show_percentage(weight):
    if weight == "NA":
        return weight
    return "{:.1f} %".format(weight * 100)