from .enums.vectorAlgorithm import VectorAlgorithm
from .criterion import Criterion
from .enums.aem import AlternativeEvaluationModel
import json
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsLayerTreeLayer)
import os
from ..utilities.layerhelpers import set_color_map

MESSAGE_CATEGORY = 'AlgRunnerTask'

# Project model
class Project:
    def __init__(self, dict=None, proj_file=None):
        if dict is None:
            self.project_name = ""
            self.description = ""
            self.output_file = ""
            self.project_file = ""
            self.mask_file = ""
            self.crs = ""
            self.alternative_evaluation_model = AlternativeEvaluationModel.WPM
            self.initialize_criteria_definitions()
        else:
            self.initialize_from_dictionary(dict)
        
        if proj_file is not None:
            self.project_file = proj_file
        
        self.output_layer = None
        self.output = None
        self.merged_restrict_output = None
        self.merged_restrict_output_layer = None
        self.masked = False

    def initialize_criteria_definitions(self):
        self.criteria_definitions = list()
        top_level_criteria_group = Criterion()
        top_level_criteria_group.is_group = True
        top_level_criteria_group.criterion_name = "Main"
        top_level_criteria_group.parent_group = "*"
        self.criteria_definitions.append(top_level_criteria_group)

    def initialize_from_dictionary(self, dict):
        self.project_name = dict["project_name"]
        self.description = dict["description"]
        self.output_file = dict["output_file"]
        self.mask_file = dict["mask_file"]
        self.crs = dict["crs"]
        self.alternative_evaluation_model = dict.get("alternative_evaluation_model", AlternativeEvaluationModel.WPM)
        
        self.criteria_definitions = list()
        for criterion_dict in dict["criteria_definitions"]:
            criterion = Criterion(dict=criterion_dict)
            self.criteria_definitions.append(criterion)
        self.project_file = ""

    def remove_criterion(self, index: int):
        for i, crit in enumerate(self.criteria_definitions):
            print("{}. {}".format(i, crit.criterion_name))

        criterion = self.criteria_definitions[index]
        print(criterion.criterion_name)
        if criterion.is_group and self.get_non_restrict_criteria(criterion.criterion_name).__len__() > 0:
            print(self.get_non_restrict_criteria(criterion.criterion_name).__len__())
            return False
        del self.criteria_definitions[index]
        for i, crit in enumerate(self.criteria_definitions):
            print("{}. {}".format(i, crit.criterion_name))
            for j, pairwise_comparison_to_remove in enumerate(crit.pairwise_comparisons):
                if pairwise_comparison_to_remove.other_criteria_name == criterion.criterion_name:
                    for pairwise_comparison in crit.pairwise_comparisons:
                        if pairwise_comparison.index > pairwise_comparison_to_remove.index:
                            pairwise_comparison.index -= 1
                    del crit.pairwise_comparisons[j]
        return True

    def update_pairwise_comparisons(self, old_criterion_name, new_criterion_name):
        if old_criterion_name == new_criterion_name:
            return
        
        for criterion in self.criteria_definitions:
            for comparison in criterion.pairwise_comparisons:
                if comparison.other_criteria_name == old_criterion_name:
                    comparison.other_criteria_name = new_criterion_name
                    print("{}.[{}]->[{}]".format(criterion.criterion_name, old_criterion_name, new_criterion_name))
               
    def get_layers_for_woa(self):
        return [criterion.classification_output_layer for criterion in self.get_woa_criteria()]

    def get_layer_weight_pairs_for_woa(self):
        return [criterion.get_layer_weight_pair() for criterion in self.get_woa_criteria()]
    
    def get_layers_for_restrict(self):
        return [criterion.algorithm_output_layer for criterion in self.criteria_definitions 
              if criterion.algorithm == VectorAlgorithm.RESTRICT]

    def get_woa_criteria(self):
        return list(filter(lambda criterion: criterion.algorithm != VectorAlgorithm.RESTRICT and not criterion.is_group, self.criteria_definitions))

    def get_non_restrict_criteria(self, parent_name=None):
        if parent_name is None:
            return list(filter(lambda criterion: criterion.algorithm != VectorAlgorithm.RESTRICT, self.criteria_definitions))
        else:
            return list(filter(lambda criterion: criterion.algorithm != VectorAlgorithm.RESTRICT and criterion.parent_group == parent_name, self.criteria_definitions))

    def get_restrict_criteria(self):
        return list(filter(lambda criterion: criterion.algorithm == VectorAlgorithm.RESTRICT, self.criteria_definitions))
    
    def get_criteria_group_names(self):
        return [criterion.criterion_name for criterion in self.criteria_definitions 
              if criterion.is_group]

    def get_criteria_groups(self):
        list_of_parent_names = self.get_criteria_group_names()
        groups = []
        for parent_name in list_of_parent_names:
            groups.append( { "name":parent_name, "criteria": self.get_non_restrict_criteria(parent_name) })
        return groups

    def get_weighted_criteria(self, only_leafs = False):
        if not only_leafs:
            return [criterion for criterion in self.criteria_definitions 
                if criterion.criterion_name != "Main" and criterion.algorithm is not VectorAlgorithm.RESTRICT]
        else:
            return [criterion for criterion in self.criteria_definitions 
                if not criterion.is_group and criterion.algorithm is not VectorAlgorithm.RESTRICT]

    def toJSON(self):
        return json.dumps(
            self, 
            default= lambda o: o.__dict__,
            sort_keys=True,
            indent=2)
    
    def save_to_file(self):
        project_json = self.toJSON()
        if self.project_file is not None and self.project_file != "":
            with open(self.project_file, "w") as file:
                file.write(project_json)
                
    def set_output_layer(self):
        self.output_layer = QgsRasterLayer(self.output, "AHP Output")
        QgsProject.instance().addMapLayer(self.output_layer, False)
        self.project_group.insertChildNode(1, QgsLayerTreeLayer(self.output_layer))
        self.criteria_group.setItemVisibilityCheckedRecursive(False)
        set_color_map(self.output_layer)

    def set_merged_restrict_layer(self):
        self.merged_restrict_output_layer = self.merged_restrict_output
        self.merged_restrict_output_layer.setName("Merged Restrict Layer")
        QgsProject.instance().addMapLayer(self.merged_restrict_output_layer, False)
        self.restrict_group.insertChildNode(0, QgsLayerTreeLayer(self.merged_restrict_output_layer))
        self.restrict_group.setItemVisibilityCheckedRecursive(False)

    def load_mask_layer(self):
        self.mask_layer = QgsVectorLayer(self.mask_file, "Mask")
        mask_style = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/mask-style.qml")
        self.mask_layer.loadNamedStyle(mask_style)

        self.project_group.insertChildNode(0, QgsLayerTreeLayer(self.mask_layer))
        self.masked = True
            
    def init_project_group(self):
        self.project_group = QgsProject.instance().layerTreeRoot().addGroup(self.project_name)
        self.criteria_group = self.project_group.insertGroup(0, "Criteria")
        self.restrict_group = self.project_group.addGroup("Restrict Zones")

    def is_valid(self):
        validation_message = ""
        if self.string_empty(self.project_name):
            validation_message += "Project name cannot be empty.\n"
        if self.string_empty(self.project_file):
            validation_message += "Project file cannot be empty.\n"
        if self.string_empty(self.output_file):
            validation_message += "Output folder cannot be empty.\n"
        if self.string_empty(self.mask_file):
            validation_message += "Mask file cannot be empty.\n"
        if self.get_woa_criteria().__len__() <= 1:
            validation_message += "There should at least be 2 criteria.\n"
        else:
            for criterion in self.criteria_definitions:
                validation_message += criterion.validate()

        return validation_message
    
    def string_empty(self, value):
        return value is None or value == ""