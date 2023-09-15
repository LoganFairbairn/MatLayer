# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty, CollectionProperty
from .core.mesh_map_baking import update_bake_width
from .core.texture_set_settings import TEXTURE_SET_RESOLUTIONS

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
    ("SUBSURFACE_COLOR", "Subsurface Color", "Subsurface Color"),
    ("METALLIC", "Metallic", "Metallic"),
    ("SPECULAR", "Specular", "Specular"),
    ("ROUGHNESS", "Roughness", "Roughness"),
    ("EMISSION", "Emission", "Emission"),
    ("NORMAL", "Normal", "Normal"),
    ("HEIGHT", "Height", "Height"),
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", "Ambient Occlusion"),
    ("CURVATURE", "Curvature", "Curvature"),
    ("THICKNESS", "Thickness", "Thickness"),
    ("BASE_NORMALS", "Base Normals", "Base Normals"),
    ("OPACITY", "Opacity", "Opacity"),
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
    ("JPG", "jpg", "Exports the selected material channel in JPG texture format. This is a compressed format, which could be used for textures applied to models that will be shown in a web browser"),
    ("TARGA", "tga", "Exports the selected material channel in TARGA texture format"),
    ("EXR", "exr", "Exports the selected material channel in open exr texture format")
]

MESH_MAP_QUALITY_SETTINGS = [
    ("LOW_QUALITY", "Low Quality (for testing)", "Extremly low quality baking, generally used only for testing baking functionality or previewing a really rough version of baked textures. Using this quality will significantly reduce time it takes to bake mesh maps"), 
    ("RECOMMENDED_QUALITY", "Recommended Quality", "The suggested quality for baking texture maps"),
    ("HIGH_QUALITY", "High Quality", "A higher than average baking quality. This should be used for when fine, accurate detail is required in mesh map textures. Using this quality will significantly slow down baking speeds")
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
    input_textures: PointerProperty(type=MATLAYER_pack_textures, name="Input Textures")
    input_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Input Pack Channels")
    output_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Output Pack Channels")
    image_format: EnumProperty(items=TEXTURE_EXPORT_FORMAT, default='PNG')
    bit_depth: EnumProperty(items=BIT_DEPTH, default='EIGHT')

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    #----------------------------- FILE MANAGEMENT PROPERTIES -----------------------------#

    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=True,
        description="Saves all imported textures to the 'Layers' folder. This helps provided a constant external folder for saving images used in layers which helps keep your files consistent."
    )

    auto_delete_unused_images: BoolProperty(
        name="Delete Unused Images on Export",
        default=True,
        description="Deletes all images not used within a layer or mask when textures are exported. This helps avoid unused images taking up memory, but could delete textures you intend to use in extremely rare cases."
    )

    layer_texture_folder_path: StringProperty(
        name="Layer Textures Folder",
        default="",
        description="Folder path where layer textures are saved. If this is blank, all layer textures will be saved to a 'Layer' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    mesh_map_texture_folder_path: StringProperty(
        name="Mesh Map Textures Folder",
        default="",
        description="Folder path where baked mesh maps are saved. If this is blank, all mesh maps will be saved to a 'MeshMaps' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    exported_textures_folder_path: StringProperty(
        name="Exported Textures Folder",
        default="",
        description="Folder path where exported textures are saved. If this is blank all exported textures will be saved to a 'Textures' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    #----------------------------- DEBUGGING -----------------------------#

    logging: BoolProperty(
        name="Debug Logging",
        default=True,
        description="Prints debugging info for functions this add-on runs in Blenders terminal."
    )

    #----------------------------- MESH MAP BAKING PROPERTIES -----------------------------#

    output_quality: EnumProperty(items=MESH_MAP_QUALITY_SETTINGS, name="Output Quality", description="Output quality of the baked mesh maps", default='RECOMMENDED_QUALITY')
    output_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS,name="Output Height",description="Image size for the baked texure map result(s)", default='TWOK', update=update_bake_width)
    output_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Output Height", description="Image size for the baked texure map result(s)", default='TWOK')
    bake_ambient_occlusion: BoolProperty(name="Bake Ambient Occlusion", description="Toggle for baking ambient occlusion as part of the batch baking operator", default=True)
    ambient_occlusion_image_name: StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: FloatProperty(name="Ambient Occlusion Intensity", description="", min=0.1, max=0.99, default=0.15)
    ambient_occlusion_samples: IntProperty(name="Ambient Occlusion Samples", description="The amount of samples for ambient occlusion taken", min=1, max=128, default=64)
    ambient_occlusion_local: BoolProperty(name="Local Ambient Occlusion", description="Ambient occlusion will not bake shadows cast by other objects", default=True)
    bake_curvature: BoolProperty(name="Bake Curvature", description="Toggle for baking curvature as part of the batch baking process", default=True)
    curvature_image_name: StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: FloatProperty(name="Edge Intensity", description="Brightens edges", min=0.0, max=10.0, default=3.0)
    curvature_edge_radius: FloatProperty(name="Edge Radius", description="Edge radius", min=0.001, max=0.1, default=0.01)
    curvature_ao_masking: FloatProperty(name="AO Masking", description="Mask the curvature edges using ambient occlusion", min=0.0, max=1.0, default=1.0)
    bake_thickness: BoolProperty(name="Bake Thickness", description="Toggle for baking thickness as part of the batch baking operator", default=True)
    thickness_samples: IntProperty(name="Thickness Samples", description="The amount of samples for thickness baking. Increasing this value will increase the quality of the output thickness maps", min=1, max=128, default=64)
    bake_normals: BoolProperty(name="Bake Normal", description="Toggle for baking normal maps for baking as part of the batch baking operator", default=True)
    cage_extrusion: FloatProperty(name="Cage Extrusion", description="Infaltes the active object by the specified amount for baking. This helps matching to points nearer to the outside of the selected object meshes", default=0.111, min=0.0, max=1.0)
    bake_bevel_normals: BoolProperty(name="Bake Bevel Normal", description="Toggle for baking a bevel normal map for baking as part of the batch baking operator", default=False)
    bake_world_space_normals: BoolProperty(name="Bake World Space Normals", description="Toggle for baking world space normals as part of the batch baking operator", default=True)

    #----------------------------- TEXTURE EXPORTING PROPERTIES -----------------------------#

    export_template_name: StringProperty(name="Export Template Name", default="Unreal Engine 4 (Metallic, Packed)")
    padding: IntProperty(name="Padding", default=16)
    export_textures: CollectionProperty(type=MATLAYER_texture_export_settings)
    delete_unpacked_images: BoolProperty(name="Delete Unpacked Images", default=True, description="Deletes unpacked image textures after packing")
    roughness_mode: EnumProperty(name="Roughness Mode", items=ROUGHNESS_MODE, default='ROUGHNESS')
    normal_map_mode: EnumProperty(name="Normal Map Mode", items=NORMAL_MAP_MODE, default='OPEN_GL')

    #----------------------------- DRAWING -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "logging")