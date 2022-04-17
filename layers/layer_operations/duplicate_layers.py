import bpy
from bpy.types import Operator
from ..import add_layer_slot
from ..import layer_nodes
from ..import material_channels
from ..import update_layer_nodes
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
        selected_layer_index = context.scene.coater_layer_stack.layer_index

        original_layer_index = selected_layer_index

        # Duplicate layer information into a new layer.
        add_layer_slot.add_layer_slot(context)
        new_layer_index = context.scene.coater_layer_stack.layer_index
        layers[new_layer_index] = layers[original_layer_index]

        # TODO: Create general nodes for the duplicated layer.
        material_channel_node = material_channels.get_material_channel_node(context, "COLOR")
        add_layer.add_general_layer_nodes(context, material_channel_node)

        # TODO: Add texture node for the duplicated layer based on the layer being copied.

        # TODO: Copy all the settings from the original layer.

        # Update layer nodes indicies.
        update_layer_nodes.update_layer_node_indicies(context, "COLOR")

        # Organize nodes.
        update_layer_nodes.organize_all_nodes(context)

        return{'FINISHED'}