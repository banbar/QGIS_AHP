import processing

class RasterInterpolationSynchronous:
    def __init__(self):
        pass

    def execute(self, input, mask_layer):
        params = {
            'INPUT': input,
            'BAND': 1,
            'OUTPUT': "TEMPORARY_OUTPUT"
        }

        result = processing.run("gdal:fillnodata", params)["OUTPUT"]
        
        params = {
            'INPUT': result,
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
