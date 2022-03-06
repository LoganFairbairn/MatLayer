# This files handles drawing the exporting section's user interface.

import bpy
from .import ui_section_tabs

def draw_export_section_ui(self, context):
    layout = self.layout

    ui_section_tabs.draw_section_tabs(self, context)

    # Draw export settings.
    export_settings = context.scene.coater_export_settings
    
    layout.label(text="NOT YET IMPLEMENTED")

    scale_y = 1.4

    row = layout.row()
    row.operator("coater.export")
    row.scale_y = 2.0

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_base_color")
    row.operator("coater.export_base_color", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_roughness")
    row.operator("coater.export_roughness", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_metallic")
    row.operator("coater.export_metallic", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_normals")
    row.operator("coater.export_normals", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_emission")
    row.operator("coater.export_emission", text="", icon='RENDER_STILL')