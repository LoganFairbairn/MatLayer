# This module provides functions to access layer nodes make with this add-on.

import bpy
from ..nodes import material_channel_nodes

# Set of node names.
LAYER_NODE_NAMES = ("TEXTURE", "OPACITY", "COORD", "MAPPING", "MIXLAYER")

def get_layer_node_names():
    '''Returns a list of all layer node names.'''
    return LAYER_NODE_NAMES

def get_layer_node(node_name, material_channel, layer_index, context):
    '''Finds the desired layer node using it's name and returns it.'''

    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

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

def get_layer_node_from_name(node_name, material_channel, context):
    '''Gets the desired layer node using it's name.'''

    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    node = material_channel_node.node_tree.nodes.get(node_name)

    if node:
        return node

    else:
        print("Error: Failed to get layer node from name.")

def get_all_nodes_in_layer(material_channel_node, layers, layer_index):
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

# TODO: This should take a material channel and a layer index only, sub layers for context.
def get_layer_frame(material_channel_node, layers, layer_index):
    '''Returns the layer frame if one exists.'''
    if material_channel_node:
        return material_channel_node.node_tree.nodes.get(layers[layer_index].frame_name)

    else:
        print("Error: Failed to get layer frame.")
        return None

def rename_layer_frame(name, layer_index, context):
    '''Renames the layer frame in all material channels.'''
    material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")
    layers = context.scene.coater_layers
    layer_frame = get_layer_frame(material_channel_node, layers, layer_index)

    # Set the new frame name.
    new_name = name + "_" + str(layers[layer_index].id) + "_" + str(layer_index)

    # Rename the layers name & label.
    layer_frame.name = new_name
    layer_frame.label = layer_frame.name

    # Store the frames name in the layer.
    layers[layer_index].frame_name = layer_frame.name

    #material_channel_list = material_channel_nodes.get_material_channel_list()

    #for material_channel in material_channel_list:
    #    material_channel_nodes.get_material_channel_node(context)
    #    get_layer_frame()

def mute_layer(mute, layer_index, context):
    '''Mutes (hides) all nodes in all material channels.'''
    layers = context.scene.coater_layers
    material_channels = material_channel_nodes.get_material_channel_list()
    for material_channel in material_channels:
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

        nodes = get_all_nodes_in_layer(material_channel_node, layers, layer_index)

        for n in nodes:
            n.mute = mute

def mute_material_channel(mute, material_channel, context):
    '''Mutes (hides) or unmutes all nodes in all layers in the specified material channel.'''
    layers = context.scene.coater_layers
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    for i in range(0, len(layers)):
        nodes = get_all_nodes_in_layer(material_channel_node, layers, i)

        for n in nodes:
            n.mute = mute