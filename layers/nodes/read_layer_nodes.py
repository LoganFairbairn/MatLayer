import bpy
from bpy.types import Operator, PropertyGroup
from . import update_layer_nodes
from . import coater_materials

class COATER_OT_read_layer_nodes(Operator):
    bl_idname = "coater.read_layer_nodes"
    bl_label = "Read Layer Nodes"
    bl_description = "Reads the material nodes in the active material and updates the layer stack with that"

    def execute(self, context):
        # Make sure the active material is a Coater material before attempting to refresh the layer stack.
        if coater_materials.verify_material(context) == False:
            self.report({'ERROR'}, "Material is not a Coater material, can't read layer stack.")
            return {'FINISHED'}

        # TODO: Read the layer stack nodes and update values.

        # Update layer nodes.
        update_layer_nodes.update_layer_nodes(context)

        return {'FINISHED'}
