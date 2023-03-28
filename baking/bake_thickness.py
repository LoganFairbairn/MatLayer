# This file contains the function for baking thickness maps.

import bpy
from bpy.types import Operator

class MATLAY_OT_bake_thickness(Operator):
    bl_idname = "matlay.bake_thickness"
    bl_label = "Bake Thickness"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}