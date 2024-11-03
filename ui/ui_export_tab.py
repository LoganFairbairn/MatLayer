# This files handles drawing the exporting section's user interface.

import bpy
from bpy.types import Menu
from . import ui_tabs
from ..core import material_layers

def draw_export_tab_ui(self, context):
    '''Draws user interface for the export section.'''
    layout = self.layout

    ui_tabs.draw_addon_tabs(self, context)

    # Draw export button.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.operator("matlayer.export", text="Export Texture")

    # Draw a warning for users using their CPU to export textures.
    scene = bpy.data.scenes["Scene"]
    if scene.cycles.device == 'CPU':
        row = layout.row()
        row.separator()
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Exporting is slow with CPUs, it's recommended to use your GPU.", icon='ERROR')
        row = layout.row()
        row.separator()

    # Split the UI into a two column layout.
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()
    
    # Draw the render device.
    row = first_column.row()
    row.label(text="Render Device")
    row = second_column.row()
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    # Draw the export folder.
    baking_settings = bpy.context.scene.matlayer_baking_settings
    texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
    row = first_column.row()
    row.label(text="Export Folder")
    row = second_column.row(align=True)
    row.prop(bpy.context.scene, "matlayer_export_folder", text="")
    row.operator("matlayer.set_export_folder", text="", icon='FOLDER_REDIRECT')
    row.operator("matlayer.open_export_folder", text="", icon='FILE_FOLDER')

    # Draw the export template options.
    row = first_column.row()
    row.label(text="Export Template")
    row = second_column.row(align=True)
    row.prop(texture_export_settings, "export_template_name", text="")
    row.menu("MATLAYER_MT_export_template_menu", text="Load Template")
    row.menu("MATLAYER_MT_export_setting_utility_sub_menu", text="", icon='DOWNARROW_HLT')

    # Draw the export mode.
    row = first_column.row()
    row.label(text="Export Mode")
    row = second_column.row()
    row.prop(texture_export_settings, "export_mode", text="")
    
    row = first_column.row()
    row.label(text="Normal Map Mode")
    row = second_column.row(align=True)
    row.prop_enum(texture_export_settings, "normal_map_mode", 'OPEN_GL')
    row.prop_enum(texture_export_settings, "normal_map_mode", 'DIRECTX')

    row = first_column.row()
    row.label(text="Roughness Mode")
    row = second_column.row(align=True)
    row.prop_enum(texture_export_settings, "roughness_mode", 'ROUGHNESS')
    row.prop_enum(texture_export_settings, "roughness_mode", 'SMOOTHNESS')

    row = first_column.row()
    row.label(text="UV Padding")
    row = second_column.row()
    row.prop(baking_settings, "uv_padding", text="")
    
    active_object = bpy.context.active_object
    if active_object:
        export_uv_map_node = material_layers.get_material_layer_node('EXPORT_UV_MAP')
        if export_uv_map_node:
            row = first_column.row()
            row.label(text="Export UV Map")
            row = second_column.row()
            row.prop_search(export_uv_map_node, "uv_map", active_object.data, "uv_layers", text="")

    # Draw export textures and their settings.
    row = first_column.row()
    row.scale_y = 1.5
    row.label(text="EXPORT TEXTURES")
    row = second_column.row(align=True)
    row.scale_x = 1.5
    row.scale_y = 1.5
    row.alignment = 'RIGHT'
    row.operator("matlayer.add_export_texture", text="", icon='ADD')

    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()
    for i, texture in enumerate(texture_export_settings.export_textures):

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
        col_1.label(text="Textures")
        col_1.label(text="In / Out")

        col_2 = split.column(align=True)
        split = col_2.split(factor=0.9)
        col_1 = split.column(align=True)

        # Draw menus with shader channels that can be used as inputs for RGBA channel packing.
        row = col_1.row(align=True)
        for key in texture.pack_textures.__annotations__.keys():
            row.prop(texture.pack_textures, key, text="")
        
        # Draw RGBA channels for desired input and output channels.
        row = col_1.row(align=True)
        for key in texture.input_rgba_channels.__annotations__.keys():
            row.prop(texture.input_rgba_channels, key, text="")
            row.prop(texture.output_rgba_channels, key, text="")

        col = split.column()
        col.ui_units_x = 0.7
        op = col.operator("matlayer.remove_export_texture", icon='X', text="")
        op.export_texture_index = i

class ExportSettingUtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_export_setting_utility_sub_menu"
    bl_label = "Export Setting Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.save_export_template", text="Save Export Template", icon='FILE_TICK')
        layout.operator("matlayer.refresh_export_template_list", text="Refresh Export Template List", icon='FILE_REFRESH')
        layout.operator("matlayer.delete_export_template", text="Delete Export Template", icon='TRASH')