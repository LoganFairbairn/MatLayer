import bpy
from bpy.types import Operator, PropertyGroup
from . import update_layer_nodes
from . import coater_materials

# TODO: Rename this to refresh layer stack.
class COATER_OT_read_layer_stack(Operator):
    bl_idname = "coater.refresh_layers"
    bl_label = "Refresh Layers"
    bl_description = "Reads the layers in the active material and updates the layer stack based on that"

    def execute(self, context):
        # Make sure the active material is a Coater material before attempting to refresh the layer stack.
        if coater_materials.verify_material(context) == False:
            self.report({'ERROR'}, "Material is not a Coater material, can't read layer stack.")
            return {'FINISHED'}

        # TODO: Read the layer stack nodes and update values.

        # Organize all nodes.
        update_layer_nodes.organize_all_nodes(context)

        return {'FINISHED'}
