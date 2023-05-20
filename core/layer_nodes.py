# This module provides functions which effect all nodes, such as node organization and node relinking functions.

import bpy
from ..core import material_channels
from ..core import material_filters
from ..core import layer_masks
from ..utilities import matlay_utils
from ..utilities import logging

# Node organization settings.
NODE_WIDTH = 300
NODE_SPACING = 50

# Constant names for all material nodes. All material nodes must use one of these names.
LAYER_NODE_NAMES = ('TEXTURE', 'OPACITY', 'COORD', 'MAPPING', 'MIX-LAYER', 'NORMAL-ROTATION-FIX', 'TEXTURE-SAMPLE-1', 'TEXTURE-SAMPLE-2', 'TEXTURE-SAMPLE-3')

def set_node_active(node, active):
    '''Marks the node as inactive by changing it's color.'''
    # Marking the nodes inactive using their color is a work-around for a memory leak within Blender caused by compiling shaders that contain muted group nodes.
    if active:
        node.use_custom_color = False
        node.color = (0.1, 0.1, 0.1)
    else:
        node.use_custom_color = True
        node.color = (1.0, 0.0, 0.0)

def get_node_active(node):
    '''Returns true if the provided node is marked as active according to this add-on.'''
    # Marking the nodes inactive using their color is a work-around for a memory leak within Blender caused by compiling shaders that contain muted group nodes.
    if node == None:
        return False
    
    if node.color.r == 1.0 and node.color.g == 0.0 and node.color.b == 0.0:
        return False
    else:
        return True

def organize_material_channel_nodes(context):
    '''Organizes all material channel group nodes.'''
    material_channel_nodes = material_channels.get_all_material_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in material_channel_nodes:
        if node:
            node.hide = True
            node.location = (-node.width + -NODE_SPACING, header_position[1])
            header_position[1] -= (node.height + (NODE_SPACING * 0.5))

def organize_all_layer_nodes():
    '''Organizes all nodes (material nodes, filter nodes, and mask nodes) in all material channels.'''
    layers = bpy.context.scene.matlay_layers

    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

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
            material_layer_index = i - 1
            header_position[0] -= NODE_WIDTH + NODE_SPACING
            header_position[1] = 0.0

            # IMPORTANT: The nodes won't move when they are framed, delete the layer's frame and re-add it after organization.
            frame = get_layer_frame(material_channel_name, material_layer_index, bpy.context)
            if frame:
                frame_name = frame.name
                material_channel_node.node_tree.nodes.remove(frame)
            else:
                print("Error: frame doesn't exist.")

            # Create a list of all nodes in the layer and then organize them.
            node_list = get_all_nodes_in_layer(material_channel_name, material_layer_index, bpy.context)
            for node in node_list:
                node.hide = True
                node.width = NODE_WIDTH
                node.location = (header_position[0], header_position[1])
                header_position[1] -= (node.dimensions.y) + NODE_SPACING

            # Re-frame the layer nodes.
            frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
            frame.name = frame_name
            frame.label = frame.name
            layers[material_layer_index].frame_name = frame.name
            for node in node_list:
                node.parent = frame

            # Add space between layers.
            header_position[0] -= NODE_SPACING

def relink_material_layers():
    '''Re-links the last node in every material layer to the next layer if one exists.'''
    layers = bpy.context.scene.matlay_layers

    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

        for i in range(len(layers)):
            # Disconnect all mix layer nodes.
            mix_layer_node = get_layer_node("MIX-LAYER", material_channel_name, i, bpy.context)
            if mix_layer_node:
                output = mix_layer_node.outputs[0]
                for l in output.links:
                    if l != 0:
                        material_channel_node.node_tree.links.remove(l)

            # Disconnect all filter nodes.
            total_filter_nodes = material_filters.get_filter_nodes_count(i)
            for x in range(total_filter_nodes - 1):
                last_material_filter_node = material_filters.get_material_filter_node(material_channel_name, x, total_filter_nodes - 1)
                if last_material_filter_node:
                    for l in last_material_filter_node.outputs[0].links:
                        if l != 0:
                            material_channel_node.node_tree.links.remove(l)

        # Connect mix layer nodes for every layer.
        for i in range(0, len(layers)):
            current_layer_index = i
            next_layer_index = i + 1
            current_mix_layer_node = get_layer_node("MIX-LAYER", material_channel_name, current_layer_index, bpy.context)
            next_mix_layer_node = get_layer_node("MIX-LAYER", material_channel_name, next_layer_index, bpy.context)
            texture_node = get_layer_node("TEXTURE", material_channel_name, current_layer_index, bpy.context)

            # If the current layer is disabled, skip connecting it.
            if get_node_active(current_mix_layer_node) == False:
                continue

            # Find the next non disabled layer.
            if next_mix_layer_node:
                while get_node_active(next_mix_layer_node) == False:
                    next_layer_index += 1
                    next_mix_layer_node = get_layer_node("MIX-LAYER", material_channel_name, next_layer_index, bpy.context)
                    if not next_mix_layer_node:
                        break

            # Find the first active material filter node.
            total_filter_nodes = material_filters.get_filter_nodes_count(i)
            first_active_filter_index = 0 
            first_active_filter_node = material_filters.get_material_filter_node(material_channel_name, i, first_active_filter_index)
            while get_node_active(first_active_filter_node) == False:
                first_active_filter_index += 1
                first_active_filter_node = material_filters.get_material_filter_node(material_channel_name, i, first_active_filter_index)
                if not first_active_filter_node:
                    break

            # ALWAYS connect the texture output to the first material filter based on it's type if one exists and is ACTIVE.
            if first_active_filter_node:
                match first_active_filter_node.bl_static_type:
                    case 'INVERT':
                        material_channel_node.node_tree.links.new(texture_node.outputs[0], first_active_filter_node.inputs[1])
                    case 'VALTORGB':
                        material_channel_node.node_tree.links.new(texture_node.outputs[0], first_active_filter_node.inputs[0])
                    case 'HUE_SAT':
                        material_channel_node.node_tree.links.new(texture_node.outputs[0], first_active_filter_node.inputs[4])
                    case 'CURVE_RGB':
                        material_channel_node.node_tree.links.new(texture_node.outputs[0], first_active_filter_node.inputs[1])
                    case 'BRIGHTCONTRAST':
                        material_channel_node.node_tree.links.new(texture_node.outputs[0], first_active_filter_node.inputs[0])

                # Connect the last ACTIVE filter node to the current mix node.
                last_active_filter_node_index = total_filter_nodes - 1
                last_material_filter_node = material_filters.get_material_filter_node(material_channel_name, i, last_active_filter_node_index)
                while get_node_active(last_material_filter_node) == False:
                    last_active_filter_node_index -= 1
                    last_material_filter_node = material_filters.get_material_filter_node(material_channel_name, i, last_active_filter_node_index)
                    if not first_active_filter_node:
                        break

                if last_material_filter_node:
                    material_channel_node.node_tree.links.new(last_material_filter_node.outputs[0], current_mix_layer_node.inputs[2])

            # No material active material filter exists, connect the texture node directly to the mix layer node.
            else:
                material_channel_node.node_tree.links.new(texture_node.outputs[0], current_mix_layer_node.inputs[2])

            # Connect the last layer node to the next material layer if another material layer exists.
            if next_mix_layer_node:
                material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])

            # If no more material layers exist past this one, link the current mix layer node to the group nodes output / bump / normal node.
            else:
                if material_channel_name == "HEIGHT":
                    bump_node = material_channel_node.node_tree.nodes.get("Bump")
                    material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], bump_node.inputs[2])

                elif material_channel_name == "NORMAL":
                    normal_map_node = material_channel_node.node_tree.nodes.get("Normal Map")
                    material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], normal_map_node.inputs[1])

                else:
                    group_output_node = material_channel_node.node_tree.nodes.get("Group Output")
                    material_channel_node.node_tree.links.new(current_mix_layer_node.outputs[0], group_output_node.inputs[0])

def relink_material_nodes(material_layer_index):
    '''Relinks all material and filter nodes for the specified material layer index.'''

    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
        link_nodes = material_channel_node.node_tree.links.new

        # Unlink all material nodes.
        material_layer_nodes = get_all_material_layer_nodes(material_channel_name, material_layer_index, bpy.context)
        for node in material_layer_nodes:
            for link in node.outputs[0].links:
                if link != 0:
                    material_channel_node.node_tree.links.remove(link)

        # Get material nodes.
        texture_node = get_layer_node('TEXTURE', material_channel_name, material_layer_index, bpy.context)
        coord_node = get_layer_node('COORD', material_channel_name, material_layer_index, bpy.context)
        mapping_node = get_layer_node('MAPPING', material_channel_name, material_layer_index, bpy.context)
        opacity_node = get_layer_node('OPACITY', material_channel_name, material_layer_index, bpy.context)
        mix_layer_node = get_layer_node('MIX-LAYER', material_channel_name, material_layer_index, bpy.context)
        normal_rotation_fix_node = get_layer_node('NORMAL-ROTATION-FIX', material_channel_name, material_layer_index, bpy.context)

        # If the selected layer is a decal layer, use object coordinates.
        if check_decal_layer(material_layer_index):
            link_nodes(coord_node.outputs[3], mapping_node.inputs[0])

        else:
            # Connect to the coord node based on layer projection mode.
            match bpy.context.scene.matlay_layers[material_layer_index].projection.mode:
                case 'FLAT':
                    link_nodes(coord_node.outputs[2], mapping_node.inputs[0])

                case 'TRIPLANAR':
                    # Link triplanar texture samples for material channels that use an image texture.
                    if texture_node.bl_static_type == 'GROUP':
                        if texture_node.node_tree.name == 'MATLAY_TRIPLANAR' or texture_node.node_tree.name == 'MATLAY_TRIPLANAR_NORMALS':
                            texture_sample_1 = get_layer_node('TEXTURE-SAMPLE-1', material_channel_name, material_layer_index, bpy.context)
                            texture_sample_2 = get_layer_node('TEXTURE-SAMPLE-2', material_channel_name, material_layer_index, bpy.context)
                            texture_sample_3 = get_layer_node('TEXTURE-SAMPLE-3', material_channel_name, material_layer_index, bpy.context)

                            link_nodes(mapping_node.outputs[0], texture_sample_1.inputs[0])
                            link_nodes(mapping_node.outputs[1], texture_sample_2.inputs[0])
                            link_nodes(mapping_node.outputs[2], texture_sample_3.inputs[0])
                            link_nodes(texture_sample_1.outputs[0], texture_node.inputs[0])
                            link_nodes(texture_sample_2.outputs[0], texture_node.inputs[1])
                            link_nodes(texture_sample_3.outputs[0], texture_node.inputs[2])
                            link_nodes(mapping_node.outputs[3], texture_node.inputs[3])
                            if material_channel_name == 'NORMAL':
                                link_nodes(mapping_node.outputs[4], texture_node.inputs[4])

                case 'SPHERE':
                    link_nodes(coord_node.outputs[2], mapping_node.inputs[0])

                case 'TUBE':
                    link_nodes(coord_node.outputs[2], mapping_node.inputs[0])


        # Plug the mapping node into image textures when using flat / uv projection.
        if texture_node.bl_static_type == 'TEX_IMAGE':
            link_nodes(mapping_node.outputs[0], texture_node.inputs[0])

        # Apply layer opacity by connecting the opacity node to the material layer.
        link_nodes(opacity_node.outputs[0], mix_layer_node.inputs[0])

        # Fix normal map rotation by linking to normal map rotation fix node.
        if texture_node.bl_static_type == 'TEX_IMAGE' and material_channel_name == 'NORMAL':
            link_nodes(texture_node.outputs[0], normal_rotation_fix_node.inputs[0])        

        # Relink material filter nodes with other material filter nodes.
        material_filters.relink_material_filter_nodes(material_layer_index)

        # Link the last node in the material layer to the mix layer node.
        filters = bpy.context.scene.matlay_material_filters
        last_filter_node = material_filters.get_material_filter_node(material_channel_name, material_layer_index, len(filters) - 1)
        if last_filter_node:
            if material_channel_name == 'NORMAL':
                node_to_filter_node = normal_rotation_fix_node
                link_nodes(mapping_node.outputs[1], normal_rotation_fix_node.inputs[1])
                link_nodes(texture_node.outputs[0], node_to_filter_node.inputs[0])
            else:
                node_to_filter_node = texture_node

            first_filter_node = material_filters.get_material_filter_node(material_channel_name, material_layer_index, 0)
            match first_filter_node.bl_static_type:
                case 'INVERT':
                    material_channel_node.node_tree.links.new(node_to_filter_node.outputs[0], first_filter_node.inputs[1])
                case 'VALTORGB':
                    material_channel_node.node_tree.links.new(node_to_filter_node.outputs[0], first_filter_node.inputs[0])
                case 'HUE_SAT':
                    material_channel_node.node_tree.links.new(node_to_filter_node.outputs[0], first_filter_node.inputs[4])
                case 'CURVE_RGB':
                    material_channel_node.node_tree.links.new(node_to_filter_node.outputs[0], first_filter_node.inputs[1])
                case 'BRIGHTCONTRAST':
                    material_channel_node.node_tree.links.new(node_to_filter_node.outputs[0], first_filter_node.inputs[0])
            link_nodes(last_filter_node.outputs[0], mix_layer_node.inputs[2])
        else:
            if material_channel_name == 'NORMAL':
                # Connect to a normal rotation fix node for flat projection.
                if bpy.context.scene.matlay_layers[material_layer_index].projection.mode == 'FLAT':
                    link_nodes(texture_node.outputs[0], normal_rotation_fix_node.inputs[0])
                    link_nodes(mapping_node.outputs[1], normal_rotation_fix_node.inputs[1])
                    link_nodes(normal_rotation_fix_node.outputs[0], mix_layer_node.inputs[2])

                # Triplanar normal mapping has normal rotation fixes built into the group node, connect the triplanar directly to the mix layer node.
                elif bpy.context.scene.matlay_layers[material_layer_index].projection.mode == 'TRIPLANAR':
                    link_nodes(texture_node.outputs[0], mix_layer_node.inputs[2])

            else:
                link_nodes(texture_node.outputs[0], mix_layer_node.inputs[2])

def mute_layer_material_channel(mute, layer_stack_index, material_channel_name, context):
    '''Mutes (hides) or unhides all layer nodes for the specified material channel.'''
    for node_name in LAYER_NODE_NAMES:
        node = get_layer_node(node_name, material_channel_name, layer_stack_index, context)
        if node:
            set_node_active(node, not mute)
            
    relink_material_layers()
    matlay_utils.set_valid_material_shading_mode(context)



#----------------------------- MATERIAL LAYER NODE FUNCTIONS -----------------------------#

# TODO: Move to material_layers.py

def format_material_node_name(node_name, material_layer_index, get_edited=False):
    '''Formats a material node name to follow the required naming convention for material nodes.'''
    if node_name not in LAYER_NODE_NAMES:
        print("ERROR: Layer node name {0} not found in layer node name list.".format(node_name))

    node_name = "{0}_{1}".format(node_name, str(material_layer_index))
    if get_edited:
        node_name += '~'
    return node_name

def get_layer_node(node_name, material_channel_name, layer_index, context, get_edited=False):
    '''Gets a specific layer node using a given name. Valid options include "TEXTURE", "OPACITY", "COORD", "MAPPING", "MIX-LAYER", "NORMAL-ROTATION-FIX", "MATLAY-TRIPLANAR", "MATLAY-TRIPLANAR-NORMALS", "TEXTURE-SAMPLE-1", "TEXTURE-SAMPLE-2", "TEXTURE-SAMPLE-3" '''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    if material_channel_node:
        if node_name in LAYER_NODE_NAMES:
            node_name = node_name + "_" + str(layer_index)

            if get_edited:
                node_name = node_name + "~"

            node = material_channel_node.node_tree.nodes.get(node_name)
            if node:
                return node
        else:
            print("ERROR: Layer node name not found in layer node list. Do you have a typo in a layer node name somewhere in your code?")

def get_triplanar_texture_sample_nodes(material_channel_name, material_layer_index):
    '''Returns an array of all three triplanar texture sample nodes for the given material layer index.'''
    triplanar_texture_sample_nodes = []
    triplanar_texture_sample_nodes.append(get_layer_node('TEXTURE-SAMPLE-1', material_channel_name, material_layer_index, bpy.context))
    triplanar_texture_sample_nodes.append(get_layer_node('TEXTURE-SAMPLE-2', material_channel_name, material_layer_index, bpy.context))
    triplanar_texture_sample_nodes.append(get_layer_node('TEXTURE-SAMPLE-3', material_channel_name, material_layer_index, bpy.context))
    return triplanar_texture_sample_nodes

def get_all_material_layer_nodes(material_channel_name, material_layer_index, context, get_edited=False):
    '''Returns an array of all material nodes in a specified material layer (doesn't return layer filter or layer mask nodes).'''
    nodes = []
    for node_name in LAYER_NODE_NAMES:
        node = get_layer_node(node_name, material_channel_name, material_layer_index, context, get_edited)
        if node:
            nodes.append(node)
    return nodes

def get_all_nodes_in_layer(material_channel_name, material_layer_index, context, get_edited=False):
    '''Returns an array of all nodes that belong to the specified layer (includes mask and filter nodes).'''
    nodes = []

    # Get all material layer nodes.
    material_nodes = get_all_material_layer_nodes(material_channel_name, material_layer_index, context, get_edited)
    nodes = nodes + material_nodes

    # Get all material filter nodes.
    filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, material_layer_index, get_edited)
    nodes = nodes + filter_nodes

    # Get all mask nodes.
    mask_nodes = layer_masks.get_mask_nodes_in_material_layer(material_layer_index, material_channel_name, get_edited)
    nodes = nodes + mask_nodes

    # Get all mask filter nodes.
    mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, material_layer_index, get_edited)
    nodes = nodes + mask_filter_nodes

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

def reindex_material_layer_nodes():
    '''Reindexes all material layer nodes. This should be called when a layer is added, deleted, duplcated or moved.'''

    # The array index is stored in each layer for convenience, update this index first. Array index stored in each layer should match the layer index order.
    layers = bpy.context.scene.matlay_layers
    number_of_layers = len(layers)
    for i in range(0, number_of_layers):
        layers[i].layer_stack_array_index = i

    changed_layer_index = -1
    node_added = False
    node_deleted = False

    # Check for a newly added layer (signified by a tilda at the end of the node's name).
    material_channel_name = 'COLOR'
    material_channel_node = material_channels.get_material_channel_node(bpy.context, 'COLOR')
    for i in range(0, len(layers)):
        temp_node_name = format_material_node_name("TEXTURE", i) + "~"
        node = material_channel_node.node_tree.nodes.get(temp_node_name)
        if node:
            node_added = True
            changed_layer_index = i
            break

    # Check for a deleted layer (if there isn't a newly added layer).
    if not node_added:
        for i in range(0, len(layers)):
            frame = get_layer_frame(material_channel_name, i, bpy.context)
            if not frame:
                node_deleted = True
                changed_layer_index = i
                break

    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

        # Re-index the all layer nodes above the changed layer if any exist.
        if node_added:
            for i in range(len(layers), changed_layer_index + 1, -1):
                index = i - 1

                # Re-index the layer frame.
                frame_name = layers[index].name + "_" + str(layers[index].id) + "_" + str(index - 1)
                frame = material_channel_node.node_tree.nodes.get(frame_name)
                frame.name = layers[index].name + "_" + str(layers[index].id) + "_" + str(index)
                frame.label = frame.name
                layers[index].cached_frame_name = frame.name

                # Re-index the layer nodes.
                material_nodes = get_all_material_layer_nodes(material_channel_name, index - 1, bpy.context)
                for node in material_nodes:
                    node_info = node.name.split('_')
                    node.name = format_material_node_name(node_info[0], index, False)
                    node.label = node.name

                # Re-index all filter nodes.
                material_filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, index - 1, False)
                for node in material_filter_nodes:
                    node_info = node.name.split('_')
                    node.name = material_filters.format_filter_node_name(index, node_info[2], False)
                    node.label = node.name

                # Re-index all mask nodes.
                mask_nodes = layer_masks.get_mask_nodes_in_material_layer(index - 1, material_channel_name, False)
                for node in mask_nodes:
                    node_info = node.name.split('_')
                    node.name = layer_masks.format_mask_node_name(node_info[0], index, node_info[2], False)
                    node.label = node.name

                # Re-index all mask filter group nodes.
                mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, index - 1, False)
                for node in mask_filter_nodes:
                    node_info = node.name.split('_')
                    old_name = layer_masks.format_mask_filter_node_name(index - 1, node_info[3], node_info[4])
                    new_name = layer_masks.format_mask_filter_node_name(index, node_info[3], node_info[4])
                    layer_masks.rename_mask_filter_group_node(material_channel_name, old_name, new_name)

            # Remove the tilda from the new frame and nodes.
            temp_frame_name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(temp_frame_name)
            frame.name = layers[changed_layer_index].name + "_" + str(layers[changed_layer_index].id) + "_" + str(changed_layer_index)
            frame.label = frame.name
            layers[changed_layer_index].cached_frame_name = frame.name
            
            material_nodes = get_all_material_layer_nodes(material_channel_name, changed_layer_index, bpy.context, True)
            for node in material_nodes:
                node_info = node.name.split('_')
                node.name = format_material_node_name(node_info[0], changed_layer_index)
                node.label = node.name

        # Re-index all nodes on layers past the deleted layer if any exist.
        if node_deleted and len(layers) > 0:
            for i in range(changed_layer_index, len(layers), 1):
                index = i + 1

                # Re-index layer frames.
                old_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index)
                frame = material_channel_node.node_tree.nodes.get(old_frame_name)
                new_frame_name = layers[index - 1].name + "_" + str(layers[index - 1].id) + "_" + str(index - 1)
                frame.name = new_frame_name
                frame.label = frame.name
                layers[changed_layer_index].cached_frame_name = frame.name

                # Re-index material layer nodes.
                material_nodes = get_all_material_layer_nodes(material_channel_name, index, bpy.context, False)
                for node in material_nodes:
                    node_info = node.name.split('_')
                    node.name = format_material_node_name(node_info[0], index - 1)
                    node.label = node.name

                # Re-index filter nodes.
                material_filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, index, False)
                for node in material_filter_nodes:
                    node_info = node.name.split('_')
                    node.name = material_filters.format_filter_node_name(index - 1, node_info[2])
                    node.label = node.name

                # Re-index mask nodes.
                mask_nodes = layer_masks.get_mask_nodes_in_material_layer(index, material_channel_name, False)
                for node in mask_nodes:
                    node_info = node.name.split('_')
                    node.name = layer_masks.format_mask_node_name(node_info[0], index - 1, node_info[2], False)
                    node.label = node.name

                # Re-index mask filter nodes.
                mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, index, False)
                for node in mask_filter_nodes:
                    node_info = node.name.split('_')
                    old_name = layer_masks.format_mask_filter_node_name(index, node_info[3], node_info[4])
                    new_name = layer_masks.format_mask_filter_node_name(index - 1, node_info[3], node_info[4])
                    layer_masks.rename_mask_filter_group_node(material_channel_name, old_name, new_name)

    if node_added:
        masks = bpy.context.scene.matlay_masks
        mask_filters = bpy.context.scene.matlay_mask_filters

        # Reindex mask filter node trees above the newly added layer.
        for c in range(len(layers), changed_layer_index + 1, -1):
            for i in range(0, len(masks)):
                for x in range(0, len(mask_filters)):
                    old_name = layer_masks.format_mask_filter_node_name(index - 2, i, x)
                    new_name = layer_masks.format_mask_filter_node_name(index - 1, i, x)
                    layer_masks.rename_mask_filter_node_tree(old_name, new_name)
            
        # Remove the tilda from all mask filter node trees for all mask nodes.
        for i in range(0, len(masks)):
            for x in range(0, len(mask_filters)):
                old_name = layer_masks.format_mask_filter_node_name(changed_layer_index, i, x)
                new_name = layer_masks.format_mask_filter_node_name(changed_layer_index, i, x)
                layer_masks.rename_mask_filter_node_tree(old_name, new_name)

    if node_deleted:
        for i in range(changed_layer_index, len(layers), 1):
            index = i + 1
            mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, index, False)
            for node in mask_filter_nodes:
                old_name = layer_masks.format_mask_filter_node_name(index + 1, node_info[3], node_info[4])
                new_name = layer_masks.format_mask_filter_node_name(index, node_info[3], node_info[4])
                layer_masks.rename_mask_filter_node_tree(old_name, new_name)

def check_decal_layer(material_layer_index):
    '''Checks if the material layer at the provided material layer index is a decal layer.'''
    # Check if the material layer is a decal layer by checking if there is an object within the coord node of the layer.
    coord_node = get_layer_node('COORD', 'COLOR', material_layer_index, bpy.context)
    if coord_node:
        if coord_node.object != None:
            return True
    return False


#----------------------------- LAYER FRAME FUNCTIONS -----------------------------#

# TODO: Move to layer_frames.py

def get_layer_frame_name(layer_stack_index, get_edited=False):
    '''Returns a formatted layer frame name which follows the naming convention for layer frames created with this add-on.'''
    layers = bpy.context.scene.matlay_layers
    frame_name = "{0}_{1}_{2}".format(layers[layer_stack_index].name, str(layers[layer_stack_index].id), str(layer_stack_index))
    if get_edited:
        frame_name += '~'
    return frame_name

def get_layer_frame(material_channel_name, layer_stack_index, context, get_edited=False):
    '''Returns the frame node for the given layer. This function requires the layer id to be stored in the layer stack.'''
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    if material_channel_node:
        layers = context.scene.matlay_layers

        # Return a frame being edited if requested.
        if get_edited:
            layer_frame_name = layers[layer_stack_index].name + "_" + str(layers[layer_stack_index].id) + "_" + str(layer_stack_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(layer_frame_name)

        # Return the frame.
        else:
            layer_frame_name = get_layer_frame_name(layer_stack_index)
            frame = material_channel_node.node_tree.nodes.get(layer_frame_name)
        return frame
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