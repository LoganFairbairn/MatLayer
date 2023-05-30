# This module provides functions to edit material channel nodes made with this add-on.

import bpy
from bpy.types import Operator
from ..core import layer_nodes
from ..utilities import logging

# List of all channel names.
# Material channels are listed in the order of relative sockets in the Principled BSDF node so they will organize properly.
MATERIAL_CHANNEL_NAMES = ("COLOR", "SUBSURFACE", "SUBSURFACE_COLOR", "METALLIC", "SPECULAR", "ROUGHNESS", "EMISSION", "NORMAL", "HEIGHT")

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
    texture_set_settings = context.scene.matlayer_texture_set_settings

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
    '''Returns the material channel (group) node for the given material channel name on the active (selected) object.'''
    if context.active_object:
        if context.active_object.active_material:
            material_name = context.active_object.active_material.name
            if context.active_object.active_material.node_tree:
                if not material_channel_name in MATERIAL_CHANNEL_NAMES:
                    print("Error: " + material_channel_name +  " is an invalid material channel name. Do you have a typo in your code?")
                    return None
                else:
                    material_channel_node = context.active_object.active_material.node_tree.nodes.get(material_name + "_" + str(material_channel_name))
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

def set_material_channel_node_active_state(material_channel_name, active):
    '''Marks the give material channel node as active or inactive.'''
    # The material channel node is marked as being inactive by setting the node color to red. 
    # This visually marks the node as being inactive for users, and can be checked in code when the material nodes are read / refreshed to determine if it's active.
    material_channel_node = get_material_channel_node(bpy.context, material_channel_name)
    layer_nodes.set_node_active(material_channel_node, active)

def get_material_channel_node_active(material_channel_name):
    '''Returns true or false depending if the node is marked as active in this add-on.'''
    # The material node can be identified as being inactive if it's color is red, otherwise the material channel node is considered to be active.
    material_channel_node = get_material_channel_node(bpy.context, material_channel_name)
    return layer_nodes.get_node_active(material_channel_node)

def create_channel_group_nodes(context):
    '''Creates group and secondary nodes (e.g normal map mixing nodes) for all active material channels.'''
    active_material = context.active_object.active_material
    layer_stack = context.scene.matlayer_layer_stack

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

    # Set the material channels active states.
    for material_channel_name in get_material_channel_list():
        material_channel_node = get_material_channel_node(context, material_channel_name)
        material_channel_node.use_custom_color = True
        texture_set_settings = bpy.context.scene.matlayer_texture_set_settings
        material_channel_active = getattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle", None)
        set_material_channel_node_active_state(material_channel_name, material_channel_active)
        if not material_channel_active:
            disconnect_material_channel(context, material_channel_name)

    # Organize the newly created group nodes.
    layer_nodes.organize_material_channel_nodes(context)

def create_empty_group_node(context):
    '''Creates an empty group node as a placeholder for custom group nodes.'''
    empty_group_node_name = "MATLAYER_EMPTY"
    if bpy.data.node_groups.get(empty_group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(empty_group_node_name, 'ShaderNodeTree')
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = context.scene.matlayer_layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketColor', 'Color')
        group_output_node.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

def connect_material_channel(context, material_channel_name):
    '''Connects the specified material channel group node to the main principled BSDF shader or a secondary node.'''
    material_nodes = context.active_object.active_material.node_tree.nodes
    material_channel_node = get_material_channel_node(context, material_channel_name)
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    mix_normal_maps_node = material_nodes.get('MATLAYER_NORMALMIX')
    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings

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
            # If the height material channel is active when the height channel is toggled back on, connect the inputs to the mix normal map node for connecting to the principled bsdf.
            if texture_set_settings.global_material_channel_toggles.height_channel_toggle:
                node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[4])
                node_links.new(mix_normal_maps_node.outputs[1], principled_bsdf_node.inputs[22])

                height_material_channel_node = get_material_channel_node(context, "HEIGHT")
                if height_material_channel_node:
                    node_links.new(height_material_channel_node.outputs[0], mix_normal_maps_node.inputs[5])
            else:
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

        if material_channel_name == "HEIGHT":
            # If the normal material channel is active when the height channel is toggled back on, connect the inputs to the mix normal map node for connecting to the principled bsdf.
            if texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
                node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[5])
                node_links.new(mix_normal_maps_node.outputs[1], principled_bsdf_node.inputs[22])

                normal_material_channel_node = get_material_channel_node(context, "NORMAL")
                if normal_material_channel_node:
                    node_links.new(normal_material_channel_node.outputs[0], mix_normal_maps_node.inputs[4])
            else:
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

        if material_channel_name == "EMISSION":
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])

def disconnect_material_channel(context, material_channel_name):
    '''Disconnects the specified material channel group node from the main principled BSDF shader.'''
    node_links = context.active_object.active_material.node_tree.links
    material_channel_node = get_material_channel_node(context, material_channel_name)

    if material_channel_node:
        for l in node_links:
            if l.from_node.name == material_channel_node.name:
                node_links.remove(l)

    # If one of the height or normal material channels were disconnected, and one of them is still active, connect it directly to the principled bsdf shader.
    principled_bsdf_node = context.active_object.active_material.node_tree.nodes.get('Principled BSDF')
    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings

    if material_channel_name == 'NORMAL':
        if texture_set_settings.global_material_channel_toggles.height_channel_toggle:
            height_material_channel_node = get_material_channel_node(context, "HEIGHT")
            node_links.new(height_material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

    if material_channel_name == 'HEIGHT':
        if texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
            normal_material_channel_node = get_material_channel_node(context, "NORMAL")
            node_links.new(normal_material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

def validate_material_channel_name(material_channel_name):
    if material_channel_name in MATERIAL_CHANNEL_NAMES:
        return True
    else:
        logging.popup_message_box(material_channel_name + " is not a valid material channel name. Did you make a typo in your code?", "Programming Error", 'ERROR')
        return False

def isolate_material_channel(isolate, material_channel_name, context):
    '''Isolates the given material channel (used in material channel previews and baking specific material channels).'''
    texture_set_settings = context.scene.matlayer_texture_set_settings
    material_nodes = context.active_object.active_material.node_tree.nodes
    node_links = context.active_object.active_material.node_tree.links
    material_output_node = material_nodes.get('Material Output')

    # Validate the provided material channel name.
    validate_material_channel_name(material_channel_name)

    if isolate:
        emission_node = material_nodes.get('Emission')

        # Disconnect everything.
        for l in node_links:
            node_links.remove(l)

        # Connect the selected material channel to the emission node to preview the material channel.
        material_channel_node = get_material_channel_node(context, material_channel_name)
        node_links.new(material_channel_node.outputs[0], emission_node.inputs[0])
        node_links.new(emission_node.outputs[0], material_output_node.inputs[0])

        # Correct node connections for height / normal map channels so they preview as color rather than as vector rgb values.
        normal_channel_node = get_material_channel_node(context, "NORMAL")
        last_layer_index = layer_nodes.get_total_number_of_layers(context) - 1
        last_normal_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "NORMAL", last_layer_index, context)
        group_output_node = normal_channel_node.node_tree.nodes.get('Group Output')
        if last_normal_mix_node:
            for link in normal_channel_node.node_tree.links:
                if link.from_node == last_normal_mix_node:
                    normal_channel_node.node_tree.links.remove(link)
                    normal_channel_node.node_tree.links.new(last_normal_mix_node.outputs[0], group_output_node.inputs[0])
    
        height_channel_node = get_material_channel_node(context, "HEIGHT")
        last_height_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "HEIGHT", last_layer_index, context)
        group_output_node = height_channel_node.node_tree.nodes.get('Group Output')
        if last_height_mix_node:
            for link in height_channel_node.node_tree.links:
                if link.from_node == last_height_mix_node:
                    height_channel_node.node_tree.links.remove(link)
                    height_channel_node.node_tree.links.new(last_height_mix_node.outputs[0], group_output_node.inputs[0])
        

    else:
        principled_bsdf_node = material_nodes.get('Principled BSDF')
        mix_normal_maps_node = material_nodes.get('MATLAYER_NORMALMIX')

        # Disconnects all nodes in the active material.
        for l in node_links:
            node_links.remove(l)

        # Connect principled BSDF to material output.
        node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])

        # Connect all active material channels.
        if texture_set_settings.global_material_channel_toggles.color_channel_toggle:
            material_channel_node = get_material_channel_node(context, "COLOR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[0])

        if texture_set_settings.global_material_channel_toggles.subsurface_channel_toggle:
            material_channel_node = get_material_channel_node(context, "SUBSURFACE")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[1])

        if texture_set_settings.global_material_channel_toggles.subsurface_color_channel_toggle:
            material_channel_node = get_material_channel_node(context, "SUBSURFACE_COLOR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[3])

        if texture_set_settings.global_material_channel_toggles.metallic_channel_toggle:
            material_channel_node = get_material_channel_node(context, "METALLIC")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[6])

        if texture_set_settings.global_material_channel_toggles.specular_channel_toggle:
            material_channel_node = get_material_channel_node(context, "SPECULAR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[7])

        if texture_set_settings.global_material_channel_toggles.roughness_channel_toggle:
            material_channel_node = get_material_channel_node(context, "ROUGHNESS")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[9])

        if texture_set_settings.global_material_channel_toggles.emission_channel_toggle:
            material_channel_node = get_material_channel_node(context, "EMISSION")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])

        if texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
            material_channel_node = get_material_channel_node(context, "NORMAL")

            # If the height material channel isn't active, connect the normal channel directly to the principled bsdf.
            if texture_set_settings.global_material_channel_toggles.height_channel_toggle:
                node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[4])
            else:
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

        if texture_set_settings.global_material_channel_toggles.height_channel_toggle:
            material_channel_node = get_material_channel_node(context, "HEIGHT")

            # If the normal material channel isn't active, connect the height channel directly to the pricipled bsdf.
            if texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
                mix_normal_maps_node.get('A')
                node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[5])

            else:
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

        # Re-connect the normal mix node to the principled bsdf shader (only if both normal and height are toggled on).
        if texture_set_settings.global_material_channel_toggles.height_channel_toggle and texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
            node_links.new(mix_normal_maps_node.outputs[1], principled_bsdf_node.inputs[22])

        # Connect the last active normal mix node to the normal map node.
        last_layer_index = layer_nodes.get_total_number_of_layers(context) - 1
        last_normal_mix_index = last_layer_index
        last_normal_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "NORMAL", last_normal_mix_index, context)
        while layer_nodes.get_node_active(last_normal_mix_node) == False:
            last_normal_mix_index -= 1
            last_normal_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "NORMAL", last_normal_mix_index, context)
            if not last_normal_mix_node:
                break

        normal_material_channel_node = get_material_channel_node(context, "NORMAL")
        normal_map_node = normal_material_channel_node.node_tree.nodes.get('Normal Map')
        normal_group_output_node = normal_material_channel_node.node_tree.nodes.get('Group Output')

        if last_normal_mix_node and normal_map_node:
            for link in material_channel_node.node_tree.links:
                if link.from_node == last_normal_mix_node:
                    material_channel_node.node_tree.links.remove(link)
            normal_material_channel_node.node_tree.links.new(last_normal_mix_node.outputs[0], normal_map_node.inputs[1])
            normal_material_channel_node.node_tree.links.new(normal_map_node.outputs[0], normal_group_output_node.inputs[0])


        # Connect the last active height mix node to the bump node.
        last_height_mix_index = last_layer_index
        last_height_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "HEIGHT", last_height_mix_index, context)
        while layer_nodes.get_node_active(last_height_mix_node) == False:
            last_height_mix_index -= 1
            last_height_mix_node = layer_nodes.get_layer_node("MIX-LAYER", "HEIGHT", last_height_mix_index, context)
            if not last_height_mix_node:
                break

        height_material_channel_node = get_material_channel_node(context, "HEIGHT")
        bump_node = height_material_channel_node.node_tree.nodes.get('Bump')
        height_group_output_node = height_material_channel_node.node_tree.nodes.get('Group Output')
        if last_height_mix_node and bump_node:
            for link in height_material_channel_node.node_tree.links:
                if link.from_node == last_height_mix_node:
                    height_material_channel_node.node_tree.links.remove(link)
            height_material_channel_node.node_tree.links.new(last_height_mix_node.outputs[0], bump_node.inputs[2])
            height_material_channel_node.node_tree.links.new(bump_node.outputs[0], height_group_output_node.inputs[0])

class MATLAYER_OT_toggle_material_channel_preview(Operator):
    bl_idname = "matlayer.toggle_material_channel_preview"
    bl_label = "Toggle Channel Preview"
    bl_description = "Toggles a preview which displays only the information stored in the currently selected material channel"

    def execute(self, context):
        material_preview = context.scene.matlayer_layer_stack.material_channel_preview
        selected_material_channel = context.scene.matlayer_layer_stack.selected_material_channel
        if material_preview == True:
            isolate_material_channel(False, selected_material_channel, context)
            context.scene.matlayer_layer_stack.material_channel_preview = False
        else:
            isolate_material_channel(True, selected_material_channel, context)
            context.scene.matlayer_layer_stack.material_channel_preview = True
            
        return {'FINISHED'}