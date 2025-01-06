from qgis.core import (Qgis, QgsMessageLog)
from ..models.project import Project
from .algorithmSycnhronous import AlgorithmSycnhronous
from .rasterInterpolationSynchronous import RasterInterpolationSynchronous
from .classifierSynchronous import ClassifierSynchronous
from .vectorConverterSynchronous import VectorConvertorSynchronous
from .ahpTask import AhpTask
from ..utilities.layerhelpers import save_layer

MESSAGE_CATEGORY = 'AHP-RunAlgorithmsAndClassify'

class RunAlgorithmsAndClassify(AhpTask): 
    """Governing class that handles running all the operations in correct order. 
    This class itself is not a long running operation class."""
    def __init__(self, project: Project, iface):
        super().__init__("Run Algorithms and Classify", MESSAGE_CATEGORY)
        self.project = project
        self.iface = iface


    def execute(self):
        for criterion in self.project.get_woa_criteria():
            criterion.algorithm_output = AlgorithmSycnhronous().execute(criterion.data_type, criterion.input, criterion.algorithm, self.project.mask_layer, criterion.criterion_name)
            QgsMessageLog.logMessage('Algorithm for "{}" ran successfully'.format(criterion.criterion_name), MESSAGE_CATEGORY, Qgis.Success)

        QgsMessageLog.logMessage('All algorithms ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
        for criterion in self.project.get_woa_criteria():
            criterion.algorithm_output = RasterInterpolationSynchronous().execute(criterion.algorithm_output, self.project.mask_layer)
            QgsMessageLog.logMessage('Raster interpolation for "{}" ran successfully'.format(criterion.criterion_name), MESSAGE_CATEGORY, Qgis.Success)

        QgsMessageLog.logMessage('All raster interpolations ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
        for criterion in self.project.get_woa_criteria():
            criterion.classification_output = ClassifierSynchronous().execute(criterion.algorithm_output, criterion, self.project.mask_layer)
            QgsMessageLog.logMessage('Classifier for "{}" ran successfully'.format(criterion.criterion_name), MESSAGE_CATEGORY, Qgis.Success)

        QgsMessageLog.logMessage('All classifiers ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
        for criterion in self.project.get_restrict_criteria():        
            criterion.algorithm_output = VectorConvertorSynchronous().execute(criterion)
            QgsMessageLog.logMessage('Vector convertor for "{}" ran successfully'.format(criterion.criterion_name), MESSAGE_CATEGORY, Qgis.Success)
            
        QgsMessageLog.logMessage('All vector convertors ran successfully', MESSAGE_CATEGORY, Qgis.Success)
        
    def succeeded(self):
        for criterion in self.project.get_woa_criteria():
            criterion.set_algorithm_output_layer()
            criterion.set_classification_output_layer()
            
        for criterion in self.project.get_restrict_criteria(): 
            criterion.set_algorithm_output_layer()

        for criterion in self.project.get_woa_criteria():
            file_path = save_layer(criterion.algorithm_output_layer, self.project)
            QgsMessageLog.logMessage(f'Algorithm File Path: "{file_path}"', MESSAGE_CATEGORY, Qgis.Info)
            
            file_path = save_layer(criterion.classification_output_layer, self.project)
            QgsMessageLog.logMessage(f'Classification File Path: "{file_path}"', MESSAGE_CATEGORY, Qgis.Info)

