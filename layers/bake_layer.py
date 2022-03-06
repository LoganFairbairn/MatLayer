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
        return {'FINISHED'}