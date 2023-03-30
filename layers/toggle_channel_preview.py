import bpy
from bpy.types import Operator
from . import material_channel_nodes
from . import layer_nodes

def toggle_material_channel_preview(on, material_channel_name, context):
    '''Toggles a preview for the selected material channel.'''
    texture_set_settings = context.scene.matlay_texture_set_settings
    material_nodes = context.active_object.active_material.node_tree.nodes
    node_links = context.active_object.active_material.node_tree.links
    material_output_node = material_nodes.get('Material Output')

    if on:
        emission_node = material_nodes.get('Emission')

        # Disconnect everything.
        for l in node_links:
            node_links.remove(l)

        # Connect the selected material channel to the emission node to preview the material channel.
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
        node_links.new(material_channel_node.outputs[0], emission_node.inputs[0])
        node_links.new(emission_node.outputs[0], material_output_node.inputs[0])

        # Correct node connections for height / normal map channels so they preview as color rather than as vector rgb values.
        normal_channel_node = material_channel_nodes.get_material_channel_node(context, "NORMAL")
        last_layer_index = layer_nodes.get_total_number_of_layers(context) - 1
        last_normal_mix_node = layer_nodes.get_layer_node("MIXLAYER", "NORMAL", last_layer_index, context)
        group_output_node = normal_channel_node.node_tree.nodes.get('Group Output')
        if last_normal_mix_node:
            for link in normal_channel_node.node_tree.links:
                if link.from_node == last_normal_mix_node:
                    normal_channel_node.node_tree.links.remove(link)
                    normal_channel_node.node_tree.links.new(last_normal_mix_node.outputs[0], group_output_node.inputs[0])
    
        height_channel_node = material_channel_nodes.get_material_channel_node(context, "HEIGHT")
        last_height_mix_node = layer_nodes.get_layer_node("MIXLAYER", "HEIGHT", last_layer_index, context)
        group_output_node = height_channel_node.node_tree.nodes.get('Group Output')
        if last_height_mix_node:
            for link in height_channel_node.node_tree.links:
                if link.from_node == last_height_mix_node:
                    height_channel_node.node_tree.links.remove(link)
                    height_channel_node.node_tree.links.new(last_height_mix_node.outputs[0], group_output_node.inputs[0])
        

    else:
        principled_bsdf_node = material_nodes.get('Principled BSDF')
        mix_normal_maps_node = material_nodes.get('MATLAY_NORMALMIX')

        # Disconnects all nodes in the active material.
        for l in node_links:
            node_links.remove(l)

        # Connect principled BSDF to material output.
        node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])

        # Connect all active material channels.
        if texture_set_settings.global_material_channel_toggles.color_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[0])

        if texture_set_settings.global_material_channel_toggles.subsurface_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "SUBSURFACE")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[1])

        if texture_set_settings.global_material_channel_toggles.subsurface_color_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "SUBSURFACE_COLOR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[3])

        if texture_set_settings.global_material_channel_toggles.metallic_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "METALLIC")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[6])

        if texture_set_settings.global_material_channel_toggles.specular_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "SPECULAR")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[7])

        if texture_set_settings.global_material_channel_toggles.roughness_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "ROUGHNESS")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[9])

        if texture_set_settings.global_material_channel_toggles.emission_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "EMISSION")
            node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])

        if texture_set_settings.global_material_channel_toggles.normal_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "NORMAL")
            node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[0])

        if texture_set_settings.global_material_channel_toggles.height_channel_toggle:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "HEIGHT")
            node_links.new(material_channel_node.outputs[0], mix_normal_maps_node.inputs[1])

        # Re-connect the height and normal material channel.
        normal_material_channel_node = material_channel_nodes.get_material_channel_node(context, "NORMAL")
        last_layer_index = layer_nodes.get_total_number_of_layers(context) - 1
        last_normal_mix_node = layer_nodes.get_layer_node("MIXLAYER", "NORMAL", last_layer_index, context)
        normal_map_node = normal_material_channel_node.node_tree.nodes.get('Normal Map')
        normal_group_output_node = normal_material_channel_node.node_tree.nodes.get('Group Output')

        if last_normal_mix_node:
            for link in material_channel_node.node_tree.links:
                if link.from_node == last_normal_mix_node:
                    material_channel_node.node_tree.links.remove(link)
        normal_material_channel_node.node_tree.links.new(last_normal_mix_node.outputs[0], normal_map_node.inputs[0])
        normal_material_channel_node.node_tree.links.new(normal_map_node.outputs[0], normal_group_output_node.inputs[0])

        height_material_channel_node = material_channel_nodes.get_material_channel_node(context, "HEIGHT")
        last_height_mix_node = layer_nodes.get_layer_node("MIXLAYER", "HEIGHT", last_layer_index, context)
        bump_node = material_channel_node.node_tree.nodes.get('Bump')
        height_group_output_node = height_material_channel_node.node_tree.nodes.get('Group Output')
        if last_height_mix_node:
            for link in height_material_channel_node.node_tree.links:
                if link.from_node == last_height_mix_node:
                    height_material_channel_node.node_tree.links.remove(link)
        height_material_channel_node.node_tree.links.new(last_height_mix_node.outputs[0], bump_node.inputs[0])
        height_material_channel_node.node_tree.links.new(bump_node.outputs[0], height_group_output_node.inputs[0])

        # Re-connect the normal mix node to the principled bsdf shader.
        node_links.new(mix_normal_maps_node.outputs[0], principled_bsdf_node.inputs[22])
        

class MATLAY_OT_toggle_channel_preview(Operator):
    bl_idname = "matlay.toggle_channel_preview"
    bl_label = "Toggle Channel Preview"
    bl_description = "Toggles a preview which displays only the information stored in the currently selected material channel"

    def execute(self, context):
        material_preview = context.scene.matlay_layer_stack.material_channel_preview
        selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel
        if material_preview == True:
            toggle_material_channel_preview(False, selected_material_channel, context)
            context.scene.matlay_layer_stack.material_channel_preview = False
        else:
            toggle_material_channel_preview(True, selected_material_channel, context)
            context.scene.matlay_layer_stack.material_channel_preview = True
            
        return {'FINISHED'}