from os import dup
import bpy
from bpy.types import Operator
from ..import add_layer_slot

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
        layer_index = context.scene.coater_layer_stack.layer_index

        # Duplicate layer information into a new layer.
        add_layer_slot.add_layer_slot(context)

        layer = layers[layer_index + 1]
        duplicate_layer = layers[layer_index]

        duplicate_layer.name = layer.name + " copy"
        duplicate_layer.type = layer.type
        duplicate_layer.projection = layer.projection
        duplicate_layer.mask_projection = layer.mask_projection
        duplicate_layer.opacity = layer.opacity


        # TODO: Create nodes for the duplicated layer.

        # TODO: Organize nodes.

        return{'FINISHED'}