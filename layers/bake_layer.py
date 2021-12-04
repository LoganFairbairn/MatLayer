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

class COATER_OT_bake_layer(Operator):
    '''Bakes the selected layer to an image layer.'''
    bl_idname = "coater.bake_layer"
    bl_label = "Bake Layer"
    bl_description = "Bakes the selected layer to an image layer."

    @ classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}