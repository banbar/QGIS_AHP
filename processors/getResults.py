from qgis.core import (Qgis, QgsMessageLog, QgsProject)
from ..models.project import Project
from .weightedOverlayAnalysisSynchronous import WOA
from .resultRestrictorSynchronous import ResultRestrictorSynchronous
from .ahpTask import AhpTask
from ..utilities.layerhelpers import save_layer

MESSAGE_CATEGORY = 'AHP-GetResults'

class GetResults(AhpTask): 
    """Governing class that handles running all the operations in correct order. 
    This class itself is not a long running operation class."""
    def __init__(self, project: Project, iface):
        super().__init__("Run WOA and Restrict Results", MESSAGE_CATEGORY)
        self.project = project
        self.iface = iface

    def execute(self):        
        self.project.output = WOA().execute(self.project)
        QgsMessageLog.logMessage('WOA ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
        if self.project.get_restrict_criteria().__len__() > 0:
            self.project.output, self.project.merged_restrict_output = ResultRestrictorSynchronous().execute(self.project)
            QgsMessageLog.logMessage('Result Restrictor ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
    
    def succeeded(self):
        self.project.set_output_layer()
        
        if self.project.get_restrict_criteria().__len__() > 0:
            self.project.set_merged_restrict_layer()

        self.iface.mapCanvas().setExtent(self.project.output_layer.extent())
        QgsMessageLog.logMessage('Everything ran successfully', MESSAGE_CATEGORY, Qgis.Success)

        file_path = save_layer(self.project.output_layer, self.project, True)
        QgsMessageLog.logMessage(f'AHP Output File Path: "{file_path}"', MESSAGE_CATEGORY, Qgis.Info)
