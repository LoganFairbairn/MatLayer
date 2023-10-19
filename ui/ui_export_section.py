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
    
    # Export mode.
    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Export Template")
    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "export_template_name", text="")
    row.menu("MATLAYER_MT_export_template_menu", text="Load Template", icon='FILE_TICK')
    row.operator("matlayer.save_export_template", text="", icon='FILE_TICK')
    row.operator("matlayer.refresh_export_template_list", text="", icon='FILE_REFRESH')
    row.operator("matlayer.delete_export_template", text="", icon='TRASH')

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Export Mode")
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "export_mode", text="")

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Render Device")
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Normal Map Mode")
    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.prop_enum(addon_preferences, "normal_map_mode", 'OPEN_GL')
    row.prop_enum(addon_preferences, "normal_map_mode", 'DIRECTX')

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="Roughness Mode")
    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.prop_enum(addon_preferences, "roughness_mode", 'ROUGHNESS')
    row.prop_enum(addon_preferences, "roughness_mode", 'SMOOTHNESS')

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.label(text="UV Padding")
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "uv_padding", text="")

    # Split layout into 2 columns.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.alignment = 'LEFT'
    row.label(text="EXPORT TEXTURE SETTINGS")

    row = second_column.row(align=True)
    row.scale_y = SCALE_Y
    row.alignment = 'RIGHT'
    row.operator("matlayer.add_export_texture", text="Add Export Texture")

    # Draw settings for textures that will be exported.
    for i, texture in enumerate(addon_preferences.export_textures):

        # Draw texture settings.
        col = first_column.column(align=True)
        col.prop(texture, "name_format", text="")
        row = col.row(align=True)
        row.prop(texture, "image_format", text="", emboss=True)
        row.prop(texture, "colorspace", text="", emboss=True)
        row.prop(texture, "bit_depth", text="", emboss=True)

        # Draw channel packing settings.
        split = second_column.split(factor=0.2)
        col_1 = split.column(align=True)
        col_1.alignment = 'RIGHT'
        col_1.label(text="In Texture")
        col_1.label(text="In / Out")

        col_2 = split.column(align=True)
        split = col_2.split(factor=0.9)
        col_1 = split.column(align=True)

        row = col_1.row(align=True)
        for key in texture.input_textures.__annotations__.keys():
            row.prop(texture.input_textures, key, text="")

        row = col_1.row(align=True)
        for key in texture.input_rgba_channels.__annotations__.keys():
            row.prop(texture.input_rgba_channels, key, text="")
            row.prop(texture.output_rgba_channels, key, text="")

        col = split.column()
        op = col.operator("matlayer.remove_export_texture", icon='X', text="")
        op.export_texture_index = i
