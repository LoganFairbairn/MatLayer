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


class COATER_properties(bpy.types.PropertyGroup):
    coater_sections: bpy.props.EnumProperty(
        items=[('SECTION_LAYERS', "Layers", "Layers category."),
               ('SECTION_BAKING', "Baking", ""),
               ('SECTION_DISPLAY', "Display", ""),
               ('SECTION_COATER_SETTINGS', "Settings", "")
               ],
        name="Coater Sections",
        description="Current coater category"
    )


class COATER_PT_Panel(bpy.types.Panel):
    bl_label = "Coater " + "1.0"
    bl_idname = "COATER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Coater"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        coater_properties = scene.coater_properties

        # Color Picker

        # Brush Presets (seperate panel)

        if coater_properties.coater_sections == "SECTION_LAYERS":
            # Draw add-on section buttons.
            row = layout.row()
            layout.prop(coater_properties, "coater_sections", expand=True)

            # TODO: Show the currently selected material name.
            row = layout.row()
            layout.label(text=bpy.context.active_object.active_material.name)

            # Export to image editor.
            row = layout.row()
            row.operator("coater.image_editor_export", icon="EXPORT")

            # TODO: Draw selected material.

            # TODO: Layers Channel

            # Layer Operations
            row = layout.row()
            row.operator("coater.add_color_layer", icon="COLOR")
            row.operator("coater.merge_layer", icon="TRIA_DOWN_BAR")
            row.operator("coater.duplicate_layer", icon="DUPLICATE")
            row.operator("coater.move_layer",
                         icon="TRIA_UP").direction = 'UP'
            row.operator("coater.move_layer",
                         icon="TRIA_DOWN").direction = 'DOWN'
            row.operator("coater.delete_layer", icon="TRASH")
            row.scale_y = 2.0
            row.alignment = 'EXPAND'

            # Draw Layer Stack
            row = layout.row()
            row.template_list("COATER_UL_layer_list", "The_List",
                              scene, "my_list", scene, "layer_index")

        if coater_properties.coater_sections == "SECTION_BAKING":
            # Draw add-on section buttons.
            layout.prop(coater_properties, "coater_sections", expand=True)

            # Color Grid
            row = layout.row()
            row.operator("coater.apply_color_grid")

            # Ambient Occlusion
            row = layout.row()
            row.operator("coater.bake_ambient_occlusion")

        if coater_properties.coater_sections == "SECTION_DISPLAY":
            # Draw add-on section buttons.
            layout.prop(coater_properties, "coater_sections", expand=True)

            row = layout.row()
            row.operator("material.set_hand_painted")

        if coater_properties.coater_sections == "SECTION_COATER_SETTINGS":
            # Draw add-on section buttons.
            layout.prop(coater_properties, "coater_sections", expand=True)
