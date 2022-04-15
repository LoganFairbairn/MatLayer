# This file contains functions used to update layer nodes after they are edited.
from cgitb import text
from email import header
import bpy
from .import layer_nodes
from .import material_channels

NODE_WIDTH = 300
NODE_SPACING = 50

def update_layer_node_indicies(context, channel):
    '''Updates the layer node names and labels with the correct layer index. This allows the layer nodes to be read to determine their spot in the layer stack.'''
    material_channel_node = material_channels.get_material_channel_node(context, channel)
    layers = context.scene.coater_layers

    for i in range(len(layers), 0, -1):
        index = i - 1
        layer_name = context.scene.coater_layers[index].name
        layer_id = context.scene.coater_layers[index].id

        # Re-index frame nodes.
        layer_frame = layer_nodes.get_layer_frame(material_channel_node, layers, index)
        if layer_frame:
            layer_frame.name = layer_name + "_" + str(layer_id) + "_" + str(index)
            layer_frame.label = layer_frame.name
            layers[index].frame_name = layer_frame.name

        else:
            print("Error: Missing layer frame.")

        # Re-index layer nodes.
        texture_node = layer_nodes.get_node("TEXTURE", material_channel_node, index, context)
        if texture_node:
            texture_node.name = "TEXTURE_" + str(index)
            texture_node.label = texture_node.name
            layers[index].texture_node_name = texture_node.name

        opacity_node = layer_nodes.get_node("OPACITY", material_channel_node, index, context)
        if opacity_node:
            opacity_node.name = "OPACITY_" + str(index)
            opacity_node.label = texture_node.name
            layers[index].opacity_node_name = opacity_node.name

        mix_layer_node = layer_nodes.get_node("MIXLAYER", material_channel_node, index, context)
        if mix_layer_node:
            mix_layer_node.name = "MIXLAYER_" + str(index)
            mix_layer_node.label = mix_layer_node.name
            layers[index].mix_layer_node_name = mix_layer_node.name

        coord_node = layer_nodes.get_node("COORD", material_channel_node, index, context)
        if coord_node:
            coord_node.name = "COORD_" + str(index)
            coord_node.label = coord_node.name
            layers[index].coord_node_name = coord_node.name

        mapping_node = layer_nodes.get_node("MAPPING", material_channel_node, index, context)
        if mapping_node:
            mapping_node.name = "MAPPING_" + str(index)
            mapping_node.label = mapping_node.name
            layers[index].mapping_node_name = mapping_node.name


def organize_all_nodes(context):
    '''Organizes all Coater nodes.'''

    # Organize all channel nodes.
    active_material_channel_nodes = material_channels.get_active_material_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in active_material_channel_nodes:
        if node != None:
            node.location = (-node.width + -NODE_SPACING, header_position[1])
            header_position[1] -= (node.height + (NODE_SPACING * 0.5))
    
    # Organize all layers nodes for all material channels.

    '''
    # Organize group input node.
    if channel_node != None:
        header_position[0] -= layer_stack.node_default_width + node_spacing
        group_input_node = channel_node.node_tree.nodes.get('Group Input')
        group_input_node.location = (header_position[0], 0.0)
    
    # Organize group output node.
    if channel_node != None:
        group_output_node = channel_node.node_tree.nodes.get('Group Output')
        group_output_node.location = (0.0, 0.0)

    # If the current channel is a height channel, organize the bump node too.
    if layer_stack.channel == 'HEIGHT':
        if channel_node != None:
            bump_node = channel_node.node_tree.nodes.get('Bump')

            if bump_node != None:
                bump_node.location = (0.0, -group_input_node.dimensions.y - node_spacing)'''

def organize_material_channel_nodes(context):
    '''Oranizes all material channel nodes.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    color_channel_node = material_channels.get_material_channel_node(context, "COLOR")

    # Organizes all nodes.
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= NODE_WIDTH + NODE_SPACING
        header_position[1] = 0.0

        node_list = layer_nodes.get_all_layer_nodes(color_channel_node, layers, layer_index)
        for node in node_list:
            node.width = NODE_WIDTH
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + NODE_SPACING

def link_layers(context):
    '''Links all mix layer nodes together.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    group_input_node = node_group.nodes.get('Group Input')
    group_output_node = node_group.nodes.get('Group Output')

    # Remove all existing output links for mix layer or mix mask nodes.
    group_input = node_group.nodes.get('Group Input')
    output = group_input.outputs[0]
    for l in output.links:
        if l != 0:
            node_group.links.remove(l)

    group_output = node_group.nodes.get('Group Output')
    output = group_output.inputs[0]

    for l in output.links:
        if l != 0:
            node_group.links.remove(l)

    number_of_layers = len(layers)
    for x in range(number_of_layers - 1):
        mix_layer_node = node_group.nodes.get(layers[x].mix_layer_node_name)
        if mix_layer_node != None:
            output = mix_layer_node.outputs[0]
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)

        mix_mask_node = node_group.nodes.get(layers[x].mask_mix_node_name)
        if mix_mask_node != None:
            output = mix_mask_node.outputs[0]
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)
    
    # Connect mix layer nodes.
    for x in range(number_of_layers, 0, -1):
        current_layer_index = x - 1
        next_layer_index = x - 2

        # Connect the group input value to the first mix layer node or mix mask node (prioritize mask node connections).
        if x == number_of_layers:
            for i in range(number_of_layers, 0, -1):
                mix_mask_node = node_group.nodes.get(layers[i - 1].mask_mix_node_name)
                if layers[i - 1].hidden == False:
                    if mix_mask_node != None:
                        mix_layer_node = node_group.nodes.get(layers[i - 1].mix_layer_node_name)
                        mix_mask_node = node_group.nodes.get(layers[i - 1].mask_mix_node_name)
                        node_group.links.new(group_input_node.outputs[0], mix_layer_node.inputs[1])
                        node_group.links.new(group_input_node.outputs[0], mix_mask_node.inputs[1])
                    else:
                        mix_layer_node = node_group.nodes.get(layers[i - 1].mix_layer_node_name)
                        node_group.links.new(group_input_node.outputs[0], mix_layer_node.inputs[1])
                    break

        # Only connect layers that are not hidden.
        if layers[current_layer_index].hidden == False:
            mix_layer_node = node_group.nodes.get(layers[current_layer_index].mix_layer_node_name)
            mix_mask_node = node_group.nodes.get(layers[current_layer_index].mask_mix_node_name)
            next_mix_layer_node = node_group.nodes.get(layers[next_layer_index].mix_layer_node_name)
            next_mix_mask_node = node_group.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # Deal with hidden layers.
            while layers[next_layer_index].hidden:
                next_layer_index -= 1

                if next_layer_index < 0:
                    next_mix_layer_node = None
                    next_mix_mask_node = None
                    break

                else:
                    next_mix_layer_node = node_group.nodes.get(layers[next_layer_index].mix_layer_node_name)
                    next_mix_mask_node = node_group.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # Connect to the next mix layer node or mix mask node (prioritize mask node connections).
            if next_layer_index >= 0:
                if mix_mask_node != None:
                    if next_mix_mask_node != None:
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])

                else:
                    if next_mix_mask_node != None:
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])

            # For the last layer, connect the layer mix node or the mask mix node to the output (prioritize mask node connections).
            else:
                # If the channel is a Height channel, connect to the bump node first before connecting to the output.
                if layer_stack.channel == 'HEIGHT':
                    bump_node = node_group.nodes.get("Bump")

                    if bump_node != None:
                        if mix_mask_node != None:
                            node_group.links.new(mix_mask_node.outputs[0], bump_node.inputs[2])
                            node_group.links.new(mix_mask_node.outputs[0], group_output_node.inputs[1])
                            node_group.links.new(bump_node.outputs[0], group_output_node.inputs[0])

                        else:
                            node_group.links.new(mix_layer_node.outputs[0], bump_node.inputs[2])
                            node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[1])
                            node_group.links.new(bump_node.outputs[0], group_output_node.inputs[0])
                else:
                    if mix_mask_node != None:
                        node_group.links.new(mix_mask_node.outputs[0], group_output_node.inputs[0])

                    else:
                        node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])

            # Connect the mix layer node to the mix mask node if a mask exists.
            if mix_mask_node != None:
                node_group.links.new(mix_layer_node.outputs[0], mix_mask_node.inputs[2])
        
        # TODO: Link to alpha to calculate alpha nodes if required.

def create_calculate_alpha_node(context):
    '''Creates a group node aimed used to calculate alpha blending properly between layers.'''
    layer_stack = context.scene.coater_layer_stack
    channel_node = layer_nodes.get_channel_node(context)

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