import bpy
from bpy.types import Operator
from ..nodes import layer_nodes

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
    '''Moves a layer up or down the layer stack.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    index_to_move_to = max(0, min(layer_index + (-1 if direction == "Up" else 1), len(layers) - 1))
    layers.move(layer_index, index_to_move_to)
    layer_stack.layer_index = index_to_move_to

    # Update layer nodes.
    layer_nodes.update_layer_nodes(context)