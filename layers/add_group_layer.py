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

class COATER_OT_add_group_layer(Operator):
    '''Adds a new layer with a group layer to the layer stack.'''
    bl_idname = "coater.add_group_layer"
    bl_label = "Add Group Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new layer with a custom group node as the color value."

    @ classmethod
    def poll(cls, context):
        return False

    def execute(self, context):

        return {'FINISHED'}