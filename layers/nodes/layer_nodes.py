# This module provides functions to edit layer nodes made with this add-on.

import bpy
from ..nodes import material_channel_nodes

# Node organization settings.
NODE_WIDTH = 300
NODE_SPACING = 50

# Set of node names.
LAYER_NODE_NAMES = ("TEXTURE", "OPACITY", "COORD", "MAPPING", "MIXLAYER")



''' LAYER NODE FUNCTIONS '''

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
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)

    if node_name in LAYER_NODE_NAMES:
        return material_channel_node.node_tree.nodes.get(node_name + "_" + str(layer_index))

    else:
        print("ERROR: Layer node name not found in layer node list.")

def get_layer_node_from_name(node_name, material_channel, context):
    '''Gets the desired layer node using it's name.'''
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
    node = material_channel_node.node_tree.nodes.get(node_name)

    if node:
        return node

    else:
        print("Error: Failed to get: " + node_name)

# Returns a list of all layer nodes that belong to the specified layer within the specified material channel.
def get_all_nodes_in_layer(material_channel_name, layer_index, context):
    nodes = []

    for node_name in LAYER_NODE_NAMES:
        node = get_layer_node(node_name, material_channel_name, layer_index, context)
        if not node:
            print("Error: Missing " + node_name + " from " + material_channel_name + ".")
        nodes.append(node)

    return nodes



''' LAYER FRAME '''

def get_layer_frame_name(layers, layer_stack_index):
    return layers[layer_stack_index].name + "_" + str(layers[layer_stack_index].id) + "_" + str(layer_stack_index)

# Returns the frame name.
def get_frame_name(layer_stack_array_index, context):
    layers = context.scene.coater_layers
    return layers[layer_stack_array_index].name + "_" + str(layers[layer_stack_array_index].id) + "_" + str(layer_stack_array_index)

# Returns the frame node for the given layer.
def get_layer_frame(material_channel_name, layer_stack_index, context):
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)

    if material_channel_node:
        layers = context.scene.coater_layers
        layer_frame_name = get_layer_frame_name(layers, layer_stack_index)
        return material_channel_node.node_tree.nodes.get(layer_frame_name)

    else:
        print("Error: Failed to get layer frame, material channel node is invalid.")
        return None

# Renames the given layer name.
def rename_layer_frame(frame, layer_stack_index, context):
    if frame:
        layers = context.scene.coater_layers
        frame.name = layers[layer_stack_index].name + "_" + str(layers[layer_stack_index].id) + "_" + str(layer_stack_index)
        frame.label = frame.name

    else:
        print("Unable to rename the given frame, frame is invalid.")

# Renames all layer node frame names in all material channels.
def rename_all_layer_frames(name, layer_index, context):
    '''Renames the layer frame in all material channels.'''
    layers = context.scene.coater_layers

    # Get the layer stack index for this layer (opposite value of the layer stack array index).
    # The layer stack index is added to the end of the layer frame name instead of the layer array index.
    layer_stack_index = layers[layer_index].layer_stack_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel in material_channel_list:
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
        layer_frame = get_layer_frame(material_channel_node, layers, layer_index)

        if layer_frame:
            new_name = name + "_" + str(layers[layer_index].id) + "_" + str(layer_stack_index)
            layer_frame.name = new_name
            layer_frame.label = layer_frame.name

    layers[layer_index].frame_name =  name + "_" + str(layers[layer_index].id) + "_" + str(layer_stack_index)



''' LAYER MUTING FUNCTIONS '''

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



''' LAYER UPDATING FUNCTIONS '''

def update_layer_nodes(context):
    '''Organizes all nodes in all material channels for every layer and links them all nodes together. This should be called after adding or removing layer nodes.'''

    # Organize all material channel group nodes.
    organize_material_channel_nodes(context)

    # Update all layer organize and link all layer nodes.
    material_channel_names = material_channel_nodes.get_material_channel_list()
    for material_channel in material_channel_names:

        # Update all layer node indicies.
        update_layer_indicies(context)
        update_layer_node_indicies(material_channel, context)

        # Organize all layer nodes.
        organize_layer_nodes_in_material_channel(material_channel, context)

        # Link all layers.
        #link_layers_in_material_channel(material_channel, context)

def update_layer_indicies(context):
    '''Matches layer stack indicies stored in each layer to the layer stack array indicies.'''
    # Layer stack indicies are stored in the layers for convenience and debugging purposes.
    layers = context.scene.coater_layers
    number_of_layers = len(layers)
    for i in range(0, number_of_layers):
        layers[i].layer_stack_array_index = i

def update_layer_node_indicies(material_channel_name, context):
    '''Updates the layer stack indicies stored in material (layer) nodes.'''
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
    changed_layer_index = -1

    layers = context.scene.coater_layers
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
        # Rename any layers past the selected layer index (in reverse to avoid duplicate node names).
        for i in range(len(layers), changed_layer_index + 1, -1):
            index = i - 1
            frame = material_channel_node.node_tree.nodes.get(layers[index].name + "_" + str(layers[index].id) + "_" + str(index - 1))

            frame.name = layers[index].name + "_" + str(layers[index].id) + "_" + str(index)
            frame.label = frame.name

            for node_name in layer_node_names:
                node = get_layer_node(node_name, material_channel_name, index - 1, context)
                rename_layer_node(node, node_name, index)

        # Remove the tilda from the new frame. ---- ERROR HERE LAYER FRAME WRONG ID
        temp_frame_name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index) + "~"
        frame = material_channel_node.node_tree.nodes.get(temp_frame_name)
        frame.name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index)
        frame.label = frame.name

        # Remove the tilda from the new nodes.
        for node_name in layer_node_names:
            temp_node_name = get_layer_node_name(node_name, changed_layer_index) + "~"
            node = material_channel_node.node_tree.nodes.get(temp_node_name)
            rename_layer_node(node, node_name, changed_layer_index)


        

    # Don't attempt to rename layer nodes if there are no more layers.
    if node_deleted and len(layers) > 0:
        for i in range(changed_layer_index, len(layers), 1):
            index = i + 1

            old_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index - 1)
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = get_layer_node(node_name, material_channel_name, index, context)
                rename_layer_node(node, node_name, index - 1)









''' NODE ORGANIZATION FUNCTIONS '''

def organize_material_channel_nodes(context):
    '''Organizes material channel nodes.'''
    active_material_channel_nodes = material_channel_nodes.get_all_material_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in active_material_channel_nodes:
        if node != None:
            node.location = (-node.width + -NODE_SPACING, header_position[1])
            header_position[1] -= (node.height + (NODE_SPACING * 0.5))

def organize_layer_nodes_in_material_channel(material_channel, context):
    '''Organizes all nodes in a specified material channel.'''
    layers = context.scene.coater_layers
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    # Organize the output node.
    group_output_node = material_channel_node.node_tree.nodes.get('Group Output')
    if group_output_node:
        group_output_node.location = (0.0, 0.0)

    # Organize the normal map node.
    if material_channel == 'NORMAL':
        normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
        normal_map_node.location = (0.0, -100.0)

    # Organize the bump node.
    if material_channel == 'HEIGHT':
        bump_node = material_channel_node.node_tree.nodes.get("Bump")
        bump_node.location = (0.0, -100.0)

    # Organizes all nodes (in reverse order).
    header_position = [0.0, 0.0]
    for i in range(len(layers), 0, -1):
        index = i - 1
        header_position[0] -= NODE_WIDTH + NODE_SPACING
        header_position[1] = 0.0

        # IMPORTANT: The nodes won't move when the frame is in place. Delete the layer's frame.
        frame = get_layer_frame(material_channel, index, context)
        if frame:
            frame_name = frame.name
            material_channel_node.node_tree.nodes.remove(frame)    

        # Organize the layer nodes.
        node_list = get_all_nodes_in_layer(material_channel, index, context)
        for node in node_list:
            node.width = NODE_WIDTH
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + NODE_SPACING

        # Re-frame the layers.
        frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
        frame.name = frame_name
        frame.label = frame.name
        layers[index].frame_name = frame.name

        # Frame all the nodes in the given layer in the newly created frame.
        nodes = get_all_nodes_in_layer(material_channel, index, context)
        for n in nodes:
            n.parent = frame

        # Add spacing between layers.
        header_position[0] -= NODE_SPACING



''' NODE LINKING FUNCTIONS '''

def link_layers_in_material_channel(material_channel, context):
    '''Links all layers in the given material channel together by linking the mix layer and mix mask nodes together.'''
    layers = context.scene.coater_layers
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    # Remove all existing output links for mix layer or mix mask nodes.
    for x in range(len(layers) - 1):
        mix_layer_node = get_layer_node("MIXLAYER", material_channel, x, context)
        if mix_layer_node != None:
            output = mix_layer_node.outputs[0]
            for l in output.links:
                if l != 0:
                    material_channel_node.node_tree.links.remove(l)

        mix_mask_node = material_channel_node.node_tree.nodes.get(layers[x].mask_mix_node_name)
        if mix_mask_node != None:
            output = mix_mask_node.outputs[0]
            for l in output.links:
                if l != 0:
                    material_channel_node.node_tree.links.remove(l)



# REWRITE THIS THERES AN ERROR HERE
def link_layers_in_material_channel_old(material_channel, context):
    '''Links all layers in the given material channel together by linking the mix layer and mix mask nodes together.'''
    layers = context.scene.coater_layers
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    # Remove all existing output links for mix layer or mix mask nodes.
    for x in range(len(layers) - 1):
        mix_layer_node = get_layer_node("MIXLAYER", material_channel, x, context)
        if mix_layer_node != None:
            output = mix_layer_node.outputs[0]
            for l in output.links:
                if l != 0:
                    material_channel_node.node_tree.links.remove(l)

        mix_mask_node = material_channel_node.node_tree.nodes.get(layers[x].mask_mix_node_name)
        if mix_mask_node != None:
            output = mix_mask_node.outputs[0]
            for l in output.links:
                if l != 0:
                    material_channel_node.node_tree.links.remove(l)


    # Connect mix layer nodes for every layer.
    for x in range(len(layers), 0, -1):
        current_layer_index = x - 1
        next_layer_index = x - 2

        # Only connect layers that are not hidden.
        if layers[current_layer_index].hidden == False:
            mix_layer_node = material_channel_node.node_tree.nodes.get(layers[current_layer_index].mix_layer_node_name)
            next_mix_layer_node = material_channel_node.node_tree.nodes.get(layers[next_layer_index].mix_layer_node_name)

            mix_mask_node = material_channel_node.node_tree.nodes.get(layers[current_layer_index].mask_mix_node_name)
            next_mix_mask_node = material_channel_node.node_tree.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # Skip hidden layers.
            while layers[next_layer_index].hidden == True:
                next_layer_index -= 1

                if next_layer_index < 0:
                    next_mix_layer_node = None
                    next_mix_mask_node = None
                    break

                else:
                    next_mix_layer_node = material_channel_node.node_tree.nodes.get(layers[next_layer_index].mix_layer_node_name)
                    next_mix_mask_node = material_channel_node.node_tree.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # If another layer above this layer exists, connect to the next mix layer or mix mask node (prioritize mask node connections).
            if next_layer_index >= 0:
                if mix_mask_node != None:
                    if next_mix_mask_node != None:
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])

                else:
                    if next_mix_mask_node != None:
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])

            # For the last layer, connect to the group output node.
            # For height and normal channels, connect to the bump / normal map node instead.
            else:
                group_output_node = material_channel_node.node_tree.nodes.get("Group Output")

                if mix_mask_node != None:
                    if material_channel == 'HEIGHT':
                        bump_node = material_channel_node.node_tree.nodes.get("Bump")
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], bump_node.inputs[2])

                    elif material_channel == 'NORMAL':
                        normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], normal_map_node.inputs[1])

                    else:
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], group_output_node.inputs[0])

                else:
                    if material_channel == 'HEIGHT':
                        bump_node = material_channel_node.node_tree.nodes.get("Bump")
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], bump_node.inputs[2])

                    elif material_channel == 'NORMAL':
                        normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], normal_map_node.inputs[1])

                    else:
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])      


# TODO: Fix this function.
def create_calculate_alpha_node(context):
    '''Creates a group node aimed used to calculate alpha blending properly between layers.'''
    layer_stack = context.scene.coater_layer_stack
    #channel_node = get_channel_node(context)

    group_node_name = "Coater Calculate Alpha"
    if bpy.data.node_groups.get(group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        # Create Nodes
        input_node = new_node_group.nodes.new('NodeGroupInput')
        output_node = new_node_group.nodes.new('NodeGroupOutput')
        subtract_node = new_node_group.nodes.new(type='ShaderNodeMath')
        multiply_node = new_node_group.nodes.new(type='ShaderNodeMath')
        add_node = new_node_group.nodes.new(type='ShaderNodeMath')

        # Add Sockets
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 1')
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 2')
        new_node_group.outputs.new('NodeSocketFloat', 'Alpha')

        # Set node values.
        subtract_node.operation = 'SUBTRACT'
        multiply_node.operation = 'MULTIPLY'
        add_node.operation = 'ADD'
        subtract_node.inputs[0].default_value = 1

        # Link nodes.
        link = new_node_group.links.new
        link(input_node.outputs[0], subtract_node.inputs[1])
        link(subtract_node.outputs[0], multiply_node.inputs[0])
        link(input_node.outputs[0], multiply_node.inputs[1])
        link(multiply_node.outputs[0], add_node.inputs[1])
        link(input_node.outputs[1], add_node.inputs[0])
        link(add_node.outputs[0], output_node.inputs[0])

        calculate_alpha_node = channel_node.node_tree.nodes.new('ShaderNodeGroup')
        calculate_alpha_node.node_tree = bpy.data.node_groups[group_node_name]
        calculate_alpha_node.name = group_node_name
        calculate_alpha_node.label = group_node_name
        calculate_alpha_node.width = layer_stack.node_default_width

        # Organize nodes.
        nodes = []
        nodes.append(input_node)
        nodes.append(subtract_node)
        nodes.append(multiply_node)
        nodes.append(add_node)
        nodes.append(output_node)

        header_position = [0.0, 0.0]
        for n in nodes:
            n.width = layer_stack.node_default_width
            n.location = (header_position[0], header_position[1])
            header_position[0] -= (layer_stack.node_default_width + layer_stack.node_spacing)