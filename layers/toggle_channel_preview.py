import bpy
from bpy.types import Operator
from . import layer_nodes

class COATER_OT_toggle_channel_preview(Operator):
    bl_idname = "coater.toggle_channel_preview"
    bl_label = "Toggle Channel Preview"
    bl_description = "Toggles the preview for the current material channel"

    def execute(self, context):
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes
        active_material = context.active_object.active_material
        node_links = context.active_object.active_material.node_tree.links
        group_node_name = active_material.name + "_" + str(layer_stack.channel)
        group_node = material_nodes.get(group_node_name)
            
        if group_node != None:
            # Toggle channel preview off.
            if layer_stack.channel_preview == True:
                layer_stack.channel_preview = False

                principled_bsdf_node = material_nodes.get('Principled BSDF')
                material_output_node = material_nodes.get('Material Output')

                # Remove all links.
                channel_nodes = layer_nodes.get_channel_nodes(context)
                for node in channel_nodes:
                    node_links.clear()

                base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
                metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
                roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
                emission_group = material_nodes.get(active_material.name + "_" + "EMISSION")
                height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")

                if base_color_group != None:
                    node_links.new(base_color_group.outputs[0], principled_bsdf_node.inputs[0])
                    
                if metallic_group != None:
                    node_links.new(metallic_group.outputs[0], principled_bsdf_node.inputs[6])

                if roughness_group != None:
                    node_links.new(roughness_group.outputs[0], principled_bsdf_node.inputs[9])

                if emission_group != None:
                    node_links.new(emission_group.outputs[0], principled_bsdf_node.inputs[19])

                if height_group != None:
                    node_links.new(height_group.outputs[0], principled_bsdf_node.inputs[22])

                node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])

            # Toggle channel preview on.
            elif layer_stack.channel_preview == False:
                layer_stack.channel_preview = True

                # De-attach all channels from Principled BSDF shader.
                channel_nodes = layer_nodes.get_channel_nodes(context)
                for node in channel_nodes:
                    node_links.clear()

                # Attach the selected channel to the emission shader.
                emission_node = material_nodes.get('Emission')
                material_output_node = material_nodes.get('Material Output')

                if layer_stack.channel == 'HEIGHT':
                    node_links.new(group_node.outputs[1], emission_node.inputs[0])
                        
                else:
                    node_links.new(group_node.outputs[0], emission_node.inputs[0])

                node_links.new(emission_node.outputs[0], material_output_node.inputs[0])

            return {'FINISHED'}
        else:
            return {'FINISHED'}