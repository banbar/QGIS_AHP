import processing
from qgis.core import (Qgis, QgsMessageLog)

MESSAGE_CATEGORY = 'AHP-GetResults'

class ResultRestrictorSynchronous:
    def __init__(self):
        pass

    def execute(self, project):
        QgsMessageLog.logMessage('Will Run Result Restrictor', MESSAGE_CATEGORY, Qgis.Info)
        try:
            params = {
                'LAYERS': project.get_layers_for_restrict(),
                'OUTPUT': "TEMPORARY_OUTPUT"
            }

            merged_layers = processing.run("native:mergevectorlayers", params)["OUTPUT"]
                    
            QgsMessageLog.logMessage('native:mergevectorlayers ran successfully', MESSAGE_CATEGORY, Qgis.Info)

            params = {
                'INPUT': merged_layers,
                'INPUT_RASTER': project.output,
                'BURN': 0,
                'UNITS': 1, # Georeferenced units
                'WIDTH': 10,
                'HEIGHT': 10, # todo: min res of other inputs
                'OUTPUT': "TEMPORARY_OUTPUT"
            }

            result = processing.run("gdal:rasterize_over_fixed_value", params)["OUTPUT"]
            QgsMessageLog.logMessage('Result Restrictor ran successfully', MESSAGE_CATEGORY, Qgis.Success)
            return result, merged_layers
        except Exception as ex:
            QgsMessageLog.logMessage('Result Restrictor failed. Exception: {}'.format(ex), MESSAGE_CATEGORY, Qgis.Critical)
            raise ex
        