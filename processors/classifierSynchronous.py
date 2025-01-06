from ..models.enums.reclassificationMethod import ReclassificationMethod
import processing

class ClassifierSynchronous:
    def __init__(self):
        pass

    def execute(self, input, criterion, mask_layer):
        table = self.convert_suitability_class_ranges_to_string(criterion)
        params = {
            'INPUT_RASTER': input,
            'TABLE': table,
            'NODATA_FOR_MISSING': True,
            'RASTER_BAND': 1,
            'OUTPUT': "TEMPORARY_OUTPUT"
        }

        result = processing.run("qgis:reclassifybytable", params)["OUTPUT"]
        
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
    
    def convert_suitability_class_ranges_to_string(self, criterion):
        table = ""
        if criterion.reclassification_method == ReclassificationMethod.MANUAL:
            for suitability_class_range in criterion.suitability_class_ranges:
                table += "{min},{max},{value},".format(
                    min=suitability_class_range.min_value,
                    max=suitability_class_range.max_value,
                    value=suitability_class_range.suitability_class.value)
                
            table = table[:-1]
        elif criterion.reclassification_method == ReclassificationMethod.EQUAL_INTERVAL:
            # todo: get rasters min max, separate it equally
            pass
        
        return table