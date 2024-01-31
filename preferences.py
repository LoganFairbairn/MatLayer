# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty

ADDON_NAME = __package__

BIT_DEPTH = [
    ("EIGHT", "8-bit", "8-bit depth is the standard color bit depth for games"),
    ("THIRTY_TWO", "32-bit", "32-bit uses more memory in RGB channels, but will result in less color banding (not visible on old monitors)")
]

NORMAL_MAP_MODE = [
    ("OPEN_GL", "OpenGL", "Normal maps will be exported in Open GL format (same as they are in Blender)"),
    ("DIRECTX", "DirectX", "Exported normal maps will have their green channel automatically inverted so they export in Direct X format")
]

ROUGHNESS_MODE = [
    ("ROUGHNESS", "Roughness", "Roughness will be exported as is."),
    ("SMOOTHNESS", "Smoothness", "Roughness textures will be converted (inverted) to smoothness textures before exporting / packing. This supports some software which uses smoothness maps (e.g. Unity).")
]

EXPORT_CHANNELS = [
    ("COLOR", "Color", "Color"),
    ("SUBSURFACE", "Subsurface", "Subsurface"),
    ("SUBSURFACE-TINT", "Subsurface Tint", "Subsurface Tint"),
    ("SUBSURFACE-RADIUS", "Subsurface Radius", "Subsurface Radius"),
    ("SUBSURFACE-SCALE", "Subsurface Scale", "Subsurface Scale"),
    ("SUBSURFACE-ANISOTROPY", "Subsurface Anisotropy", "Subsurface Anisotropy"),
    ("METALLIC", "Metallic", "Metallic"),
    ("SPECULAR", "Specular (IOR Level)", "Specular"),
    ("SPECULAR-TINT", "Specular Tint", "Specular Tint"),
    ("SPECULAR-ANISOTROPIC", "Specular Anisotropic", "Specular Anisotropic"),
    ("SPECULAR-ANISOTROPIC-ROTATION", "Specular Anisotropic Rotation", "Specular Anisotropic Rotation"),
    ("ROUGHNESS", "Roughness", "Roughness"),
    ("EMISSION", "Emission", "Emission"),
    ("NORMAL", "Normal", "Normal"),
    ("HEIGHT", "Height", "Height"),
    ("NORMAL_HEIGHT", "Normal + Height", "Normal + Height"),
    ("AMBIENT-OCCLUSION", "Ambient Occlusion", "Ambient Occlusion"),
    ("CURVATURE", "Curvature", "Curvature"),
    ("THICKNESS", "Thickness", "Thickness"),
    ("BASE_NORMALS", "Base Normals", "Base Normals"),
    ("WORLD_SPACE_NORMALS", "World Space Normals", "World Space Normals"),
    ("ALPHA", "Alpha", "Alpha"),
    ("IOR", "IOR / 4", "IOR / 4"),
    ("TRANSMISSION-WEIGHT", "Transmission Weight", "Transmission Weight"),
    ("COAT", "Coat", "Coat (a.k.a clear coat)"),
    ("COAT-ROUGHNESS", "Coat Roughness", "Coat Roughness"),
    ("COAT-IOR", "Coat IOR / 4", "Coat IOR / 4"),
    ("COAT-TINT", "Coat Tint", "Coat Tint"),
    ("COAT-NORMAL", "Coat Normal", "Coat Normal"),
    ("SHEEN", "Sheen", "Sheen"),
    ("SHEEN-ROUGHNESS", "Sheen Roughness", "Sheen"),
    ("SHEEN-TINT", "Sheen Tint", "Sheen Tint"),
    ("DISPLACEMENT", "Displacement", "Displacement"),
    ("NONE", "None", "None")
]

PACKING_COLOR_CHANNELS = [
    ("R", "R", "Red Channel"),
    ("G", "G", "Green Channel"),
    ("B", "B", "Blue Channel"),
    ("A", "A", "Alpha Channel")
]

TEXTURE_EXPORT_FORMAT = [
    ("PNG", "png", "Exports the selected material channel in png texture format. This is a non-compressed format, and generally a good default"),
    ("JPEG", "jpg", "Exports the selected material channel in JPG texture format. This is a compressed format, which could be used for textures applied to models that will be shown in a web browser"),
    ("TARGA", "tga", "Exports the selected material channel in TARGA texture format"),
    ("OPEN_EXR", "exr", "Exports the selected material channel in open exr texture format")
]

EXPORT_MODE = [
    ("ONLY_ACTIVE_MATERIAL", "Only Active Material", "Export only the active material to a texture set"),
    ("EXPORT_ALL_MATERIALS", "Export All Materials", "Exports every object on the active material as it's own texture set"),
    ("SINGLE_TEXTURE_SET", "Single Texture Set", "Bakes all materials in all texture slots on the active object to 1 texture set. Separating the final material into separate smaller materials assigned to different parts of the mesh and then baking them to a single texture set can be efficient for workflow, and can reduce shader compilation time while editing")
]

IMAGE_COLORSPACE_SETTINGS = [
    ("SRGB", "sRGB", ""),
    ("NON_COLOR", "Non-Color", "")
]

class MATLAYER_pack_textures(PropertyGroup):
    r_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name='R Texture')
    g_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name='G Texture')
    b_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name='B Texture')
    a_texture: EnumProperty(items=EXPORT_CHANNELS, default='NONE', name='A Texture')

class MATLAYER_RGBA_pack_channels(PropertyGroup):
    r_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='R', name="R")
    g_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='G', name="G")
    b_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='B', name="B")
    a_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='A', name="A")

class MATLAYER_texture_export_settings(PropertyGroup):
    name_format: StringProperty(name="Name Format", default="T_/MaterialName_C", description="Name format for the texture. You can add trigger words that will be automatically replaced upon export to name formats including: '/MaterialName', '/MeshName' ")
    image_format: EnumProperty(items=TEXTURE_EXPORT_FORMAT, default='PNG')
    bit_depth: EnumProperty(items=BIT_DEPTH, default='EIGHT')
    colorspace: EnumProperty(items=IMAGE_COLORSPACE_SETTINGS, default='SRGB')
    input_textures: PointerProperty(type=MATLAYER_pack_textures, name="Input Textures")
    input_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Input Pack Channels")
    output_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Output Pack Channels")

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    #----------------------------- FILE MANAGEMENT PROPERTIES -----------------------------#

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

    #----------------------------- DEBUGGING -----------------------------#

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

    #----------------------------- TEXTURE EXPORTING PROPERTIES -----------------------------#

    export_template_name: StringProperty(name="Export Template Name", default="PBR Metallic Roughness")
    export_textures: CollectionProperty(type=MATLAYER_texture_export_settings)
    roughness_mode: EnumProperty(name="Roughness Mode", items=ROUGHNESS_MODE, default='ROUGHNESS')
    normal_map_mode: EnumProperty(name="Normal Map Mode", items=NORMAL_MAP_MODE, default='OPEN_GL')
    export_mode: EnumProperty(name="Export Active Material", items=EXPORT_MODE, description="Exports only the active material using the defined export settings", default='SINGLE_TEXTURE_SET')

    #----------------------------- TEXTURE PROPERTIES -----------------------------#

    thirty_two_bit: BoolProperty(
        name="32 Bit Color", 
        description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients", 
        default=True
    )

    #----------------------------- DRAWING -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_main_operations")
        layout.prop(self, "log_sub_operations")
        layout.prop(self, "save_imported_textures")
        layout.prop(self, "auto_save_images")
        layout.prop(self, "image_auto_save_interval")