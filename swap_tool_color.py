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

# This file handles custom settings and operators related to tools.

import bpy

class COATER_OT_swap_primary_color(bpy.types.Operator):
    '''Swaps the primary color with the secondary color'''
    bl_idname = "coater.swap_primary_color"
    bl_label = ""
    bl_description = "Swaps the primary color with the secondary color."

    def execute(self, context):
        scene = context.scene
        color = scene.tool_settings.unified_paint_settings.color
        primary_color = (color.r, color.g, color.b)
        scene.tool_settings.unified_paint_settings.color = scene.tool_settings.unified_paint_settings.secondary_color
        scene.tool_settings.unified_paint_settings.secondary_color = primary_color
        
        return{'FINISHED'}