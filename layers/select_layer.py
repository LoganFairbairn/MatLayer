import bpy
from bpy.types import Operator
from .import coater_node_info

class COATER_OT_select_layer_image(Operator):
    bl_idname = "coater.select_layer_image"
    bl_label = "Select Layer Image"
    bl_description = "Selects the layer image for the selected layer if one exists."

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        channel_node_group = coater_node_info.get_channel_node_group(context)

        if layers[layer_index].type == 'IMAGE_LAYER':
            if channel_node_group != None:
                color_node = channel_node_group.nodes.get(layers[layer_index].color_node_name)
                
                if color_node != None:
                    context.scene.tool_settings.image_paint.canvas = color_node.image
        return {'FINISHED'}

class COATER_OT_select_layer_mask(Operator):
    bl_idname = "coater.select_layer_mask"
    bl_label = "Select Layer Mask"
    bl_description = "Selects the layer mask image if one exists."

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        channel_node_group = coater_node_info.get_channel_node_group(context)

        if channel_node_group != None:
            mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)

            if mask_node != None:
                bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
                context.scene.tool_settings.image_paint.canvas = mask_node.image
        return {'FINISHED'}