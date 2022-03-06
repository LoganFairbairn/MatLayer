import os
import bpy
from bpy.types import Operator
from .import coater_node_info
from .import link_layers
from .import organize_layer_nodes
from .import update_node_labels

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
        # Delete the nodes stored in this layer.
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        # Remove all nodes for this layer if they exist.
        channel_node = coater_node_info.get_channel_node(context)
        node_list = coater_node_info.get_layer_nodes(context, layer_index)
        for node in node_list:
            channel_node.node_tree.nodes.remove(node)

        # Remove node frame if it exists.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            channel_node.node_tree.nodes.remove(frame)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Re-link layers.
        link_layers.link_layers(context)

        # Re-organize all nodes.
        organize_layer_nodes.organize_layer_nodes(context)

        # If there are no layers left, delete the channel's node group from the blend file.
        active_material = context.active_object.active_material
        material_nodes = active_material.node_tree.nodes
        if layer_stack.layer_index == -1:
            group_node_name = active_material.name + "_" + str(layer_stack.channel)
            node_group = bpy.data.node_groups.get(group_node_name)
            group_node = material_nodes.get(group_node_name)

            if group_node != None:
                material_nodes.remove(group_node)

            if node_group != None:
                bpy.data.node_groups.remove(node_group)

        update_node_labels.update_node_labels(context)          # Update the node lables.
        organize_layer_nodes.organize_layer_nodes(context)      # Organize nodes

        return {'FINISHED'}