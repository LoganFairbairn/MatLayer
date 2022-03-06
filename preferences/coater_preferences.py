# Coater preferences are defined and drawn to the add-on preferences window here.

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class COATER_AddonPreferences(AddonPreferences):
    bl_idname = "Coater"

    image_size_presets: bpy.props.EnumProperty(
        items=[('LR', "512x512", "Low resolution"),
               ('ONE_K', "1024x1024", "1k image size"),
               ('TWO_K', "2048x2048", "2K image size"),
               ('FOUR_K', "4096x4096", "4k image size")],
        name="Image Size Presets",
        description="Preset Sizes for images",
    )

    # Output Folders
    layer_folder: bpy.props.StringProperty(default="", name="Layers")
    bake_folder: bpy.props.StringProperty(default="", name="Bakes")
    export_textures_folder: bpy.props.StringProperty(default="", name="Exports")

    # Interface Settings
    show_color_picker: bpy.props.BoolProperty(default=False, name="Show Color Picker")
    show_color_palette: bpy.props.BoolProperty(default=False, name="Show Color Palette")
    show_brush_settings: bpy.props.BoolProperty(default=True, name="Show Brush Settings")

    # Layer Settings
    auto_delete_images: bpy.props.BoolProperty(default=True, name="Auto Delete Images")

    def draw(self, context):
        layout = self.layout
        addon_preferences = context.preferences.addons["Coater"].preferences
        
        layout.label(text="Custom output folders: ")
        layout.prop(addon_preferences, "layer_folder")
        layout.prop(addon_preferences, "bake_folder")
        layout.prop(addon_preferences, "export_textures_folder")

        layout.label(text="Tools")
        layout.prop(addon_preferences, "show_brush_settings")
        layout.prop(addon_preferences, "show_color_picker")
        layout.prop(addon_preferences, "show_color_palette")
        
        layout.label(text="Layers")
        layout.prop(addon_preferences, "auto_delete_images")