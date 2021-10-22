import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

class COATER_OT_image_editor_export(Operator):
    '''Exports the select image layer to the image editor defined in Blender's preferences'''
    bl_idname = "coater.image_editor_export"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports the select image layer to the image editor defined in Blender's preferences"

    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers
        False

    def execute(self, context):
        # TODO: Export the selected image layer to the image editor defined in Blender's preferences.
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        print("Image Filepath: " + layers[layer_index].color_image.filepath)
        bpy.ops.image.external_edit(filepath=layers[layer_index].color_image.filepath)
        return {'FINISHED'}