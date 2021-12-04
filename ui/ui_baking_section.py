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

def draw_baking_section_ui(self, context):
    layout = self.layout
    baking_settings = context.scene.coater_baking_settings

    # Draw section tabs.
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw bake button.
    row = layout.row()
    row.operator("coater.bake")
    row.scale_y = 2.0

    # Draw baking types.
    scale_y = 1.4

    row = layout.row()
    row.prop(baking_settings, "bake_ambient_occlusion", text="")
    row.prop_enum(baking_settings, "bake_type", 'AMBIENT_OCCLUSION')
    row.operator("coater.bake_ambient_occlusion", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    row = layout.row()
    row.prop(baking_settings, "bake_curvature", text="")
    row.prop_enum(baking_settings, "bake_type", 'CURVATURE')
    row.operator("coater.bake_curvature", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    # Draw global bake settings.
    layout.label(text="Global Bake Settings:")

    split = layout.split()
    col = split.column()
    col.scale_y = scale_y
    col.prop(baking_settings, "output_width", text="")

    col = split.column()
    col.scale_y = scale_y
    if baking_settings.match_output_resolution:
        col.prop(baking_settings, "match_output_resolution", text="", icon="LOCKED")

    else:
        col.prop(baking_settings, "match_output_resolution", text="", icon="UNLOCKED")

    col = split.column()
    col.scale_y = scale_y
    if baking_settings.match_output_resolution:
        col.enabled = False
        
    col.prop(baking_settings, "output_height", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "output_quality", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")
    row.prop(bpy.data.scenes["Scene"].render.bake, "margin", slider=True)

    # Draw specific bake settings based on selected bake type.
    if baking_settings.bake_type == 'AMBIENT_OCCLUSION':
        layout.label(text="Ambient Occlusion Bake Settings:")
        layout.prop(baking_settings, "ambient_occlusion_intensity", slider=True)
        layout.prop(baking_settings, "ambient_occlusion_samples", slider=True)
        row = layout.row()
        row.prop(baking_settings, "ambient_occlusion_local")
        row.prop(baking_settings, "ambient_occlusion_inside")

    if baking_settings.bake_type == 'CURVATURE':
        layout.label(text="Curvature Bake Settings:")
        layout.prop(baking_settings, "curvature_edge_radius", slider=True)
        layout.prop(baking_settings, "curvature_edge_intensity", slider=True)

        # Ambient Occlusion Settings.
        layout.prop(baking_settings, "ambient_occlusion_intensity", slider=True)
        layout.prop(baking_settings, "ambient_occlusion_samples", slider=True)
        row = layout.row()
        row.prop(baking_settings, "ambient_occlusion_local")
        row.prop(baking_settings, "ambient_occlusion_inside")