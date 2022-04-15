# This file contains the function for baking thickness maps.

import bpy
from bpy.types import Operator

class COATER_OT_bake_thickness(Operator):
    bl_idname = "coater.bake_thickness"
    bl_label = "Bake Thickness"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}


class COATER_OT_toggle_thickness_preview(Operator):
    bl_idname = "coater.toggle_thickness_preview"
    bl_label = "Preview Thickness"
    bl_description = "Previews thickness map bake result on the active object"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        material_name  = "Coater_Thickness"
        return {'FINISHED'}