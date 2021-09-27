# This file contains quick operations to adjust blender's display settings.
import bpy


class COATER_OT_set_hand_painted(bpy.types.Operator):
    bl_idname = "material.set_hand_painted"
    bl_label = "Set hand painted."
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Selects a layer from the layer stack."

    def execute(self, context):
        bpy.context.scene.view_settings.view_transform = 'Standard'
        return {'FINISHED'}
