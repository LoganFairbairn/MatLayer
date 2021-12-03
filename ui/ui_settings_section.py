import bpy
from .import ui_section_tabs

def draw_settings_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences
    
    ui_section_tabs.draw_section_tabs(self, context)    # Draw section buttons.
    scale_y = 1.4

    layout.label(text="Custom Output folders: ")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "layer_folder")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "bake_folder")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(addon_preferences, "export_textures_folder")

    layout.prop(addon_preferences, "show_brush_settings")
    layout.prop(addon_preferences, "show_color_picker")
    layout.prop(addon_preferences, "show_color_palette")