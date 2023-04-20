import bpy
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path

class MATLAY_OT_append_workspace(Operator):
    '''Appends a suggested layout for using this add-on.'''
    bl_idname = "matlay.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        USER = Path(resource_path('USER'))
        ADDON = "Matlay"
        BLEND_FILE = "Matlay.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)

        blendfile = source_path
        section   = "\\WorkSpace\\"
        object    = "Matlay"

        filepath  = blendfile + section + object
        directory = blendfile + section
        filename  = object

        bpy.ops.wm.append(
            filepath=filepath, 
            filename=filename,
            directory=directory)

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['Matlay']

        return {'FINISHED'}