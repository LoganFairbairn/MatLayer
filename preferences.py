# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty, CollectionProperty
from .core.mesh_map_baking import update_bake_width, update_occlusion_samples, update_occlusion_distance, update_occlusion_contrast, update_curvature_bevel_radius, update_curvature_bevel_samples, update_curvature_edge_intensity, update_curvature_occlusion_masking
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
    ("ALPHA", "Alpha", "Alpha"),
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

EXPORT_MODE = [
    ("ONLY_ACTIVE_MATERIAL", "Only Active Material", "Export only the active material to a texture set"),
    ("EXPORT_ALL_MATERIALS", "Export All Materials", "Exports every object on the active material as it's own texture set"),
    ("SINGLE_TEXTURE_SET", "Single Texture Set", "Bakes all materials in all texture slots on the active object to 1 texture set. Separating the final material into separate smaller materials assigned to different parts of the mesh and then baking them to a single texture set can be efficient for workflow, and can reduce shader compilation time while editing")
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

    output_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS,name="Output Height",description="Image size for the baked texure map result(s)", default='TWOK', update=update_bake_width)
    output_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Output Height", description="Image size for the baked texure map result(s)", default='TWOK')

    bake_normals: BoolProperty(name="Bake Normal", description="Toggle for baking normal maps for baking as part of the batch baking operator", default=True)
    bake_ambient_occlusion: BoolProperty(name="Bake Ambient Occlusion", description="Toggle for baking ambient occlusion as part of the batch baking operator", default=True)
    bake_curvature: BoolProperty(name="Bake Curvature", description="Toggle for baking curvature as part of the batch baking operator", default=True)
    bake_thickness: BoolProperty(name="Bake Thickness", description="Toggle for baking thickness as part of the batch baking operator", default=True)
    bake_world_space_normals: BoolProperty(name="Bake World Space Normals", description="Toggle for baking world space normals as part of the batch baking operator", default=True)

    occlusion_samples: IntProperty(
        name="Occlusion Samples", 
        description="Number of rays to trace for occlusion shader evaluation. Higher values help slightly with quality occlusion quality", 
        default=64, 
        min=1, 
        max=128, 
        update=update_occlusion_samples
    )
    
    occlusion_distance: FloatProperty(
        name="Occlusion Distance", 
        description="Occlusion distance between polygons. Lower values results in less occlusion",
        default=1.0,
        min=0.1,
        max=1.0,
        update=update_occlusion_distance
    )

    occlusion_contrast: FloatProperty(
        name="Occlusion Contrast",
        description="Occlusion contrast. Higher values result in more intense differences between white and black pixel values in the occlusion map output",
        default=0.333,
        min=0.1,
        max=2.0,
        update=update_occlusion_contrast
    )

    curvature_bevel_radius: FloatProperty(
        name="Curvature Bevel Radius",
        description="The radius of the bevel baked into the curvature map output",
        default=5.0,
        min=0.0,
        max=10.0,
        update=update_curvature_bevel_radius
    )

    curvature_bevel_samples: IntProperty(
        name="Curvature Bevel Samples",
        description = "The number of rays to trace per shader evaluation for the marked bevel baked into the curvature map output. Increasing the bevel samples results in a sharper more defined bevel",
        default=6,
        min=2,
        max=16,
        update=update_curvature_bevel_samples
    )

    curvature_edge_intensity: FloatProperty(
        name="Curvature Edge Intensity",
        description="Intensity of the edges baked into the curvature map output",
        default=5.0,
        min=0.0,
        max=10.0,
        update=update_curvature_edge_intensity
    )

    curvature_occlusion_masking: FloatProperty(
        name="Curvature Occlusion Masking",
        description="The intensity of the occlusion masking applied to the curvature bevel. Higher masking values results in bevels being less prominant in areas with tight geometry",
        default=0.75,
        min=0.0,
        max=2.0,
        update=update_curvature_occlusion_masking
    )

    local_occlusion: BoolProperty(
        name="Local Occlusion",
        description="When off, other objects within the scene will contribute occlusion to the output maps",
        default=True
    )

    cage_extrusion: FloatProperty(
        name="Cage Extrusion",
        description="Infaltes the active object by the specified amount for baking. This helps matching to points nearer to the outside of the selected object meshes", 
        default=0.111, 
        min=0.0,
        max=1.0
    )

    #----------------------------- TEXTURE EXPORTING PROPERTIES -----------------------------#

    export_template_name: StringProperty(name="Export Template Name", default="Unreal Engine 4 (Metallic, Packed)")
    padding: IntProperty(name="Padding", default=16)
    export_textures: CollectionProperty(type=MATLAYER_texture_export_settings)
    delete_unpacked_images: BoolProperty(name="Delete Unpacked Images", default=True, description="Deletes unpacked image textures after packing")
    roughness_mode: EnumProperty(name="Roughness Mode", items=ROUGHNESS_MODE, default='ROUGHNESS')
    normal_map_mode: EnumProperty(name="Normal Map Mode", items=NORMAL_MAP_MODE, default='OPEN_GL')
    export_mode: EnumProperty(name="Export Active Material", items=EXPORT_MODE, description="Exports only the active material using the defined export settings", default='ONLY_ACTIVE_MATERIAL')

    #----------------------------- DRAWING -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "logging")