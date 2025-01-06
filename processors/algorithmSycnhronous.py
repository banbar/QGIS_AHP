import processing
from ..models.enums.rasterAlgorithm import RasterAlgorithm
from ..models.enums.dataType import DataType

class AlgorithmSycnhronous:
    def __init__(self):
        pass

    def execute(self, data_type, input, algorithm, mask_layer, name):
        if data_type == DataType.RASTER:
            if algorithm == RasterAlgorithm.NO_PREPROCESS:
                return input
            
            qgis_algorithm = ""
            if algorithm == RasterAlgorithm.ASPECT:
                qgis_algorithm = "qgis:aspect"
                params = {
                    'INPUT': input,
                    'OUTPUT': "TEMPORARY_OUTPUT"
                }
            if algorithm == RasterAlgorithm.SLOPE:
                qgis_algorithm = "gdal:slope"
                params = {
                    'INPUT': input,
                    'AS_PERCENT': True,
                    'OUTPUT': "TEMPORARY_OUTPUT"
                }

            return processing.run(qgis_algorithm, params)["OUTPUT"]

        elif data_type == DataType.VECTOR:
            extent = mask_layer.extent()
            params = {
                'INPUT': input,
                'BURN': 1,
                'INIT': 0,
                'UNITS': 1, # Georeferenced units
                'WIDTH': 10,
                'HEIGHT': 10, # todo: min res of other inputs
                "EXTENT":"%f,%f,%f,%f"% (extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum()),
                'EXTRA': f'-a_srs {mask_layer.crs().authid()}',
                'OUTPUT': "TEMPORARY_OUTPUT"
            }

            result = processing.run("gdal:rasterize", params)["OUTPUT"]

            print('gdal:rasterize done for "{}"'.format(name))

            params = {
                'INPUT': result,
                'BAND': 1,
                'UNITS': 0, # Georeferenced units
                'MAX_DISTANCE': 20000, # todo: how do we get this? can giving a very large number work?
                'OUTPUT': "TEMPORARY_OUTPUT",
            }

            return processing.run("gdal:proximity", params)["OUTPUT"]
        else:
            pass
