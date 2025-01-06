import processing
from qgis.core import (Qgis, QgsMessageLog, QgsFeatureRequest, QgsWkbTypes)

MESSAGE_CATEGORY = 'AHP-RunAlgorithmsAndClassify'

class VectorConvertorSynchronous:
    def __init__(self):
        pass

    def execute(self, criterion):
        geometry = QgsWkbTypes.geometryDisplayString(QgsWkbTypes.geometryType(criterion.input_layer.wkbType()))
        QgsMessageLog.logMessage('For {}: input geometry is {}'.format(criterion.criterion_name, geometry), MESSAGE_CATEGORY, Qgis.Info)
        
        if geometry == 'Polygon':
            result = criterion.input_layer.materialize(QgsFeatureRequest().setFilterFids(criterion.input_layer.allFeatureIds()))
            QgsMessageLog.logMessage('Input is polygon, not touching it', MESSAGE_CATEGORY, Qgis.Info)
        elif geometry == 'Line' or geometry == 'Point':
            params = { 
                'DISSOLVE' : True, 
                'DISTANCE' : 10, 
                'END_CAP_STYLE' : 0, 
                'INPUT' : criterion.input_layer, 
                'JOIN_STYLE' : 0, 
                'MITER_LIMIT' : 2, 
                'OUTPUT' : 'TEMPORARY_OUTPUT', 
                'SEGMENTS' : 5, 
                'SEPARATE_DISJOINT' : False 
            }
            result = processing.run("native:buffer", params)["OUTPUT"]
            QgsMessageLog.logMessage('Input is line, buffered it', MESSAGE_CATEGORY, Qgis.Info)
        
        QgsMessageLog.logMessage('Vector Convertor ran successfully ({})'.format(geometry), MESSAGE_CATEGORY, Qgis.Success)
        return result
