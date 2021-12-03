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
from .import ui_section_tabs

def draw_export_section_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences

    # Draw add-on section buttons.
    ui_section_tabs.draw_section_tabs(self, context)
    
    scale_y = 1.4

    row = layout.row()
    row.operator("coater.export")
    row.scale_y = 2.0

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_base_color")
    row.operator("coater.export_base_color", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_roughness")
    row.operator("coater.export_roughness", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_metallic")
    row.operator("coater.export_metallic", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_normals")
    row.operator("coater.export_normals", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_emission")
    row.operator("coater.export_emission", text="", icon='RENDER_STILL')