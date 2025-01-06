import os
import traceback
from qgis.core import (
    QgsProject, 
    QgsColorRampShader,
    QgsRasterRendererUtils,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer, 
    QgsRasterFileWriter, QgsRasterPipe
)

def set_color_map(lyr):
    """Sets the custom color map to given layer"""
    color_map_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/custom-color-map.txt")

    try:
        loading, ramp_shader_items, shader_type, errors = QgsRasterRendererUtils.parseColorMapFile(color_map_file)

        if not loading:
            raise OSError(", ".join(errors))

        shader = QgsRasterShader()
        ramp_shader = QgsColorRampShader()
        ramp_shader.setColorRampType(shader_type)
        ramp_shader.setColorRampItemList(ramp_shader_items)
        shader.setRasterShaderFunction(ramp_shader)

        band = 1
        renderer = QgsSingleBandPseudoColorRenderer(
            input=lyr.dataProvider(),
            band=band,
            shader=shader
        )
        lyr.setRenderer(renderer)
        QgsProject.instance().reloadAllLayers()
    except Exception:
        return False

def save_layer(layer_to_write, project, is_final_result = False):
    try:
        project_criteria_folder_path = os.path.join(project.output_file, project.project_name, "Criteria") if not is_final_result else os.path.join(project.output_file, project.project_name)
        os.makedirs(project_criteria_folder_path, exist_ok=True)

        provider = layer_to_write.dataProvider()
        pipe = QgsRasterPipe()
        pipe.set(provider.clone())
        
        file_path = os.path.join(project_criteria_folder_path, layer_to_write.name() + ".tif")
        
        # Write the output layer to the file system
        writer = QgsRasterFileWriter(file_path)
        writer.setCreateOptions(['COMPRESS=LZW']) 
        writer.setOutputProviderKey(layer_to_write.providerType())
        writer.setOutputFormat('GTiff')
        writer.writeRaster(pipe, provider.xSize(), provider.ySize(), layer_to_write.extent(), provider.crs())

        ## couldn't get below part to work properly, it changes everything about the raster layers
        # layer_to_write.setDataSource(file_path, layer_to_write.name(), "gdal")

        # if is_final_result:
        #     project_file_path = os.path.join(project_criteria_folder_path, project.project_name + ".qgz")
        #     QgsProject.instance().write(project_file_path)

        return file_path
    except Exception:
        traceback.print_exc()
        return False

