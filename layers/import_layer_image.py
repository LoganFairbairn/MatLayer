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

import os
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
from .import coater_node_info
from .import organize_layer_nodes

class COATER_OT_import_color_image(Operator, ImportHelper):
    bl_idname = "coater.import_color_image"
    bl_label = "Import Color Image"
    bl_description = "Opens a menu that allows the user to import a color image."

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        bpy.ops.image.open(filepath=self.filepath)

        layers[layer_index].color_image_name = self.filepath

        # Put the image in the node.
        group_node = coater_node_info.get_channel_node_group(context)
        color_node_name = layers[layer_index].color_node_name
        color_node = group_node.nodes.get(color_node_name)

        if (color_node != None):
            color_node.image = bpy.data.images[image_name]

        organize_layer_nodes.organize_layer_nodes(context)
        
        return {'FINISHED'}

class COATER_OT_import_mask_image(Operator, ImportHelper):
    bl_idname = "coater.import_mask_image"
    bl_label = "Import Mask Image"
    bl_description = "Opens a menu that allows the user to import an image to use as a mask"
    
    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        bpy.ops.image.open(filepath=self.filepath)
        
        group_node = coater_node_info.get_channel_node_group(context)
        mask_node = group_node.nodes.get(layers[layer_index].mask_node_name)

        if mask_node != None:
            mask_node.image = bpy.data.images[image_name]

        organize_layer_nodes.organize_layer_nodes(context)
        
        return {'FINISHED'}
