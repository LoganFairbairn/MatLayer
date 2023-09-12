# This module contains misc / general Blender add-on utility functions such as, appending assets from an asset blend file, and adjusting modes.

import bpy
from bpy.utils import resource_path
import numpy as np
from pathlib import Path
from ..core import debug_logging
from .. import preferences

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

def verify_material_operation_context(self, display_message=True, check_active_object=True, check_mesh=True, check_active_material=True):
    '''Runs checks to verify that a material editing operation can be ran without errors. Returns True if the all conditions are correct for a material editing operation to be ran.'''
    
    # Check for an active object.
    if check_active_object and not bpy.context.active_object:
        if display_message:
            debug_logging.log_status("No active object.", self, 'ERROR')
        return False
    
    # Check the active object is a mesh.
    if check_mesh and bpy.context.active_object.type != 'MESH':
        if display_message:
            debug_logging.log_status("Selected object must be a mesh.", self, 'ERROR')
        return False
    
    # Check for an active material.
    if check_active_material and not bpy.context.active_object.active_material:
        if display_message:
            debug_logging.log_status("No active material.", self, 'ERROR')
        return False
    
    # No context issues found, return true.
    return True

def get_blend_assets_path():
    '''Returns the asset path for the blend file.'''
    blend_assets_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "blend" / "Assets.blend")
    return blend_assets_path

def duplicate_node_group(node_group_name):
    '''Duplicates (makes a unique version of) the provided node group.'''
    node_group = bpy.data.node_groups.get(node_group_name)
    if node_group:
        duplicated_node_group = node_group.copy()
        duplicated_node_group.name = node_group_name + "_Copy"
        return duplicated_node_group
    else:
        debug_logging.log("Error: Can't duplicate node, group node with the provided name does not exist.")
        return None

def append_default_node_groups():
    '''Appends default nodes used by this add-on to the current blend file. Appending node groups in an initial batch helps avoid appending duplicates of node groups.'''
    append_group_node("ML_TriplanarNormalsBlend", never_auto_delete=True)
    append_group_node("ML_DefaultLayer", never_auto_delete=True)
    append_group_node("ML_DecalLayer", never_auto_delete=True)
    append_group_node("ML_LayerBlur", never_auto_delete=True)
    append_group_node("ML_TriplanarBlur", never_auto_delete=True)
    append_group_node("ML_TriplanarLayerBlur", never_auto_delete=True)
    append_group_node("ML_UVProjection", never_auto_delete=True)
    append_group_node("ML_TriplanarProjection", never_auto_delete=True)
    append_group_node("ML_TriplanarNormalFix", never_auto_delete=True)
    append_group_node("ML_WorldToTangentSpace", never_auto_delete=True)
    append_group_node("ML_TriplanarBlend", never_auto_delete=True)
    append_group_node("ML_ImageMask", never_auto_delete=True)
    append_group_node("ML_EdgeWear", never_auto_delete=True)
    append_group_node("ML_Blur", never_auto_delete=True)
    append_group_node("ML_NormalAndHeightMix", never_auto_delete=True)
    append_group_node("ML_AdjustNormalIntensity", never_auto_delete=True)
    append_group_node("ML_FixNormalRotation", never_auto_delete=True)
    append_group_node("ML_OffsetRotationScale", never_auto_delete=True)
    append_group_node("ML_CheapContrast", never_auto_delete=True)
    append_group_node("ML_DefaultColor", never_auto_delete=True)
    append_group_node("ML_DefaultSubsurface", never_auto_delete=True)
    append_group_node("ML_DefaultMetallic", never_auto_delete=True)
    append_group_node("ML_DefaultSpecular", never_auto_delete=True)
    append_group_node("ML_DefaultRoughness", never_auto_delete=True)
    append_group_node("ML_DefaultEmission", never_auto_delete=True)
    append_group_node("ML_DefaultNormal", never_auto_delete=True)
    append_group_node("ML_DefaultHeight", never_auto_delete=True)

def cleanse_duplicated_node_groups(old_node_groups, cleanse_node_groups=True, cleanse_materials=True):
    '''Replaces and removes all duplicated node groups within blender that were appended from sub-node groups.'''
    # Replace and remove duplicate node trees from group nodes.
    if cleanse_node_groups:
        for node_tree in bpy.data.node_groups:
            for node in node_tree.nodes:
                if node.type == 'GROUP':
                    if node.node_tree != None:
                        (original_node_group_name, separator, duplicate_number) = node.node_tree.name.rpartition('.')
                        if duplicate_number.isnumeric() and len(duplicate_number) == 3:
                            duplicate_node_tree = node.node_tree
                            original_node_group = bpy.data.node_groups.get(original_node_group_name)
                            if original_node_group:
                                if original_node_group:
                                    duplicate_node_tree.use_fake_user = False
                                    bpy.data.node_groups.remove(duplicate_node_tree)
                                    node.node_tree = original_node_group

    # Replace and remove duplicate node trees from material node trees.
    if cleanse_materials:
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'GROUP':
                        if node.node_tree != None:
                            (original_node_group_name, separator, duplicate_number) = node.node_tree.name.rpartition('.')
                            if duplicate_number.isnumeric() and len(duplicate_number) == 3:
                                duplicate_node_tree = node.node_tree
                                original_node_group = bpy.data.node_groups.get(original_node_group_name)
                                if original_node_group:
                                    if original_node_group:
                                        duplicate_node_tree.use_fake_user = False
                                        bpy.data.node_groups.remove(duplicate_node_tree)
                                        node.node_tree = original_node_group

    # In some cases, it's possible to append node trees that don't exist in group nodes any materials or node trees.
    # Remove all recently appended group nodes with 0 users.
    new_node_groups = [group for group in bpy.data.node_groups]
    node_group_existed = np.isin(new_node_groups, old_node_groups)
    for i in range(0, len(node_group_existed)):
        if not node_group_existed[i]:
            if new_node_groups[i].users == 0:
                bpy.data.node_groups.remove(new_node_groups[i])

def append_group_node(node_group_name, keep_link=False, return_unique=False, append_missing=True, never_auto_delete=True):
    '''Returns the group node with the provided name. appends appends it from the asset blend file for this add-on if it doesn't exist.'''

    node_tree = bpy.data.node_groups.get(node_group_name)

    # If the node group doesn't exist, attempt to append it from the blend asset file for the add-on.
    if not node_tree and append_missing:
        old_node_groups = [group for group in bpy.data.node_groups]

        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=keep_link) as (data_from, data_to):
            data_to.node_groups = [node_group_name]
        
        # Check if the node group was successfully appended.
        node_tree = bpy.data.node_groups.get(node_group_name)
        if node_tree:

            # Mark appended node trees with a 'fake user' to stop them from being auto deleted from the blend file if they are not actively used.
            if never_auto_delete:
                node_tree.use_fake_user = True

            cleanse_duplicated_node_groups(old_node_groups, cleanse_node_groups=True, cleanse_materials=False)

        # Throw an error if the node group doesn't exist and can't be appended.
        else:
            debug_logging.log_status("{0} does not exist and has failed to append from the blend asset file.".format(node_group_name))
            return None

    # Returning a duplicated version of an existing node group (rather than appending a new one) can be beneficial to help avoid appending duplicated of sub node groups.
    # Return a unique (duplicated) version of the node group if specified.
    if return_unique:
        duplicated_node_group = duplicate_node_group(node_group_name)
        return duplicated_node_group
    
    # Return the node tree.
    return node_tree

def append_material(material_name, append_missing=True):
    '''Appends a material with the provided name from the asset blend file for this add-on'''

    material = bpy.data.materials.get(material_name)

    # If the material doesn't exist, attempt to append it from the blend asset file for this add-on.
    if not material and append_missing:
        old_node_groups = [group for group in bpy.data.node_groups]

        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=False) as (data_from, data_to):
            data_to.materials = [material_name]
        material = bpy.data.materials.get(material_name)

        cleanse_duplicated_node_groups(old_node_groups, cleanse_node_groups=True, cleanse_materials=True)

        return material
    
    # The material already exists, return the material.
    else:
        return material

def append_image(image_name):
    '''Appends the specified texture from the blend asset file for this add-on.'''
    image = bpy.data.images.get(image_name)
    if image == None:
        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=False) as (data_from, data_to):
            data_to.images = [image_name]
        image = bpy.data.images.get(image_name)
        return image
    return image

def get_node_by_bl_static_type(nodes, bl_static_type):
    '''Finds and returns a node by it's bl_static_type.'''
    # When using a different language, default nodes must be accessed using their type because their default name translates.
    for node in nodes:
        if node.bl_static_type == bl_static_type:
            return node

def create_image(image_name, image_width, image_height, alpha_channel=False, thirty_two_bit=False, data=False)
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

def set_node_active(node, active):
    '''Marks the node as inactive by changing it's color. This is a work-around for a memory leak within Blender caused by compiling shaders that contain muted group nodes'''
    if active:
        node.use_custom_color = False
        node.color = (0.1, 0.1, 0.1)
    else:
        node.use_custom_color = True
        node.color = (1.0, 0.0, 0.0)

def get_node_active(node):
    '''Returns true if the provided node is marked as active according to this add-on. This is a work-around for a memory leak within Blender caused by compiling shaders that contain muted group nodes'''
    if node == None:
        return False
    
    if node.color.r == 1.0 and node.color.g == 0.0 and node.color.b == 0.0:
        return False
    else:
        return True
    
def unlink_node(node, node_tree, unlink_inputs=True, unlink_outputs=True):
    '''Unlinks the given nodes input and / or outputs.'''

    if unlink_inputs:
        for input in node.inputs:
            for link in input.links:
                node_tree.links.remove(link)
    
    if unlink_outputs:
        for output in node.outputs:
            for link in output.links:
                node_tree.links.remove(link)

def set_texture_paint_image(image):
    '''Sets the image being actively edited using Blender's texture paint mode to the provided image if it exists within the texture paint slots from the active material.'''
    if image:
        #texture_paint_images = bpy.context.active_object.active_material.texture_paint_images
        #texture_paint_slot_index = texture_paint_images.find(image.name)
        #if texture_paint_slot_index >= 0 and texture_paint_slot_index < len(texture_paint_images):
        #    bpy.context.object.active_material.paint_active_slot = texture_paint_slot_index
        bpy.context.scene.tool_settings.image_paint.canvas = image
    else:
        debug_logging.log("Can't set texture paint image, invalid image provided.")