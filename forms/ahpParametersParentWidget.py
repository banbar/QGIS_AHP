from PyQt5 import QtWidgets
from .ahpParametersWidget import AhpParametersWidget
from ..utilities.uihelpers import get_ui_class

MESSAGE_CATEGORY = 'AHP-Weight Calculations'

class AhpParametersParentWidget(QtWidgets.QWidget, get_ui_class('ahpParametersParent.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(AhpParametersParentWidget, self).__init__(parent)
        self.setupUi(self)
        self.relatedLabel = parent.ahp_lbl
        self.project = parent.project
        self.load_ahp_criteria_groups()
         
    def load_ahp_criteria_groups(self):
        for group in self.project.get_criteria_groups():
            if group["criteria"].__len__() > 0:
                self.ahp_container.insertWidget(len(self.ahp_container) - 1, AhpParametersWidget(group["name"], self))

    def all_weights_calculated(self):
        all_weights_calculated = True

        # if all non-main, non-restrict criteria has groupwise-weight, then we can start
        for criterion in self.project.get_weighted_criteria():
            if criterion.groupwise_weight == "NA":
                all_weights_calculated = False
                print(criterion.criterion_name)
                break
        
        if not all_weights_calculated:
            print("not all weights are calculated")
        else:
            print("all weights are calculated")
        
        return all_weights_calculated
    
    def weights_calculated(self):
        if not self.all_weights_calculated():
            return
                
        for criterion in self.project.get_weighted_criteria(only_leafs=True):
            ancestors = criterion.get_ancestral_criteria([], self.project.criteria_definitions)
            print("CriterionName: " + criterion.criterion_name)
            product_of_ancestral_weights = 1
            for ancestor in ancestors:
                print("ancestor: " + ancestor.criterion_name + ", groupwise_weight: " + str(ancestor.groupwise_weight))
                product_of_ancestral_weights *= ancestor.groupwise_weight

            criterion.weight = product_of_ancestral_weights

        