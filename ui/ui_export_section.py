# This files handles drawing the exporting section's user interface.

import bpy
from .import ui_section_tabs
from .. import preferences

def draw_export_section_ui(self, context):
    '''Draws user interface for the export section.'''
    layout = self.layout

    ui_section_tabs.draw_section_tabs(self, context)

    # Draw export settings.
    export_settings = context.scene.matlay_export_settings
    
    scale_y = 1.4

    row = layout.row()
    row.operator("matlay.export")
    row.scale_y = 2.0

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_base_color", text="")
    row.label(text="Base Color")
    row.operator("matlay.export_base_color", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_subsurface", text="")
    row.label(text="Subsurface")
    row.operator("matlay.export_subsurface", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_subsurface_color", text="")
    row.label(text="Subsurface Color")
    row.operator("matlay.export_subsurface_color", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_metallic", text="")
    row.label(text="Metallic")
    row.operator("matlay.export_metallic", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_specular", text="")
    row.label(text="Specular")
    row.operator("matlay.export_specular", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_roughness", text="")
    row.label(text="Roughness")
    row.operator("matlay.export_roughness", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_emission", text="")
    row.label(text="Emission")
    row.operator("matlay.export_emission", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_normals", text="")
    row.label(text="Normals")
    row.operator("matlay.export_normals", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_height", text="")
    row.label(text="Height")
    row.operator("matlay.export_height", text="", icon='RENDER_STILL')


    # Draw additioanl export settings.
    # A dual column layout is used so the properties vertically align.
    row = layout.row()
    row.separator()
    layout.label(text="EXPORT TEXTURE NAME SETTINGS")
    addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
    split = layout.split(factor=0.35)
    first_column = split.column()
    first_column.scale_x = 0.1
    second_column = split.column()
    
    row = first_column.row()
    row.scale_y = scale_y
    row.label(text="Texture Name Format Mode:")
    row = second_column.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "texture_name_export_format", text="")

    row = first_column.row()
    row.scale_y = scale_y
    row.label(text="Texture Name Format:")
    row = second_column.row()
    row.scale_y = scale_y
    export_format_example = ""
    match addon_preferences.texture_name_export_format:
        case 'STANDARD':
            export_format_example = "ObjectName_MaterialChannelName"
        case 'UE_UNITY':
            export_format_example = "T_ObjectName_MaterialChannelAbreviation"
    row.label(text=export_format_example)

    '''
    row = first_column.row()
    row.scale_y = scale_y
    row.label(text="Prefix Mode:")
    row = second_column.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "texture_name_export_prefix_mode", text="")

    
    if addon_preferences.texture_name_export_prefix_mode == 'CUSTOM':
        row = first_column.row()
        row.scale_y = scale_y
        row.label(text="Texture Prefix:")
        row = second_column.row()
        row.scale_y = scale_y
        row.prop(export_settings, "texture_export_name", text="")
    '''




