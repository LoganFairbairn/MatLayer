# This files handles drawing the exporting section's user interface.

import bpy
from .import ui_section_tabs

def draw_export_section_ui(self, context):
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
    row.prop(export_settings, "export_folder")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_base_color", text="")
    row.operator("matlay.export_base_color", text="Export Base Color", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_metallic", text="")
    row.operator("matlay.export_metallic", text="Export Metallic", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_roughness", text="")
    row.operator("matlay.export_roughness", text="Export Roughness", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_normals", text="")
    row.operator("matlay.export_normals", text="Export Normals", icon='RENDER_STILL')

    #row = layout.row()
    #row.scale_y = scale_y
    #row.prop(export_settings, "export_height", text="")
    #row.operator("matlay.export_height", text="Export Height", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_emission", text="")
    row.operator("matlay.export_emission", text="Export Emission", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(export_settings, "export_scattering", text="")
    row.operator("matlay.export_scattering", text="Export Scattering", icon='RENDER_STILL')