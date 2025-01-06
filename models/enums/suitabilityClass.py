from enum import Enum

class SuitabilityClass(int, Enum):
    N_NOT_SUITABLE = 1
    S3_MARGINALLY_SUITABLE = 2
    S2_MODERATELY_SUITABLE = 3
    S1_HIGHLY_SUITABLE = 4