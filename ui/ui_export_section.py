# This files handles drawing the exporting section's user interface.

import bpy
from ..ui import ui_section_tabs
from ..core import exporting
from .. import preferences

def draw_export_section_ui(self, context):
    '''Draws user interface for the export section.'''
    layout = self.layout

    ui_section_tabs.draw_section_tabs(self, context)
    export_settings = context.scene.matlayer_export_settings
    SCALE_Y = 1.4

    # Draw export texture tempaltes.
    # A dual column layout is used so the properties vertically align.
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
    row = second_column.row()
    row.scale_y = SCALE_Y
    row.prop(addon_preferences, "texture_export_template", text="")

    # Draw export button.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.operator("matlayer.export")
    row.operator("matlayer.open_export_folder", text="", icon='FILE_FOLDER')

    # Draw toggles for exporting material channels and a preview of their name.
    split = layout.split(factor=0.5)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.label(text="Output Textures")
    row = second_column.row()
    row.label(text="Export Image Name Preview")

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_base_color", text="")
    row.label(text="Base Color")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('COLOR')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_subsurface", text="")
    row.label(text="Subsurface")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('SUBSURFACE')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_subsurface_color", text="")
    row.label(text="Subsurface Color")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('SUBSURFACE_COLOR')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_metallic", text="")
    row.label(text="Metallic")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('METALLIC')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_specular", text="")
    row.label(text="Specular")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('SPECULAR')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_roughness", text="")
    row.label(text="Roughness")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('ROUGHNESS')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_emission", text="")
    row.label(text="Emission")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('EMISSION')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_normals", text="")
    row.label(text="Normals")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('NORMAL')
    row.label(text=export_image_name)

    row = first_column.row()
    row.scale_y = SCALE_Y
    row.prop(export_settings, "export_height", text="")
    row.label(text="Height")
    row = second_column.row()
    row.scale_y = SCALE_Y
    export_image_name = exporting.format_export_image_name('HEIGHT')
    row.label(text=export_image_name)
