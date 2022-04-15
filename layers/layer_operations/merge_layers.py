import bpy
from bpy.types import Operator

class COATER_OT_merge_layer(Operator):
    """Merges the selected layer with the layer below."""
    bl_idname = "coater.merge_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the selected layer with the layer below."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return False

    def execute(self, context):
        return{'FINISHED'}