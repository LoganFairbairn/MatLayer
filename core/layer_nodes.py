# This module provides functions to edit layer material nodes created with this add-on.

import bpy
from . import material_channels
from ..core import layer_filters

# Node organization settings.
NODE_WIDTH = 300
NODE_SPACING = 50

# Set of node names.
LAYER_NODE_NAMES = ("TEXTURE", "OPACITY", "COORD", "MAPPING", "MIXLAYER")

#----------------------------- LAYER NODE FUNCTIONS -----------------------------#

def get_layer_node_names():
    '''Returns a list of all layer node names.'''
    return LAYER_NODE_NAMES

def get_layer_node_name(node_name, layer_stack_index):
    return node_name + "_" + str(layer_stack_index)

def rename_layer_node(node, node_name, layer_stack_index):
    '''Renames both the node name and the node's label to the new node name.'''
    if node:
        node.name = node_name + "_" + str(layer_stack_index)
        node.label = node.name

    else:
        print("Unable to rename " + node_name + " layer node isn't valid.")

def get_layer_node(node_name, material_channel_name, layer_index, context):
    '''Gets a specific layer node using a given name.'''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    if material_channel_node:
        if node_name in LAYER_NODE_NAMES:
            return material_channel_node.node_tree.nodes.get(node_name + "_" + str(layer_index))
        else:
            print("ERROR: Layer node name not found in layer node list. Do you have a typo in a layer node name somewhere in your code?")

def get_layer_node_from_name(node_name, material_channel, context):
    '''Gets the desired layer node using it's name.'''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel)
    node = material_channel_node.node_tree.nodes.get(node_name)

    if node:
        return node

    else:
        print("Error: Failed to get: " + node_name)

def get_all_nodes_in_layer(material_channel_name, layer_index, context):
    '''Returns a list of all layer nodes that belong to the specified layer within the specified material channel.'''
    nodes = []

    for node_name in LAYER_NODE_NAMES:
        node = get_layer_node(node_name, material_channel_name, layer_index, context)
        if not node:
            print("Error: Missing " + node_name + " from " + material_channel_name + ".")
        nodes.append(node)

    return nodes

def get_total_number_of_layers(context):
    '''Reads the material node tree and returns the total number of layers. This function won't work if the layer nodes don't follow the standard format of this add-on.'''
    layer_index = 0
    found_last_index = False

    while found_last_index == False:
        node = get_layer_node('TEXTURE', "COLOR", layer_index, context)
        if node:
            layer_index += 1
        else:
            found_last_index = True
            return layer_index



#----------------------------- LAYER FRAME FUNCTIONS -----------------------------#

# TODO: Replace 'layers' argument with context.
def get_layer_frame_name(layers, layer_stack_index):
    '''Gets the frame name for the given layer stack index.'''
    return layers[layer_stack_index].name + "_" + str(layers[layer_stack_index].id) + "_" + str(layer_stack_index)

def get_frame_name(layer_stack_array_index, context):
    '''Returns the frame name.'''
    layers = context.scene.matlay_layers
    return layers[layer_stack_array_index].name + "_" + str(layers[layer_stack_array_index].id) + "_" + str(layer_stack_array_index)

def get_layer_frame(material_channel_name, layer_stack_index, context):
    '''Returns the frame node for the given layer. This function requires the layer id to be stored in the layer stack.'''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

    if material_channel_node:
        layers = context.scene.matlay_layers
        layer_frame_name = get_layer_frame_name(layers, layer_stack_index)
        return material_channel_node.node_tree.nodes.get(layer_frame_name)

    else:
        print("Error: Failed to get layer frame, material channel node is invalid.")
        return None

def get_layer_frame_id(e):
    '''Returns the layer frame id from the layer frame name / label.'''
    if e:
        layer_frame_info = e.label.split('_')
        return layer_frame_info[2]
    else:
        print("Error: Layer frame invalid when attempting to read the layer frame id.")

def get_layer_frame_nodes(context):
    '''Returns all layer frame nodes in order by reading the material tree of the color group channel node.'''
    layer_frame_nodes = []
    material_channel_node = material_channels.get_material_channel_node(context, 'COLOR')
    for node in material_channel_node.node_tree.nodes:
        if node.type == 'FRAME':
            layer_frame_nodes.append(node)

    # Organize the layer frames in the array by their layer stack index.
    layer_frame_nodes.sort(key=get_layer_frame_id)
    return layer_frame_nodes

#----------------------------- LAYER MASK FUNCTIONS -----------------------------#

def get_all_layer_mask_nodes(layer_stack_index, material_channel_name, context):
    '''Gets all the mask nodes for a given layer.'''
    mask_nodes = []

    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    for i in range(0, 20):
        mask_node = material_channel_node.node_tree.nodes.get("MASK_" + str(layer_stack_index) + "_" + str(i + 1))
        if mask_node:
            mask_nodes.append()
        else:
            break

    return mask_nodes


#----------------------------- LAYER MUTING FUNCTIONS -----------------------------#

def mute_layer_material_channel(mute, layer_stack_index, material_channel_name, context):
    '''Mutes (hides) or unhides all layer nodes for a specific material channel.'''
    for node_name in LAYER_NODE_NAMES:
        node = get_layer_node(node_name, material_channel_name, layer_stack_index, context)
        if node:
            node.mute = mute


#----------------------------- NODE ORGANIZATION FUNCTIONS -----------------------------#

def organize_material_channel_nodes(context):
    '''Organizes material channel nodes.'''
    active_material_channel_nodes = material_channels.get_all_material_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in active_material_channel_nodes:
        if node != None:
            node.location = (-node.width + -NODE_SPACING, header_position[1])
            header_position[1] -= (node.height + (NODE_SPACING * 0.5))

def organize_layer_nodes_in_material_channel(material_channel_name, context):
    '''Organizes all nodes in a specified material channel.'''
    layers = context.scene.matlay_layers
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

    # Organize the output node.
    group_output_node = material_channel_node.node_tree.nodes.get('Group Output')
    if group_output_node:
        group_output_node.location = (0.0, 0.0)

    # Organize the normal map node.
    if material_channel_name == 'NORMAL':
        normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
        normal_map_node.location = (0.0, -100.0)

    # Organize the bump node.
    if material_channel_name == 'HEIGHT':
        bump_node = material_channel_node.node_tree.nodes.get("Bump")
        bump_node.location = (0.0, -100.0)

    # Organizes all other layer nodes.
    header_position = [0.0, 0.0]
    for i in range(len(layers), 0, -1):
        index = i - 1
        header_position[0] -= NODE_WIDTH + NODE_SPACING
        header_position[1] = 0.0

        # IMPORTANT: The nodes won't move when they are framed, delete the layer's frame and re-add it after organization.
        frame = get_layer_frame(material_channel_name, index, context)
        if frame:
            frame_name = frame.name
            material_channel_node.node_tree.nodes.remove(frame)    

        # Create a list of all nodes in the layer and then organize them.
        node_list = get_all_nodes_in_layer(material_channel_name, index, context)
        mask_nodes = get_all_layer_mask_nodes(index, material_channel_name, context)
        for mask_node in mask_nodes:
            node_list.append(mask_node)

        filter_nodes = layer_filters.get_all_layer_filter_nodes(index, material_channel_name, context)
        for filter_node in filter_nodes:
            node_list.append(filter_node)

        for node in node_list:
            node.width = NODE_WIDTH
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + NODE_SPACING

        # Re-frame the layers.
        frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
        frame.name = frame_name
        frame.label = frame.name
        layers[index].frame_name = frame.name

        # Re-frame all the layer nodes.
        for node in node_list:
            node.parent = frame

        # Add spacing between layers.
        header_position[0] -= NODE_SPACING

def organize_all_matlay_materials(context):
    '''Organizes both material channel group nodes and layer nodes within those material channel group nodes.'''
    organize_material_channel_nodes(context)
    material_channel_names = material_channels.get_material_channel_list()
    for material_channel in material_channel_names:
        organize_layer_nodes_in_material_channel(material_channel, context)


#----------------------------- NODE LINKING FUNCTIONS -----------------------------#

def link_layers_in_material_channel(material_channel, context):
    '''Links all layers in the given material channel together by linking the mix layer and mix mask nodes together.'''
    layers = context.scene.matlay_layers
    material_channel_node = material_channels.get_material_channel_node(context, material_channel)

    # Remove all existing output links for mix layer or mix mask nodes.
    for x in range(len(layers) - 1):
        mix_layer_node = get_layer_node("MIXLAYER", material_channel, x, context)
        if mix_layer_node != None:
            output = mix_layer_node.outputs[0]
            for l in output.links:
                if l != 0:
                    material_channel_node.node_tree.links.remove(l)
    
    # TODO: Prioritize linking FILTERS and MASKS.
    # Connect mix layer nodes for every layer.
    for i in range(0, len(layers)):
        current_layer_index = i
        next_layer_index = i + 1

        current_mix_layer_node = get_layer_node("MIXLAYER", material_channel, current_layer_index, context)
        next_mix_layer_node = get_layer_node("MIXLAYER", material_channel, next_layer_index, context)

        # Link layers.
        if next_mix_layer_node:
            material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])
        
        # Link to material channel output.
        else:
            if material_channel == "HEIGHT":
                bump_node = material_channel_node.node_tree.nodes.get("Bump")
                material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], bump_node.inputs[2])

            elif material_channel == "NORMAL":
                normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
                material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], normal_map_node.inputs[1])

            else:
                group_output_node = material_channel_node.node_tree.nodes.get("Group Output")
                material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], group_output_node.inputs[0])


#----------------------------- LAYER UPDATING FUNCTIONS -----------------------------#

def update_layer_nodes(context):
    '''Organizes all nodes in all material channels for every layer and links them all nodes together. This should be called after adding or removing layer nodes.'''

    # Organize all material channel group nodes.
    organize_material_channel_nodes(context)

    # Update all layer organize and link all layer nodes.
    material_channel_names = material_channels.get_material_channel_list()
    for material_channel in material_channel_names:

        # Update all layer node indicies.
        update_layer_indicies(context)
        update_layer_node_indicies(material_channel, context)

        # Organize all layer nodes.
        organize_layer_nodes_in_material_channel(material_channel, context)

        # Link all layers.
        link_layers_in_material_channel(material_channel, context)

def update_layer_indicies(context):
    '''Matches layer stack indicies stored in each layer to the layer stack array indicies (layer stack indicies are stored in the layers for convenience and debugging purposes).'''
    layers = context.scene.matlay_layers
    number_of_layers = len(layers)
    for i in range(0, number_of_layers):
        layers[i].layer_stack_array_index = i

def update_layer_node_indicies(material_channel_name, context):
    '''Updates the layer stack indicies stored in material (layer) nodes.'''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    changed_layer_index = -1

    layers = context.scene.matlay_layers
    layer_node_names = get_layer_node_names()

    node_added = False
    node_deleted = False

    # 1. Check for a newly added layer (signified by a tilda at the end of the node's name).
    for i in range(0, len(layers)):
        temp_node_name = get_layer_node_name("TEXTURE", i) + "~"
        node = material_channel_node.node_tree.nodes.get(temp_node_name)

        if node:
            node_added = True
            changed_layer_index = i
            break


    # 2. Check for a deleted layer (if there isn't a newly added layer).
    if not node_added:
        for i in range(0, len(layers)):
            frame = get_layer_frame(material_channel_name, i, context)

            if not frame:
                node_deleted = True
                changed_layer_index = i
                break


    # 3. Rename the all layer nodes starting with the changed layer and remove the tilda from the newly added layer.
    if node_added:
        for i in range(len(layers), changed_layer_index + 1, -1):
            index = i - 1
            frame = material_channel_node.node_tree.nodes.get(layers[index].name + "_" + str(layers[index].id) + "_" + str(index - 1))

            frame.name = layers[index].name + "_" + str(layers[index].id) + "_" + str(index)
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = get_layer_node(node_name, material_channel_name, index - 1, context)
                rename_layer_node(node, node_name, index)

        # Remove the tilda from the new frame.
        temp_frame_name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index) + "~"
        frame = material_channel_node.node_tree.nodes.get(temp_frame_name)
        frame.name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index)
        frame.label = frame.name

        # Update the cached layer frame name (used for accessing nodes if their name changes).
        layers[changed_layer_index].cached_frame_name = frame.name

        # Remove the tilda from the new nodes.
        for node_name in layer_node_names:
            temp_node_name = get_layer_node_name(node_name, changed_layer_index) + "~"
            node = material_channel_node.node_tree.nodes.get(temp_node_name)
            rename_layer_node(node, node_name, changed_layer_index)


    # 4. Rename filter nodes past the deleted layer if they exist.
    if node_deleted and len(layers) > 0:
        for i in range(changed_layer_index, len(layers), 1):
            index = i + 1

            old_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index - 1)
            frame.name = new_frame_name
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[changed_layer_index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = get_layer_node(node_name, material_channel_name, index, context)
                rename_layer_node(node, node_name, index - 1)