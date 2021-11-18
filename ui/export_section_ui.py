import bpy
from .import draw_section_buttons

def draw_export_section_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences

    # Draw add-on section buttons.
    draw_section_buttons.draw_section_buttons(self, context)

    layout.prop(addon_preferences, "export_folder")

    scale_y = 1.4

    row = layout.row()
    row.operator("coater.export")
    row.scale_y = 2.0

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_base_color")
    row.operator("coater.export_base_color", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_roughness")
    row.operator("coater.export_roughness", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_metallic")
    row.operator("coater.export_metallic", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_normals")
    row.operator("coater.export_normals", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_emission")
    row.operator("coater.export_emission", text="", icon='RENDER_STILL')