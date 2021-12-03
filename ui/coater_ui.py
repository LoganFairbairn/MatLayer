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
# This file handles the coater user interface.

import bpy
from .import ui_layer_section
from .import ui_baking_section
from .import ui_export_section
from .import ui_settings_section

class COATER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_LAYERS', "Layers", "This section contains a layer stack for the active material."),
               ('SECTION_BAKE', "Bake", "This section contains operations to quickly bake common texture maps for your model."),
               ('SECTION_EXPORT', "Export", "This section contains operations to quickly export textures made with Coater."),
               ('SECTION_SETTINGS', "Settings", "This section contains Coater Settings.")],
        name="Coater Sections",
        description="Current coater category",
        default='SECTION_LAYERS'
    )

class COATER_PT_Panel(bpy.types.Panel):
    bl_label = "Coater " + "0.6"
    bl_idname = "COATER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Coater"

    def draw(self, context):
        panel_properties = context.scene.coater_panel_properties

        if check_blend_saved():
            if panel_properties.sections == "SECTION_LAYERS":
                ui_layer_section.draw_layers_section_ui(self, context)

            if panel_properties.sections == "SECTION_BAKE":
                ui_baking_section.draw_baking_section_ui(self, context)

            if panel_properties.sections == 'SECTION_EXPORT':
                ui_export_section.draw_export_section_ui(self, context)

            if panel_properties.sections == 'SECTION_SETTINGS':
                ui_settings_section.draw_settings_ui(self, context)

        else:
            layout = self.layout
            layout.label(text="Save your .blend file to use Coater.")

def check_blend_saved():
    if bpy.path.abspath("//") == "":
        return False
    else:
        return True