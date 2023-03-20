import bpy
from bpy.types import Operator
from . import material_channel_nodes

class COATER_OT_toggle_channel_preview(Operator):
    bl_idname = "coater.toggle_channel_preview"
    bl_label = "Toggle Channel Preview"
    bl_description = "Toggles a preview which displays only the information stored in the currently selected material channel"

    def execute(self, context):
        layer_stack = context.scene.coater_layer_stack
        selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
        texture_set_settings = context.scene.coater_texture_set_settings
        material_nodes = context.active_object.active_material.node_tree.nodes

        node_links = context.active_object.active_material.node_tree.links

        
        emission_node = material_nodes.get('Emission')
        material_output_node = material_nodes.get('Material Output')

        # Toggle material channel preview off.
        if layer_stack.material_channel_preview:
            layer_stack.material_channel_preview = False

            principled_bsdf_node = material_nodes.get('Principled BSDF')

            # Disconnect everything.
            for l in node_links:
                node_links.remove(l)

            # Connect principled BSDF to material output.
            node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])
            
            # Connect all active material channels.
            if texture_set_settings.color_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[0])

            if texture_set_settings.metallic_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "METALLIC")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[6])

            if texture_set_settings.roughness_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "ROUGHNESS")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[9])

            if texture_set_settings.normal_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "NORMAL")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[22])

            if texture_set_settings.emission_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "EMISSION")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[19])

            if texture_set_settings.scattering_channel_toggle:
                material_channel_node = material_channel_nodes.get_material_channel_node(context, "SCATTERING")
                node_links.new(material_channel_node.outputs[0], principled_bsdf_node.inputs[3])


        # Toggle material channel preview on.
        else:
            layer_stack.material_channel_preview = True

            # Disconnect everything.
            for l in node_links:
                node_links.remove(l)

            # Connect the selected material channel to the emission node to preview the material channel.
            selected_material_channel_node = material_channel_nodes.get_material_channel_node(context, selected_material_channel)
            node_links.new(selected_material_channel_node.outputs[0], emission_node.inputs[0])

            node_links.new(emission_node.outputs[0], material_output_node.inputs[0])
            
            
        return {'FINISHED'}