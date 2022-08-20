import bpy
from bpy.types import Operator
from ..nodes import layer_nodes
from ..nodes import material_channel_nodes

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

        # Remove all nodes for all material channels.
        material_channel_list = material_channel_nodes.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)

            # Remove layer frame.
            frame = layer_nodes.get_layer_frame(material_channel_name, layers[selected_layer_index].layer_stack_index, context)
            if frame != None:
                material_channel_node.node_tree.nodes.remove(frame)

            # Removed layer nodes.
            node_list = layer_nodes.get_all_nodes_in_layer(material_channel_name, layers[selected_layer_index].layer_stack_index, context)
            for node in node_list:
                material_channel_node.node_tree.nodes.remove(node)



        # Remove the layer slot from the layer stack and reset the layer index.
        layers.remove(selected_layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Update the layer nodes.
        layer_nodes.update_layer_nodes(context)

        return {'FINISHED'}