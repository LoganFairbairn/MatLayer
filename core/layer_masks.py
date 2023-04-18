# Masking module containing properties and functions for masking material layers.

# Imports from Blender.
import bpy
from bpy.types import Operator, PropertyGroup, UIList
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty

# Imports from this add-on.
from ..core.layers import PROJECTION_MODES, TEXTURE_EXTENSION_MODES, TEXTURE_INTERPOLATION_MODES
from ..core.layer_filters import FILTER_NODE_TYPES
from . import layer_nodes
from . import material_channels
from . import texture_set_settings
from ..utilities import info_messages

# Imports for saving / importing mask images.
import os
import random
from bpy_extras.io_utils import ImportHelper

# A list of mask node types available in this add-on.
MASK_NODE_TYPES = [
    ("TEXTURE", "Texture", "An image texture is used as a mask for the selected material layer."),
    ("GROUP_NODE", "Group Node", "A custom group node is used as a mask for the selected material layer. You can create a custom group node and use it for this mask, with the only requirement being the first node output is the output used to mask the selected material layer."),
    ("NOISE", "Noise", "Procedurally generated noise is used to mask the selected material layer."),
    ("VORONOI", "Voronoi", "A procedurally generated voronoi pattern is used to mask the selected material layer."),
    ("MUSGRAVE", "Musgrave", "A procedurally generated musgrave pattern is used to mask the selected material layer.")
    ]

# Constant mask node names.
MASK_NODE_NAMES = ("MaskTexture", "MaskCoord", "MaskMapping", "MaskMix")

# The maximum number of masks a single layer can use. Realistically users should never need more masks on a single layer than this.
MAX_LAYER_MASKS = 5

# The maximum number of mask filter nodes that can be applied to a single mask. Users should never need more masks than the number defined here. Imposing a maximum number of mask filters helps with optimization and proper workflow.
MAX_MASK_FILTERS = 3

#----------------------------- MASK AUTO UPDATING FUNCTIONS -----------------------------#

def update_mask_stack_index(self, context):
    '''Performs actions when the mask stack index is changed.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    # If the mask is an image type, select the image mask so users can edited it.
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    mask_texture_node = get_mask_node('MaskTexture', 'COLOR', selected_material_layer_index, selected_mask_index, False)
    if mask_texture_node:
        if mask_texture_node.bl_static_type == 'TEX_IMAGE':
            if mask_texture_node.image != None:
                context.scene.tool_settings.image_paint.canvas = mask_texture_node.image

    refresh_mask_filter_stack(context)

def update_mask_node_type(self, context):
    '''Updates the mask node type.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return

    selected_material_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    masks = context.scene.matlay_masks

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

        # Delete the old mask node from all material channels.
        mask_texture_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, selected_mask_index)
        if mask_texture_node:
            material_channel_node.node_tree.nodes.remove(mask_texture_node)

        # Add a new node based on the selected type.
        new_mask_node = None
        match masks[selected_mask_index].node_type:
            case 'TEXTURE':
                new_mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexImage')

                # Connect the mapping and coord node based on projection settings of the mask.
                selected_mask = masks[selected_mask_index]
                mapping_node = get_mask_node('MaskMapping', material_channel_name, selected_material_index, selected_mask_index)
                coord_node = get_mask_node("MaskCoord", material_channel_name, selected_material_index, selected_mask_index)

                material_channel_node.node_tree.links.new(mapping_node.outputs[0], new_mask_node.inputs[0])

                match selected_mask.projection.projection_mode:
                    case 'FLAT':
                        material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])

                    case 'TRI-PLANAR':
                        material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])

                    case 'SPHERE':
                        material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])

                    case 'TUBE':
                        material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])

            case 'GROUP_NODE':
                new_mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeGroup')
                empty_group_node = bpy.data.node_groups['MATLAY_EMPTY']
                if not empty_group_node:
                    material_channels.create_empty_group_node(context)
                new_mask_node.node_tree = bpy.data.node_groups['MATLAY_EMPTY']

            case 'NOISE':
                new_mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexNoise')

            case 'VORONOI':
                new_mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexVoronoi')

            case 'MUSGRAVE':
                new_mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexMusgrave')

        # Name the mask node.
        new_mask_node.name = format_mask_node_name('MaskTexture', selected_material_index, selected_mask_index)
        new_mask_node.label = new_mask_node.name

        # Re-link the mask nodes.
        relink_layer_mask_nodes(context)

        # Re-organize nodes.
        layer_nodes.update_layer_nodes(context)

def update_mask_image(self, context):
    '''Updates the mask image in all material channels when the mask image is manually changed.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return

    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    for material_channel_name in material_channels.get_material_channel_list():
        mask_texture_node = get_mask_node('MaskTexture', material_channel_name, selected_material_layer_index, selected_mask_index)
        if mask_texture_node:
            mask_texture_node.image = self.mask_image

def update_mask_hidden(self, context):
    '''Hides / unhides masks when the hide icon on the mask layer stack is clicked by a user.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return

    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index

    for material_channel_name in material_channels.get_material_channel_list():
        mask_nodes = get_mask_nodes(material_channel_name, selected_material_layer_index, self.stack_index)
        for node in mask_nodes:
            # Unhide mask nodes.
            if self.hidden:
                node.mute = True

            # Hide mask nodes.
            else:
                node.mute = False

#----------------------------- UPDATE MASK PROJECTION -----------------------------#

def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

        # Get nodes.
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        coord_node = layer_nodes.get_layer_node("COORD", material_channel_name, selected_layer_index, context)
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if texture_node.type == 'TEX_IMAGE':
            # Delink coordinate node.
            if coord_node:
                outputs = coord_node.outputs
                for o in outputs:
                    for l in o.links:
                        if l != 0:
                            material_channel_node.node_tree.links.remove(l)

                if selected_layer_index > -1:
                    # Connect nodes based on projection type.
                    if layers[selected_layer_index].projection.projection_mode == 'FLAT':
                        material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])
                        texture_node.projection = 'FLAT'

                    if layers[selected_layer_index].projection.projection_mode == 'BOX':
                        material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                        texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, selected_layer_index, context)
                        if texture_node and texture_node.type == 'TEX_IMAGE':
                            texture_node.projection_blend = self.projection_blend
                        texture_node.projection = 'BOX'

                    if layers[selected_layer_index].projection.projection_mode == 'SPHERE':
                        material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                        texture_node.projection = 'SPHERE'

                    if layers[selected_layer_index].projection.projection_mode == 'TUBE':
                        material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                        texture_node.projection = 'TUBE'

def update_projection_interpolation(self, context):
    '''Updates the image texture interpolation mode when it's changed.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.interpolation = layers[selected_layer_index].projection.texture_interpolation

def update_projection_extension(self, context):
    '''Updates the image texture extension projection mode when it's changed.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.extension = layers[selected_layer_index].projection.texture_extension

def update_projection_blend(self, context):
    '''Updates the projection blend node values when the cube projection blend value is changed.'''
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return

    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.projection_blend = layers[selected_layer_index].projection.texture_extension

def update_projection_offset_x(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

            if mapping_node:
                mapping_node.inputs[1].default_value[0] = layers[selected_layer_index].projection.projection_offset_x

def update_projection_offset_y(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

            if mapping_node:
                mapping_node.inputs[1].default_value[1] = layers[selected_layer_index].projection.projection_offset_y

def update_projection_rotation(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    '''Updates the layer projections rotation for all layers.'''
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
            if mapping_node:
                mapping_node.inputs[2].default_value[2] = layers[selected_layer_index].projection.projection_rotation

def update_projection_scale_x(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    '''Updates the layer projections x scale for all mapping nodes in the selected layer.'''
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

            if mapping_node:
                mapping_node.inputs[3].default_value[0] = layers[selected_layer_index].projection.projection_scale_x

            if self.match_layer_scale:
                layers[selected_layer_index].projection.projection_scale_y = layers[selected_layer_index].projection.projection_scale_x

def update_projection_scale_y(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
            
            if mapping_node:
                mapping_node.inputs[3].default_value[1] = layers[selected_layer_index].projection.projection_scale_y

def update_match_layer_scale(self, context):
    if context.scene.matlay_mask_stack.auto_update_mask_properties == False:
        return
    
    '''Updates matching of the projected layer scales.'''
    if self.match_layer_scale and context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        layer_index = context.scene.matlay_layer_stack.layer_index
        layers[layer_index].projection.projection_scale_y = layers[layer_index].projection.projection_scale_x

#----------------------------- CORE MASK FUNCTIONS -----------------------------#

def format_mask_node_name(mask_node_name, material_layer_index, mask_index, get_edited=False):
    '''All node names including mask node names must be formatted properly so they can be re-read from the layer stack. This function should be used to properly format the name of a mask node. Get edited will return the name of a mask node with a tilda at the end, signifying that the node is actively being changed.'''
    if get_edited:
        return  "{0}_{1}_{2}~".format(mask_node_name, str(material_layer_index), str(mask_index))
    else:
        return  "{0}_{1}_{2}".format(mask_node_name, str(material_layer_index), str(mask_index))

def get_mask_node(mask_node_name, material_channel_name, material_layer_index, mask_index, get_edited=False):
    '''Returns a layer mask node based on the given name and mask stack index. Valid options include "MaskTexture", "MaskCoord", "MaskMapping", "MaskMix".'''
    if mask_node_name in MASK_NODE_NAMES:
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
        if material_channel_node:
            if get_edited:
                node_name = "{0}_{1}_{2}~".format(mask_node_name, str(material_layer_index), str(mask_index))
            else:
                node_name = format_mask_node_name(mask_node_name, material_layer_index, mask_index)
            return material_channel_node.node_tree.nodes.get(node_name)
    else:
        info_messages.popup_message_box("Mask node name invalid, did you make a typo in your code?", "Coding Error", 'ERROR')
        return None

def get_mask_nodes(material_channel_name, material_stack_index, mask_stack_index, get_edited=False):
    '''Returns an array of mask node for the specific mask index.'''
    nodes = []
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for name in MASK_NODE_NAMES:
            mask_node = get_mask_node(name, material_channel_name, material_stack_index, mask_stack_index, get_edited)
            if mask_node:
                nodes.append(mask_node)
    return nodes

def get_all_mask_nodes_in_layer(material_stack_index, material_channel_name, get_edited=False):
    '''Returns all the mask nodes in the given material layer within the given material channel. If get edited is passed as true, all nodes part of the given material layer marked as being edited (signified by a tilda at the end of their name) will be returned.'''
    nodes = []
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for i in range(0, MAX_LAYER_MASKS):
            for name in MASK_NODE_NAMES:
                mask_node_name = format_mask_node_name(name, material_stack_index, i, get_edited)
                mask_node = material_channel_node.node_tree.nodes.get(mask_node_name)
                if mask_node:
                    nodes.append(mask_node)
                else:
                    break
    return nodes

def update_mask_indicies(context):
    '''Updates mask node indicies.'''

    # Update mask stack indicies first.
    masks = context.scene.matlay_masks
    number_of_layers = len(masks)
    for i in range(0, number_of_layers):
        masks[i].stack_index = i
    
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        selected_layer_index = bpy.context.scene.matlay_layer_stack.layer_index

        changed_index = -1
        mask_added = False
        mask_deleted = False

        # 1. Check for a newly added mask (signified by a tilda at the end of the node's name).
        for i in range(0, len(masks)):
            temp_mask_node_name = format_mask_node_name('MaskTexture', selected_layer_index, i, True)
            temp_mask_node = material_channel_node.node_tree.nodes.get(temp_mask_node_name)
            if temp_mask_node:
                mask_added = True
                changed_index = i
                break

        # 2. Check for a deleted mask.
        if not mask_added:
            for i in range(0, len(masks)):
                temp_mask_node_name = format_mask_node_name('MaskTexture', selected_layer_index, i)
                temp_mask_node = material_channel_node.node_tree.nodes.get(temp_mask_node_name)
                if not temp_mask_node:
                    mask_deleted = True
                    changed_index = i
                    break

        # 3. Rename mask nodes above the newly added mask on the mask stack if any exist (in reverse order to avoid naming conflicts).
        if mask_added:
            for i in range(len(masks), changed_index + 1, -1):
                index = i - 1
                for name in MASK_NODE_NAMES:
                    full_mask_node_name = "{0}_{1}_{2}".format(name, str(selected_layer_index), str(index - 1))
                    mask_node = material_channel_node.node_tree.nodes.get(full_mask_node_name)
                    if mask_node:
                        mask_node.name = format_mask_node_name(name, selected_layer_index, index)
                        mask_node.label = mask_node.name
                        masks[changed_index].stack_index = changed_index

            # Remove tilda from newly added mask nodes.
            for name in MASK_NODE_NAMES:
                new_mask_node_name = format_mask_node_name(name, selected_layer_index, changed_index, True)
                new_mask_node = material_channel_node.node_tree.nodes.get(new_mask_node_name)
                if new_mask_node:
                    new_mask_node.name = new_mask_node_name.replace('~', '')
                    new_mask_node.label = new_mask_node.name
                    masks[changed_index].stack_index = changed_index

        # 4. Rename mask nodes above the deleted mask if any exist.
        if mask_deleted and len(masks) > 0:
            for i in range(changed_index + 1, len(masks), 1):
                for name in MASK_NODE_NAMES:
                    old_name = format_mask_node_name(name, selected_layer_index, i)
                    mask_node = material_channel_node.node_tree.nodes.get(old_name)
                    if mask_node:
                        mask_node.name = format_mask_node_name(name, selected_layer_index, i - 1)
                        mask_node.label = mask_node.name
                        masks[i].stack_index = i - 1

def relink_layer_mask_nodes(context):
    '''Re-links layer mask nodes to other mask nodes and the layer (by connecting to the material layer's opacity node).'''
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_material_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
    masks = context.scene.matlay_masks
    mask_filters = context.scene.matlay_mask_filters

    # 1. Relink existing mask filters together.
    relink_mask_filter_nodes()

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        for i in range(0, len(masks)):

            # 2. Unlink all mask mix nodes.
            mix_mask_node = get_mask_node('MaskMix', material_channel_name, selected_material_layer_index, i)
            if mix_mask_node:
                output = mix_mask_node.outputs[0]
                for l in output.links:
                    if l != 0:
                        material_channel_node.node_tree.links.remove(l)

            # 3. Connect the mask texture node or the last mask filter (if one exists) to the mix mask node.
            last_node = None
            last_mask_filter_node = get_mask_filter_node(material_channel_name, selected_material_index, selected_mask_index, len(mask_filters) - 1)
            if last_mask_filter_node:
                last_node = last_mask_filter_node
            else:
                last_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, selected_mask_index, False)

            mix_mask_node = get_mask_node('MaskMix', material_channel_name, selected_material_index, selected_mask_index, False)
            if mix_mask_node and last_node:
                material_channel_node.node_tree.links.new(last_node.outputs[0], mix_mask_node.inputs[2])

            # 4. Re-link to the next mask if another one exists on this layer.
            next_mix_mask_node = get_mask_node('MaskMix', material_channel_name, selected_material_layer_index, i + 1)
            if next_mix_mask_node:
                material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], next_mix_mask_node.inputs[1])

        # 5. Link the last mask node to the layer's opacity node.
        opacity_node = layer_nodes.get_layer_node('OPACITY', material_channel_name, selected_material_layer_index, context)
        last_mask_node = get_mask_node('MaskMix', material_channel_name, selected_material_layer_index, len(masks) - 1)
        if opacity_node and last_mask_node:
            material_channel_node.node_tree.links.new(last_mask_node.outputs[0], opacity_node.inputs[0])

def count_masks(material_stack_index):
    '''Counts the total number of masks applied to a specified material layer by reading the material node tree.'''
    count = 0
    for i in range(0, MAX_LAYER_MASKS):
        if get_mask_node('MaskTexture', 'COLOR', material_stack_index, i):
            count += 1
        else:
            break
    return count

def read_masks(context):
    '''Reads the material node tree into the mask stack.'''
    masks = context.scene.matlay_masks
    mask_stack = context.scene.matlay_mask_stack
    selected_material_index = context.scene.matlay_layer_stack.layer_index

    # Only clear the mask stack if no masks exist on the selected material layer.
    masks.clear()
    total_number_of_masks = count_masks(selected_material_index)
    if total_number_of_masks <= 0:
        return
    
    # 1. Disable auto-updating for mask properties (properties auto-updating when being set can cause errors).
    mask_stack.auto_update_mask_properties = False

    # 2. Cache the selected mask index so we can refresh it to the closest index.
    previously_selected_mask_index = mask_stack.selected_mask_index
    
    # 3. Refresh the mask stack for the selected layer.
    for i in range(0, total_number_of_masks):
        masks.add()
        masks[i].stack_index = i
        masks[i].name = 'MASK'

    # 4. Reset the selected mask index.
    if len(masks) > 0 and previously_selected_mask_index < len(masks) - 1 and previously_selected_mask_index >= 0:
        mask_stack.selected_mask_index = previously_selected_mask_index
    else:
        mask_stack.selected_mask_index

    # 5. Read ui properties for the selected mask.
    # Mask nodes settings across all material channels should be the same, only read from the color material channel nodes.
    material_channel_name = 'COLOR'
    selected_mask_index = mask_stack.selected_mask_index
    texture_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, selected_mask_index)
    if texture_node:
        # TODO: Read the node type.
        match texture_node.bl_static_type:
            case 'TEX_IMAGE':
                masks[selected_mask_index].node_type = 'TEXTURE'

            case 'GROUP':
                masks[selected_mask_index].node_type = 'GROUP'
            
            case 'TEX_NOISE':
                masks[selected_mask_index].node_type = 'NOISE'

            case 'TEX_VORONOI':
                masks[selected_mask_index].node_type = 'VORONOI'

            case 'TEX_MUSGRAVE':
                masks[selected_mask_index].node_type = 'MUSGRAVE'


        if texture_node.bl_static_type == 'TEX_IMAGE':
            if texture_node.image:
                masks[selected_mask_index].mask_image = texture_node.image

    # Read mapping projection.
    mapping_node = get_mask_node('MaskMapping', material_channel_name, selected_material_index, selected_mask_index)
    if mapping_node:
        masks[selected_mask_index].projection.projection_offset_x = mapping_node.inputs[1].default_value[0]
        masks[selected_mask_index].projection.projection_offset_y = mapping_node.inputs[1].default_value[1]
        masks[selected_mask_index].projection.projection_rotation = mapping_node.inputs[2].default_value[2]
        masks[selected_mask_index].projection.projection_scale_x = mapping_node.inputs[3].default_value[0]
        masks[selected_mask_index].projection.projection_scale_y = mapping_node.inputs[3].default_value[1]
        if masks[selected_mask_index].projection.projection_scale_x != masks[i].projection.projection_scale_y:
            masks[selected_mask_index].projection.match_layer_scale = False

    # Read projection mode.
    mask_texture_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, selected_mask_index)
    if mask_texture_node and mask_texture_node.type == 'TEX_IMAGE':
        masks[selected_mask_index].projection.projection_blend = mask_texture_node.projection_blend
        masks[selected_mask_index].projection.texture_extension = mask_texture_node.extension
        masks[selected_mask_index].projection.texture_interpolation = mask_texture_node.interpolation
        masks[selected_mask_index].projection.projection_mode = mask_texture_node.projection
    else:
        masks[selected_mask_index].projection.projection_mode = 'FLAT'

    # Read hidden (muted) masks.
    for i in range(0, len(masks)):
        mask_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, i)
        if mask_node:
            if mask_node.mute:
                masks[i].hidden = True

    # 6. Re-enable auto-updating for mask properties.
    mask_stack.auto_update_mask_properties = True

def add_mask_slot(context):
    '''Adds a new mask slot and selects it.'''
    masks = context.scene.matlay_masks
    mask_stack = context.scene.matlay_mask_stack
    selected_layer_mask_index = mask_stack.selected_mask_index
    masks.add()
    masks[len(masks) - 1].name = "MASK"

    mask_stack.auto_update_mask_properties = False
    if selected_layer_mask_index < 0:
        move_index = len(masks) - 1
        move_to_index = 0
        masks.move(move_index, move_to_index)
        mask_stack.selected_mask_index = move_to_index
        selected_layer_mask_index = len(masks) - 1

    else:
        move_index = len(masks) - 1
        move_to_index = max(0, min(selected_layer_mask_index + 1, len(masks) - 1))
        masks.move(move_index, move_to_index)
        mask_stack.selected_mask_index = move_to_index
        selected_layer_mask_index = max(0, min(selected_layer_mask_index + 1, len(masks) - 1))
    mask_stack.auto_update_mask_properties = True

def add_default_mask_nodes(context):
    '''Adds default mask nodes to all material channels.'''
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
                
            # Create default mask nodes.
            mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexImage')
            mask_node.name = format_mask_node_name("MaskTexture", selected_layer_index, selected_mask_index, True)
            mask_node.label = mask_node.name
                
            mask_coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
            mask_coord_node.name = format_mask_node_name("MaskCoord", selected_layer_index, selected_mask_index, True)
            mask_coord_node.label = mask_coord_node.name

            mask_mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
            mask_mapping_node.name = format_mask_node_name("MaskMapping", selected_layer_index, selected_mask_index, True)
            mask_mapping_node.label = mask_mapping_node.name

            # Each mask gets it's own mix layer node to allow mixing with other masks.
            # The mix mask node also handles opacity blending between masks.
            mask_mix_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMixRGB')
            mask_mix_node.name = format_mask_node_name("MaskMix", selected_layer_index, selected_mask_index, True)
            mask_mix_node.label = mask_mix_node.name
            mask_mix_node.inputs[0].default_value = 1.0
            mask_mix_node.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
            mask_mix_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
            mask_mix_node.use_clamp = True
                
            # Link newly created nodes.
            material_channel_node.node_tree.links.new(mask_node.outputs[0], mask_mix_node.inputs[2])
            material_channel_node.node_tree.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
            material_channel_node.node_tree.links.new(mask_mapping_node.outputs[0], mask_node.inputs[0])

def add_mask(mask_type, context):
    '''Adds a mask of the specified type to the selected material layer.'''
    masks = context.scene.matlay_masks
    mask_stack = context.scene.matlay_mask_stack
    selected_layer_mask_index = mask_stack.selected_mask_index
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    # Stop users from adding too many masks.
    if len(masks) >= MAX_LAYER_MASKS:
        info_messages.popup_message_box("You can't have more than {0} masks on a single layer. This is a safeguard to stop users from adding an unnecessary amount of masks, which will impact performance.".format(MAX_LAYER_MASKS), 'User Error', 'ERROR')
        return

    add_mask_slot(context)
    add_default_mask_nodes(context)
    update_mask_indicies(context)
    relink_layer_mask_nodes(context)

    # TODO: Should only need to re-organize nodes here, instead of re-index & re-link.
    layer_nodes.update_layer_nodes(context)

    # Create a black or white mask image for the new mask.
    match mask_type:
        case 'BLACK_MASK':
            bpy.ops.matlay.add_mask_image(image_fill='BLACK')

        case 'WHITE_MASK':
            bpy.ops.matlay.add_mask_image(image_fill='WHITE')

def move_mask(direction, context):
    '''Moves the selected layer mask up or down on the layer stack.'''
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    masks = context.scene.matlay_masks
    mask_stack = context.scene.matlay_mask_stack

    mask_stack.auto_update_mask_properties = False
    
    # Don't move the mask if the user is trying to move the layer out of range.
    if direction == 'UP' and selected_mask_index + 1 > len(masks) - 1:
        return
    if direction == 'DOWN' and selected_mask_index - 1 < 0:
        return
    
    # Get the layer index over or under the selected layer, depending on the direction the layer is being moved.
    if direction == 'UP':
        moving_to_index = max(min(selected_mask_index + 1, len(masks) - 1), 0)
    else:
        moving_to_index = max(min(selected_mask_index - 1, len(masks) - 1), 0)

    # 1. Add a tilda to the end of all the mask nodes to signify they are being edited (and to avoid naming conflicts).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        nodes = get_mask_nodes(material_channel_name, selected_material_layer_index, selected_mask_index)
        for node in nodes:
            node.name = node.name + "~"
            node.label = node.name

    # 2. Update the mask node names for the layer below or above the selected index.
    for material_channel_name in material_channel_list:
        nodes = get_mask_nodes(material_channel_name, selected_material_layer_index, moving_to_index)
        for node in nodes:
            node_info = node.name.split('_')
            node.name = node_info[0] + "_" + str(selected_material_layer_index) + "_" + str(selected_mask_index)
            node.label = node.name

    # 3. Remove the tilda from the end of the mask node names that were edited and re-index them.
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        nodes = get_mask_nodes(material_channel_name, selected_material_layer_index, selected_mask_index, True)
        for node in nodes:
            node_info = node.name.split('_')
            node.name = node_info[0] + "_" + str(selected_material_layer_index) + "_" + str(moving_to_index)
            node.label = node.name

    # 4. Move the selected mask on the ui stack.
    if direction == 'UP':
        index_to_move_to = max(min(selected_mask_index + 1, len(masks) - 1), 0)
    else:
        index_to_move_to = max(min(selected_mask_index - 1, len(masks) - 1), 0)
    masks.move(selected_mask_index, index_to_move_to)
    context.scene.matlay_mask_stack.selected_mask_index = index_to_move_to

    # 6. Re-link and organize mask nodes.
    update_mask_indicies(context)
    relink_layer_mask_nodes(context)
    layer_nodes.update_layer_nodes(context)     # TODO: Swap this out for a function that only organizes all nodes, instead of re-linking and re-indexing nodes too.

    mask_stack.auto_update_mask_properties = True

#----------------------------- MASK PROPERTIES & OPERATORS -----------------------------#

class MaskProjectionSettings(PropertyGroup):
    '''Projection settings for this add-on.'''
    projection_mode: EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='FLAT')
    texture_extension: EnumProperty(items=TEXTURE_EXTENSION_MODES, name="Extension", description="", default='REPEAT')
    texture_interpolation: EnumProperty(items=TEXTURE_INTERPOLATION_MODES, name="Interpolation", description="", default='Linear')
    projection_blend: FloatProperty(name="Projection Blend", description="The projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR')
    projection_offset_x: FloatProperty(name="Offset X", description="Projected x offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_offset_y: FloatProperty(name="Offset Y", description="Projected y offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_rotation: FloatProperty(name="Rotation", description="Projected rotation of the selected layer", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE')
    projection_scale_x: FloatProperty(name="Scale X", description="Projected x scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')
    projection_scale_y: FloatProperty(name="Scale Y", description="Projected y scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')
    match_layer_scale: BoolProperty(name="Match Layer Scale", default=True,update=update_match_layer_scale)
    match_layer_mask_scale: BoolProperty(name="Match Layer Mask Scale", default=True)

class MATLAY_mask_stack(PropertyGroup):
    '''Properties for the mask stack.'''
    selected_mask_index: IntProperty(default=-1, update=update_mask_stack_index)
    mask_property_tab: EnumProperty(
        items=[('MASK', "MASK", "Properties for the selected mask."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected mask."),
               ('FILTERS', "FILTERS", "Filters for the selcted mask.")],
        name="Mask Properties Tab",
        description="Tabs for mask properties.",
        default='MASK',
        options={'HIDDEN'},
    )
    auto_update_mask_properties: BoolProperty(name="Auto Update Mask Properties", description="When true, changing mask properties will trigger automatic updates.", default=True)

class MATLAY_masks(PropertyGroup):
    '''Properties for layer masks.'''
    stack_index: bpy.props.IntProperty(name="Stack Array Index", description="The array index of this mask within the mask stack, stored here to make it easy to access the array index of a specific layer", default=-9)
    name: StringProperty(name="Mask Name", default="Mask Naming Error")
    projection: PointerProperty(type=MaskProjectionSettings)
    node_type: EnumProperty(items=MASK_NODE_TYPES, name="Mask Node Type", description="The node type used to represent the mask", default='TEXTURE', update=update_mask_node_type)
    hidden: BoolProperty(name="Hidden", default=False, description="Hides / unhides (mutes) the layer mask", update=update_mask_hidden)

    # Define a mask texture property to use for masks using images. This allows the mask image to be properly updated in ALL material channels when the mask image is changed by assigning it an update function.
    mask_image: PointerProperty(type=bpy.types.Image, name="Mask Image", description="The image texture used for the selected mask", update=update_mask_image)

class MATLAY_UL_mask_stack(bpy.types.UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Draw hidden (muted masks)
            row = layout.row(align=True)
            row.ui_units_x = 1
            if item.hidden == True:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.hidden == False:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

            # Draw the mask name + layer index.
            row = layout.row(align=True)
            row.ui_units_x = 3
            row.label(text="Mask " + str(item.stack_index + 1))

            # Draw the mask opacity and blend mode.
            selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel
            selected_material_index = context.scene.matlay_layer_stack.layer_index
            selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
            mix_mask_node = get_mask_node("MaskMix", selected_material_channel, selected_material_index, item.stack_index)

            if mix_mask_node:
                row = layout.row(align=True)
                row.ui_units_x = 2
                split = layout.split()
                col = split.column(align=True)
                col.ui_units_x = 1.6
                col.scale_y = 0.5
                col.prop(mix_mask_node.inputs[0], "default_value", text="", emboss=True, slider=True)
                col.prop(mix_mask_node, "blend_type", text="")

class MATLAY_OT_add_black_layer_mask(Operator):
    '''Creates a new completely black texture and adds it to a new mask. Use this for when only a portion of the object is planned to be masked'''
    bl_idname = "matlay.add_black_layer_mask"
    bl_label = "Add Black Mask"
    bl_description = "Creates a new completely black texture and adds it to a new mask. Use this for when only a portion of the object is planned to be masked"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('BLACK_MASK', context)
        return{'FINISHED'}

class MATLAY_OT_add_white_layer_mask(Operator):
    '''Creates a new completely white texture and adds it to a new mask. Use this for when the majority of the object is masked.'''
    bl_idname = "matlay.add_white_layer_mask"
    bl_label = "Add White Mask"
    bl_description = "Adds a mask to the selected layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('WHITE_MASK', context)
        return{'FINISHED'}
    
class MATLAY_OT_add_empty_layer_mask(Operator):
    '''Adds a layer mask to the selected layer with no texture assigned to it's texture slot. Use this operator to add a mask for when you will load a custom texture into the newly added mask, or you plan to change to a procedural node type after adding the mask (noise, voronoi, musgrave).'''
    bl_idname = "matlay.add_empty_layer_mask"
    bl_label = "Add Empty Mask"
    bl_description = "Adds a layer mask to the selected layer with no texture assigned to it's texture slot"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('EMPTY', context)
        return{'FINISHED'}

class MATLAY_OT_open_layer_mask_menu(Operator):
    '''Opens a menu of masks that can be added to the selected material layer.'''
    bl_idname = "matlay.open_layer_mask_menu"
    bl_label = "Open Layer Mask Menu"
    bl_description = "Opens a menu of masks that can be added to the selected material layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the menu when the button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlay.add_black_layer_mask", text="Black Mask")
        col.operator("matlay.add_white_layer_mask", text="White Mask")
        col.operator("matlay.add_empty_layer_mask", text="Empty Mask")

class MATLAY_OT_delete_layer_mask(Operator):
    bl_idname = "matlay.delete_layer_mask"
    bl_label = "Delete Layer Mask"
    bl_description = "Deletes the mask for the selected layer if one exists"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        selected_layer_index = context.scene.matlay_layer_stack.layer_index
        masks = context.scene.matlay_masks

        # 1. Delete the mask nodes (in all material channels).
        for material_channel_name in material_channels.get_material_channel_list():
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            mask_nodes = get_mask_nodes(material_channel_name, selected_layer_index, selected_mask_index)
            for node in mask_nodes:
                material_channel_node.node_tree.nodes.remove(node)

        # 2. Re-index and re-link any remaining layer mask nodes.
        update_mask_indicies(context)
        relink_layer_mask_nodes(context)

        # 3. Remove the mask slot.
        masks.remove(selected_mask_index)

        # 4. Reset the selected mask index.
        context.scene.matlay_mask_stack.selected_mask_index = max(min(selected_mask_index - 1, len(masks) - 1), 0)

        # TODO: Optimization write a function in layer nodes that organizes all layer nodes in all material channels WITHOUT re-linking or re-indexing nodes.
        # 5. Re-link and re-organize layers.
        relink_layer_mask_nodes(context)
        layer_nodes.update_layer_nodes(context)

        return{'FINISHED'}

class MATLAY_OT_move_layer_mask_up(Operator):
    '''Moves the selected layer up on the layer stack'''
    bl_idname = "matlay.move_layer_mask_up"
    bl_label = "Move Layer Mask Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer up on the layer stack"

    def execute(self, context):
        move_mask('UP', context)
        return {'FINISHED'}

class MATLAY_OT_move_layer_mask_down(Operator):
    '''Moves the selected layer down on the layer stack'''
    bl_idname = "matlay.move_layer_mask_down"
    bl_label = "Move Layer Mask Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer down on the layer stack"

    def execute(self, context):
        move_mask('DOWN', context)
        return {'FINISHED'}

class MATLAY_OT_add_mask_image(Operator):
    '''Creates a new image in Blender's data and inserts it into the selected mask.'''
    bl_idname = "matlay.add_mask_image"
    bl_label = "Add Mask Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a new image in Blender's data and inserts it into the selected mask"

    # Valid mask image fill options: BLACK, WHITE, EMPTY
    image_fill: StringProperty(default='BLACK')

    def execute(self, context):
        # 1. Assign the new mask image a name.
        image_name = "Mask_" + str(random.randrange(10000,99999))
        while bpy.data.images.get(image_name) != None:
            image_name = "Mask_" + str(random.randrange(10000,99999))

        # 2. Create a new image of the texture size defined in the texture set settings.
        image_width = texture_set_settings.get_texture_width()
        image_height = texture_set_settings.get_texture_height()
        match self.image_fill:
            case 'BLACK':
                image_fill = (0.0, 0.0, 0.0, 1.0)

            case 'WHITE':
                image_fill = (1.0, 1.0, 1.0, 1.0)

            case 'EMPTY':
                image_fill = (0.0, 0.0, 0.0, 0.0)

            case _:
                print("Error: Image mask fill type given is invalid.")
                image_fill = (0.0, 0.0, 0.0, 1.0)

        image = bpy.ops.image.new(name=image_name,
                                  width=image_width,
                                  height=image_height,
                                  color=image_fill,
                                  alpha=True,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)
        
        # TODO: Packing doesn't work after creating a new layer because the image file isn't considered 'dirty' as no pixels were changed.
        image = bpy.data.images[image_name]
        image.pack()

        # 3. Add the new image to the selected mask (for all material channels).
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        masks = context.scene.matlay_masks

        for material_channel_name in material_channels.get_material_channel_list():
            mask_texture_node = get_mask_node('MaskTexture',  material_channel_name, selected_material_layer_index, selected_mask_index)
            if mask_texture_node:
                masks[selected_mask_index].mask_image = bpy.data.images[image_name]

                # Select the new image so it can be edited.
                context.scene.tool_settings.image_paint.canvas = mask_texture_node.image

        return {'FINISHED'}

class MATLAY_OT_delete_mask_image(Operator):
    '''Deletes the mask image from Blender's data.'''
    bl_idname = "matlay.delete_mask_image"
    bl_label = "Delete Mask Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the mask image from Blender's data."

    def execute(self, context):
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        mask_texture_node  = get_mask_node('MaskTexture', 'COLOR', selected_material_layer_index, selected_mask_index)
        if mask_texture_node:
            if mask_texture_node.image != None:
                bpy.data.images.remove(mask_texture_node.image)
        return {'FINISHED'}

class MATLAY_OT_import_mask_image(Operator, ImportHelper):
    '''Opens a new window from which a user can import an image that will be inserted into the selected mask texture slot.'''
    bl_idname = "matlay.import_mask_image"
    bl_label = "Import Mask Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Opens a new window from which a user can import an image that will be inserted into the selected mask texture slot"

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # 1. Open a window to allow the user to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]
        bpy.ops.image.open(filepath=self.filepath)

        # 2. Put the imported mask into the selected mask texture slot (for all material channels).
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        for material_channel_name in material_channels.get_material_channel_list():
            mask_texture_node = get_mask_node('MaskTexture',  material_channel_name, selected_material_layer_index, selected_mask_index)
            if mask_texture_node:
                image = bpy.data.images.get(image_name)
                if image:
                    mask_texture_node.image = image

        # 3. Set the mask colorspace to non-color data.
        image.colorspace_settings.name = 'Non-Color'

        return {'FINISHED'}

#----------------------------- MASK FILTERS -----------------------------#

# Mask filter names are all the same (this makes them a bit easier to access in some cases).
MASK_FILTER_NAME = "MaskFilter"

def format_mask_filter_node_name(material_layer_index, mask_index, mask_filter_index, get_edited=False):
    '''All node names including mask node names must be formatted properly so they can be read from the material node tree. This function should be used to properly format the name of a mask filter node. Get edited will return the name of a mask filter node with a tilda at the end, signifying that the node is actively being changed.'''
    if get_edited:
        return  "{0}_{1}_{2}_{3}~".format(MASK_FILTER_NAME, str(material_layer_index), str(mask_index), str(mask_filter_index))
    else:
        return  "{0}_{1}_{2}_{3}".format(MASK_FILTER_NAME, str(material_layer_index), str(mask_index), str(mask_filter_index))

def get_mask_filter_node(material_channel_name, material_layer_index, mask_index, mask_filter_index, get_edited=False):
    '''Returns the mask filter node for the given material layer index at the filter index by reading through existing nodes within the specified material channel.'''
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        node_name = format_mask_filter_node_name(material_layer_index, mask_index, mask_filter_index, get_edited)
        return material_channel_node.node_tree.nodes.get(node_name)

def get_all_mask_filter_nodes(material_channel_name, material_layer_index, mask_index, get_edited=False):
    '''Returns all mask filter nodes belonging to the mask at the provided mask index.'''
    nodes = []
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for i in range(0, MAX_MASK_FILTERS):
            node_name = format_mask_filter_node_name(material_layer_index, mask_index, i, get_edited)
            node = material_channel_node.node_tree.nodes.get(node_name)
            if node:
                nodes.append(node)
    return nodes

def get_all_mask_filter_nodes_in_layer(material_channel_name, material_layer_index, get_edited=False):
    '''Returns an array of all mask filter nodes within the given material index.'''
    nodes = []
    for i in range(0, len(bpy.context.scene.matlay_masks)):
        mask_filter_nodes = get_all_mask_filter_nodes(material_channel_name, material_layer_index, i, get_edited)
        for node in mask_filter_nodes:
            nodes.append(node)
    return nodes

def reindex_mask_filters_nodes():
    '''Reindexes mask filters by renaming nodes based added, edited, or deleted nodes.'''
    selected_material_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
    mask_filters = bpy.context.scene.matlay_mask_filters

    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

        changed_filter_index = -1
        filter_added = False
        filter_deleted = False

        # 1. Update the mask filter indicies first.
        number_of_filters = len(mask_filters)
        for i in range(0, number_of_filters):
            mask_filters[i].stack_index = i

        # 2. Check for a newly added mask filter (signified by a tilda at the end of the node's name).
        for i in range(0, len(mask_filters)):
            temp_node_name = format_mask_filter_node_name(selected_material_index, selected_mask_index, i) + "~"
            temp_node = material_channel_node.node_tree.nodes.get(temp_node_name)
            if temp_node:
                filter_added = True
                changed_filter_index = i
                break

        # 3. Check for a deleted filter.
        if not filter_added:
            for i in range(0, len(mask_filters)):
                temp_node_name = format_mask_filter_node_name(selected_material_index, selected_mask_index, i)
                temp_node = material_channel_node.node_tree.nodes.get(temp_node_name)
                if not temp_node:
                    filter_deleted = True
                    changed_filter_index = i
                    break

        # 4. Rename filter nodes above the newly added mask filter on the stack if any exist (in reverse order to avoid naming conflicts).
        if filter_added:
            for i in range(len(mask_filters), changed_filter_index + 1, -1):
                index = i - 1
                node_name = format_mask_filter_node_name(selected_material_index, selected_mask_index, index - 1)
                node = material_channel_node.node_tree.nodes.get(node_name)

                if node:
                    node.name = format_mask_filter_node_name(selected_material_index, selected_mask_index, index)
                    node.label = node.name
                    mask_filters[index].stack_index = index

            # Remove the tilda from the newly added mask filter.
            new_node_name = format_mask_filter_node_name(selected_material_index, selected_mask_index, changed_filter_index) + "~"
            new_node = material_channel_node.node_tree.nodes.get(new_node_name)
            if new_node:
                new_node.name = new_node_name.replace('~', '')
                new_node.label = new_node.name
                mask_filters[changed_filter_index].stack_index = changed_filter_index

        # 5. Rename mask filter nodes above the deleted mask filter if any exist.
        if filter_deleted and len(mask_filters) > 0:
            for i in range(changed_filter_index + 1, len(mask_filters), 1):
                old_node_name = format_mask_filter_node_name(selected_material_index, selected_mask_index, i)
                old_node = material_channel_node.node_tree.nodes.get(old_node_name)

                if old_node:
                    old_node.name = format_mask_filter_node_name(selected_material_index, selected_mask_index, i - 1)
                    old_node.label = old_node.name
                    mask_filters[i].stack_index = i - 1
    
def relink_mask_filter_nodes():
    '''Relinks all mask filters.'''
    selected_material_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index

    for material_channel_name in material_channels.get_material_channel_list():
        mask_filter_nodes = get_all_mask_filter_nodes(material_channel_name, selected_material_index, selected_mask_index, False)
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

        for i in range(0, len(mask_filter_nodes)):
            mask_filter_node = mask_filter_nodes[i]

            next_filter_node = None
            if len(mask_filter_nodes) - 1 > i:

                # 1. Unlink all mask filter nodes.
                node_links = material_channel_node.node_tree.links
                for l in node_links:
                    if l.from_node.name == mask_filter_node.name:
                        node_links.remove(l)

                # 2. Link to the next mask mix node in the mask filter stack if it exists.
                next_filter_node = mask_filter_nodes[i + 1]
                if next_filter_node:
                    match next_filter_node.bl_static_type:
                        case 'INVERT':
                            material_channel_node.node_tree.links.new(mask_filter_node.outputs[0], next_filter_node.inputs[1])
                        case 'VALTORGB':
                            material_channel_node.node_tree.links.new(mask_filter_node.outputs[0], next_filter_node.inputs[0])

        # 3. Connect the mask texture to the first mask filter.
        first_mask_filter_node = get_mask_filter_node(material_channel_name, selected_material_index, selected_mask_index, 0)
        mask_texture_node = get_mask_node('MaskTexture', material_channel_name, selected_material_index, selected_mask_index, False)
        if mask_texture_node and first_mask_filter_node:
            match first_mask_filter_node.bl_static_type:
                case 'INVERT':
                    material_channel_node.node_tree.links.new(mask_texture_node.outputs[0], first_mask_filter_node.inputs[1])
                case 'VALTORGB':
                    material_channel_node.node_tree.links.new(mask_texture_node.outputs[0], first_mask_filter_node.inputs[0])

def refresh_mask_filter_stack(context):
    '''Reads the material node tree to rebuild the mask filter stack in the ui.'''
    mask_filters = context.scene.matlay_mask_filters
    mask_filter_stack = context.scene.matlay_mask_filter_stack
    selected_material_index = context.scene.matlay_layer_stack.layer_index
    selected_material_channel = 'COLOR'
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index

    # When reading from the material node tree, we don't want properties to auto-update as doing so can cause errors.
    context.scene.matlay_mask_filter_stack.auto_update_properties = False

    # Cache the selected filter index, we'll reset the selected filter index to the closest index after refreshing.
    previously_selected_filter_index = mask_filter_stack.selected_mask_filter_index

    # Clear all mask filters.
    mask_filters.clear()

    # Read the material nodes and re-add mask filters to the stack.
    mask_filter_nodes = get_all_mask_filter_nodes(selected_material_channel, selected_material_index, selected_mask_index, False)
    for x in range(0, len(mask_filter_nodes)):
        mask_filters.add()
        mask_filters[x].stack_index = x

    # Reset the selected mask filter index.
    if len(mask_filters) > 0 and previously_selected_filter_index < len(mask_filters) - 1 and previously_selected_filter_index >= 0:
        mask_filter_stack.selected_mask_filter_index = previously_selected_filter_index
    else:
        mask_filter_stack.selected_mask_filter_index = 0

    # Allow auto updating for properties again.
    context.scene.matlay_mask_filter_stack.auto_update_properties = True

def add_mask_filter(filter_type, context):
    '''Adds a new filter to the selected layer mask. Valid mask filter types include: 'ShaderNodeInvert', 'ShaderNodeValToRGB' '''
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    mask_filters = context.scene.matlay_mask_filters
    mask_filter_stack = context.scene.matlay_mask_filter_stack
    selected_mask_filter_index = context.scene.matlay_mask_filter_stack.selected_mask_filter_index

    # Stop users from adding too many mask filters.
    if len(mask_filters) >= MAX_MASK_FILTERS:
        info_messages.popup_message_box("You can't have more than {0} filters on a single layer. This is a safeguard to stop users from adding an unnecessary amount of filters, which will impact performance.".format(MAX_MASK_FILTERS), 'User Error', 'ERROR')
        return

    # Add a new mask filter slot, name and select it.
    mask_filters.add()

    if selected_mask_filter_index < 0:
        move_index = len(mask_filters) - 1
        move_to_index = 0
        mask_filters.move(move_index, move_to_index)
        mask_filter_stack.selected_mask_filter_index = move_to_index
        selected_mask_filter_index = len(mask_filters) - 1
    
    else:
        move_index = len(mask_filters) - 1
        move_to_index = max(0, min(selected_mask_filter_index + 1, len(mask_filters) - 1))
        mask_filters.move(move_index, move_to_index)
        mask_filter_stack.selected_filter_index = move_to_index
        selected_mask_filter_index = max(0, min(selected_mask_filter_index + 1, len(mask_filters) - 1))

    # Create a new mask filter node (in all material channels).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
            new_node = material_channel_node.node_tree.nodes.new(filter_type)
            new_node.name = format_mask_filter_node_name(selected_layer_index, selected_mask_index, selected_mask_filter_index) + "~"
            new_node.label = new_node.name

            # Add the new nodes to the layer frame.
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
            if frame:
                new_node.parent = frame

    # Re-index then relink nodes.
    reindex_mask_filters_nodes()
    relink_mask_filter_nodes()

    # Re-organize nodes.
    layer_nodes.update_layer_nodes(context)

def move_mask_filter(direction, context):
    '''Moves the mask filter up or down on the mask filter stack.'''
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
    selected_mask_filter_index = context.scene.matlay_mask_filter_stack.selected_mask_filter_index
    mask_filters = context.scene.matlay_mask_filters
    mask_filter_stack = context.scene.matlay_mask_filter_stack

    mask_filter_stack.auto_update_properties = False

    # Don't move the mask if the user is trying to move the slot out of range.
    if direction == 'UP' and selected_mask_filter_index + 1 > len(mask_filters) - 1:
        return
    if direction == 'DOWN' and selected_mask_filter_index - 1 < 0:
        return
    
    # Get the layer index over or under the selected layer, depending on the direction the layer is being moved.
    if direction == 'UP':
        moving_to_index = max(min(selected_mask_filter_index + 1, len(mask_filters) - 1), 0)
    else:
        moving_to_index = max(min(selected_mask_filter_index - 1, len(mask_filters) - 1), 0)

    # 1. Add a tilda to the end of all the mask nodes to signify they are being edited (and to avoid naming conflicts).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        node = get_mask_filter_node(material_channel_name, selected_material_layer_index, selected_mask_index, selected_mask_filter_index, False)
        if node:
            node.name = node.name + "~"
            node.label = node.name

    # 2. Update the mask node names for the layer below or above the selected index.
    for material_channel_name in material_channel_list:
        node = get_mask_filter_node(material_channel_name, selected_material_layer_index, selected_mask_index, moving_to_index)
        if node:
            node.name = format_mask_filter_node_name(selected_material_layer_index, selected_mask_index, selected_mask_filter_index, False)
            node.label = node.name

    # 3. Remove the tilda from the end of the mask node names that were edited and re-index them.
    for material_channel_name in material_channel_list:
        node = get_mask_filter_node(material_channel_name, selected_material_layer_index, selected_mask_index, selected_mask_filter_index, True)
        if node:
            node.name = format_mask_filter_node_name(selected_material_layer_index, selected_mask_index, moving_to_index)
            node.label = node.name

    # 4. Move the selected mask on the ui stack.
    if direction == 'UP':
        index_to_move_to = max(min(selected_mask_filter_index + 1, len(mask_filters) - 1), 0)
    else:
        index_to_move_to = max(min(selected_mask_filter_index - 1, len(mask_filters) - 1), 0)
    mask_filters.move(selected_mask_filter_index, index_to_move_to)
    context.scene.matlay_mask_filter_stack.selected_mask_filter_index = index_to_move_to   

    # 5. Re-link and organize mask filter nodes.
    layer_nodes.update_layer_nodes(context)

    mask_filter_stack.auto_update_properties = True

class MATLAY_mask_filter_stack(PropertyGroup):
    '''Properties for the mask stack.'''
    selected_mask_filter_index: IntProperty(default=-1)
    auto_update_properties: BoolProperty(default=True, description="If auto update properties is on, when select mask filter property changes will trigger automatic updates.")

class MATLAY_mask_filters(PropertyGroup):
    stack_index: IntProperty(name="Stack Index", description = "The (array) stack index for this filter used to define the order in which filters should be applied to the material", default=-999)

class MATLAY_UL_mask_filter_stack(UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Draw the filter name based on the filters node type.
            material_layer_index = context.scene.matlay_layer_stack.layer_index
            selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
            mask_filter_node = get_mask_filter_node('COLOR', material_layer_index, selected_mask_index, item.stack_index, False)
            filter_node_name = ""
            if mask_filter_node:
                match mask_filter_node.bl_static_type:
                    case 'INVERT':
                        filter_node_name = "Invert"
                    case 'VALTORGB':
                        filter_node_name = "Levels"
            layout.label(text=filter_node_name + " " + str(item.stack_index))

class MATLAY_OT_add_mask_filter_invert(Operator):
    '''Adds an invert adjustment to the masks applied to the selected layer'''
    bl_idname = "matlay.add_mask_filter_invert"
    bl_label = "Add Invert Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an invert adjustment to the masks applied to the selected layer"

    def execute(self, context):
        add_mask_filter('ShaderNodeInvert', context)
        return {'FINISHED'}

class MATLAY_OT_add_mask_filter_levels(Operator):
    '''Adds a level adjustment to the masks applied to the selected layer'''
    bl_idname = "matlay.add_mask_filter_levels"
    bl_label = "Add Levels Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a level adjustment to the masks applied to the selected layer"

    def execute(self, context):
        add_mask_filter('ShaderNodeValToRGB', context)
        return {'FINISHED'}

class MATLAY_OT_add_layer_mask_filter_menu(Operator):
    '''Opens a menu of filters that can be added to the selected mask.'''
    bl_label = ""
    bl_idname = "matlay.add_layer_mask_filter_menu"
    bl_description = "Opens a menu of layer filters that can be added to the selected mask stack"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlay.add_mask_filter_invert")
        col.operator("matlay.add_mask_filter_levels")

class MATLAY_OT_delete_mask_filter(Operator):
    bl_idname = "matlay.delete_mask_filter"
    bl_label = "Delete Mask Filter"
    bl_description = "Deletes the mask filter"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        selected_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        mask_filters = context.scene.matlay_mask_filters
        selected_mask_filter_index = context.scene.matlay_mask_filter_stack.selected_mask_filter_index

        # 1. Delete the mask filter nodes in all material channels.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            node = get_mask_filter_node(material_channel_name, selected_layer_index, selected_mask_index, selected_mask_filter_index)
            if node:
                material_channel_node.node_tree.nodes.remove(node)

        # 2. Re-index and re-link mask filter nodes.
        reindex_mask_filters_nodes()
        relink_mask_filter_nodes()

        # 3. Remove the selected mask filter slot.
        mask_filters.remove(selected_mask_filter_index)

        # 4. Reset the selected mask filter index.
        context.scene.matlay_mask_filter_stack.selected_mask_filter_index = max(min(selected_mask_filter_index - 1, len(mask_filters) - 1), 0)

        # 5. Re-organize nodes.
        layer_nodes.update_layer_nodes(context)

        return{'FINISHED'}
    
class MATLAY_OT_move_layer_mask_filter(Operator):
    '''Moves the selected layer mask filter on the layer stack'''
    bl_idname = "matlay.move_layer_mask_filter"
    bl_label = "Move Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer mask filter on the layer stack"

    direction: StringProperty(default="True")

    def execute(self, context):
        if self.direction == 'UP':
            move_mask_filter('UP', context)
        else:
            move_mask_filter('DOWN', context)
        return {'FINISHED'}