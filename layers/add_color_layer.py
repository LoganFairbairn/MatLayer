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
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        coater_material_functions.ready_coater_material(context)
        create_channel_group_node.create_channel_group_node(context)
        add_layer_slot.add_layer_slot(context)
        create_layer_nodes.create_layer_nodes(context, 'COLOR_LAYER')
        organize_layer_nodes.organize_layer_nodes(context)
        link_layers.link_layers(context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'COLOR_LAYER'

        set_material_shading.set_material_shading(context)

        return {'FINISHED'}
