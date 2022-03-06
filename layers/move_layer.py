import bpy
from bpy.types import Operator
from .import organize_layer_nodes
from .import link_layers
from .import update_node_labels

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
        move_layer(context, "Up")
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
        move_layer(context, "Down")
        return{'FINISHED'}

def move_layer(context, direction):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    index_to_move_to = max(0, min(layer_index + (-1 if direction == "Up" else 1), len(layers) - 1))
    layers.move(layer_index, index_to_move_to)
    layer_stack.layer_index = index_to_move_to

    update_node_labels.update_node_labels(context)          # Re-name nodes.
    organize_layer_nodes.organize_layer_nodes(context)      # Re-organize nodes.
    link_layers.link_layers(context)                        # Re-connect layers.