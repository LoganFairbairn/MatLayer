# This module provides functions to access layer nodes make with this add-on.

import bpy
from ..nodes import material_channel_nodes

# Set of node names.
LAYER_NODE_NAMES = ("TEXTURE", "OPACITY", "COORD", "MAPPING", "MIXLAYER")

def get_layer_node_names():
    '''Returns a list of all layer node names.'''
    return LAYER_NODE_NAMES

def get_layer_frame(material_channel_node, layers, layer_index):
    '''Returns the layer frame if one exists.'''
    return material_channel_node.node_tree.nodes.get(layers[layer_index].frame_name)

def get_layer_node(node_name, material_channel, layer_index, context):
    '''Returns the desired layer node.'''

    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    if not material_channel_node:
        print("Error: Missing material channel node when trying to get a layer node.")
        return

    if node_name in LAYER_NODE_NAMES:
        layers = context.scene.coater_layers

        if node_name == "TEXTURE":
            return material_channel_node.node_tree.nodes.get(layers[layer_index].texture_node_name)

        if node_name == "OPACITY":
            return material_channel_node.node_tree.nodes.get(layers[layer_index].opacity_node_name)

        if node_name == "COORD":
            return material_channel_node.node_tree.nodes.get(layers[layer_index].coord_node_name)

        if node_name == "MAPPING":
            return material_channel_node.node_tree.nodes.get(layers[layer_index].mapping_node_name)

        if node_name == "MIXLAYER":
            return material_channel_node.node_tree.nodes.get(layers[layer_index].mix_layer_node_name)
    else:
        print("ERROR: Layer node name not found in layer node list.")

def get_all_layer_nodes(material_channel_node, layers, layer_index):
    '''Returns a list of all layer nodes that belong to the specified layer within the specified material channel.'''
    nodes = []

    texture_node = material_channel_node.node_tree.nodes.get(layers[layer_index].texture_node_name)
    if texture_node:
        nodes.append(texture_node)

    opacity_node = material_channel_node.node_tree.nodes.get(layers[layer_index].opacity_node_name)
    if opacity_node:
        nodes.append(opacity_node)

    coord_node = material_channel_node.node_tree.nodes.get(layers[layer_index].coord_node_name)
    if coord_node:
        nodes.append(coord_node)

    mapping_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mapping_node_name)
    if mapping_node:
        nodes.append(mapping_node)

    mix_layer_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mix_layer_node_name)
    if mix_layer_node:
        nodes.append(mix_layer_node)

    return nodes