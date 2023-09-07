# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty
from ..core import layer_masks
from ..core import baking
from ..core import blender_addon_utils
from ..core import debug_logging
import random

# List of node types that can be used in the texture slot.

PROJECTION_MODES = [
    ("UV", "UV / Flat", "Projects the texture using the model's UV map."),
    ("TRIPLANAR", "Triplanar", "Projects the textures onto the object from each axis. This projection method can be used to quickly remove seams from objects."),
    #("SPHERE", "Sphere", ""),
    #("TUBE", "Tube", "")
]

VALUE_NODE_TYPES = [
    ("GROUP", "GROUP", ""),
    ("TEXTURE", "TEXTURE", ""),
]

TEXTURE_INTERPOLATION_MODES = [
    ("Linear", "Linear", ""),
    ("Cubic", "Cubic", ""),
    ("Closest", "Closest", ""),
    ("Smart", "Smart", "")
]

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

MATERIAL_LAYER_TYPES = [
    ("FILL", "Fill", "A layer that fills the entier object with a material."), 
    ("DECAL", "Decal", "A material projected onto the model using a decal object (empty) which allows users to dynamically position textures.")
]

#----------------------------- UPDATING PROPERTIES -----------------------------#

def update_layer_index(self, context):
    '''Updates properties and user interface when a new layer is selected.'''
    layer_masks.refresh_mask_slots()

def replace_material_channel_node(material_channel_name, node_type):
    '''Replaces the existing material channel node with a new node of the given type.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_group_node = get_layer_node_tree(selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
    old_node_location = value_node.location

    layer_group_node.nodes.remove(value_node)

    match node_type:
        case 'GROUP':
            new_node = layer_group_node.nodes.new('ShaderNodeGroup')
            channel_name = material_channel_name.lower()
            default_node_tree = bpy.data.node_groups.get("ML_Default{0}".format(channel_name.capitalize()))
            new_node.node_tree = default_node_tree
        case 'TEXTURE':
            new_node = layer_group_node.nodes.new('ShaderNodeTexImage')
            layer_blur_node = get_material_layer_node('LAYER_BLUR', selected_layer_index)
            if layer_blur_node:
                layer_group_node.links.new(layer_blur_node.outputs.get(material_channel_name.capitalize()), new_node.inputs[0])

    new_node.name = "{0}_VALUE".format(material_channel_name)
    new_node.label = new_node.name
    new_node.location = old_node_location
    new_node.width = 200

    mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
    layer_group_node.links.new(new_node.outputs[0], mix_node.inputs[7])

def update_color_channel_node_type(self, context):
    replace_material_channel_node('COLOR', self.color_node_type)

def update_subsurface_channel_node_type(self, context):
    replace_material_channel_node('SUBSURFACE', self.subsurface_node_type)

def update_metallic_channel_node_type(self, context):
    replace_material_channel_node('METALLIC', self.metallic_node_type)

def update_specular_channel_node_type(self, context):
    replace_material_channel_node('SPECULAR', self.specular_node_type)

def update_roughness_channel_node_type(self, context):
    replace_material_channel_node('ROUGHNESS', self.roughness_node_type)

def update_emission_channel_node_type(self, context):
    replace_material_channel_node('EMISSION', self.emission_node_type)

def update_normal_channel_node_type(self, context):
    replace_material_channel_node('NORMAL', self.normal_node_type)

def update_height_channel_node_type(self, context):
    replace_material_channel_node('HEIGHT', self.height_node_type)

def update_alpha_channel_node_type(self, context):
    replace_material_channel_node('ALPHA', self.alpha_node_type)

def update_layer_projection_mode(self, context):
    '''Updates the projection mode for the selected layer'''
    print("Placeholder...")

def update_sync_layer_projection_scale(self, context):
    print("Placeholder...")

#----------------------------- HELPER FUNCTIONS -----------------------------#

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

def format_layer_group_node_name(active_material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(active_material_name, layer_index)

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    
    if not bpy.context.active_object:
        return None
    
    if not bpy.context.active_object.active_material:
        return None
    
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)

    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index=0, material_channel_name='COLOR', get_changed=False):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''
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
        
        case 'LAYER_BLUR':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("LAYER_BLUR")

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
            value_node_name = "{0}_VALUE".format(material_channel_name)
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
                node_tree.nodes.get('Group Output')
            return None
        
        case 'INPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_tree.nodes.get('Group Input')
            return None
        
        case 'DECAL_COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_tree.nodes.get('DECAL_COORDINATES')
            return None
        
        case 'DECAL_MASK':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_tree.nodes.get('DECAL_MASK')
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
    active_object = bpy.context.active_object

    blender_addon_utils.append_default_node_groups()        # Append all required node groups first to avoid node group duplication from re-appending.

    # Run checks the make sure this operator can be ran without errors, display info messages to users if it can't be ran.
    if active_object.type != 'MESH':
        blender_addon_utils.log_status("Selected object must be a mesh to add materials", self, 'ERROR')
        return {'FINISHED'}

    # If there are no material slots, or no material in the active material slot, make a new MatLayer material by appending the default material setup.
    if len(active_object.material_slots) == 0:
        new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")
        new_material.name = active_object.name
        active_object.data.materials.append(new_material)
        active_object.active_material_index = 0

    elif active_object.material_slots[active_object.active_material_index].material == None:
        new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")
        new_material.name = active_object.name
        active_object.material_slots[active_object.active_material_index].material = new_material

    new_layer_slot_index = add_material_layer_slot()

    # Add a material layer group node based on the specified layer type.
    active_material = bpy.context.active_object.active_material
    match layer_type:
        case 'DEFAULT':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DefaultLayer", return_unique=True, never_auto_delete=True)

        case 'PAINT':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DefaultLayer", return_unique=True, never_auto_delete=True)

        case 'DECAL':
            default_layer_node_group = blender_addon_utils.append_group_node("ML_DecalLayer", return_unique=True, never_auto_delete=True)

    default_layer_node_group.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
    new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
    new_layer_group_node.node_tree = default_layer_node_group
    new_layer_group_node.name = str(new_layer_slot_index) + "~"
    new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
    
    reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
    organize_layer_group_nodes()
    link_layer_group_nodes()
    layer_masks.organize_mask_nodes()

    # For specific layer types, perform additional setup steps.
    match layer_type:
        case 'PAINT':
            print("Placeholder...")

        case 'DECAL':
            # Append a default decal image.
            decal_mask_node = get_material_layer_node('DECAL_MASK', new_layer_slot_index)
            if decal_mask_node:
                default_decal_image = blender_addon_utils.append_image('DefaultDecal')
                decal_mask_node.image = default_decal_image

            # Create a new decal object.
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 0.1))
            decal_object = bpy.context.active_object

            # Add the new decal object to the decal coordinate node.
            decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', new_layer_slot_index)
            if decal_coordinate_node:
                decal_coordinate_node.object = decal_object

            # TODO: Set ideal decal snapping settings.

def duplicate_layer(original_layer_index, self):
    '''Duplicates the material layer at the provided layer index.'''

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
            link_layer_group_nodes()
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

def delete_layer(self):
    '''Deletes the selected layer'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return {'FINISHED'}

    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    active_material = bpy.context.active_object.active_material

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
    link_layer_group_nodes()
    layer_masks.organize_mask_nodes()

    # Remove the layer slot and reset the selected layer index.
    layers.remove(selected_layer_index)
    bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

def move_layer(direction, self):
    '''Moves the selected layer up or down on the material layer stack.'''
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

                active_material_name = bpy.context.active_object.active_material.name
                above_layer_mask_count = layer_masks.count_masks(selected_layer_index + 1)
                for i in range(0, above_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name = layer_masks.format_mask_name(active_material_name, selected_layer_index, i)
                    mask_node.node_tree.name = mask_node.name

                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                    mask_node.name = layer_masks.format_mask_name(active_material_name, selected_layer_index + 1, i)
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

                active_material_name = bpy.context.active_object.active_material.name
                below_layer_mask_count = layer_masks.count_masks(selected_layer_index - 1)
                for i in range(0, below_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                    mask_node.name = layer_masks.format_mask_name(active_material_name, selected_layer_index, i)
                    mask_node.label = mask_node.name
                    mask_node.node_tree.name = mask_node.name

                for i in range(0, selected_layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                    mask_node.name = layer_masks.format_mask_name(active_material_name, selected_layer_index - 1, i)
                    mask_node.label = mask_node.name
                    mask_node.node_tree.name = mask_node.name

            else:
                debug_logging.log("Can't move layer down, no layers exist below the selected layer.")

        case _:
            debug_logging.log_status("Invalid direction provided for moving a material layer.", self, 'ERROR')
            return

    organize_layer_group_nodes()
    link_layer_group_nodes()
    layer_masks.organize_mask_nodes()
    layer_masks.refresh_mask_slots()

def count_layers():
    '''Counts the total layers in the active material by reading the active material's node tree.'''
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

def link_layer_group_nodes():
    '''Connects all layer group nodes to other existing group nodes, and the principled BSDF shader.'''
    # Note: This function may be able to be optimized by only diconnecting nodes that must be disconnected, potentially reducing re-compile time for shaders.

    if not bpy.context.active_object:
        return

    if not bpy.context.active_object.active_material:
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
                        material_channel_active = getattr(texture_set_settings.global_material_channel_toggles, "{0}_channel_toggle".format(material_channel_name.lower()))
                        if not material_channel_active:
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
                material_channel_active = getattr(texture_set_settings.global_material_channel_toggles, "{0}_channel_toggle".format(material_channel_name.lower()))
                if not material_channel_active:
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

def apply_mesh_maps():
    '''Searches for all mesh map texture nodes in the node tree and applies mesh maps if they exist.'''
    # Apply baked mesh maps to all group nodes used as masks for all material layers.
    layers = bpy.context.scene.matlayer_layers
    for layer_index in range(0, len(layers)):
        mask_count = layer_masks.count_masks(layer_index)
        for mask_index in range(0, mask_count):
            for mesh_map_type in baking.MESH_MAP_TYPES:
                mask_node = layer_masks.get_mask_node('MASK', layer_index, mask_index)
                mesh_map_node = mask_node.node_tree.get(mesh_map_type)
                if mesh_map_node:
                    if mesh_map_node.bl_static_type == 'TEX_IMAGE':
                        mesh_map_node.image = baking.get_meshmap_image(bpy.context.active_object.name, mesh_map_type)
    debug_logging.log("Applied baked mesh maps.")

#----------------------------- OPERATORS -----------------------------#

class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer", update=update_layer_index)
    material_channel_preview: BoolProperty(name="Material Channel Preview", description="If true, only the rgb output values for the selected material channel will be used on the object.", default=False)
    selected_material_channel: EnumProperty(items=MATERIAL_CHANNEL, name="Material Channel", description="The currently selected material channel", default='COLOR')

class ProjectionSettings(PropertyGroup):
    '''Projection settings for this add-on.'''
    mode: EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='UV', update=update_layer_projection_mode)
    sync_projection_scale: BoolProperty(name="Sync Projection Scale", description="When enabled Y and Z projection (if the projection mode has a z projection) will be synced with the X projection", default=True,update=update_sync_layer_projection_scale)

class MaterialChannelNodeType(PropertyGroup):
    '''An enum node type for the material node used to represent the material channel texture in every material channel.'''
    color_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Color Channel Node Type", description="The node type for the color channel", default='GROUP', update=update_color_channel_node_type)
    subsurface_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Subsurface Scattering Channel Node Type", description="The node type for the subsurface scattering channel", default='GROUP', update=update_subsurface_channel_node_type)
    metallic_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Metallic Channel Node Type", description="The node type for the metallic channel", default='GROUP', update=update_metallic_channel_node_type)
    specular_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Specular Channel Node Type", description="The node type for the specular channel", default='GROUP', update=update_specular_channel_node_type)
    roughness_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Roughness Channel Node Type", description="The node type for roughness channel", default='GROUP', update=update_roughness_channel_node_type)
    emission_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Emission Channel Node Type", description="The node type for the emission channel", default='GROUP', update=update_emission_channel_node_type)
    normal_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Normal Channel Node Type", description="The node type for the normal channel", default='GROUP', update=update_normal_channel_node_type)
    height_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Height Channel Node Type", description="The node type for the height channel", default='GROUP', update=update_height_channel_node_type)
    alpha_node_type: EnumProperty(items=VALUE_NODE_TYPES, name="Alpha Channel Node Type", description="The node type for the alpha channel", default='GROUP', update=update_emission_channel_node_type)

# Can these properties be removed in favor of using properties stored in the material node tree?
class MATLAYER_layers(PropertyGroup):
    material_channel_node_types: PointerProperty(type=MaterialChannelNodeType)
    projection: PointerProperty(type=ProjectionSettings)

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
    bl_description = "Toggle on / off a blur filter for the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default="COLOR")

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index

        # TODO: Disable and disconnect the layer blur if it's applied.
        layer_blur_node = get_material_layer_node('LAYER_BLUR', selected_layer_index)
        if layer_blur_node:
            layer_blur_node.mute = True

        # Enable blurring for the specified material channel.
        blur_node = get_material_layer_node('BLUR', selected_layer_index, self.material_channel_name)
        if blur_node:
            if blur_node.mute:
                blur_node.mute = False

                # Connect the projection node to the blur node.
                layer_node_tree = get_layer_node_tree(selected_layer_index)
                projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
                if projection_node and layer_node_tree:
                    layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

                # Connect to the value node if it's a texture.
                value_node = get_material_layer_node('VALUE', selected_layer_index, self.material_channel_name)
                if value_node:
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        layer_node_tree.links.new(blur_node.outputs[0], value_node.inputs[0])

            else:
                blur_node.mute = True
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

        link_layer_group_nodes()
        return {'FINISHED'}