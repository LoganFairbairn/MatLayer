# This module contains misc / general Blender add-on utility functions such as debug logging, appending assets from an asset blend file, and adjusting modes.

import bpy
from bpy.utils import resource_path
from pathlib import Path
from .. import preferences
import datetime

def set_valid_material_editing_mode():
    '''Verifies texture or object mode is being used. This should be used to avoid attempting to run material editing functions in the wrong mode (Edit Mode, Pose Mode, Weight Paint, etc...) which may throw errors.'''
    if (bpy.context.object.mode != 'TEXTURE_PAINT' and bpy.context.object.mode != 'OBJECT'):
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')

def set_valid_material_shading_mode(context):
    '''Verifies the user is using material or rendered shading mode and corrects the shading mode if they are using a different mode. This allows users to visually see the changes they to the material make when calling select operators.'''
    if context.space_data:
        if context.space_data.type == 'VIEW_3D':
            if context.space_data.shading.type != 'MATERIAL' and context.space_data.shading.type != 'RENDERED':
                context.space_data.shading.type = 'MATERIAL'

def get_blend_assets_path():
    '''Returns the asset path for the blend file.'''
    blend_assets_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "blend" / "Assets.blend")
    return blend_assets_path

def append_default_node_groups():
    '''Appends default nodes to the current blend file. This ensures sub node groups will not be duplicated when appending node groups that contain sub node groups.'''
    append_node_group("ML_AdjustNormalIntensity", never_auto_delete=True)
    append_node_group("ML_AmbientOcclusion", never_auto_delete=True)
    append_node_group("ML_Blur", never_auto_delete=True)
    append_node_group("ML_CheapContrast", never_auto_delete=True)
    append_node_group("ML_Curvature", never_auto_delete=True)
    append_node_group("ML_FixNormalRotation", never_auto_delete=True)
    append_node_group("ML_NormalAndHeightMix", never_auto_delete=True)
    append_node_group("ML_OffsetRotationScale", never_auto_delete=True)
    append_node_group("ML_Thickness", never_auto_delete=True)
    append_node_group("ML_Triplanar", never_auto_delete=True)
    append_node_group("ML_TriplanarBlur", never_auto_delete=True)
    append_node_group("ML_TriplanarMapping", never_auto_delete=True)
    append_node_group("ML_TriplanarNormalFix", never_auto_delete=True)
    append_node_group("ML_TriplanarNormals", never_auto_delete=True)
    append_node_group("ML_WorldSpaceNormals", never_auto_delete=True)
    append_node_group("ML_WorldToTangentSpace", never_auto_delete=True)

def append_node_group(node_group_name, never_auto_delete):
    '''Appends a node tree with the provided name from the asset blend file for this add-on.'''
    node_tree = bpy.data.node_groups.get(node_group_name)
    if node_tree == None:
        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=False) as (data_from, data_to):
            data_to.node_groups = [node_group_name]

        # Mark node trees with a 'fake user' to stop them from being auto deleted from the blend file if they are not used.
        # This makes loading group nodes slightly faster for the next use if they were previously deleted, and allows users to look at the appended group nodes.
        node_tree = bpy.data.node_groups.get(node_group_name)
        if never_auto_delete:
            node_tree.use_fake_user = True
        return node_tree
    return node_tree

def append_material(material_name):
    '''Appends a material with the provided name from the asset blend file for this add-on'''
    material = bpy.data.materials.get(material_name)
    if material == None:
        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=False) as (data_from, data_to):
            data_to.materials = [material_name]
        material = bpy.data.materials.get(material_name)
        return material
    return material

def get_node_by_bl_static_type(nodes, bl_static_type):
    '''Finds and returns a node by it's bl_static_type.'''
    # When using a different language, default nodes must be accessed using their type because their default name translates.
    for node in nodes:
        if node.bl_static_type == bl_static_type:
            return node

def create_image(image_name, image_width, image_height, alpha_channel=False, thirty_two_bit=False, data=False):
    '''Deletes existing images with the same name if it exists, then creates a new image in Blender's data with the provided settings.'''

    # Delete an image that shares the same name if one exists.
    new_image = bpy.data.images.get(image_name)
    if new_image:
        bpy.data.images.remove(new_image)

    # Create a new image.
    new_image = bpy.data.images.new(name=image_name,
                                    width=image_width,
                                    height=image_height,
                                    alpha=alpha_channel,
                                    float_buffer=thirty_two_bit,
                                    stereo3d=False,
                                    is_data=data,
                                    tiled=False)
    return new_image

def log(message):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.logging:
        print("[{0}]: {1}".format(datetime.datetime.now(), message))

def log_status(message, self, type='ERROR'):
    '''Prints the given message to Blender's console window and displays the message in Blender's status bar.'''
    log(message)
    self.report({type}, message)

def popup_message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw_popup_box(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_popup_box, title = title, icon = icon)
    print(title + ": " + message)