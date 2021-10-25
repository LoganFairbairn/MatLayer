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

    image_folder: bpy.props.StringProperty(default="", name="Image Folder")
    use_32_bit: bpy.props.BoolProperty(default=False, name="Use 32-bit by default.")
    pack_images: bpy.props.BoolProperty(default=False, name="Pack Images", description="When this option is enabled, images will be saved with the .blend file by default. Packed images can not use the 'export to external image edit' function.")
    organize_nodes: bpy.props.BoolProperty(default=False, name="Organize Nodes", description="Automatically organize nodes when the layer stack is changed.")
    show_color_picker: bpy.props.BoolProperty(default=False, name="Show Color Picker")
    show_color_palette: bpy.props.BoolProperty(default=False, name="Show Color Palette")
    show_brush_colors: bpy.props.BoolProperty(default=True, name="Show Brush Colors")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "image_folder")
        
# TODO: EXAMPLE DELETE LATER
class COATER_OT_addon_preferences(Operator):
    '''Display example preferences'''
    bl_idname = "coater.addon_preferences"
    bl_label = "Add-on Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_preferences = context.preferences.addons["Coater"].preferences
        
        info = "Image Folder: " + addon_preferences.image_folder

        return {'FINISHED'}