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
# This file draws section tabs.

import bpy

def draw_section_tabs(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    #row.prop(panel_properties, "sections", expand=True)
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", 'SECTION_BAKE')
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')
    row.prop_enum(panel_properties, "sections", 'SECTION_SETTINGS', text="", icon="SETTINGS")
    row.scale_y = 2.0
