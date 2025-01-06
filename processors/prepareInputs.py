from qgis.core import (Qgis, QgsMessageLog)
from ..models.project import Project
from .clipperSynchronous import ClipperSynchronous
from .ahpTask import AhpTask

MESSAGE_CATEGORY = 'AHP-PrepareInputs'

class PrepareInputs(AhpTask): 
    """Governing class that handles running all the operations in correct order. 
    This class itself is not a long running operation class."""
    def __init__(self, project: Project, iface):
        super().__init__("Prepare the inputs", MESSAGE_CATEGORY)
        self.project = project
        self.iface = iface

    def prepare_input_layers(self):
        self.project.init_project_group()
        self.project.load_mask_layer()
        
        for criterion in self.project.get_woa_criteria():        
            criterion.load_input_layer(self.project.criteria_group, self.project.masked)

        for criterion in self.project.get_restrict_criteria():        
            criterion.load_input_layer(self.project.restrict_group, self.project.masked)

    def execute(self):
        for criterion in list(set(self.project.get_woa_criteria()).union(self.project.get_restrict_criteria())):
            criterion.input = ClipperSynchronous().execute(criterion.data_type, criterion.input_layer, self.project.mask_layer)
            QgsMessageLog.logMessage('Clipper for "{}" ran successfully'.format(criterion.criterion_name), MESSAGE_CATEGORY, Qgis.Success)

        QgsMessageLog.logMessage('All clippers ran successfully', MESSAGE_CATEGORY, Qgis.Success)
    
    def succeeded(self):
        for criterion in self.project.get_woa_criteria():
            criterion.update_input_layer(criterion.input)
            
        for criterion in self.project.get_restrict_criteria():
            criterion.update_input_layer(criterion.input)
