import processing
from qgis.core import (Qgis, QgsMessageLog)
from ..models.enums.aem import AlternativeEvaluationModel

MESSAGE_CATEGORY = 'AHP-GetResults'

class WOA:
    def __init__(self):
        pass

    def execute(self, project):
        params = {
            'LAYERS': project.get_layers_for_woa(),
            'EXPRESSION': self.get_formula(project),
            'OUTPUT': "TEMPORARY_OUTPUT"
        }

        return processing.run("qgis:rastercalculator", params)["OUTPUT"]

    def get_formula(self, project):

        QgsMessageLog.logMessage(f'Using "{project.alternative_evaluation_model}", formula:' , MESSAGE_CATEGORY, Qgis.Info)

        formula = ""
        if project.alternative_evaluation_model == AlternativeEvaluationModel.WPM:
            formula = " * ".join([f'("{layer.name()}@1" ^ {weight})' for layer, weight in project.get_layer_weight_pairs_for_woa()])
        elif project.alternative_evaluation_model == AlternativeEvaluationModel.WSM:
            formula = " + ".join([f'("{layer.name()}@1" * {weight})' for layer, weight in project.get_layer_weight_pairs_for_woa()])

        woa_layers_equal_to_one = [f'"{layer.name()}@1" = 1' for layer, _ in project.get_layer_weight_pairs_for_woa()]
        
        QgsMessageLog.logMessage(formula, MESSAGE_CATEGORY, Qgis.Info)

        formula = "IF(" + " OR ".join(woa_layers_equal_to_one) + ", 1, " + formula + ")"

        QgsMessageLog.logMessage(formula, MESSAGE_CATEGORY, Qgis.Info)

        return formula