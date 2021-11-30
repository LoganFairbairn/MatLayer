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
# This file contains operators that quickly bake common texture maps.

import bpy
from bpy.types import Operator

# Bakes all selected texture maps.
class COATER_OT_bake(Operator):
    bl_idname = "coater.bake"
    bl_label = "Bake"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        addon_preferences = context.preferences.addons["Coater"].preferences

        if addon_preferences.bake_ao:
            bpy.ops.coater.bake_ambient_occlusion()

        if addon_preferences.bake_curvature:
            bpy.ops.coater.bake_curvature()
        return {'FINISHED'}