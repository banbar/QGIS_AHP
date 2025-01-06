from enum import Enum

# Enum definitions
class RasterAlgorithm(str, Enum):
    NO_PREPROCESS = "No Preprocess"
    SLOPE = "Slope Analysis"
    ASPECT = "Aspect Analysis"
