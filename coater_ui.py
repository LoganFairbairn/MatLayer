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

class COATER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_LAYERS', "Layers", "Layers category"),
               ('SECTION_BAKING', "Baking", "Baking category"),
               ('SECTION_COATER_SETTINGS', "Settings", "Settings category")],
        name="Coater Sections",
        description="Current coater category",
        default='SECTION_LAYERS'
    )

class COATER_PT_Panel(bpy.types.Panel):
    bl_label = "Coater " + "0.1"
    bl_idname = "COATER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Coater"

    def draw(self, context):
        panel_properties = context.scene.coater_panel_properties

        if panel_properties.sections == "SECTION_LAYERS":
            draw_layer_stack_ui(self, context)

        if panel_properties.sections == "SECTION_BAKING":
            draw_baking_ui(self, context)

        if panel_properties.sections == "SECTION_COATER_SETTINGS":
            draw_setting_ui(self, context)

def draw_layer_stack_ui(self, context):
    layout = self.layout
    scene = context.scene
    panel_properties = context.scene.coater_panel_properties
    active_object = context.active_object

    # Draw add-on section buttons.
    row = layout.row()
    row.prop(panel_properties, "sections", expand=True)
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
    row.prop(scene.tool_settings.unified_paint_settings, "secondary_color", text="")
    row.operator("coater.swap_primary_color", icon='UV_SYNC_SELECT')

    # TODO: Draw Brush *Presets* ONLY

    # Draw curently selected material AND dropdown list of attached materials.
    row = layout.row()
    if active_object != None:
        if active_object.active_material != None:
            row.template_ID(active_object, "active_material")

        else:
            layout.label(text="No active material")

    else:
        layout.label(text="No object selected.")

    row.operator("coater.refresh_layers", icon='FILE_REFRESH')

    # Layer Operations
    row = layout.row(align=True)
    row.operator("coater.add_layer_menu", icon="ADD")
    row.operator("coater.add_mask_menu", icon="MOD_MASK")
    row.operator("coater.edit_layer_properties", icon='PROPERTIES')
    row.operator("coater.move_layer_up", icon="TRIA_UP")
    row.operator("coater.move_layer_down", icon="TRIA_DOWN")
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
    row = layout.row(align=True)
    row.template_list("COATER_UL_layer_list", "The_List", scene, "coater_layers", scene.coater_layer_stack, "layer_index")
    row.scale_y = 2

def draw_baking_ui(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row()
    row.prop(panel_properties, "sections", expand=True)
    row.scale_y = 2.0

    # Color Grid
    scale = 1.4
    row = layout.row()
    row.operator("coater.apply_color_grid")
    row.scale_y = scale

    # Bake Common Maps
    row = layout.row()
    row.operator("coater.bake_common_maps")
    row.scale_y = scale

    # Ambient Occlusion
    row = layout.row()
    row.operator("coater.bake_ambient_occlusion")
    row.scale_y = scale

    # Curvature
    row = layout.row()
    row.operator("coater.bake_curvature")
    row.scale_y = scale

    # Bake Edges
    row = layout.row()
    row.operator("coater.bake_edges")
    row.scale_y = scale

def draw_setting_ui(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row()
    row.prop(panel_properties, "sections", expand=True)
    row.scale_y = 2.0

    # TODO: Draw coater settings (addon preferences)
