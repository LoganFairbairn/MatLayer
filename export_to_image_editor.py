import bpy


class COATER_OT_image_editor_export(bpy.types.Operator):
    '''Exports the select image layer to the image editor defined in Blender's preferences'''
    bl_idname = "coater.image_editor_export"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports the select image layer to the image editor defined in Blender's preferences"

    def execute(self, context):
        # TODO: Export the selected image layer to the image editor defined in Blender's preferences.
        return {'FINISHED'}
