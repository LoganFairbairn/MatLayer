# This module provides functions to edit material channel nodes made with this add-on.

import bpy

# List of all channel names.
# Material channels are listed in the order of relative sockets in the Principled BSDF node so they will organize properly.
MATERIAL_CHANNEL_NAMES = ("COLOR", "SCATTERING", "METALLIC", "ROUGHNESS", "EMISSION", "NORMAL", "HEIGHT")

# Enum property item of material channels.
MATERIAL_CHANNELS = [
    ("COLOR", "Color", ""), 
    ("SCATTERING", "Scattering", ""),
    ("METALLIC", "Metallic", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", "")
    ]

def verify_material_channel(material_channel_node):
    '''Verifies that a material channel exists.'''
    if material_channel_node == None:
        print("Error, no material channel found.")
        return False
    return True

def get_material_channel_list():
    '''Returns a set of all material channel names.'''
    return MATERIAL_CHANNEL_NAMES

def get_all_material_channel_nodes(context):
    '''Returns a list of all material channel nodes.'''
    material_channel_list = get_material_channel_list()

    material_channel_nodes = []
    for material_channel in material_channel_list:
        node = get_material_channel_node(context, material_channel)
        material_channel_nodes.append(node)

    return material_channel_nodes

def get_active_material_channel_nodes(context):
    '''Returns a list of all active material channel nodes.'''
    texture_set_settings = context.scene.coater_texture_set_settings

    active_material_channel_nodes = []
    if texture_set_settings.color_channel_toggle == True:
        node = get_material_channel_node(context, "COLOR")
        active_material_channel_nodes.append(node)

    if texture_set_settings.scattering_channel_toggle == True:
        node = get_material_channel_node(context, "SCATTERING")
        active_material_channel_nodes.append(node)

    if texture_set_settings.metallic_channel_toggle == True:
        node = get_material_channel_node(context, "METALLIC")
        active_material_channel_nodes.append(node)

    if texture_set_settings.roughness_channel_toggle == True:
        node = get_material_channel_node(context, "ROUGHNESS")
        active_material_channel_nodes.append(node)

    if texture_set_settings.emission_channel_toggle == True:
        node = get_material_channel_node(context, "EMISSION")
        active_material_channel_nodes.append(node)

    if texture_set_settings.normal_channel_toggle == True:
        node = get_material_channel_node(context, "NORMAL")
        active_material_channel_nodes.append(node)

    if texture_set_settings.height_channel_toggle == True:
        node = get_material_channel_node(context, "HEIGHT")
        active_material_channel_nodes.append(node)

    return active_material_channel_nodes

def get_material_channel_node(context, material_channel_name):
    '''Returns the material channel (group) node for the given material channel.'''
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes

    material_channel_node = material_nodes.get(active_material.name + "_" + str(material_channel_name))

    if material_channel_node == None:
        print("Error: Missing " + material_channel_name +  " material channel node.")

    return material_channel_node

def get_material_channel_output_node(context, channel):
    '''Returns the output node for the given material channel.'''
    channel_node = get_material_channel_node(context, channel)
    return channel_node.node_tree.nodes["Group Output"]

def add_material_channel(context, group_node_name, node_width, channel):
    '''Adds the material channel group node and links it to the Principled BSDF shader.'''
    material_nodes = context.active_object.active_material.node_tree.nodes
    if material_nodes.get(group_node_name) == None:
        group_node = material_nodes.new('ShaderNodeGroup')
        group_node.node_tree = bpy.data.node_groups[group_node_name]
        group_node.name = group_node_name
        group_node.label = group_node_name
        group_node.width = node_width * 1.2

        # Link the group node with the Principled BSDF node.
        principled_bsdf_node = material_nodes.get('Principled BSDF')

        if principled_bsdf_node != None:
            active_material = context.active_object.active_material
            node_links = active_material.node_tree.links

            if channel == "COLOR":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[0])
                
            if channel == "METALLIC":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[6])

            if channel == "ROUGHNESS":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[9])

            if channel == "NORMAL":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[22])

            #if channel == "HEIGHT":
            #    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[22])

            if channel == "EMISSION":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[19])

            if channel == "SCATTERING":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[3])

def remove_material_channel(context, channel):
    '''Removes the given material channels group node.'''
    material_channel_node = get_material_channel_node(context, channel)
    if material_channel_node != None:
        material_nodes = context.active_object.active_material.node_tree.nodes
        material_nodes.remove(material_channel_node)

def create_channel_group_nodes(context):
    '''Creates group nodes for all active material channels.'''
    active_material = context.active_object.active_material
    layer_stack = context.scene.coater_layer_stack

    # Create color group node.
    color_group_node_name = active_material.name + "_COLOR"
    if bpy.data.node_groups.get(color_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(color_group_node_name, 'ShaderNodeTree')

        # Create output nodes & sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Color')
        new_node_group.outputs.new('NodeSocketFloat', 'Alpha')

        # Set default values.
        group_output_node.inputs[0].default_value = (0.25, 0.25, 0.25, 1.0)
        group_output_node.inputs[1].default_value = 1.0
        
    # Create metallic group node.
    metallic_group_node_name = active_material.name + "_METALLIC"
    if bpy.data.node_groups.get(metallic_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(metallic_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketFloat', 'Metallic')

    # Create roughness group node.
    roughness_group_node_name = active_material.name + "_ROUGHNESS"
    if bpy.data.node_groups.get(roughness_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(roughness_group_node_name, 'ShaderNodeTree')
        
        # Create output nodes.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketFloat', 'Roughness')

        # Set default values.
        group_output_node.inputs[0].default_value = 0.5

    # Create normal group node.
    normal_group_node_name = active_material.name + "_NORMAL"
    if bpy.data.node_groups.get(normal_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(normal_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketVector', 'Normal')
        group_output_node.inputs[0].default_value = (0.0, 0.0, 1.0)

        # Create normal map node and connect it to the output.
        normal_map_node = new_node_group.nodes.new('ShaderNodeNormalMap')
        new_node_group.links.new(normal_map_node.outputs[0], group_output_node.inputs[0])

    # Create height group node.
    height_group_node_name  = active_material.name + "_HEIGHT"
    if bpy.data.node_groups.get(height_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(height_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketVector', 'Height')
        group_output_node.inputs[0].default_value = (0.0, 0.0, 1.0)

        # Create bump node and connect it to the output.
        bump_node = new_node_group.nodes.new('ShaderNodeBump')
        new_node_group.links.new(bump_node.outputs[0], group_output_node.inputs[0])

    # Create emission group node.
    emission_group_node_name = active_material.name + "_EMISSION"
    if bpy.data.node_groups.get(emission_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(emission_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Emission')

    # Create scattering group node.
    scattering_group_node_name = active_material.name + "_SCATTERING"
    if bpy.data.node_groups.get(scattering_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(scattering_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Scattering')

        # Set default values.
        group_output_node.inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)
    
    # Add the group node to the active material and link it if there is there isn't a group node already.
    add_material_channel(context, color_group_node_name, layer_stack.node_default_width, "COLOR")
    add_material_channel(context, metallic_group_node_name, layer_stack.node_default_width, "METALLIC")
    add_material_channel(context, roughness_group_node_name, layer_stack.node_default_width, "ROUGHNESS")
    add_material_channel(context, normal_group_node_name, layer_stack.node_default_width, "NORMAL")
    add_material_channel(context, height_group_node_name, layer_stack.node_default_width, "HEIGHT")
    add_material_channel(context, emission_group_node_name, layer_stack.node_default_width, "EMISSION")
    add_material_channel(context, scattering_group_node_name, layer_stack.node_default_width, "SCATTERING")

def disconnect_material_channel(context, material_channel_name):
    '''Disconnects the specified material channel group node from the main principled BSDF shader.'''
    node_links = context.active_object.active_material.node_tree.links
    material_channel_node = get_material_channel_node(context, material_channel_name)

    if material_channel_node:
        for l in node_links:
            if l.from_node.name == material_channel_node.name:
                node_links.remove(l)

def connect_material_channel(context, material_channel_name):
    '''Connects the specified material channel group node from the main principled BSDF shader.'''
    material_nodes = context.active_object.active_material.node_tree.nodes
    material_channel_node = get_material_channel_node(context, material_channel_name)
    principled_bsdf_node = material_nodes.get('Principled BSDF')

    if material_channel_node:
        active_material = context.active_object.active_material
        node_links = active_material.node_tree.links

        if material_channel_name == "COLOR":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[0])
                
        if material_channel_name == "METALLIC":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[6])

        if material_channel_name == "ROUGHNESS":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[9])

        if material_channel_name == "NORMAL":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

        #if channel == "HEIGHT":
        #    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[22])

        if material_channel_name == "EMISSION":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])

        if material_channel_name == "SCATTERING":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[3])