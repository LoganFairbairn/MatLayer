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
import random
from .import add_layer_slot
from .import create_channel_group_node
from .import coater_material_functions
from .import link_layers
from .import create_layer_nodes
from .import organize_layer_nodes
from .import coater_node_info
from .import set_material_shading

class COATER_OT_add_image_layer(Operator):
    '''Adds a new blank image layer to the layer stack'''
    bl_idname = "coater.add_image_layer"
    bl_label = "Add Blank Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with a new blank image assigned to it"

    def execute(self, context):
        coater_material_functions.ready_coater_material(context)
        create_channel_group_node.create_channel_group_node(context)
        add_layer_slot.add_layer_slot(context)
        create_layer_nodes.create_layer_nodes(context, 'IMAGE_LAYER')
        organize_layer_nodes.organize_layer_nodes(context)
        link_layers.link_layers(context)
        
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        layers[layer_index].layer_type = 'IMAGE_LAYER'
        
        # Assign the image the name of the layer and a random number.
        layer_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))
        while bpy.data.images.get(layer_name) != None:
            layer_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

        # Create a new image, assign it to the node.
        bpy.ops.image.new(name=layer_name,
                          width=1024,
                          height=1024,
                          color=(0.0, 0.0, 0.0, 0.0),
                          alpha=True,
                          generated_type='BLANK',
                          float=False,
                          use_stereo_3d=False,
                          tiled=False)

        # Auto-save the image to the image folder (defined in addon preferences).
        bpy.data.images[layer_name].filepath = "G:/Projects/Coater/Layers/" + layer_name + ".png"
        bpy.data.images[layer_name].file_format = 'PNG'
        bpy.data.images[layer_name].save()

        # Put the image in the image node.
        node_group = coater_node_info.get_channel_node_group(context)
        color_node = node_group.nodes.get(layers[layer_index].color_node_name)
        color_node.image = bpy.data.images[layer_name]

        # Store the active image in the layer.
        layers[layer_index].color_image = bpy.data.images[layer_name]

        # Update the active paint slot to the new image.
        context.scene.tool_settings.image_paint.canvas = bpy.data.images[layer_name]

        # Set the material shading mode, so the user can see the changes.
        set_material_shading.set_material_shading(context)

        return {'FINISHED'}

class COATER_OT_add_empty_image_layer(Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_empty_image_layer"
    bl_label = "Add Empty Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with no image assigned to it"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        coater_material_functions.ready_coater_material(context)
        create_channel_group_node.create_channel_group_node(context)
        add_layer_slot.add_layer_slot(context)
        create_layer_nodes.create_layer_nodes(context, 'IMAGE_LAYER')
        organize_layer_nodes.organize_layer_nodes(context)
        link_layers.link_layers(context)
        set_material_shading.set_material_shading(context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'IMAGE_LAYER'

        return {'FINISHED'}

