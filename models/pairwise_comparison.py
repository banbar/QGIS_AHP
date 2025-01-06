from fractions import Fraction
# from decimal import Decimal, getcontext
# from ..utilities.decimalEncoder import DecimalEncoder
import json

# PairwiseComparison model
class PairwiseComparison:
    def __init__(self, index: int, other_criteria_name: str, value: str):
        self.index = index
        self.other_criteria_name = other_criteria_name
        self.value = value
        self.normalized_value = 0
        
    def toJSON(self):
        return json.dumps(
            self, 
            default= lambda o: o.__dict__,
            sort_keys=True,
            indent=2)

    def set_value(self, value):
        self.value = value

    def get_value_number(self):
        # getcontext().prec = 4
        fraction = Fraction(self.value)
        # return fraction
        # return Decimal(fraction.numerator) / Decimal(fraction.denominator)
        return float(fraction.numerator) / float(fraction.denominator)
