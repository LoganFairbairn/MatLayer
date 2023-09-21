# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import IntProperty, EnumProperty, StringProperty
from ..core import layer_masks
from . import mesh_map_baking
from ..core import blender_addon_utils
from ..core import debug_logging
from ..core import texture_set_settings as tss
import random

# List of node types that can be used in the texture slot.

MATERIAL_CHANNEL = [
    ("COLOR", "Color", ""), 
    ("SUBSURFACE", "Subsurface", ""),
    ("METALLIC", "Metallic", ""),
    ("SPECULAR", "Specular", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", ""),
    ("ALPHA", "Alpha", "")
]

MATERIAL_CHANNEL_LIST = (
    'COLOR',
    'SUBSURFACE',
    'METALLIC',
    'SPECULAR',
    'ROUGHNESS',
    'EMISSION',
    'NORMAL',
    'HEIGHT',
    'ALPHA'
)

#----------------------------- UPDATING PROPERTIES -----------------------------#

def update_layer_index(self, context):
    '''Updates properties and user interface when a new layer is selected.'''

    # Check that the active object attribute exists within the current Blender context.
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if active_object_attribute == None:
        return
    
    show_layer()
    layer_masks.refresh_mask_slots()

    # Select the image for texture painting.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
    value_node = get_material_layer_node('VALUE', selected_layer_index, selected_material_channel)
    if value_node:
        if value_node.bl_static_type == 'TEX_IMAGE':
            if value_node.image != None:
                blender_addon_utils.set_texture_paint_image(value_node.image)
    
    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:

            # Apply snapping mode based on the layer type.
            projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
            if projection_node:
                match projection_node.node_tree.name:
                    case 'ML_UVProjection':
                        blender_addon_utils.set_snapping('DEFAULT', snap_on=False)
                    case 'ML_TriplanarProjection':
                        blender_addon_utils.set_snapping('DEFAULT', snap_on=False)
                    case 'ML_DecalProjection':
                        blender_addon_utils.set_snapping('DECAL', snap_on=True)

            # Hide all decal objects excluding the one for this layer (if this layer is a decal layer).
            material_layers = bpy.context.scene.matlayer_layers
            for i in range(0, len(material_layers)):
                decal_coordinates_node = get_material_layer_node('DECAL_COORDINATES', i)
                if decal_coordinates_node:
                    if decal_coordinates_node.object:
                        if i == selected_layer_index:
                            decal_coordinates_node.object.hide_set(False)
                        else:
                            decal_coordinates_node.object.hide_set(True)

def sync_triplanar_samples():
    '''Syncs triplanar texture samples to match the first texture sample (only if triplanar projection is being used).'''
    if blender_addon_utils.verify_material_operation_context(display_message=False) == False:
        return

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        if projection_node.node_tree.name == 'ML_TriplanarProjection':
            for material_channel_name in MATERIAL_CHANNEL_LIST:
                value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=1)
                if value_node:
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        texture_sample_2 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=2)
                        texture_sample_3 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=3)
                        
                        # Running these additional if checks to avoid accidentally triggering shader re-compiling by changing an image to the same image.
                        if texture_sample_2:
                            if texture_sample_2.image != value_node.image:
                                texture_sample_2.image = value_node.image
                        if texture_sample_3:
                            if texture_sample_3.image != value_node.image:
                                texture_sample_3.image = value_node.image

def get_shorthand_material_channel_name(material_channel_name):
    '''Returns the short-hand version of the provided material channel name.'''
    match material_channel_name:
        case 'COLOR':
            return 'COLOR'
        case 'SUBSURFACE':
            return 'SUBSURF'
        case 'METALLIC':
            return 'METAL'
        case 'SPECULAR':
            return 'SPEC'
        case 'ROUGHNESS':
            return 'ROUGH'
        case 'EMISSION':
            return 'EMIT'
        case 'NORMAL':
            return 'NORMAL'
        case 'HEIGHT':
            return 'HEIGHT'
        case 'ALPHA':
            return 'ALPHA'

def format_layer_group_node_name(material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(material_name, layer_index)

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    
    if not bpy.context.active_object:
        return None
    
    if not bpy.context.active_object.active_material:
        return None
    
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)

    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index=0, material_channel_name='COLOR', node_number=1, get_changed=False):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''

    # This function exists to allow easy access to premade nodes from materials a node tree appended from an asset blend file.
    # Using specified names for nodes allows consistent access to specific nodes accross languages in Blender (as Blender's auto translate feature will translate default node names).
    # This function also has the benefit of being able to return nodes in sub-node groups, if required.

    if bpy.context.active_object == None:
        return
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return
    
    layer_group_node_name = format_layer_group_node_name(active_material.name, layer_index)

    match layer_node_name:
        case 'LAYER':
            if get_changed:
                return active_material.node_tree.nodes.get(str(layer_index) + "~")
            else:
                return active_material.node_tree.nodes.get(str(layer_index))
            
        case 'GLOBAL':
            global_channel_toggle_node_name = "GLOBAL_{0}_TOGGLE".format(material_channel_name)
            return active_material.node_tree.nodes.get(global_channel_toggle_node_name)
        
        case 'PROJECTION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("PROJECTION")
            return None
        
        case 'TRIPLANAR_BLEND':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("TRIPLANAR_BLEND_{0}".format(material_channel_name))
            return None

        case 'MIX_IMAGE_ALPHA':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("MIX_{0}_IMAGE_ALPHA".format(material_channel_name))
            return None  

        case 'BLUR':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("BLUR")
            return None

        case 'MIX':
            mix_node_name = "{0}_MIX".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(mix_node_name)
            return None
        
        case 'OPACITY':
            opacity_node_name = "{0}_OPACITY".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(opacity_node_name)
            return None
        
        case 'VALUE':
            value_node_name = "{0}_VALUE_{1}".format(material_channel_name, node_number)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(value_node_name)
            return None
        
        case 'FILTER':
            filter_node_name = "{0}_FILTER".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(filter_node_name)
            return None
        
        case 'OUTPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('Group Output')
            return None
        
        case 'INPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('Group Input')
            return None
        
        case 'COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                decal_projection_node = node_tree.nodes.get('PROJECTION')
                if decal_projection_node:
                    return decal_projection_node.node_tree.nodes.get('COORDINATES')
            return None

        case 'DECAL_COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('DECAL_COORDINATES')
            return None

        case 'SEPARATE':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("SEPARATE_{0}".format(material_channel_name))
            return None

        case _:
            debug_logging.log("Invalid material node name passed to get_material_layer_node.")
            return None

def add_material_layer_slot():
    '''Adds a new slot to the material layer stack, and returns the index of the new layer slot.'''
    layers = bpy.context.scene.matlayer_layers
    layer_stack = bpy.context.scene.matlayer_layer_stack

    layer_slot = layers.add()

    # Assign a random, unique number to the layer slot. This allows the layer slot array index to be found using the name of the layer slot as a key.
    unique_random_slot_id = str(random.randrange(0, 999999))
    while layers.find(unique_random_slot_id) != -1:
        unique_random_slot_id = str(random.randrange(0, 999999))
    layer_slot.name = unique_random_slot_id

    # If there is no layer selected, move the layer to the top of the stack.
    if bpy.context.scene.matlayer_layer_stack.selected_layer_index < 0:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = len(layers) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(layers) - 1
        move_to_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))

    return bpy.context.scene.matlayer_layer_stack.selected_layer_index

def add_material_layer(layer_type, self):
    '''Adds a material layer to the active materials layer stack.'''

    refresh_layer_stack("Added material layer.")

    blender_addon_utils.append_default_node_groups()        # Append all required node groups first to avoid node group duplication from re-appending.

    if blender_addon_utils.verify_material_operation_context(self, check_active_material=False) == False:
        return

    active_object = bpy.context.active_object
    # If there are no material slots, or no material in the active material slot, make a new MatLayer material by appending the default material setup.
    if len(active_object.material_slots) == 0:
        new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")
        new_material.name = active_object.name
        active_object.data.materials.append(new_material)
        active_object.active_material_index = 0

    elif active_object.material_slots[active_object.active_material_index].material == None:
        new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")

        # Get a unique name for the new material.
        material_variation_id = 0
        new_material_name = active_object.name
        material = bpy.data.materials.get(new_material_name)
        while material:
            material_variation_id += 1
            new_material_name = active_object.name + str(material_variation_id)
            material = bpy.data.materials.get(new_material_name)

        new_material.name = new_material_name
        active_object.material_slots[active_object.active_material_index].material = new_material

    new_layer_slot_index = add_material_layer_slot()

    # Add a material layer group node based on the specified layer type.
    active_material = bpy.context.active_object.active_material
    match layer_type:
        case 'DEFAULT':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DefaultLayer", return_unique=True, never_auto_delete=True)
            debug_logging.log("Added material layer.")

        case 'PAINT':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DefaultLayer", return_unique=True, never_auto_delete=True)
            debug_logging.log("Added paint layer.")

        case 'DECAL':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DecalLayer", return_unique=True, never_auto_delete=True)
            debug_logging.log("Added decal layer.")

    default_layer_node_group.name = format_layer_group_node_name(active_material.name, str(new_layer_slot_index))
    new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
    new_layer_group_node.node_tree = default_layer_node_group
    new_layer_group_node.name = str(new_layer_slot_index) + "~"
    new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
    
    reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()

    # For specific layer types, perform additional setup steps.
    match layer_type:
        case 'PAINT':
            replace_material_channel_node('COLOR', 'TEXTURE')
            new_image = blender_addon_utils.create_image("Paint", base_color=(0.0, 0.0, 0.0, 0.0), alpha_channel=True, add_unique_id=True)
            texture_node = get_material_layer_node('VALUE', new_layer_slot_index, 'COLOR')
            if texture_node:
                texture_node.image = new_image
            blender_addon_utils.set_texture_paint_image(new_image)
            blender_addon_utils.save_image(new_image)

            for material_channel_name in MATERIAL_CHANNEL_LIST:
                if material_channel_name != 'COLOR':
                    mix_layer_node = get_material_layer_node('MIX', new_layer_slot_index, material_channel_name)
                    if mix_layer_node:
                        mix_layer_node.mute = True

            # Use image alpha blending by default.
            toggle_image_alpha_blending('COLOR')

        case 'DECAL':

            # Create a new empty to use as a decal object.
            unique_decal_name = blender_addon_utils.get_unique_object_name("Decal", start_id_number=1)
            decal_object = bpy.data.objects.new(unique_decal_name, None)
            decal_object.empty_display_type = 'CUBE'
            decal_object.scale[2] = 0.1
            blender_addon_utils.add_object_to_collection("Decals", decal_object, color_tag='COLOR_03', unlink_from_other_collections=True)

            # Add the new decal object to the decal coordinate node.
            decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', new_layer_slot_index)
            if decal_coordinate_node:
                decal_coordinate_node.object = decal_object

            # Add a default decal to the color material channel.
            default_decal_image = blender_addon_utils.append_image('DefaultDecal')
            replace_material_channel_node('COLOR', 'TEXTURE')
            texture_node = get_material_layer_node('VALUE', new_layer_slot_index, 'COLOR')
            if texture_node:
                if texture_node.bl_static_type == 'TEX_IMAGE':
                    texture_node.image = default_decal_image
                    blender_addon_utils.set_texture_paint_image(default_decal_image)
                    blender_addon_utils.save_image(default_decal_image)

            # Use image alpha blending by default for this layer.
            toggle_image_alpha_blending('COLOR')
            
            blender_addon_utils.set_snapping('DECAL', snap_on=True)

def duplicate_layer(original_layer_index, self):
    '''Duplicates the material layer at the provided layer index.'''

    refresh_layer_stack("Duplicated material layer.")

    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    # Duplicate the node tree and add it to the layer stack.
    layer_node_tree = get_layer_node_tree(original_layer_index)
    if layer_node_tree:
        duplicated_node_tree = blender_addon_utils.duplicate_node_group(layer_node_tree.name)
        if duplicated_node_tree:
            active_material = bpy.context.active_object.active_material

            new_layer_slot_index = add_material_layer_slot()

            duplicated_node_tree.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
            new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_layer_group_node.node_tree = duplicated_node_tree
            new_layer_group_node.name = str(new_layer_slot_index) + "~"
            new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
            
            reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
            organize_layer_group_nodes()
            link_layer_group_nodes(self)
            layer_masks.organize_mask_nodes()

        # Clear the mask stack from the new layer.
        masks = bpy.context.scene.matlayer_masks
        masks.clear()

        # Duplicate mask node trees and add them as group nodes to the active material.
        mask_count = layer_masks.count_masks(original_layer_index)
        for i in range(0, mask_count):
            original_mask_node = layer_masks.get_mask_node('MASK', original_layer_index, i)
            if original_mask_node:
                duplicated_node_tree = blender_addon_utils.duplicate_node_group(original_mask_node.node_tree.name)
                if duplicated_node_tree:
                    new_mask_slot_index = layer_masks.add_mask_slot()
                    duplicated_mask_name = layer_masks.format_mask_name(bpy.context.active_object.active_material.name, new_layer_slot_index, new_mask_slot_index) + "~"
                    duplicated_node_tree.name = duplicated_mask_name
                    new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                    new_mask_group_node.node_tree = duplicated_node_tree
                    new_mask_group_node.name = duplicated_mask_name
                    new_mask_group_node.label = original_mask_node.label

                    layer_masks.reindex_masks('ADDED_MASK', new_layer_slot_index, affected_mask_index=i)

        layer_masks.link_mask_nodes(new_layer_slot_index)
        layer_masks.organize_mask_nodes()

        debug_logging.log("Duplicated material layer.")

def delete_layer(self):
    '''Deletes the selected layer'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return {'FINISHED'}

    refresh_layer_stack("Deleted material layer.")

    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    active_material = bpy.context.active_object.active_material

    # For decal layers, delete the accociated empty object if one exists.
    decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', selected_layer_index)
    if decal_coordinate_node:
        decal_object = decal_coordinate_node.object
        if decal_object:
            bpy.data.objects.remove(decal_object)

    # Remove all mask group nodes and node trees associated with the layer.
    mask_count = layer_masks.count_masks(selected_layer_index)
    for i in range(0, mask_count):
        mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
        if mask_node.bl_static_type == 'GROUP' and mask_node.node_tree:
            bpy.data.node_groups.remove(mask_node.node_tree)
        active_material.node_tree.nodes.remove(mask_node)

    # Remove the layer group node (node tree) from Blender's data.
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    if layer_node_tree:
        bpy.data.node_groups.remove(layer_node_tree)

    # Remove the layer node from the active materials node tree.
    layer_group_node = get_material_layer_node('LAYER', selected_layer_index)
    if layer_group_node:
        active_material.node_tree.nodes.remove(layer_group_node)

    reindex_layer_nodes(change_made='DELETED_LAYER', affected_layer_index=selected_layer_index)
    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()

    # Remove the layer slot and reset the selected layer index.
    layers.remove(selected_layer_index)
    bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

    debug_logging.log("Deleted material layer.")

def move_layer(direction, self):
    '''Moves the selected layer up or down on the material layer stack.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return
    
    refresh_layer_stack("Moved material layer.")

    match direction:
        case 'UP':
            # Swap the layer index for all layer nodes in this layer with the layer above it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if selected_layer_index < len(layers) - 1:
                layer_node = get_material_layer_node('LAYER', selected_layer_index)
                if layer_node:
                    layer_node.name += "~"
                    if layer_node.node_tree:
                        layer_node.node_tree.name += "~"

                above_layer_node = get_material_layer_node('LAYER', selected_layer_index + 1)
                if above_layer_node:
                    above_layer_node.name = str(selected_layer_index)
                    if above_layer_node.node_tree:
                        above_layer_node.node_tree.name = above_layer_node.node_tree.name.split('_')[0] + "_" + str(selected_layer_index)

                layer_node.name = str(selected_layer_index + 1)
                layer_node.node_tree.name = layer_node.node_tree.name.split('_')[0] + "_" + str(selected_layer_index + 1)

                bpy.context.scene.matlayer_layer_stack.selected_layer_index = selected_layer_index + 1

                # Swap the layer index for all mask nodes in this layer with the layer above it.
                selected_layer_mask_count = layer_masks.count_masks(selected_layer_index)
                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name += "~"
                    mask_node.node_tree.name = mask_node.name

                above_layer_mask_count = layer_masks.count_masks(selected_layer_index + 1)
                for i in range(0, above_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name = layer_masks.format_mask_name(selected_layer_index, i)
                    mask_node.node_tree.name = mask_node.name

                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                    mask_node.name = layer_masks.format_mask_name(selected_layer_index + 1, i)
                    mask_node.node_tree.name = mask_node.name

            else:
                debug_logging.log("Can't move layer up, no layers exist above the selected layer.")

        case 'DOWN':
            # Swap the layer index for all nodes in this layer with the layer below it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if selected_layer_index - 1 >= 0:
                layer_node = get_material_layer_node('LAYER', selected_layer_index)
                layer_node.name += "~"
                layer_node.node_tree.name += "~"

                below_layer_node = get_material_layer_node('LAYER', selected_layer_index - 1)
                below_layer_node.name = str(selected_layer_index)
                below_layer_node.node_tree.name = below_layer_node.node_tree.name.split('_')[0] + "_" + str(selected_layer_index)

                layer_node.name = str(selected_layer_index - 1)
                layer_node.node_tree.name = layer_node.node_tree.name.split('_')[0] + "_" + str(selected_layer_index - 1)

                bpy.context.scene.matlayer_layer_stack.selected_layer_index = selected_layer_index - 1

                # Swap the layer index for all mask nodes in this layer with the layer below it.
                selected_layer_mask_count = layer_masks.count_masks(selected_layer_index)
                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name += "~"
                    mask_node.node_tree.name = mask_node.name

                below_layer_mask_count = layer_masks.count_masks(selected_layer_index - 1)
                for i in range(0, below_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name = layer_masks.format_mask_name(selected_layer_index, i)
                    mask_node.node_tree.name = mask_node.name

                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                    mask_node.name = layer_masks.format_mask_name(selected_layer_index - 1, i)
                    mask_node.node_tree.name = mask_node.name

            else:
                debug_logging.log("Can't move layer down, no layers exist below the selected layer.")

        case _:
            debug_logging.log_status("Invalid direction provided for moving a material layer.", self, 'ERROR')
            return

    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()
    layer_masks.refresh_mask_slots()

    debug_logging.log("Moved material layer.")

def count_layers(material=None):
    '''Counts the total layers in the specified material (active material if no material is specified) by reading the active material's node tree.'''
    # Count the number of layers in the specified material.
    if material != None:
        layer_count = 0
        while material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        return layer_count
    
    # Count the active material, since no material was specified to have it's layers counted.
    else:
        active_object_attribute = getattr(bpy.context, "active_object", None)
        if active_object_attribute == None:
            return 0
        if not bpy.context.active_object:
            return 0
        if not bpy.context.active_object.active_material:
            return 0
        
        active_material = bpy.context.active_object.active_material
        layer_count = 0
        while active_material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        return layer_count

def organize_layer_group_nodes():
    '''Organizes all layer group nodes in the active material to ensure the node tree is easy to read.'''
    active_material = bpy.context.active_object.active_material
    layer_count = count_layers()

    position_x = -500
    for i in range(layer_count, 0, -1):
        layer_group_node = active_material.node_tree.nodes.get(str(i - 1))
        if layer_group_node:
            layer_group_node.width = 300
            layer_group_node.location = (position_x, 0)
            position_x -= 500
    debug_logging.log("Organized layer group nodes.")

def link_layer_group_nodes(self):
    '''Connects all layer group nodes to other existing group nodes, and the principled BSDF shader.'''
    # Note: This function may be able to be optimized by only diconnecting nodes that must be disconnected, potentially reducing re-compile time for shaders.

    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings
    active_material = bpy.context.active_object.active_material
    node_tree = active_material.node_tree

    # Don't attempt to link layer group nodes if there are no layers.
    layer_count = count_layers()
    if layer_count <= 0:
        return

    # Disconnect all layer group nodes (Don't disconnect masks).
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if layer_node:
            for input in layer_node.inputs:
                if input.name != 'LayerMask':
                    for link in input.links:
                        node_tree.links.remove(link)
            for output in layer_node.outputs:
                for link in output.links:
                    node_tree.links.remove(link)

    # Re-connect all (non-muted / active) layer group nodes.
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if blender_addon_utils.get_node_active(layer_node):
            next_layer_index = i + 1
            next_layer_node = get_material_layer_node('LAYER', next_layer_index)
            if next_layer_node:
                while not blender_addon_utils.get_node_active(next_layer_node) and next_layer_index <= layer_count - 1:
                    next_layer_index += 1
                    next_layer_node = get_material_layer_node('LAYER', next_layer_index)

            if next_layer_node:
                if blender_addon_utils.get_node_active(next_layer_node):
                    for material_channel_name in MATERIAL_CHANNEL_LIST:

                        # Only connect active material channels.
                        if not tss.get_material_channel_active(material_channel_name):
                            continue

                        output_socket_name = material_channel_name.capitalize()
                        input_socket_name = "{0}Mix".format(material_channel_name.capitalize())
                        node_tree.links.new(layer_node.outputs.get(output_socket_name), next_layer_node.inputs.get(input_socket_name))


    # Connect the last (non-muted / active) layer node to the principled BSDF.
    normal_and_height_mix = active_material.node_tree.nodes.get('NORMAL_HEIGHT_MIX')
    principled_bsdf = active_material.node_tree.nodes.get('MATLAYER_BSDF')

    last_layer_node_index = layer_count - 1
    last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
    if last_layer_node:
        while not blender_addon_utils.get_node_active(last_layer_node) and last_layer_node_index >= 0:
            last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
            last_layer_node_index -= 1

    if last_layer_node:
        if blender_addon_utils.get_node_active(last_layer_node):
            for material_channel_name in MATERIAL_CHANNEL_LIST:

                # Only connect active material channels.
                if not tss.get_material_channel_active(material_channel_name):
                    continue

                match material_channel_name:
                    case 'COLOR':
                        node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), principled_bsdf.inputs.get('Base Color'))

                    case 'NORMAL':
                        node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), normal_and_height_mix.inputs.get(material_channel_name.capitalize()))
                
                    case 'HEIGHT':
                        node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), normal_and_height_mix.inputs.get(material_channel_name.capitalize()))

                    case _:
                        node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), principled_bsdf.inputs.get(material_channel_name.capitalize()))

    debug_logging.log("Linked layer group nodes.")

def reindex_layer_nodes(change_made, affected_layer_index):
    '''Reindexes layer group nodes to keep them properly indexed. This should be called after a change is made that effects the layer stack order such as adding, duplicating, deleting, or moving a material layer on the layer stack.'''
    match change_made:
        case 'ADDED_LAYER':
            # Increase the layer index for all layer group nodes and their node trees that exist above the affected layer.
            total_layers = count_layers()
            for i in range(total_layers, affected_layer_index, -1):
                layer_node = get_material_layer_node('LAYER', i - 1)
                if layer_node:
                    layer_node.name = str(int(layer_node.name) + 1)
                    split_node_tree_name = layer_node.node_tree.name.split('_')
                    layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(int(split_node_tree_name[1]) + 1))

            new_layer_node = get_material_layer_node('LAYER', affected_layer_index, get_changed=True)
            if new_layer_node:
                new_layer_node.name = str(affected_layer_index)
                split_node_tree_name = new_layer_node.node_tree.name.split('_')
                new_layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(affected_layer_index))

        case 'DELETED_LAYER':
            # Reduce the layer index for all layer group nodes and their nodes trees that exist above the affected layer.
            layer_count = len(bpy.context.scene.matlayer_layers)
            for i in range(layer_count, affected_layer_index + 1, -1):
                layer_node = get_material_layer_node('LAYER', i - 1)
                layer_node.name = str(int(layer_node.name) - 1)
                split_node_tree_name = layer_node.node_tree.name.split('_')
                layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(int(split_node_tree_name[1]) - 1))

    debug_logging.log("Re-indexed material layers.")

def apply_mesh_maps():
    '''Searches for all mesh map texture nodes in the node tree and applies mesh maps if they exist.'''
    # Apply baked mesh maps to all group nodes used as masks for all material layers.
    layers = bpy.context.scene.matlayer_layers
    for layer_index in range(0, len(layers)):
        mask_count = layer_masks.count_masks(layer_index)
        for mask_index in range(0, mask_count):
            for mesh_map_type in mesh_map_baking.MESH_MAP_TYPES:
                mask_node = layer_masks.get_mask_node('MASK', layer_index, mask_index)
                mesh_map_node = mask_node.node_tree.get(mesh_map_type)
                if mesh_map_node:
                    if mesh_map_node.bl_static_type == 'TEX_IMAGE':
                        mesh_map_node.image = mesh_map_baking.get_meshmap_image(bpy.context.active_object.name, mesh_map_type)
    debug_logging.log("Applied baked mesh maps.")

def relink_layer_projection(relink_material_channel_name="", delink_layer_projection_nodes=True):
    '''Relinks the projection / blurring nodes and then links them to material channels based on the current projection node tree being used. If no material channel is specified to have it's projection relinked, relink them all.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    blur_node = get_material_layer_node('BLUR', selected_layer_index)

    # Disconnect the projection and blur nodes.
    if delink_layer_projection_nodes:
        blender_addon_utils.unlink_node(projection_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)
        blender_addon_utils.unlink_node(blur_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)

    # Relink the projection node and blur node.
    match projection_node.node_tree.name:
        case 'ML_UVProjection':
            layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

        case "ML_TriplanarProjection":
            layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])
            layer_node_tree.links.new(projection_node.outputs[1], blur_node.inputs[1])
            layer_node_tree.links.new(projection_node.outputs[2], blur_node.inputs[2])

        case 'ML_DecalProjection':
            layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])
            layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

    # Relink projection for all material channels if no channel is specified.
    for material_channel_name in MATERIAL_CHANNEL_LIST:
        if relink_material_channel_name == "" or relink_material_channel_name == material_channel_name:
            match projection_node.node_tree.name:
                case 'ML_UVProjection':
                    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
                    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        if blender_addon_utils.get_node_active(blur_node):
                            layer_node_tree.links.new(blur_node.outputs.get(material_channel_name.capitalize()), value_node.inputs[0])
                        else:
                            layer_node_tree.links.new(projection_node.outputs[0], value_node.inputs[0])
                            layer_node_tree.links.new(value_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

                case 'ML_TriplanarProjection':
                    for i in range(0, 3):
                        # Link projection / blur nodes to the image textures.
                        value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=i + 1)
                        triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)

                        if value_node.bl_static_type == 'TEX_IMAGE':
                            if blender_addon_utils.get_node_active(blur_node):
                                layer_node_tree.links.new(blur_node.outputs.get(material_channel_name.capitalize() + str(i + 1)), value_node.inputs[0])
                            else:
                                layer_node_tree.links.new(projection_node.outputs[i], value_node.inputs[0])
                            
                            layer_node_tree.links.new(value_node.outputs.get('Color'), triplanar_blend_node.inputs[i])
                            layer_node_tree.links.new(value_node.outputs.get('Alpha'), triplanar_blend_node.inputs[i + 3])

                        # Link triplanar blending nodes.
                        if triplanar_blend_node:
                            layer_node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))
                            if material_channel_name == 'NORMAL':
                                layer_node_tree.links.new(projection_node.outputs.get('Rotation'), triplanar_blend_node.inputs.get('Rotation'))

                        # No need to link projection for layers not using image textures.
                        else:
                            break

                case 'ML_DecalProjection':
                    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
                    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        if blender_addon_utils.get_node_active(blur_node):
                            layer_node_tree.links.new(blur_node.outputs.get(material_channel_name.capitalize()), value_node.inputs[0])
                        else:
                            layer_node_tree.links.new(projection_node.outputs[0], value_node.inputs[0])
                            layer_node_tree.links.new(value_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

def set_layer_projection_nodes(projection_method):
    '''Changes the layer projection nodes to use the specified layer projection method.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    BLUR_node = get_material_layer_node('BLUR', selected_layer_index)
    
    match projection_method:
        case 'UV':
            projection_node.node_tree = blender_addon_utils.append_group_node("ML_UVProjection")
            BLUR_node.node_tree = blender_addon_utils.append_group_node("ML_LayerBlur")

            if blender_addon_utils.get_node_active(BLUR_node):
                layer_node_tree.links.new(projection_node.outputs[0], BLUR_node.inputs[0])

        case 'TRIPLANAR':
            projection_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarProjection")
            BLUR_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarLayerBlur")

            if blender_addon_utils.get_node_active(BLUR_node):
                layer_node_tree.links.new(projection_node.outputs.get('X'), BLUR_node.inputs.get('X'))
                layer_node_tree.links.new(projection_node.outputs.get('Y'), BLUR_node.inputs.get('Y'))
                layer_node_tree.links.new(projection_node.outputs.get('Z'), BLUR_node.inputs.get('Z'))

def delete_triplanar_blending_nodes(material_channel_name):
    '''Deletes nodes used for triplanar texture sampling and blending for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)

    for i in range(0, 3):
        texture_sample_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, i + 1)
        if texture_sample_node:
            layer_node_tree.nodes.remove(texture_sample_node)

    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)
    if triplanar_blend_node:
        layer_node_tree.nodes.remove(triplanar_blend_node)

def apply_material_channel_projection(material_channel_name, projection_method, set_texture_node=False):
    '''Adjusts material nodes for the specified material channel to use the specified projection method.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, 1)
    mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
    
    original_value_node_type = value_node.bl_static_type
    original_node_location = value_node.location
    
    # Texture nodes are the only nodes that require a specific projection node setup, ignore other node types.
    # If set_texture_node is true, the material channel value node will be replaces with a texture node, regardless of it's original node type.
    if value_node.bl_static_type == 'TEX_IMAGE' or set_texture_node:
        match projection_method:
            case 'UV':
                # Remember original location and image of the texture node.
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image

                # Delete triplanar texture nodes if they exist.
                delete_triplanar_blending_nodes(material_channel_name)

                # Replace with a single texture node.
                texture_sample_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                texture_sample_node.name = "{0}_VALUE_{1}".format(material_channel_name, 1)
                texture_sample_node.label = texture_sample_node.name
                texture_sample_node.hide = True
                texture_sample_node.width = 300
                texture_sample_node.location = original_node_location

                if original_value_node_type == 'TEX_IMAGE':
                    texture_sample_node.image = original_image

                # Link the texture to projection / blur and mix layer nodes.
                relink_layer_projection(material_channel_name, delink_layer_projection_nodes=False)
                mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                opacity_node = get_material_layer_node('OPACITY', selected_layer_index, material_channel_name)
                layer_node_tree.links.new(texture_sample_node.outputs[0], mix_node.inputs[7])
                layer_node_tree.links.new(mix_image_alpha_node.outputs[0], opacity_node.inputs[3])
                layer_node_tree.links.new(texture_sample_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

            case 'DECAL':
                # Remember original location and image of the texture node.
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image

                # Delete triplanar texture nodes if they exist.
                delete_triplanar_blending_nodes(material_channel_name)

                # Replace with a single texture node.
                texture_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                texture_node.name = "{0}_VALUE_{1}".format(material_channel_name, 1)
                texture_node.label = texture_node.name
                texture_node.hide = True
                texture_node.width = 300
                texture_node.location = original_node_location
                texture_node.extension = 'CLIP'
                if original_value_node_type == 'TEX_IMAGE':
                    texture_node.image = original_image

                # Link the texture to projection / blur and mix layer nodes.
                relink_layer_projection(material_channel_name, delink_layer_projection_nodes=False)
                mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                opacity_node = get_material_layer_node('OPACITY', selected_layer_index, material_channel_name)
                layer_node_tree.links.new(texture_node.outputs[0], mix_node.inputs[7])
                layer_node_tree.links.new(mix_image_alpha_node.outputs[0], opacity_node.inputs[3])
                layer_node_tree.links.new(texture_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

            case 'TRIPLANAR':
                # Remember the old image and location.
                original_value_node_type = value_node.bl_static_type
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image

                # Remove the old value node.
                layer_node_tree.nodes.remove(value_node)

                # Add 3 required texture samples for triplanar projection.
                texture_sample_nodes = []
                location_x = original_node_location[0]
                location_y = original_node_location[1]
                for i in range(0, 3):
                    texture_sample_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                    texture_sample_node.name = "{0}_VALUE_{1}".format(material_channel_name, i + 1)
                    texture_sample_node.label = texture_sample_node.name
                    texture_sample_node.hide = True
                    texture_sample_node.width = 300
                    texture_sample_node.location = (location_x, location_y)
                    texture_sample_nodes.append(texture_sample_node)
                    location_y -= 50
                    if original_value_node_type == 'TEX_IMAGE':
                        texture_sample_node.image = original_image

                # Add a node for blending texture samples.
                triplanar_blend_node = layer_node_tree.nodes.new('ShaderNodeGroup')
                if material_channel_name == 'NORMAL':
                    triplanar_blend_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarNormalsBlend")
                else:
                    triplanar_blend_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarBlend")
                triplanar_blend_node.name = "TRIPLANAR_BLEND_{0}".format(material_channel_name)
                triplanar_blend_node.label = triplanar_blend_node.name
                triplanar_blend_node.width = 300
                triplanar_blend_node.hide = True
                triplanar_blend_node.location = (location_x, location_y)

                # Connect texture sample and blending nodes for material channels.
                relink_layer_projection(material_channel_name, delink_layer_projection_nodes=False)

                mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
                mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                opacity_node = get_material_layer_node('OPACITY', selected_layer_index, material_channel_name)
                layer_node_tree.links.new(triplanar_blend_node.outputs.get('Color'), mix_node.inputs[7])
                layer_node_tree.links.new(triplanar_blend_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])
                layer_node_tree.links.new(mix_image_alpha_node.outputs[0], opacity_node.inputs[3])

def replace_material_channel_node(material_channel_name, node_type):
    '''Replaces the existing material channel node with a new node of the given type. Valid node types include: 'GROUP', 'TEXTURE'.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_group_node = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)

    match node_type:
        case 'GROUP':
            original_node_location = value_node.location

            match projection_node.node_tree.name:
                case 'ML_TriplanarProjection':
                    delete_triplanar_blending_nodes(material_channel_name)
                case _:
                    layer_group_node.nodes.remove(value_node)

            new_node = layer_group_node.nodes.new('ShaderNodeGroup')
            new_node.name = "{0}_VALUE_1".format(material_channel_name)
            new_node.label = new_node.name
            new_node.location = original_node_location
            new_node.width = 300

            default_node_tree = bpy.data.node_groups.get("ML_Default{0}".format(material_channel_name.capitalize()))
            new_node.node_tree = default_node_tree

            # Link the new group node.
            mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
            layer_group_node.links.new(new_node.outputs[0], mix_node.inputs[7])

        case 'TEXTURE':
            # Apply projection to texture nodes based on the projection node tree name.
            match projection_node.node_tree.name:
                case 'ML_UVProjection':
                    apply_material_channel_projection(material_channel_name, 'UV', set_texture_node=True)

                case 'ML_TriplanarProjection':
                    apply_material_channel_projection(material_channel_name, 'TRIPLANAR', set_texture_node=True)

                case 'ML_DecalProjection':
                    apply_material_channel_projection(material_channel_name, 'DECAL', set_texture_node=True)

def set_layer_projection(projection_mode, self):
    '''Changes projection nodes for the layer to use the specified projection mode. Valid options include: 'UV', 'TRIPLANAR'.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if not projection_node:
        debug_logging.log_status("Error, missing layer projection node. The material node format is corrupt, or the active material is not made with this add-on.")
        return

    match projection_mode:
        case 'UV':
            if projection_node.node_tree.name != "ML_UVProjection":
                set_layer_projection_nodes('UV')

                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    apply_material_channel_projection(material_channel_name, 'UV')

                debug_logging.log("Changed layer projection to 'UV'.")

        case 'TRIPLANAR':
            if projection_node.node_tree.name != "ML_TriplanarProjection":
                set_layer_projection_nodes('TRIPLANAR')

                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    apply_material_channel_projection(material_channel_name, 'TRIPLANAR')

                debug_logging.log("Changed layer projection to 'TRIPLANAR'.")

def refresh_layer_stack(reason=""):
    '''Clears, and then reads the active material, to sync the number of layers in the user interface with the number of layers that exist within the material node tree.'''
    layers = bpy.context.scene.matlayer_layers

    layers.clear()

    layer_count = count_layers()
    for layer in range(0, layer_count):
        add_material_layer_slot()

    # Reset the layer index if it's out of range.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    if selected_layer_index > len(layers) - 1 or selected_layer_index < 0:
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0

    if reason != "":
        debug_logging.log("Refreshed layer stack due to: " + reason)

def isolate_material_channel(material_channel_name):
    '''Isolates the specified material channel by linking only the specified material channel output to the material channel output / emission node.'''
    active_node_tree = bpy.context.active_object.active_material.node_tree
    last_layer_index = count_layers(bpy.context.active_object.active_material) - 1

    layer_node = get_material_layer_node('LAYER', last_layer_index)
    emission_node = active_node_tree.nodes.get('EMISSION')
    material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')

    # Unlink the emission node.
    blender_addon_utils.unlink_node(emission_node, active_node_tree, unlink_inputs=True, unlink_outputs=True)

    # Connect the selected material channel.
    active_node_tree.links.new(layer_node.outputs.get(material_channel_name.capitalize()), emission_node.inputs[0])
    active_node_tree.links.new(emission_node.outputs[0], material_output.inputs[0])

def show_layer():
    '''Removes material channel or mask isolation if they are applied.'''
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if not active_object_attribute:
        return
    
    if bpy.context.active_object:
        if bpy.context.active_object.active_material:
            active_node_tree = bpy.context.active_object.active_material.node_tree
            emission_node = active_node_tree.nodes.get('EMISSION')
            if len(emission_node.outputs[0].links) != 0:
                blender_addon_utils.unlink_node(emission_node, active_node_tree, unlink_inputs=True, unlink_outputs=True)
                material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')
                principled_bsdf = active_node_tree.nodes.get('MATLAYER_BSDF')
                active_node_tree.links.new(principled_bsdf.outputs[0], material_output.inputs[0])

def toggle_image_alpha_blending(material_channel_name):
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
    if image_alpha_node.mute:
        image_alpha_node.mute = False
    else:
        image_alpha_node.mute = True

def get_material_channel_output_channel(material_channel_name):
    '''Returns the output channel for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    filter_node = get_material_layer_node('FILTER', selected_layer_index, material_channel_name)

    color_input_node = None
    if blender_addon_utils.get_node_active(filter_node):
        color_input_node = filter_node
    else:
        color_input_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
    if len(color_input_node.inputs[0].links) > 0:
        return color_input_node.inputs[7].links[0].from_socket.name
    
    return None

def set_material_channel_output_channel(material_channel_name, output_channel_name):
    '''Sets the output channel for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    separate_color_node = get_material_layer_node('SEPARATE', selected_layer_index, material_channel_name)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    filter_node = get_material_layer_node('FILTER', selected_layer_index, material_channel_name)

    color_output_node = None
    match projection_node.node_tree.name:
        case 'ML_TriplanarProjection':
            color_output_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)
        case _:
            color_output_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)

    color_input_node = None
    if blender_addon_utils.get_node_active(color_input_node):
        color_input_node = filter_node
    else:
        color_input_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)

    # Disconnect nodes.
    blender_addon_utils.unlink_node(color_output_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)
    blender_addon_utils.unlink_node(separate_color_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)

    match output_channel_name:
        case 'COLOR':
            layer_node_tree.links.new(color_output_node.outputs[0], color_input_node.inputs[7])

        case 'ALPHA':
            layer_node_tree.links.new(color_output_node.outputs[1], color_input_node.inputs[7])

        case 'RED':
            layer_node_tree.links.new(color_output_node.outputs[0], separate_color_node.inputs[0])
            layer_node_tree.links.new(separate_color_node.outputs[0], color_input_node.inputs[7])

        case 'GREEN':
            layer_node_tree.links.new(color_output_node.outputs[0], separate_color_node.inputs[0])
            layer_node_tree.links.new(separate_color_node.outputs[1], color_input_node.inputs[7])

        case 'BLUE':
            layer_node_tree.links.new(color_output_node.outputs[0], separate_color_node.inputs[0])
            layer_node_tree.links.new(separate_color_node.outputs[2], color_input_node.inputs[7])


#----------------------------- OPERATORS -----------------------------#


class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer", update=update_layer_index)
    selected_material_channel: EnumProperty(items=MATERIAL_CHANNEL, name="Material Channel", description="The currently selected material channel", default='COLOR')

class MATLAYER_layers(PropertyGroup):
    # Storing properties in the layer slot data can potentially cause many errors and often more code -
    # - Properties stored in the layer slots must be read from the material node tree when a new active material is selected.
    # - Properties stored in the layer slots must be updated first in the interface, then trigger callback functions to update their associated properties in material nodes.
    # To help avoid the errors above, all properties are stored in the material node tree of created materials (in one way or another) and referenced directly when displayed in the user interface.
    # A placeholder property is kept here so the UI still has a property group to reference to draw the UIList.
    placeholder_property: IntProperty()

class MATLAYER_OT_add_material_layer(Operator):
    bl_idname = "matlayer.add_material_layer"
    bl_label = "Add Material Layer"
    bl_description = "Adds a material layer to the active material (if the material is created with this add-on)"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('DEFAULT', self)
        return {'FINISHED'}

class MATLAYER_OT_add_paint_material_layer(Operator):
    bl_idname = "matlayer.add_paint_material_layer"
    bl_label = "Add Paint Material Layer"
    bl_description = "Creates a material layer and an image texture that's placed in the materials color channel"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('PAINT', self)
        return {'FINISHED'}

class MATLAYER_OT_add_decal_material_layer(Operator):
    bl_idname = "matlayer.add_decal_material_layer"
    bl_label = "Add Decal Material Layer"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('DECAL', self)
        return {'FINISHED'}

class MATLAYER_OT_duplicate_layer(Operator):
    bl_idname = "matlayer.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_description = "Duplicates the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        duplicate_layer(selected_layer_index, self)
        return {'FINISHED'}

class MATLAYER_OT_delete_layer(Operator):
    bl_idname = "matlayer.delete_layer"
    bl_label = "Delete Layer"
    bl_description = "Deletes the selected material layer from the active material"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_layer(self)
        return {'FINISHED'}

class MATLAYER_OT_move_material_layer_up(Operator):
    bl_idname = "matlayer.move_material_layer_up"
    bl_label = "Move Layer Up"
    bl_description = "Moves the material layer up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        move_layer('UP', self)
        return {'FINISHED'}

class MATLAYER_OT_move_material_layer_down(Operator):
    bl_idname = "matlayer.move_material_layer_down"
    bl_label = "Move Layer Down"
    bl_description = "Moves the material layer down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        move_layer('DOWN', self)
        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_preview(Operator):
    bl_idname = "matlayer.toggle_material_channel_preview"
    bl_label = "Toggle Material Channel Preview"
    bl_description = "Toggle on / off a preview for the selected material channel"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_toggle_layer_blur(Operator):
    bl_idname = "matlayer.toggle_layer_blur"
    bl_label = "Toggle Layer Blur"
    bl_description = "Toggle on / off blurring for the selected layer. Toggle blurring off when not in use to improve shader compilation time and viewport performance"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
        blur_node = get_material_layer_node('BLUR', selected_layer_index)
        if blur_node:
            # Connect the projection node to all material channels.
            if blender_addon_utils.get_node_active(blur_node):
                blender_addon_utils.set_node_active(blur_node, False)
            
            # Connect the blur node to all material channels.
            else:
                blender_addon_utils.set_node_active(blur_node, True)
        relink_layer_projection()
        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_blur(Operator):
    bl_idname = "matlayer.toggle_material_channel_blur"
    bl_label = "Toggle Material Channel Blur"
    bl_description = "Toggle on / off a blur filter for the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default="COLOR")

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index

        BLUR_node = get_material_layer_node('BLUR', selected_layer_index)
        blur_toggle_property_name = "{0}BlurToggle".format(self.material_channel_name.capitalize())
        if BLUR_node.inputs.get(blur_toggle_property_name).default_value == 1:
            BLUR_node.inputs.get(blur_toggle_property_name).default_value = 0
        else:
            BLUR_node.inputs.get(blur_toggle_property_name).default_value = 1

        return {'FINISHED'}

class MATLAYER_OT_toggle_hide_layer(Operator):
    bl_idname = "matlayer.toggle_hide_layer"
    bl_label = "Toggle Hide Layer"
    bl_description = "Hides / Unhides the layer by muting / unmuting the layer group node and triggering a relink of group nodes"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: IntProperty(default=-1)

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        layer_node = get_material_layer_node('LAYER', self.layer_index)

        if blender_addon_utils.get_node_active(layer_node):
            blender_addon_utils.set_node_active(layer_node, False)
        else:
            blender_addon_utils.set_node_active(layer_node, True)

        link_layer_group_nodes(self)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_projection_uv(Operator):
    bl_idname = "matlayer.set_layer_projection_uv"
    bl_label = "Set Layer Projection UV"
    bl_description = "Sets the projection mode for the layer to UV projection, which uses the UV layout of the object to project textures used on this material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_layer_projection('UV', self)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_projection_triplanar(Operator):
    bl_idname = "matlayer.set_layer_projection_triplanar"
    bl_label = "Set Layer Projection Triplanar"
    bl_description = "Sets the projection mode for the layer to triplanar projection which projects the textures onto the object from each axis. This projection method can be used to apply materials to objects without needing to manually blend seams"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_layer_projection('TRIPLANAR', self)
        return {'FINISHED'}

class MATLAYER_OT_change_material_channel_value_node(Operator):
    bl_idname = "matlayer.change_material_channel_value_node"
    bl_label = "Change Material Channel Node"
    bl_description = "Changes value node representing the provided layer material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')
    node_type: StringProperty(default='GROUP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        replace_material_channel_node(self.material_channel_name, node_type=self.node_type)
        return {'FINISHED'}

class MATLAYER_OT_toggle_triplanar_flip_correction(Operator):
    bl_idname = "matlayer.toggle_triplanar_flip_correction"
    bl_label = "Toggle Triplanar Flip Correction"
    bl_description = "Toggles extra shader math that correctly flips the axis projection. This allows textures with text or directional pixel information to be properly projected using triplanar projection. Most texture's don't require this, which is why it's off by default"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')
    node_type: StringProperty(default='GROUP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Mute / unmute nodes that correct triplanar projection axis flipping.
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
        projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
        if projection_node:
            if projection_node.node_tree.name == 'ML_TriplanarProjection':
                for i in range(0, 3):
                    correct_axis_flip_node = projection_node.node_tree.nodes.get("CORRECT_AXIS_FLIP_{0}".format(i + 1))
                    if correct_axis_flip_node:
                        if correct_axis_flip_node.mute:
                            correct_axis_flip_node.mute = False
                        else:
                            correct_axis_flip_node.mute = True
        return {'FINISHED'}

class MATLAYER_OT_isolate_material_channel(Operator):
    bl_idname = "matlayer.isolate_material_channel"
    bl_label = "Isolate Material Channel"
    bl_description = "Isolates the selected material channel. Select a material layer to de-isolate"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
        isolate_material_channel(selected_material_channel)
        return {'FINISHED'}

class MATLAYER_OT_toggle_image_alpha_blending(Operator):
    bl_idname = "matlayer.toggle_image_alpha_blending"
    bl_label = "Toggle Image Alpha Blending"
    bl_description = "Toggles blending the alpha channel of the image node into the layers opacity. Off by default for better shader compilation and viewport performance"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        toggle_image_alpha_blending(self.material_channel_name)
        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_filter(Operator):
    bl_idname = "matlayer.toggle_material_channel_filter"
    bl_label = "Toggle Material Channel Filter"
    bl_description = "Toggles the filter node for the material channel on / off"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Mark the material channel filter node on / off and relink the material nodes accordingly.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        layer_node_tree = get_layer_node_tree(selected_layer_index)
        filter_node = get_material_layer_node('FILTER', selected_layer_index, self.material_channel_name)
        mix_node = get_material_layer_node('MIX', selected_layer_index, self.material_channel_name)
        projection_node = get_material_layer_node('PROJECTION', selected_layer_index)

        if blender_addon_utils.get_node_active(filter_node) == True:
            blender_addon_utils.set_node_active(filter_node, False)
            blender_addon_utils.unlink_node(filter_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)

            if projection_node:
                match projection_node.node_tree.name:
                    case 'ML_TriplanarProjection':
                        triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, self.material_channel_name)
                        if triplanar_blend_node:
                            layer_node_tree.links.new(triplanar_blend_node.outputs[0], mix_node.inputs[7])

                    case _:
                        value_node = get_material_layer_node('VALUE', selected_layer_index, self.material_channel_name)
                        if value_node:
                            layer_node_tree.links.new(value_node.outputs[0], mix_node.inputs[7])

            

        else:
            blender_addon_utils.set_node_active(filter_node, True)

            if projection_node:
                match projection_node.node_tree.name:
                    case 'ML_TriplanarProjection':
                        triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, self.material_channel_name)
                        if triplanar_blend_node:
                            layer_node_tree.links.new(triplanar_blend_node.outputs[0], filter_node.inputs[0])

                    case _:
                        value_node = get_material_layer_node('VALUE', selected_layer_index, self.material_channel_name)
                        if value_node:
                            layer_node_tree.links.new(value_node.outputs[0], filter_node.inputs[0])

            layer_node_tree.links.new(filter_node.outputs[0], mix_node.inputs[7])

        return {'FINISHED'}

class MATLAYER_OT_set_material_channel_output_channel(Operator):
    bl_idname = "matlayer.set_material_channel_output_channel"
    bl_label = "Set Material Channel Output Channel"
    bl_description = "Sets the material channel to use the specified output channel"
    bl_options = {'REGISTER', 'UNDO'}

    output_channel_name: StringProperty(default='COLOR')
    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_material_channel_output_channel(self.material_channel_name, self.output_channel_name)
        return {'FINISHED'}