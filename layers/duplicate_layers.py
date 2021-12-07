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

from os import dup
import bpy
from bpy.types import Operator
from .import add_layer_slot

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
        layer_index = context.scene.coater_layer_stack.layer_index

        # Duplicate layer information into a new layer.
        add_layer_slot.add_layer_slot(context)

        layer = layers[layer_index + 1]
        duplicate_layer = layers[layer_index]

        duplicate_layer.name = layer.name + " copy"
        duplicate_layer.type = layer.type
        duplicate_layer.projection = layer.projection
        duplicate_layer.mask_projection = layer.mask_projection
        duplicate_layer.opacity = layer.opacity


        # TODO: Create nodes for the duplicated layer.

        # TODO: Organize nodes.

        return{'FINISHED'}