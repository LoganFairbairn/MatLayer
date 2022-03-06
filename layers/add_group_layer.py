import bpy
from bpy.types import Operator

class COATER_OT_add_group_layer(Operator):
    '''Adds a new layer with a group layer to the layer stack.'''
    bl_idname = "coater.add_group_layer"
    bl_label = "Add Group Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new layer with a custom group node as the color value."

    @ classmethod
    def poll(cls, context):
        return False

    def execute(self, context):

        return {'FINISHED'}