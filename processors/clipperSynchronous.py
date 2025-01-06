import processing
from ..models.enums.dataType import DataType

class ClipperSynchronous:
    def __init__(self):
        pass

    def execute(self, data_type, input, mask_layer):
        if data_type == DataType.RASTER:
            params = {
                'INPUT': input,
                'MASK': mask_layer,
                'SOURCE_CRS':None,
                'TARGET_CRS':None,
                'TARGET_EXTENT':None,
                'NODATA':None,
                'ALPHA_BAND':False,
                'CROP_TO_CUTLINE':True,
                'KEEP_RESOLUTION':False,
                'SET_RESOLUTION':False,
                'X_RESOLUTION':None,
                'Y_RESOLUTION':None,
                'MULTITHREADING':False,
                'OPTIONS':'',
                'DATA_TYPE':0,
                'EXTRA':'-co COMPRESS=LZW',
                'OUTPUT': "TEMPORARY_OUTPUT"
            }
                    
            return processing.run("gdal:cliprasterbymasklayer", params)["OUTPUT"]
        elif data_type == DataType.VECTOR:
            params = {
                'INPUT': input,
                'OVERLAY': mask_layer,
                'OUTPUT': "TEMPORARY_OUTPUT"
            }
                    
            return processing.run("native:clip", params)["OUTPUT"]
        else:
            pass
    