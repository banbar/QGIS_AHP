from .enums.dataType import DataType
from .enums.rasterAlgorithm import RasterAlgorithm
from .enums.reclassificationMethod import ReclassificationMethod
from .enums.vectorAlgorithm import VectorAlgorithm
from .suitabilityClassRange import SuitabilityClassRange
from .enums.suitabilityClass import SuitabilityClass
from .pairwise_comparison import PairwiseComparison
from ..utilities.layerhelpers import set_color_map
from qgis.core import (Qgis, QgsMessageLog, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsLayerTreeLayer)
import json
import os.path

# Criterion model
class Criterion:
    def __init__(self, dict=None):
        if dict is None:
            self.criterion_name = ""
            self.input_file = ""
            self.data_type = DataType.RASTER
            self.reclassification_method = ReclassificationMethod.MANUAL
            self.suitability_class_ranges = list()
            self.pairwise_comparisons = list()
            self.algorithm = RasterAlgorithm.NO_PREPROCESS
            self.parent_group = "Main"
            self.is_group = False
        else:
            self.initialize_from_dictionary(dict)
        self.input_layer = None
        self.input = None
        self.algorithm_output_layer = None
        self.algorithm_output = None
        self.classification_output_layer = None
        self.classification_output = None
        self.mask_layer = None
        self.weight = "NA"
        self.groupwise_weight = "NA"

    def initialize_from_dictionary(self, dict):
        self.criterion_name = dict["criterion_name"]
        self.input_file = dict["input_file"]
        self.data_type = DataType(dict["data_type"])
        if self.data_type == DataType.RASTER:
            self.set_algorithm(RasterAlgorithm(dict["algorithm"]))
        if self.data_type == DataType.VECTOR:
            self.set_algorithm(VectorAlgorithm(dict["algorithm"]))
        self.reclassification_method = ReclassificationMethod(dict["reclassification_method"])
        self.suitability_class_ranges = list()
        for suitability_class_range_dict in dict["suitability_class_ranges"]:
            suitability_class_range = SuitabilityClassRange(suitability_class_range_dict["min_value"], suitability_class_range_dict["max_value"], SuitabilityClass(suitability_class_range_dict["suitability_class"]))
            self.suitability_class_ranges.append(suitability_class_range)
        self.pairwise_comparisons = list()
        for pairwise_comparisons_dict in dict["pairwise_comparisons"]:
            pairwise_comparison = PairwiseComparison(pairwise_comparisons_dict["index"], pairwise_comparisons_dict["other_criteria_name"], pairwise_comparisons_dict["value"])
            self.pairwise_comparisons.append(pairwise_comparison)
        self.parent_group = dict.get("parent_group", "Main")
        self.is_group = dict.get("is_group", False)

    def toJSON(self):
        return json.dumps(
            self, 
            default= lambda o: o.__dict__,
            sort_keys=True,
            indent=2)
    
    # Assigning algorithm based on data_type (Raster or Vector)
    def set_algorithm(self, algorithm):
        if self.data_type == DataType.RASTER:
            if isinstance(algorithm, RasterAlgorithm):
                self.algorithm = algorithm
            else:
                raise ValueError("Invalid algorithm for raster data")
        elif self.data_type == DataType.VECTOR:
            if isinstance(algorithm, VectorAlgorithm):
                self.algorithm = algorithm
            else:
                raise ValueError("Invalid algorithm for vector data")
        
    def add_suitability_class_range(self, range: SuitabilityClassRange):
        self.suitability_class_ranges.append(range)

    def remove_suitability_class_range(self, index: int):
        del self.suitability_class_ranges[index]

    def add_pairwise_comparison(self, index: int, other_criteria_name: str, value: str):
        self.pairwise_comparisons.append(PairwiseComparison(index, other_criteria_name, value))

    def get_pairwise_comparison_by_index(self, index: int):
        for pairwise_comparison in self.pairwise_comparisons:
            if pairwise_comparison.index == index:
                return pairwise_comparison
        return None
    
    def get_pairwise_comparison_by_name(self, name):
        for pairwise_comparison in self.pairwise_comparisons:
            if pairwise_comparison.other_criteria_name == name:
                return pairwise_comparison
        return None
    
    def load_input_layer(self, layer_group, masked: bool):
        input_exists = os.path.exists(self.input_file)
        QgsMessageLog.logMessage('Input for {} exists: {}'.format(self.criterion_name, str(input_exists)), 'AHP-PrepareInputs', Qgis.Info if input_exists else Qgis.Critical)

        input_name = "Clipped Input" if masked else "Input"
        if self.data_type == DataType.RASTER:
            self.input_layer = QgsRasterLayer(self.input_file, input_name)
        else:
            self.input_layer = QgsVectorLayer(self.input_file, input_name)
        
        self.layer_group = layer_group.insertGroup(0, self.criterion_name)
        
        self.input_layer_node = QgsLayerTreeLayer(self.input_layer)
        self.layer_group.addChildNode(self.input_layer_node)
        
    def update_input_layer(self, updated):
        old_input_layer_id = self.input_layer.id()
        old_input_name = self.input_layer.name()
        QgsProject.instance().removeMapLayer(old_input_layer_id)
        self.layer_group.removeLayer(self.input_layer)
        if self.data_type == DataType.RASTER:
            self.input_layer = QgsRasterLayer(updated, old_input_name)
        elif self.data_type == DataType.VECTOR:
            updated.setName(old_input_name)
            self.input_layer = updated
        self.layer_group.addChildNode(QgsLayerTreeLayer(self.input_layer))
          
    def set_algorithm_output_layer(self):
        # this layer needs to be named uniquely because it's being used by it's name in WOA
        if self.algorithm != VectorAlgorithm.RESTRICT:    
            self.algorithm_output_layer = QgsRasterLayer(self.algorithm_output, "Algorithm Output ({})".format(self.criterion_name))
        else:
            self.algorithm_output.setName("Algorithm Output ({})".format(self.criterion_name))
            self.algorithm_output_layer = self.algorithm_output

        self.layer_group.insertChildNode(0, QgsLayerTreeLayer(self.algorithm_output_layer))
    
    def set_classification_output_layer(self):
        # this layer needs to be named uniquely because it's being used by it's name in WOA
        self.classification_output_layer = QgsRasterLayer(self.classification_output, "Classification Output ({})".format(self.criterion_name))
        
        QgsProject.instance().addMapLayer(self.classification_output_layer, False)
        self.layer_group.insertChildNode(0, QgsLayerTreeLayer(self.classification_output_layer))
        set_color_map(self.classification_output_layer)

    def set_mask_layer(self, mask_layer):
        self.mask_layer = QgsVectorLayer(mask_layer.source(), "mask-clone")
        self.layer_group.insertChildNode(0, QgsLayerTreeLayer(self.mask_layer))

    def get_layer_weight_pair(self):
        return self.classification_output_layer, self.weight
    
    def get_ancestral_criteria(self, ancestors, all_criteria):
        # if top level group, then return incoming ancestor list
        if self.is_group and self.criterion_name == "Main":
            return ancestors
        
        # if not a top level group, then add current item to ancestor list
        ancestors.append(self)

        parent = list(filter(lambda x: x.criterion_name == self.parent_group, all_criteria))[0]

        return parent.get_ancestral_criteria(ancestors, all_criteria)

    def validate(self):
        if self.string_empty(self.criterion_name):
            return "Criterion name cannot be empty.\n"
        
        if self.is_group:
            return ""
        
        validation_message = "For criterion '{}':\n".format(self.criterion_name)

        if self.string_empty(self.input_file):
            validation_message += "- Input file cannot be empty.\n"
        
        if self.algorithm == VectorAlgorithm.RESTRICT:            
            if "- " in validation_message:
                return validation_message
            return ""
        
        if self.suitability_class_ranges is None or len(self.suitability_class_ranges) <= 1 or self.suitability_class_ranges.__len__() <= 1:
            validation_message += "- There should at least be 2 suitability ranges.\n"
        else:
            for range in self.suitability_class_ranges:
                if self.string_empty(range.min_value):
                    validation_message += "- Min value for a suitability range cannot be empty.\n"
                if self.string_empty(range.max_value):
                    validation_message += "- Max value for a suitability range cannot be empty.\n"
                if self.string_empty(range.suitability_class):
                    validation_message += "- Min value for a suitability range cannot be empty.\n"
                if float(range.min_value) >= float(range.max_value):
                    validation_message += f"- Min value ({range.min_value}) should be less then Max value ({range.max_value}).\n"
        
        if self.weight == "NA" or self.weight == 1:
            validation_message += "- AHP parameters are missing.\n"

        if "- " in validation_message:
            return validation_message
        return ""
        
    def string_empty(self, value):
        return value is None or value == ""