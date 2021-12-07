# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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