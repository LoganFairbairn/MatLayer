import bpy
from bpy.types import Operator

class COATER_OT_open_settings(Operator):
    bl_idname = "coater.open_settings"
    bl_label = "Open Settings"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Opens a menu with all settings."

    def execute(self, context):
        return {'FINISHED'}