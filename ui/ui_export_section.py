# This files handles drawing the exporting section's user interface.

import bpy
from ..ui import ui_section_tabs
from .. import preferences

def draw_export_section_ui(self, context):
    '''Draws user interface for the export section.'''
    layout = self.layout

    ui_section_tabs.draw_section_tabs(self, context)
    SCALE_Y = 1.4

    # Draw export button.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.operator("matlayer.export")
    row.operator("matlayer.open_export_folder", text="", icon='FILE_FOLDER')

    # Draw export texture settings.
    row = layout.row()
    row.separator()
    addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
    split = layout.split(factor=0.2)
    first_column = split.column()
    first_column.scale_x = 0.1
    second_column = split.column()
    
    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Export Template:")
    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "export_template_name", text="")
    row.menu("MATLAYER_MT_export_template_menu", text="Load Template", icon='FILE_TICK')

    # Saving export templates will be implemented in the future.
    #row.operator("matlayer.save_export_template", text="", icon='FILE_NEW')

    row = layout.row(align=True)
    row.scale_y = SCALE_Y
    row.operator("matlayer.add_export_texture", text="Add Export Texture")

    # Split layout into 2 columns.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.alignment = 'LEFT'
    row.label(text="Texture Settings")

    row = second_column.row()
    row.alignment = 'RIGHT'
    row.label(text="Channel Packing")

    # Draw settings for textures that will be exported.
    for i, channel in enumerate(addon_preferences.export_channels):

        # Draw texture settings.
        col = first_column.column(align=True)
        col.prop(channel, "name_format", text="")
        col.prop(channel, "image_format", text="", emboss=True)
        col.prop(channel, "bit_depth", text="", emboss=True)

        # Draw channel packing settings.
        split = second_column.split(factor=0.2)
        col_1 = split.column(align=True)
        col_1.alignment = 'RIGHT'
        col_1.label(text="In Texture")
        col_1.label(text="In  RGBA")
        col_1.label(text="Out RGBA")

        col_2 = split.column(align=True)
        split = col_2.split(factor=0.9)
        col_1 = split.column(align=True)

        row = col_1.row(align=True)
        row.prop(channel, "r_input_texture", text="")
        row.prop(channel, "g_input_texture", text="")
        row.prop(channel, "b_input_texture", text="")
        row.prop(channel, "a_input_texture", text="")

        row = col_1.row(align=True)
        row.prop(channel, "r_pack_input_color_channel", text="")
        row.prop(channel, "g_pack_input_color_channel", text="")
        row.prop(channel, "b_pack_input_color_channel", text="")
        row.prop(channel, "a_pack_input_color_channel", text="")

        row = col_1.row(align=True)
        row.prop(channel, "r_pack_output_color_channel", text="")
        row.prop(channel, "g_pack_output_color_channel", text="")
        row.prop(channel, "b_pack_output_color_channel", text="")
        row.prop(channel, "a_pack_output_color_channel", text="")

        col = split.column()
        op = col.operator("matlayer.remove_export_texture", icon='X', text="")
        op.export_texture_index = i

    layout.separator()
    row = layout.row()
    row.label(text="Additional Settings")

    split = layout.split(factor=0.3)
    first_column = split.column()
    first_column.scale_x = 0.1
    second_column = split.column()

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Normal Map Mode: ")
    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.prop_enum(addon_preferences, "normal_map_mode", 'OPEN_GL')
    row.prop_enum(addon_preferences, "normal_map_mode", 'DIRECTX')

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Padding: ")
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "padding", text="")

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Delete Unpacked Images: ")
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "delete_unpacked_images", text="")
