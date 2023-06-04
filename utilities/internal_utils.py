# This module contains misc utility functions used internally (only in code) for this add-on.

import bpy
from bpy.utils import resource_path
from pathlib import Path
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

def get_blend_assets_path():
    '''Returns the asset path for the blend file.'''
    blend_assets_path = str(Path(resource_path('USER')) / "scripts/addons" / ADDON_NAME / "blend" / "Matlayer.blend")
    return blend_assets_path

def append_custom_node_tree(node_tree_name, never_auto_delete):
    '''Appends a node tree with the provided name from the asset bank blend file for this add-on.'''
    node_tree = bpy.data.node_groups.get(node_tree_name)
    if node_tree == None:
        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path) as (data_from, data_to):
            data_to.node_groups = [node_tree_name]

        # Mark node trees with a 'fake user' to stop them from being auto deleted from the blend file if they are not used.
        # This makes loading group nodes slightly faster for the next use if they were previously deleted, and allows users to look at the appended group nodes.
        node_tree = bpy.data.node_groups.get(node_tree_name)
        if never_auto_delete:
            node_tree.use_fake_user = True
        return node_tree
    return node_tree

def get_uv_mapping_node_tree():
    '''Returns a custom mapping node group for UV / flat projection. The node tree will be appended if it doesn't exist in the current blend file.'''
    return append_custom_node_tree("ML_OFFSET_ROTATION_SCALE", True)

def get_normal_map_rotation_fix_node_tree():
    '''Returns a custom node tree designed to fix normal map rotations. The node tree will be appended if it doesn't exist in the current blend file.'''
    return append_custom_node_tree("ML_FIX_NORMAL_ROTATION", True)

def get_triplanar_mapping_tree():
    '''Returns a custom node tree designed specifically for triplanar projection. The node tree will be appended if it doesn't exist in the current blend file.'''
    return append_custom_node_tree("ML_TRIPLANAR_MAPPING", True)

def get_triplanar_node_tree():
    '''Returns a custom triplanar projection node tree. The node tree will be appended if it doesn't exist in the current blend file.'''
    return append_custom_node_tree("ML_TRIPLANAR", True)

def get_normal_triplanar_node_tree():
    '''Returns a custom triplanar projection node tree specifically for correct normal map projections. The node tree will be appended if it doesn't exist in the current blend file.'''
    return append_custom_node_tree("ML_TRIPLANAR_NORMALS", True)

def get_flat_blur_node_tree():
    '''Returns a group node that can be used to blur flat / uv projected textures.'''
    return append_custom_node_tree("ML_FLAT_BLUR", True)

def get_triplanar_blur_node_tree():
    '''Returns a group node that can be used to blur triplanar projected textures.'''
    return append_custom_node_tree("ML_TRIPLANAR_BLUR", True)

def append_default_node_trees():
    '''Appends important node trees used in this add-on.'''
    # Appending node trees in a defined order helps avoid duplicate node trees.
    get_triplanar_node_tree()
    get_triplanar_mapping_tree()
    get_normal_triplanar_node_tree()
    get_normal_map_rotation_fix_node_tree()
    get_triplanar_blur_node_tree()
    get_flat_blur_node_tree()

def get_node_by_bl_static_type(nodes, bl_static_type):
    '''Finds and returns a node by it's bl_static_type.'''
    # When using a different language, default nodes must be accessed using their type because their default name translates.
    for node in nodes:
        if node.bl_static_type == bl_static_type:
            return node
