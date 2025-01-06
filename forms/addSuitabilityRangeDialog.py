from ..models.enums.dataType import DataType
from ..models.enums.suitabilityClass import SuitabilityClass

from PyQt5.QtWidgets import (QDialog)

from ..utilities.uihelpers import get_ui_class
from ..models.suitabilityClassRange import SuitabilityClassRange

class AddSuitabilityRangeDialog(QDialog, get_ui_class('addSuitabilityRangeDialog.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddSuitabilityRangeDialog, self).__init__(parent)
        self.setupUi(self)
        self.suitability_class_range = SuitabilityClassRange(0, 0, SuitabilityClass.N_NOT_SUITABLE)
        self.connect_signals_slots()
        self.populate_comboboxes()
        
    def connect_signals_slots(self):
        self.add_btn.clicked.connect(self.add_suitability_class_range)

    def populate_comboboxes(self):
        for member in SuitabilityClass:
            self.suitability_class_cb.addItem(member.name, member.name)

    def add_suitability_class_range(self):
        self.suitability_class_range = SuitabilityClassRange(self.min_tb.text(), self.max_tb.text(), SuitabilityClass[self.suitability_class_cb.currentText()])
        self.accept()
