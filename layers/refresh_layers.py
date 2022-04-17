import bpy
from bpy.types import Operator, PropertyGroup
from .import update_layer_nodes
from .import coater_material_functions

class COATER_OT_refresh_layers(Operator):
    bl_idname = "coater.refresh_layers"
    bl_label = "Refresh Layers"
    bl_description = "Reads the layers in the active material and updates the layer stack based on that"

    def execute(self, context):
        # Make sure the active material is a Coater material before attempting to refresh the layer stack.
        if coater_material_functions.check_coater_material(context) == False:
            self.report({'ERROR'}, "Material is not a Coater material, can't read layer stack.")
            return {'FINISHED'}

        # TODO: Read the layer stack nodes and update values.

        # Organize all nodes.
        update_layer_nodes.organize_all_nodes(context)

        return {'FINISHED'}
