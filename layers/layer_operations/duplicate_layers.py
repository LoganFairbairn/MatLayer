import bpy
from bpy.types import Operator
from ..layer_stack import add_layer_slot
from ..nodes import material_channel_nodes
from ..nodes import update_layer_nodes
from .import add_layer

class COATER_OT_duplicate_layer(Operator):
    """Duplicates the selected layer."""
    bl_idname = "coater.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return None

    def execute(self, context):
        layers = context.scene.coater_layers
        selected_layer_index = context.scene.coater_layer_stack.selected_layer_index

        original_layer_index = selected_layer_index

        # TODO: Duplicate all nodes in the layer.


        # TODO: Update node indicies.


        # TODO: Read nodes values, store them in the layer (read layer nodes).

        return{'FINISHED'}