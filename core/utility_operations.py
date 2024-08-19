# This module contains extra utility operations that assist with using this add-on or material editing in general.

import bpy
import os
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path
from ..core import debug_logging
from ..core import blender_addon_utils
from ..preferences import ADDON_NAME

class MATLAYER_OT_set_decal_layer_snapping(Operator):
    bl_idname = "matlayer.set_decal_layer_snapping"
    bl_label = "Set Decal Layer Snapping"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets optimal snapping settings for positioning decal layers. You can disable the snapping mode by selecting the magnet icon in the middle top area of the 3D viewport"

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
        bpy.context.scene.tool_settings.snap_target = 'CENTER'
        bpy.context.scene.tool_settings.use_snap_align_rotation = True
        return {'FINISHED'}

class MATLAYER_OT_append_workspace(Operator):
    bl_idname = "matlayer.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    def execute(self, context):
        workspace = bpy.data.workspaces.get('Matlayer')
        if workspace:
            debug_logging.log_status("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", self, 'INFO')
            return {'FINISHED'}
        
        USER = Path(resource_path('USER'))
        ADDON = ADDON_NAME
        BLEND_FILE = "Assets.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)
        
        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.workspaces = ["Matlayer"]

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['Matlayer']
        
        # Set the UI to the default tab.
        context.scene.matlayer_panel_properties.sections = 'SECTION_LAYERS'

        # Set up a material asset browser for the user.
        preferences = bpy.context.preferences
        if not preferences.filepaths.asset_libraries.get("MatLayer Default Assets"):
            bpy.ops.preferences.asset_library_add()
            new_library = bpy.context.preferences.filepaths.asset_libraries[-1]
            new_library.name = "MatLayer Default Assets"
            new_library.path = str(USER / "scripts/addons" / ADDON / "blend")

        self.report({'INFO'}, "Appended workspace (check the workspaces / user interface layouts at the top of your screen).")

        return {'FINISHED'}

class MATLAYER_OT_append_basic_brushes(Operator):
    bl_idname = "matlayer.append_basic_brushes"
    bl_label = "Append Basic Brushes"
    bl_description = "Appends basic brush presets to the current blend file"

    def execute(self, context):
        brush_prefix = "ML_"

        # Delete any Matlayer brushes if they exist before re-importing them.
        for brush in bpy.data.brushes:
            if brush.name.startswith(brush_prefix):
                bpy.data.brushes.remove(brush)

        USER = Path(resource_path('USER'))
        BLEND_FILE = "Assets.blend"
        source_path =  str(USER / "scripts/addons" / ADDON_NAME / "blend" / BLEND_FILE)

        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.brushes = [name for name in data_from.brushes if name.startswith(brush_prefix)]
            
        # For all loaded brushes, assign a brush icon image.
        brush_preview_images_path = str(USER / "scripts/addons" / ADDON_NAME / "brush_icons")
        for brush in bpy.data.brushes:
            if brush.name.startswith(brush_prefix):
                brush.use_custom_icon = True
                brush_icon_name = brush.name.split('_')[1]
                brush.icon_filepath = os.path.join(brush_preview_images_path, brush_icon_name + ".png")

        self.report({'INFO'}, "Appended basic brushes. Check the brush presets to see them (Texture Paint Mode -> Tool (3D view sidebar) -> Brushes)")

        return {'FINISHED'}

class MATLAYER_OT_append_hdri_world(Operator):
    bl_idname = "matlayer.append_hdri_world"
    bl_label = "Append HDRI World"
    bl_description = "Appends a world environment setup for HDRI lighting"

    def execute(self, context):
        blender_addon_utils.append_world('HDRIWorld')
        bpy.context.scene.world = bpy.data.worlds['HDRIWorld']
        return {'FINISHED'}

class MATLAYER_OT_remove_unused_raw_textures(Operator):
    bl_idname = "matlayer.remove_unused_textures"
    bl_label = "Remove Unused Textures"
    bl_description = "Removes all unused textures from the blend file, and all textures not used in the external raw texture folder"

    def execute(self, context):
        external_folder_path = blender_addon_utils.get_texture_folder_path(folder='RAW_TEXTURES')

        # Delete all images externally then internally for all images with no users.
        for image in bpy.data.images:
            if image.users <= 0:
                image_name = image.name
                if not image.filepath == "":
                    file_extension = os.path.splitext(image.filepath)[1]
                    image_path = os.path.join(external_folder_path, image_name + file_extension)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        debug_logging.log("Deleted unused external image: {0}".format(image_name))

                bpy.data.images.remove(image)
                debug_logging.log("Deleted unused internal image: {0}".format(image_name))

        # If the image exists externally, but doesn't exist in blend data, delete it.
        internal_image_names = []
        for image in bpy.data.images:
            internal_image_names.append(image.name)
        external_textures = os.listdir(external_folder_path)
        for texture_name_and_extension in external_textures:
            texture_name = os.path.splitext(texture_name_and_extension)[0]
            if texture_name not in internal_image_names:
                image_path = os.path.join(external_folder_path, texture_name_and_extension)
                os.remove(image_path)
                debug_logging.log("Deleted external image that doesn't exist internally: {0}".format(texture_name))

        return {'FINISHED'}