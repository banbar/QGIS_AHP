from PyQt5 import QtWidgets
from ..utilities.uihelpers import get_ui_class
from ..utilities.enumhelpers import enum_index_of
from ..models.enums.aem import AlternativeEvaluationModel

class ProjectSetupWidget(QtWidgets.QWidget, get_ui_class('projectSetup.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProjectSetupWidget, self).__init__(parent)
        self.setupUi(self)
        self.relatedLabel = parent.setup_lbl
        self.project = parent.project
        self.mask_file_tb.setFilter("Vector Files (*.shp)")
        
        for member in AlternativeEvaluationModel:
            self.aem_cb.addItem(member.value, member.name)

        self.load_project()
        self.connectSignalsSlots()
        
    def load_project(self):
        if self.project is not None:
            self.project_name_tb.setText(self.project.project_name)
            self.description_tb.setPlainText(self.project.description)
            self.mask_file_tb.setFilePath(self.project.mask_file)
            self.output_file_tb.setFilePath(self.project.output_file)            
            self.aem_cb.setCurrentIndex(enum_index_of(self.project.alternative_evaluation_model, AlternativeEvaluationModel))
    
    def connectSignalsSlots(self):
        self.project_name_tb.textEdited.connect(self.project_name_updated)
        self.description_tb.textChanged.connect(self.description_updated)
        self.mask_file_tb.fileChanged.connect(self.mask_file_changed)
        self.output_file_tb.fileChanged.connect(self.output_file_changed)
        self.aem_cb.currentTextChanged.connect(self.aem_changed)

    def project_name_updated(self, text):
        self.project.project_name = text
        
    def description_updated(self):
        self.project.description = self.description_tb.toPlainText()

    def mask_file_changed(self, mask_file):
        """set the selected value to project"""
        self.project.mask_file = mask_file
    
    def aem_changed(self, alternative_evaluation_model):
        self.project.alternative_evaluation_model = alternative_evaluation_model

    def output_file_changed(self, output_file):
        """set the selected value to project"""
        self.project.output_file = output_file
        
    def crs_changed(self, crs):
        """set the selected value to project"""
        pass
