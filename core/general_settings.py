import bpy
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path

from ..utilities import info_messages

class MATLAY_OT_append_workspace(Operator):
    '''Appends a suggested layout for using this add-on.'''
    bl_idname = "matlay.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        workspace = bpy.data.workspaces.get('Matlay')
        if workspace:
            info_messages.popup_message_box("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", 'Info', 'INFO')
            return {'FINISHED'}


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

        # Reset the main pannel tab.
        context.scene.matlay_panel_properties.sections = 'SECTION_TEXTURE_SET'

        return {'FINISHED'}