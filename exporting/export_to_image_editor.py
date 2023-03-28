import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

class MATLAY_OT_image_editor_export(Operator):
    '''Exports the selected image paint canvas to the image editor defined in Blender's preferences'''
    bl_idname = "matlay.image_editor_export"
    bl_label = "Export to External Image Editor"
    bl_description = "Exports the select image layer to the image editor defined in Blender's preferences"

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers
        False

    def execute(self, context):
        export_image = context.scene.tool_settings.image_paint.canvas

        if export_image != None:
            if export_image.packed_file == None:
                if export_image.file_format == '' or export_image.filepath == '':
                    if export_image.is_dirty:
                        export_image.save()
                else:
                    self.report({'ERROR'}, "Export image has no defined filepath.")
            else:
                self.report({'ERROR'}, "Export image can't be packed to export to an external image editor.")
            bpy.ops.image.external_edit(filepath=export_image.filepath)

        return {'FINISHED'}