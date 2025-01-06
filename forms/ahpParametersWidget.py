# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QTableWidgetItem)
from qgis.core import (Qgis, QgsMessageLog)
from PyQt5.QtGui import (QColor)
from PyQt5.QtCore import Qt
from ..utilities.uihelpers import get_ui_class

MESSAGE_CATEGORY = 'AHP-Weight Calculations'

class AhpParametersWidget(QWidget, get_ui_class('ahpParameters.ui')):
    def __init__(self, group_name, parent):
        """Constructor."""
        super(AhpParametersWidget, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.project = parent.project
        self.group_name = group_name
        self.ahp_criteria = self.project.get_non_restrict_criteria(self.group_name)
        self.group_name_lbl.setText(self.group_name_lbl.text() + self.group_name)        
        self.connect_signals_slots()
        self.initialize_pairwise_comparisons()
        self.load_ahp_table()
         
    def connect_signals_slots(self):
        self.ahp_tbl.itemChanged.connect(self.cell_changed)

    def initialize_pairwise_comparisons(self):
        print("initialize pairwise")
        for criterion_index_1, criterion_1 in enumerate(self.ahp_criteria):
            for criterion_index_2, criterion_2 in enumerate(self.ahp_criteria):
                if criterion_1.get_pairwise_comparison_by_index(criterion_index_2) is None:
                    if criterion_index_1 == criterion_index_2:
                        criterion_1.add_pairwise_comparison(criterion_index_2, criterion_2.criterion_name, "1")
                    else:
                        criterion_1.add_pairwise_comparison(criterion_index_2, criterion_2.criterion_name, "")

    def load_ahp_table(self):
        self.ahp_tbl.itemChanged.disconnect()
        
        criteria_count = self.ahp_criteria.__len__()

        self.ahp_tbl.setColumnCount(criteria_count)

        self.ahp_tbl.setRowCount(criteria_count)
        
        self.ahp_tbl.horizontalHeader().setFixedHeight(30)
        self.ahp_tbl.horizontalHeader().setMinimumSectionSize(100)

        criteria_index = 0
        for criterion in self.ahp_criteria:
            self.ahp_tbl.setHorizontalHeaderItem(criteria_index, QTableWidgetItem(criterion.criterion_name))
            self.ahp_tbl.setVerticalHeaderItem(criteria_index, QTableWidgetItem(criterion.criterion_name))
            
            for pairwise_comparison in criterion.pairwise_comparisons:
                self.ahp_tbl.setItem(criteria_index, pairwise_comparison.index, QTableWidgetItem(pairwise_comparison.value))
                cell = self.ahp_tbl.item(criteria_index, pairwise_comparison.index)
                cell.setTextAlignment(Qt.AlignCenter)
                if criteria_index == pairwise_comparison.index:
                    cell.setBackground(QColor("lightgray"))
                    cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
            criteria_index += 1
        self.ahp_tbl.resizeColumnsToContents()
        
        self.set_ahp_table_height()
        
        self.ahp_tbl.itemChanged.connect(self.cell_changed)

        if self.is_table_filled():
            self.calculate_weights()
        self.project.save_to_file()

    def set_ahp_table_height(self):
        total_height = self.ahp_tbl.verticalHeader().length() + self.ahp_tbl.horizontalHeader().height()
        total_height += self.ahp_tbl.frameWidth() * 2  # Add frame width

        # Set the table's height to fit all rows
        self.ahp_tbl.setFixedHeight(total_height)

    def cell_changed(self, item):
        row = item.row()
        column = item.column()
        if row == column:
            return
        
        old_value = self.ahp_criteria[row].get_pairwise_comparison_by_index(column).value

        try:
            value = int(item.text())  # Convert the item text to an integer
            if value < 1 or value > 9:  # Check if value is within the desired range
                item.setText(old_value)  # Clear the invalid value
        except ValueError:
            # If the value is not an integer, clear the cell
            item.setText(old_value)

        self.update_criterion(item.text(), row, column)

    def update_criterion(self, value, row, column):
        pairwise_comparison = self.ahp_criteria[row].get_pairwise_comparison_by_index(column)
        
        pairwise_comparison.value = value        
        self.update_reciprocal(value, row, column)

        self.load_ahp_table()

    def update_reciprocal(self, value, row, column):
        pairwise_comparison = self.ahp_criteria[column].get_pairwise_comparison_by_index(row)
        pairwise_comparison.value = "1/" + value

    def is_table_filled(self):
        for criterion_index_1, criterion_1 in enumerate(self.ahp_criteria):
            for criterion_index_2, criterion_2 in enumerate(self.ahp_criteria):
                pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(criterion_index_2)
                if pairwise_comparison is None:
                    return False
                if pairwise_comparison.value == "":
                    return False
        return True
    
    def calculate_weights(self):
        criteria_count = self.ahp_criteria.__len__()
        if criteria_count > 1:

            # Sum the Columns of the Matrix:
            column_sum = [0] * criteria_count
            for row, criterion_1 in enumerate(self.ahp_criteria):
                for column in range(criteria_count):
                    pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(column)
                    column_sum[column] += pairwise_comparison.get_value_number()

            log_1d_array_as_table("column_sum", column_sum, False)
            
            # Normalize the Pairwise Comparison Matrix:
            for row, criterion_1 in enumerate(self.ahp_criteria):
                for column in range(criteria_count):
                    pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(column)
                    pairwise_comparison.normalized_value = pairwise_comparison.get_value_number() / column_sum[column]

            normalized_values = generate_2d_array(criteria_count, criteria_count)
            for row, criterion_1 in enumerate(self.ahp_criteria):
                for column in range(criteria_count):
                    pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(column)
                    normalized_values[row][column] = str(pairwise_comparison.normalized_value)
            
            log_2d_array_as_table("Normalized Values", normalized_values)

            # Calculate the Average of Each Row:
            normalized_row_averages = [0] * criteria_count
            for row, criterion_1 in enumerate(self.ahp_criteria):
                weight = 0
                for column in range(criteria_count):
                    pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(column)
                    weight += pairwise_comparison.normalized_value
                criterion_1.groupwise_weight = weight / criteria_count
                normalized_row_averages[row] = criterion_1.groupwise_weight
                
            log_1d_array_as_table("group-wise weights", normalized_row_averages)

            # Compute the Consistency Ratio (CR):
            some_values = [0] * criteria_count
            for row, criterion_1 in enumerate(self.ahp_criteria):
                for column in range(criteria_count):
                    pairwise_comparison = criterion_1.get_pairwise_comparison_by_index(column)
                    some_values[row] += self.ahp_criteria[column].groupwise_weight * pairwise_comparison.get_value_number()
            
            log_1d_array_as_table("some_values", some_values)

            for row, criterion_1 in enumerate(self.ahp_criteria):
                some_values[row] /= criterion_1.groupwise_weight

            log_1d_array_as_table("some_values_updated", some_values)

            sum_of_some_values = 0
            for some_value in some_values:
                sum_of_some_values += some_value
            average = sum_of_some_values / criteria_count
            QgsMessageLog.logMessage("average: " + str(average), MESSAGE_CATEGORY, Qgis.Info)

            CI = (average - criteria_count) / (criteria_count - 1)
            QgsMessageLog.logMessage("CI: " + str(CI), MESSAGE_CATEGORY, Qgis.Info)
            if criteria_count <= 2:
                CR = 0
            else:
                RIs = [0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
                RI = RIs[criteria_count - 1]
                QgsMessageLog.logMessage("RI: " + str(RI), MESSAGE_CATEGORY, Qgis.Info)
                CR = CI/RI
        else:
            CR = 0
            for criterion in self.ahp_criteria:
                criterion.groupwise_weight = 1
        
        QgsMessageLog.logMessage("CR: " + str(CR), MESSAGE_CATEGORY, Qgis.Info)
        if CR > 0.1:
            self.consistency_index_lbl.setStyleSheet("background-color: red")
        else:
            self.consistency_index_lbl.setStyleSheet("background-color: lightgreen")
        self.consistency_index_lbl.setText(str(CR))
        
        self.parent.weights_calculated()

def generate_2d_array(rows, cols, default_value=""):
    return [[default_value for _ in range(cols)] for _ in range(rows)]

def log_2d_array_as_table(table_name, array):
    QgsMessageLog.logMessage("", MESSAGE_CATEGORY, Qgis.Info)
    QgsMessageLog.logMessage(table_name, MESSAGE_CATEGORY, Qgis.Info)
    # Create a horizontal line based on the width of the array
    if array:
        col_width = max(len(str(item)) for row in array for item in row)  # Find the maximum column width
        line = '+' + '+'.join(['-' * (col_width + 2)] * len(array[0])) + '+'

        # Log the array as a formatted table
        QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)
        for row in array:
            formatted_row = '| ' + ' | '.join(f'{str(item):0<{col_width}}' for item in row) + ' |'
            QgsMessageLog.logMessage(formatted_row, MESSAGE_CATEGORY, Qgis.Info)
            QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)

def log_1d_array_as_table(table_name, array, as_rows=True):
    QgsMessageLog.logMessage("", MESSAGE_CATEGORY, Qgis.Info)
    QgsMessageLog.logMessage(table_name, MESSAGE_CATEGORY, Qgis.Info)
    if array:
        # Find the maximum width of the elements in the array
        col_width = max(len(str(item)) for item in array)
        
        if as_rows:
            # Print as a column (each element in its own row)
            line = '+' + '-' * (col_width + 2) + '+'
            QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)
            
            for item in array:
                formatted_item = f'| {str(item):0<{col_width}} |'
                QgsMessageLog.logMessage(formatted_item, MESSAGE_CATEGORY, Qgis.Info)
                QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)
        else:
            # Print as a row (one line of multiple columns)
            line = '+' + '+'.join(['-' * (col_width + 2)] * len(array)) + '+'
            QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)
            
            formatted_row = '| ' + ' | '.join(f'{str(item):0<{col_width}}' for item in array) + ' |'
            QgsMessageLog.logMessage(formatted_row, MESSAGE_CATEGORY, Qgis.Info)
            
            QgsMessageLog.logMessage(line, MESSAGE_CATEGORY, Qgis.Info)