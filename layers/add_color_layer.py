import bpy
from bpy.types import Operator
from .import add_layer_slot
from .import create_channel_group_node
from .import coater_material_functions
from .import link_layers
from .import create_layer_nodes
from .import organize_layer_nodes
from .import set_material_shading

class COATER_OT_add_color_layer(Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_color_layer"
    bl_label = "Add Color Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new color layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.active_object

    def execute(self, context):
        coater_material_functions.ready_coater_material(context)
        create_channel_group_node.create_channel_group_node(context)
        add_layer_slot.add_layer_slot(context)
        create_layer_nodes.create_layer_nodes(context, 'COLOR_LAYER')
        organize_layer_nodes.organize_layer_nodes(context)
        link_layers.link_layers(context)

        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        layers[layer_index].type = 'COLOR_LAYER'

        set_material_shading.set_material_shading(context)

        return {'FINISHED'}
