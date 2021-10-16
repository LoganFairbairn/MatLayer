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
               ('SECTION_COATER_SETTINGS', "Settings", "")],
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
        active_object = bpy.context.active_object
        coater_properties = scene.coater_properties
        
        ###################################################################################################
        if coater_properties.coater_sections == "SECTION_LAYERS":
            # Draw add-on section buttons.
            row = layout.row()
            row.prop(coater_properties, "coater_sections", expand=True)
            row.scale_y = 2.0

            # Draw Color Picker
            row = layout.row()
            row.template_color_picker(bpy.context.scene.tool_settings.unified_paint_settings, "color")

            # Draw Color Palette
            if context.tool_settings.image_paint.palette:
                layout.template_palette(context.tool_settings.image_paint, "palette", color=True)

            # Draw Primary & Secondary Colors
            row = layout.row(align=True)
            row.prop(scene.tool_settings.unified_paint_settings, "color", text="")
            row.prop(scene.tool_settings.unified_paint_settings, "color", text="")
            row.operator("coater.swap_primary_color", icon='UV_SYNC_SELECT')

            # TODO: Draw Brush *Presets* ONLY

            # TODO: Draw curently selected material AND dropdown list of all materials.
            row = layout.row()
            if active_object != None:
                if active_object.active_material != None:
                    row.template_ID(active_object, "active_material")

                else:
                    layout.label(text="No active material")

            else:
                layout.label(text="No object selected.")

            # Layer Operations
            row = layout.row(align=True)
            row.operator("coater.add_layer_menu", icon="ADD")
            row.operator("coater.add_mask_menu", icon="MOD_MASK")
            row.operator("coater.edit_layer_properties", icon='PROPERTIES')
            row.operator("coater.move_layer", icon="TRIA_UP")
            row.operator("coater.move_layer", icon="TRIA_DOWN")
            row.operator("coater.duplicate_layer", icon="DUPLICATE")
            row.operator("coater.merge_layer", icon="AUTOMERGE_OFF")
            row.operator("coater.image_editor_export", icon="EXPORT")
            row.operator("coater.delete_layer", icon="TRASH")
            row.scale_y = 2.0
            row.scale_x = 2

            # Channels
            row = layout.row()
            row.prop(scene.coater_layer_stack, "channel")
            if scene.coater_layer_stack.channel_preview == False:
                row.operator("coater.toggle_channel_preview", icon='MATERIAL')

            elif scene.coater_layer_stack.channel_preview == True:
                row.operator("coater.toggle_channel_preview", icon='MATERIAL', depress=True)
            row.scale_x = 2
            row.scale_y = 1.4

            # Draw Layer Stack
            row = layout.row()
            row.template_list("COATER_UL_layer_list", "The_List", scene, "coater_layers", scene.coater_layer_stack, "layer_index")
            row.scale_y = 2

        ###################################################################################################
        if coater_properties.coater_sections == "SECTION_BAKING":
            # Draw add-on section buttons.
            row = layout.row()
            row.prop(coater_properties, "coater_sections", expand=True)
            row.scale_y = 2.0

            # Color Grid
            scale = 1.4
            row = layout.row()
            row.operator("coater.apply_color_grid")
            row.scale_y = scale

            row = layout.row()
            row.operator("coater.bake_common_maps")
            row.scale_y = scale

            # Ambient Occlusion
            row = layout.row()
            row.operator("coater.bake_ambient_occlusion")
            row.scale_y = scale

            row = layout.row()
            row.operator("coater.bake_curvature")
            row.scale_y = scale

            row = layout.row()
            row.operator("coater.bake_edges")
            row.scale_y = scale

        ###################################################################################################
        if coater_properties.coater_sections == "SECTION_COATER_SETTINGS":
            # Draw add-on section buttons.
            row = layout.row()
            row.prop(coater_properties, "coater_sections", expand=True)
            row.scale_y = 2.0
