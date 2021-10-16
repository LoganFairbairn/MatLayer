import bpy


class COATER_OT_toggle_texture_paint_mode(bpy.types.Operator):
    bl_idname = "coater.toggle_texture_paint_mode"
    bl_label = " "
    bl_description = "Toggles texture paint mode."

    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}
