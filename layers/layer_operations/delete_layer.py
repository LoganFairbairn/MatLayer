import os
import bpy
from bpy.types import Operator
from .. import layer_nodes
from ..import material_channels

class COATER_OT_delete_layer(Operator):
    '''Deletes the selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        # Remove all nodes for all channels.
        channel_node = layer_nodes.get_channel_node(context)
        node_list = layer_nodes.get_layer_nodes(context, layer_index)
        for node in node_list:
            channel_node.node_tree.nodes.remove(node)

        # Remove node frame if it exists.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            channel_node.node_tree.nodes.remove(frame)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        
        #link_layers.link_layers(context)                        # Re-link layers.
        #organize_layer_nodes.organize_layer_nodes(context)      # Re-organize all nodes.
        #update_node_labels.update_node_labels(context)          # Update the node labels.
        #organize_layer_nodes.organize_layer_nodes(context)      # Organize nodes

        return {'FINISHED'}

def remove_color_channel_layer_nodes(context):
    '''Delete all nodes for the color channel.'''
    color_material_channel_node = material_channels.get_material_channel_node("BASECOLOR")

    #if color_material_channel_node != None:
    #   nodes = get_all_layer_nodes(context, layer_index)


