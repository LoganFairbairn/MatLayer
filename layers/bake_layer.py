import bpy
from bpy.types import Operator

class COATER_OT_bake_layer(Operator):
    '''Bakes the selected layer to an image layer.'''
    bl_idname = "coater.bake_layer"
    bl_label = "Bake Layer"
    bl_description = "Bakes the selected layer to an image layer"

    @ classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        # TODO: Turn off all layers excluding the selected one.

        # TODO: Create an image to bake to.

        # TODO: Create an image layer and add the image to it.
        return {'FINISHED'}