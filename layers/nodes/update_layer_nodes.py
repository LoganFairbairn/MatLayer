# This file contains functions used to update layer nodes after they are edited.
import bpy
from . import layer_nodes
from . import material_channel_nodes

NODE_WIDTH = 300
NODE_SPACING = 50

def update_layer_nodes(context):
    '''Organizes all nodes in all material channels for every layer and links them all nodes together.'''
    '''Call this after making any change to the layer stack or layer nodes.'''

    # Organize all material channel group nodes.
    organize_material_channel_nodes(context)

    # Update all layer organize and link all layer nodes.
    material_channel_names = material_channel_nodes.get_material_channel_list()
    for material_channel in material_channel_names:

        # Update all layer node indicies (ran twice here to rename nodes that had been assigned existing names).
        update_layer_node_indicies(material_channel, context)
        update_layer_node_indicies(material_channel, context)

        # Organize all layer nodes.
        organize_layer_nodes_in_material_channel(material_channel, context)

        # Link all layers.
        link_layers_in_material_channel(material_channel, context)

def update_layer_indicies(context):
    '''Updates layer stack indicies stored in the layer.'''
    layers = context.scene.coater_layers

    # The layer stack index is the index in the order the layers are stacked.
    # The layer stack array index is the index of the array the layers are stored in.
    # These two values are opposites of each other.
    for i in range(0, len(layers)):
        index = len(layers) - i - 1
        layers[i].layer_stack_index = index
        layers[i].layer_stack_array_index = i

def update_layer_node_indicies(material_channel, context):
    '''Updates the layer node names and labels with the layer index. This allows the layer nodes to be read to determine their spot in the layer stack.'''
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    # Update the layer stack indicies stored in layers.
    update_layer_indicies(context)

    # Update the node indicies (in reverse order to avoid name duplications).
    layers = context.scene.coater_layers
    for i in range(len(layers), 0, -1):
        index = i - 1
        layer_stack_index = layers[index].layer_stack_index

        # Rename layer nodes with correct indicies.
        layer_node_names = layer_nodes.get_layer_node_names()
        for node_name in layer_node_names:
            node = layer_nodes.get_layer_node(node_name, material_channel, index, context)

            if node != None:
                node.name = node_name + "_" + str(layer_stack_index)
                node.label = node.name

                if node_name == "TEXTURE":
                    layers[index].texture_node_name = node.name

                if node_name == "OPACITY":
                    layers[index].opacity_node_name = node.name

                if node_name == "COORD":
                    layers[index].coord_node_name = node.name

                if node_name == "MAPPING":
                    layers[index].mapping_node_name = node.name

                if node_name == "MIXLAYER":
                    layers[index].mix_layer_node_name = node.name

        # Rename the layer frames with the correct indicies (frames are considered a layer node which is why they are updated here).
        layer_name = context.scene.coater_layers[index].name

        # Rename the layer frame.
        # IMPORTANT: The layer frame is renamed for all material channels to keep the layer frame name in sync.
        layer_nodes.rename_layer_frame(layer_name, index, context)

def organize_material_channel_nodes(context):
    # Organize all material channel group nodes.
    active_material_channel_nodes = material_channel_nodes.get_all_material_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in active_material_channel_nodes:
        if node != None:
            node.location = (-node.width + -NODE_SPACING, header_position[1])
            header_position[1] -= (node.height + (NODE_SPACING * 0.5))

def organize_layer_nodes_in_material_channel(material_channel, context):
    '''Oranizes layer nodes in the specified material channel.'''
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

    # Organizes all nodes.
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= NODE_WIDTH + NODE_SPACING
        header_position[1] = 0.0

        # IMPORTANT: The nodes won't move when the frame is in place. Delete the layer's frame.
        frame = layer_nodes.get_layer_frame(material_channel_node, layers, i)
        if frame:
            frame_name = frame.name
            material_channel_node.node_tree.nodes.remove(frame)

        # Organize the layer nodes.
        node_list = layer_nodes.get_all_nodes_in_layer(material_channel_node, layers, i)
        for c in range(0, len(node_list)):
            node_list[c].width = NODE_WIDTH
            node_list[c].location = (header_position[0], header_position[1])
            header_position[1] -= (node_list[c].dimensions.y) + NODE_SPACING

        # Re-frame the layers.
        frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
        frame.name = frame_name
        frame.label = frame.name
        layers[i].frame_name = frame.name

        # Frame all the nodes in the given layer in the newly created frame.
        nodes = layer_nodes.get_all_nodes_in_layer(material_channel_node, layers, i)
        for n in nodes:
            n.parent = frame

        # Add spacing between layers.
        header_position[0] -= NODE_SPACING

def link_layers_in_material_channel(material_channel, context):
    '''Links all layers in the given material channel together by linking the mix layer and mix mask nodes together.'''
    layers = context.scene.coater_layers
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

    # Remove all existing output links for mix layer or mix mask nodes.
    number_of_layers = len(layers)
    for x in range(number_of_layers - 1):
        mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", material_channel, x, context)
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
    for x in range(number_of_layers, 0, -1):
        current_layer_index = x - 1
        next_layer_index = x - 2

        # Only connect layers that are not hidden.
        if layers[current_layer_index].hidden == False:
            mix_layer_node = material_channel_node.node_tree.nodes.get(layers[current_layer_index].mix_layer_node_name)
            mix_mask_node = material_channel_node.node_tree.nodes.get(layers[current_layer_index].mask_mix_node_name)
            next_mix_layer_node = material_channel_node.node_tree.nodes.get(layers[next_layer_index].mix_layer_node_name)
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
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], normal_map_node.inputs[0])

                    else:
                        material_channel_node.node_tree.links.new(mix_mask_node.outputs[0], group_output_node.inputs[0])

                else:
                    if material_channel == 'HEIGHT':
                        bump_node = material_channel_node.node_tree.nodes.get("Bump")
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], bump_node.inputs[2])

                    elif material_channel == 'NORMAL':
                        normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], normal_map_node.inputs[0])

                    else:
                        material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])

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