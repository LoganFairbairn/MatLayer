import bpy
from bpy.types import Operator
from ..nodes import layer_nodes
from ..nodes import material_channel_nodes

class COATER_OT_move_layer_up(Operator):
    """Moves the selected layer up on the layer stack."""
    bl_idname = "coater.move_layer_up"
    bl_label = "Move Layer Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        move_layer(context, "UP")
        return{'FINISHED'}

class COATER_OT_move_layer_down(Operator):
    """Moves the selected layer down the layer stack."""
    bl_idname = "coater.move_layer_down"
    bl_label = "Move Layer Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"
    
    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        move_layer(context, "DOWN")
        return{'FINISHED'}

def move_layer(context, direction):
    '''Moves a layer up or down the layer stack.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Rename layer frame and nodes before the layer stack is moved.
    if direction == "DOWN":
        # Get the layer under the selected layer (if one exists).
        under_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        # Don't move the selected layer down if this is already the bottom layer.
        if selected_layer_index - 1 < 0:
            return
        
        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = old_frame_name + "~"
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, selected_layer_index, context)
                node.name = node.name + "~"
                node.label = node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[under_layer_index].name + "_" + str(layers[under_layer_index].id) + "_" + str(under_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[under_layer_index].name + "_" + str(layers[under_layer_index].id) + "_" + str(selected_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, under_layer_index, context)
                layer_nodes.rename_layer_node(node, node_name, selected_layer_index)

        # Remove the tilda from the end of the layer frame and the layer node names for the selected layer and reduce their indicies by 1.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(under_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = material_channel_node.node_tree.nodes.get(node_name + "_" + str(selected_layer_index) + "~")
                layer_nodes.rename_layer_node(node, node_name, under_layer_index)

        index_to_move_to = max(min(selected_layer_index - 1, len(layers) - 1), 0)
        layers.move(selected_layer_index, index_to_move_to)
        context.scene.coater_layer_stack.layer_index = index_to_move_to






    if direction == "UP":
        # Get the next layers index (if one exists).
        over_layer_index = max(min(selected_layer_index + 1, len(layers) - 1), 0)

        # Don't move the layer up if the selected layer is already the top layer.
        if selected_layer_index + 1 > len(layers) - 1:
            return


        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = old_frame_name + "~"
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, selected_layer_index, context)
                node.name = node.name + "~"
                node.label = node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[over_layer_index].name + "_" + str(layers[over_layer_index].id) + "_" + str(over_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[over_layer_index].name + "_" + str(layers[over_layer_index].id) + "_" + str(selected_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, over_layer_index, context)
                layer_nodes.rename_layer_node(node, node_name, selected_layer_index)

        # Remove the tilda from the end of the layer frame and the layer node names for the selected layer and reduce their indicies by 1.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(over_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = material_channel_node.node_tree.nodes.get(node_name + "_" + str(selected_layer_index) + "~")
                layer_nodes.rename_layer_node(node, node_name, over_layer_index)


        # Move the layer in the layer stack. 
        index_to_move_to = max(min(selected_layer_index + 1, len(layers) - 1), 0)
        layers.move(selected_layer_index, index_to_move_to)
        context.scene.coater_layer_stack.layer_index = index_to_move_to

    # Update the layer nodes.
    layer_nodes.update_layer_nodes(context)