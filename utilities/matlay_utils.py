# This module contains general utility functions for this add-on.

import os
import bpy
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path
from ..core import material_channels
from ..core import layer_nodes
from ..core import layer_masks
from . import logging
from ..preferences import ADDON_NAME

def set_valid_mode():
    '''Verifies texture or object mode is being used. This should be used to avoid attempting to run functions in the wrong mode which may throw errors.'''
    if (bpy.context.object.mode != 'TEXTURE_PAINT' and bpy.context.object.mode != 'OBJECT'):
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')

def set_valid_material_shading_mode(context):
    '''Verifies the user is using material or rendered shading mode and corrects the shading mode if they are using a different mode. This allows users to visually see the changes they to the material make when calling select operators.'''
    if context.space_data:
        if context.space_data.type == 'VIEW_3D':
            if context.space_data.shading.type != 'MATERIAL' and context.space_data.shading.type != 'RENDERED':
                context.space_data.shading.type = 'MATERIAL'

def delete_unused_layer_images(self, context):
    '''Deletes unused layer and mask images.'''
    # Create a list of all images used within the layer stack.
    used_image_paths = []

    material_layers = context.scene.matlay_layers
    masks = context.scene.matlay_masks
    material_channel_list = material_channels.get_material_channel_list()

    for material_channel_name in material_channel_list:
        for i in range(0, len(material_layers)):
            nodes = layer_nodes.get_all_nodes_in_layer(material_channel_name, i, context, False)
            for node in nodes:
                if node:
                    if node.bl_static_type == 'TEX_IMAGE':
                        if node.image != None and node.image.filepath != '':
                            if node.image.filepath not in used_image_paths:
                                used_image_paths.append(node.image.filepath)
                                print("Added image path: " + node.image.filepath)

    for i in range(0, len(material_layers)):
        for c in range(0, len(masks)):
            node = layer_masks.get_mask_node('MaskTexture', material_channel_name, i, c, False)
            if node:
                if node.bl_static_type == 'TEX_IMAGE':
                    if node.image != None and node.image.filepath != '':
                        if node.image.filepath not in used_image_paths:
                            used_image_paths.append(node.image.filepath)
                            print("Added image path: " + node.image.filepath)


    # Delete all images in the layer / mask folder that are not linked to any layers.
    matlay_image_path = os.path.join(bpy.path.abspath("//"), "Matlay")
    layer_image_path = os.path.join(matlay_image_path, "Layers")
    mask_image_path = os.path.join(matlay_image_path, "Masks")

    folder_images = []
    if os.path.exists(layer_image_path):
        for file in os.listdir(layer_image_path):
            file_path = os.path.join(layer_image_path, file)
            folder_images.append(file_path)
            print("Added file: " + file_path)

    if os.path.exists(mask_image_path):
        for file in os.listdir(mask_image_path):
            file_path = os.path.join(mask_image_path, file)
            folder_images.append(file_path)
            print("Added file: " + file_path)
    
    deleted_unused_images = False
    for path in folder_images:
        if path not in used_image_paths:
            if os.path.exists(path):
                os.remove(path)
                print("Deleted unused image: " + path)
                deleted_unused_images = True

    if deleted_unused_images:
        self.report({'INFO'}, "Deleted unused images.")
    else:
        self.report({'INFO'}, "No unused images to delete.")

class MATLAY_OT_set_decal_layer_snapping(Operator):
    '''Sets optimal snapping settings for positioning decal layers. You can disable the snapping mode by selecting the magnet icon in the middle top area of the 3D viewport.'''
    bl_idname = "matlay.set_decal_layer_snapping"
    bl_label = "Set Decal Layer Snapping"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets optimal snapping settings for positioning decal layers"

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
        bpy.context.scene.tool_settings.snap_target = 'CENTER'
        bpy.context.scene.tool_settings.use_snap_align_rotation = True
        return {'FINISHED'}

class MATLAY_OT_append_workspace(Operator):
    '''Appends a suggested layout for using this add-on.'''
    bl_idname = "matlay.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    def execute(self, context):
        workspace = bpy.data.workspaces.get('Matlay')
        if workspace:
            logging.popup_message_box("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", 'Info', 'INFO')
            return {'FINISHED'}

        print("Addon name: " + ADDON_NAME)
        USER = Path(resource_path('USER'))
        ADDON = ADDON_NAME
        BLEND_FILE = "Matlay.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)
        
        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.workspaces = ["Matlay"]

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['Matlay']

        # Reset the main pannel tab.
        context.scene.matlay_panel_properties.sections = 'SECTION_TEXTURE_SET'

        return {'FINISHED'}

class MATLAY_OT_append_basic_brushes(Operator):
    '''Appends basic brush presets to the current blend file.'''
    bl_idname = "matlay.append_basic_brushes"
    bl_label = "Append Basic Brushes"
    bl_description = "Not yet implemented"

    @ classmethod
    def poll(cls, context):
        #return context.active_object
        return False

    def execute(self, context):
        USER = Path(resource_path('USER'))
        ADDON = "Matlay"
        BLEND_FILE = "Matlay.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)

        blendfile = source_path
        section = "\\Brushes\\"
        object = "Matlay"

        filepath  = blendfile + section + object
        directory = blendfile + section
        filename  = object


        # TODO: Append all brushes here.
        bpy.ops.wm.append(
            filepath=filepath, 
            filename=filename,
            directory=directory)

        return {'FINISHED'}

class MATLAY_OT_delete_unused_images(Operator):
    """Deletes unused saved layer and mask images from folders."""
    bl_idname = "matlay.delete_unused_images"
    bl_label = "Delete Unused Images"
    bl_description = "Deletes unused saved layer and mask images from folders. This is a quick method for clearing out unused textures created with this add-on"

    def execute(self, context):
        delete_unused_layer_images(self, context)
        return{'FINISHED'}

