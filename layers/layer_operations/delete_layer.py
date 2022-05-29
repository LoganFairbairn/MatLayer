import bpy
from bpy.types import Operator
from ..nodes import layer_nodes
from ..nodes import material_channel_nodes
from ..nodes import update_layer_nodes

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
        selected_layer_index = context.scene.coater_layer_stack.layer_index

        # Remove all nodes for all channels.
        material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")
        node_list = layer_nodes.get_all_layer_nodes(material_channel_node, layers, selected_layer_index)
        for node in node_list:
            material_channel_node.node_tree.nodes.remove(node)

        # Remove node frame if it exists.
        frame = layer_nodes.get_layer_frame(material_channel_node, layers, selected_layer_index)
        if frame != None:
            material_channel_node.node_tree.nodes.remove(frame)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Update the layer nodes.
        update_layer_nodes.update_layer_nodes(context)

        return {'FINISHED'}

def remove_color_channel_layer_nodes(context):
    '''Delete all nodes for the color channel.'''
    color_material_channel_node = material_channel_nodes.get_material_channel_node("BASECOLOR")

    #if color_material_channel_node != None:
    #   nodes = get_all_layer_nodes(context, layer_index)


