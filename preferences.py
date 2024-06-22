# This module contains user preference settings for this add-on.

from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty

ADDON_NAME = __package__

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME
    
    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=False,
        description="When true, all textures imported through operators in this add-on will be saved to an external folder named 'Raw Textures' next to the blend file. This helps manage texture files used in materials by keeping all of them in a constant location next to the blend file in which they are used."
    )

    auto_save_images: BoolProperty(
        name="Auto Save Images",
        default=False,
        description="[RESTART BLENDER TO APPLY] If true, all images in the blend file that have defined paths, and require saving will be auto-saved at regular intervals."
    )

    image_auto_save_interval: IntProperty(
        name="Image Auto Save Interval",
        default=300,
        description="The interval in seconds for saving all images stored in the blend file"
    )

    log_main_operations: BoolProperty(
        name="Log Main Operations",
        default=True,
        description="When enabled, debug info for main functions ran by this add-on will be printed to Blenders terminal"
    )

    log_sub_operations: BoolProperty(
        name="Log Sub Processes",
        default=True,
        description="When enabled, debug info for secondary / smaller functions ran by this add-on will be printed to Blenders terminal"
    )

    thirty_two_bit: BoolProperty(
        name="32 Bit Color", 
        description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients", 
        default=True
    )

    #----------------------------- ADDON PREFERENCE MENU -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_main_operations")
        layout.prop(self, "log_sub_operations")
        layout.prop(self, "save_imported_textures")
        layout.prop(self, "auto_save_images")
        layout.prop(self, "image_auto_save_interval")