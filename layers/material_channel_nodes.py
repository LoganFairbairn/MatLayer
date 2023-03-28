# This module provides functions to edit material channel nodes made with this add-on.

from cgitb import text
import bpy

# List of all channel names.
# Material channels are listed in the order of relative sockets in the Principled BSDF node so they will organize properly.
MATERIAL_CHANNEL_NAMES = ("COLOR", "SUBSURFACE", "SUBSURFACE_COLOR", "METALLIC", "SPECULAR", "ROUGHNESS", "EMISSION", "NORMAL", "HEIGHT")

# Enum for material channels (Used in ).
MATERIAL_CHANNELS = [
    ("COLOR", "Color", ""), 
    ("SUBSURFACE", "Subsurface", ""),
    ("SUBSURFACE_COLOR", "Subsurface Color", ""),
    ("METALLIC", "Metallic", ""),
    ("SPECULAR", "Specular", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", "")
    ]

def get_material_channel_abbreviation(material_channel_name):
    '''Returns an abbreviation for the material channel name. This can be used to compact the material channel's name when displayed in the user interface.'''
    match material_channel_name:
        case 'COLOR':
            return "Color"

        case 'SUBSURFACE':
            return "SubSurf"
        
        case 'SUBSURFACE_COLOR':
            return "SS Color"

        case 'METALLIC':
            return "Metal"

        case 'SPECULAR':
            return "Spec"

        case 'ROUGHNESS':
            return "Rough"

        case 'EMISSION':
            return "Emit"
        
        case 'NORMAL':
            return "Nrm"
        
        case 'HEIGHT':
            return "Height"

def verify_material_channel(material_channel_node):
    '''Verifies that a material channel node exists.'''
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
    texture_set_settings = context.scene.matlay_texture_set_settings

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
    '''Returns the material channel (group) node for the given material channel on the active object.'''
    if context.active_object:
        if context.active_object.active_material:
            material_name = context.active_object.active_material.name
            material_nodes = context.active_object.active_material.node_tree.nodes
            material_channel_node = material_nodes.get(material_name + "_" + str(material_channel_name))

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

        # Link the new material channel group node with the Principled BSDF node or the normal mix node.
        connect_material_channel(context, channel)

def remove_material_channel(context, channel):
    '''Removes the given material channels group node.'''
    material_channel_node = get_material_channel_node(context, channel)
    if material_channel_node != None:
        material_nodes = context.active_object.active_material.node_tree.nodes
        material_nodes.remove(material_channel_node)

def create_channel_group_nodes(context):
    '''Creates group and secondary nodes (e.g normal map mixing nodes) for all active material channels.'''
    active_material = context.active_object.active_material
    layer_stack = context.scene.matlay_layer_stack

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

    # Create a subsurface group node.
    subsurface_group_node_name = active_material.name + "_SUBSURFACE"
    if bpy.data.node_groups.get(subsurface_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(subsurface_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Subsurface')

        # Set default values.
        group_output_node.inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)

    # Create a subsurface color group node.
    subsurface_color_group_node_name = active_material.name + "_SUBSURFACE_COLOR"
    if bpy.data.node_groups.get(subsurface_color_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(subsurface_color_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'SubsurfaceColor')

    # Create metallic group node.
    metallic_group_node_name = active_material.name + "_METALLIC"
    if bpy.data.node_groups.get(metallic_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(metallic_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketFloat', 'Metallic')

    # Create a specular group node.
    specular_group_node_name = active_material.name + "_SPECULAR"
    if bpy.data.node_groups.get(specular_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(specular_group_node_name, 'ShaderNodeTree')
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketFloat', 'Specular')

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

    # Create emission group node.
    emission_group_node_name = active_material.name + "_EMISSION"
    if bpy.data.node_groups.get(emission_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(emission_group_node_name, 'ShaderNodeTree')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Emission')

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
    
    # Add the group node to the active material (if there isn't one already) and link it.
    add_material_channel(context, color_group_node_name, layer_stack.node_default_width, "COLOR")
    add_material_channel(context, subsurface_group_node_name, layer_stack.node_default_width, "SUBSURFACE")
    add_material_channel(context, subsurface_color_group_node_name, layer_stack.node_default_width, "SUBSURFACE_COLOR")
    add_material_channel(context, metallic_group_node_name, layer_stack.node_default_width, "METALLIC")
    add_material_channel(context, roughness_group_node_name, layer_stack.node_default_width, "ROUGHNESS")
    add_material_channel(context, specular_group_node_name, layer_stack.node_default_width, "SPECULAR")
    add_material_channel(context, normal_group_node_name, layer_stack.node_default_width, "NORMAL")
    add_material_channel(context, height_group_node_name, layer_stack.node_default_width, "HEIGHT")
    add_material_channel(context, emission_group_node_name, layer_stack.node_default_width, "EMISSION")

def create_empty_group_node(context):
    '''Creates an empty group node as a placeholder for custom group nodes.'''
    empty_group_node_name = "MATLAY_EMPTY"
    if bpy.data.node_groups.get(empty_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(empty_group_node_name, 'ShaderNodeTree')
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = context.scene.matlay_layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Color')
        group_output_node.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

def disconnect_material_channel(context, material_channel_name):
    '''Disconnects the specified material channel group node from the main principled BSDF shader.'''
    node_links = context.active_object.active_material.node_tree.links
    material_channel_node = get_material_channel_node(context, material_channel_name)

    if material_channel_node:
        for l in node_links:
            if l.from_node.name == material_channel_node.name:
                node_links.remove(l)

def connect_material_channel(context, material_channel_name):
    '''Connects the specified material channel group node to the main principled BSDF shader or a secondary node.'''
    material_nodes = context.active_object.active_material.node_tree.nodes
    material_channel_node = get_material_channel_node(context, material_channel_name)
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    mix_normal_maps_node = material_nodes.get('MATLAY_NORMALMIX')

    if material_channel_node:
        active_material = context.active_object.active_material
        node_links = active_material.node_tree.links

        if material_channel_name == "COLOR":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[0])
                
        if material_channel_name == "SUBSURFACE":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[1])

        if material_channel_name == "SUBSURFACE_COLOR":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[3])

        if material_channel_name == "METALLIC":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[6])

        if material_channel_name == "SPECULAR":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[7])       

        if material_channel_name == "ROUGHNESS":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[9])

        if material_channel_name == "NORMAL":
            node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[0])

        if material_channel_name == "HEIGHT":
            node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[1])

        if material_channel_name == "EMISSION":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])
