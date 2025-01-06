from .enums.suitabilityClass import SuitabilityClass

# SuitabilityClass model
class SuitabilityClassRange:
    def __init__(self, min_value: float, max_value: float, suitability_class: SuitabilityClass):
        self.min_value = min_value
        self.max_value = max_value
        self.suitability_class = suitability_class
