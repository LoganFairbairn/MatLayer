# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This folder handles getting specific layer information, generally layer nodes.

import bpy


def get_channel_nodes(context):
    # Returns a list of all channel nodes that exist.
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes

    base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
    metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
    roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
    height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")
    emission_group = material_nodes.get(active_material.name + "_" + "EMISSION")

    group_nodes = []
    if base_color_group != None:
        group_nodes.append(base_color_group)
        
    if metallic_group != None:
        group_nodes.append(metallic_group)

    if roughness_group != None:
        group_nodes.append(roughness_group)

    if height_group != None:
        group_nodes.append(height_group)

    if emission_group != None:
        group_nodes.append(emission_group)

    return group_nodes

def get_channel_node_group(context):
    # Returns the active channel node group.
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    if active_material != None:
        group_node_name = active_material.name + "_" + str(layer_stack.channel)
        node_group = bpy.data.node_groups.get(group_node_name)
        return node_group
    
    else:
        return None

def get_channel_node(context):
    # Returns the active channel node (Node that connects to Principled BSDF).
    active_material = context.active_object.active_material

    if active_material != None:
        material_nodes = context.active_object.active_material.node_tree.nodes
        layer_stack = context.scene.coater_layer_stack

        return material_nodes.get(active_material.name + "_" + str(layer_stack.channel))

    return None


def get_layer_nodes(context, layer_index):
    # Returns a list of all layer nodes that exist.
    node_group = get_channel_node_group(context)
    nodes = []

    # Color nodes.
    color_node = node_group.nodes.get("Color_" + str(layer_index))
    if color_node != None:
        nodes.append(color_node)

    coord_node_name = node_group.nodes.get("Coord_" + str(layer_index))
    if coord_node_name != None:
        nodes.append(coord_node_name)

    mapping_node = node_group.nodes.get("Mapping_" + str(layer_index))
    if mapping_node != None:
        nodes.append(mapping_node)

    opacity_node = node_group.nodes.get("Opacity_" + str(layer_index))
    if opacity_node != None:
        nodes.append(opacity_node)

    mix_node = node_group.nodes.get("MixLayer_" + str(layer_index))
    if mix_node != None:
        nodes.append(mix_node)

    # Mask Nodes
    mask_node = node_group.nodes.get("Mask_" + str(layer_index))
    if mask_node != None:
        nodes.append(mask_node)

    mask_coord_node = node_group.nodes.get("MaskCoords_" + str(layer_index))
    if mask_coord_node != None:
        nodes.append(mask_coord_node)

    mask_mapping_node = node_group.nodes.get("MaskMapping_" + str(layer_index))
    if mask_mapping_node != None:
        nodes.append(mask_mapping_node)

    mask_levels_node = node_group.nodes.get("MaskLevels_" + str(layer_index))
    if mask_levels_node != None:
        nodes.append(mask_levels_node)

    mask_mix_node = node_group.nodes.get("MaskMix_" + str(layer_index))
    if mask_mix_node != None:
        nodes.append(mask_mix_node)

    return nodes

def get_node(context, node_name, index):
    # Returns a specific coater node from a specific layer index. Returns None if it does not exist.
    layers = context.scene.coater_layers
    channel_node_group = get_channel_node_group(context)

    if channel_node_group != None and index > -1:
        if node_name == 'COLOR':
            return channel_node_group.nodes.get(layers[index].color_node_name)

        if node_name == 'OPACITY':
            return channel_node_group.nodes.get(layers[index].opacity_node_name)

        if node_name == 'MIX':
            return channel_node_group.nodes.get(layers[index].mix_layer_node_name)
        
        if node_name == 'MASK':
            return channel_node_group.nodes.get(layers[index].mask_node_name)

    else:
        return None

def get_layer_image(context, layer_index):
    # Returns a layer image from the given layer index, returns None if it does not exist.
    color_node = get_node(context, 'COLOR', layer_index)

    if color_node != None:
        if color_node.bl_static_type == 'TEX_IMAGE':
            return color_node.image
        else:
            return None
    else:
        return None

def get_layer_mask_image(context, layer_index):
    # Returns the image used as a mask for the selected layer if one exists.
    mask_node = get_node(context, 'MASK', layer_index)

    if mask_node != None:
        if mask_node.bl_static_type == 'TEX_IMAGE':
            return mask_node.image
        else:
            return None
    else:
        return None
