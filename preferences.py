# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty, CollectionProperty
from .core.mesh_map_baking import update_occlusion_samples, update_occlusion_distance, update_occlusion_intensity, update_local_occlusion, update_bevel_radius, update_bevel_samples

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
    ("NORMAL_HEIGHT", "Normal + Height", "Normal + Height"),
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", "Ambient Occlusion"),
    ("CURVATURE", "Curvature", "Curvature"),
    ("THICKNESS", "Thickness", "Thickness"),
    ("BASE_NORMALS", "Base Normals", "Base Normals"),
    ("WORLD_SPACE_NORMALS", "World Space Normals", "World Space Normals"),
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
    ("JPEG", "jpg", "Exports the selected material channel in JPG texture format. This is a compressed format, which could be used for textures applied to models that will be shown in a web browser"),
    ("TARGA", "tga", "Exports the selected material channel in TARGA texture format"),
    ("OPEN_EXR", "exr", "Exports the selected material channel in open exr texture format")
]

EXPORT_MODE = [
    ("ONLY_ACTIVE_MATERIAL", "Only Active Material", "Export only the active material to a texture set"),
    ("EXPORT_ALL_MATERIALS", "Export All Materials", "Exports every object on the active material as it's own texture set"),
    ("SINGLE_TEXTURE_SET", "Single Texture Set", "Bakes all materials in all texture slots on the active object to 1 texture set. Separating the final material into separate smaller materials assigned to different parts of the mesh and then baking them to a single texture set can be efficient for workflow, and can reduce shader compilation time while editing")
]

MESH_MAP_BAKING_QUALITY = [
    ("TEST_QUALITY", "Test Quality", "Test quality sampling, ideal for quickly testing the output of mesh map bakes. Not recommended for use in production (1 sample)"),
    ("EXTREMELY_LOW_QUALITY", "Extremely Low Quality", "Low quality sampling (8 samples)"),
    ("VERY_LOW_QUALITY", "Very Low Quality", "Low quality sampling (16 samples)"),
    ("LOW_QUALITY", "Low Quality", "Low quality sampling (32 samples)"),
    ("RECOMMENDED_QUALITY", "Recommended Quality", "Recommended quality sampling, ideal for most use cases (64 samples)"),
    ("HIGH_QUALITY", "High Quality", "High quality sampling, for more accurate mesh map data (128 samples)"),
    ("INSANE_QUALITY", "Insane Quality", "Very high sampling, for hyper accurate mesh map data output, not recommended for standard use. Render times are usually long (256 samples)")
]

MESH_MAP_CAGE_MODE = [
    ("NO_CAGE", "No Cage", "No cage will be used when baking mesh maps. This can in rare cases produce better results than using a cage"),
    ("AUTO_CAGE", "Auto Cage", "A cage object will be automatically created by duplicating the low poly object and scaling it slightly by the defined amount using a complex solidify modifier. This produces good quality baking results in most cases"),
    ("MANUAL_CAGE", "Manual Cage", "Insert a manually created cage to be used when baking mesh maps. For some objects that have small crevaces where cage mesh normals would intersect if extruded defining a manual cage object will produce the best results")
]

MESH_MAP_ANTI_ALIASING = [
    ("NO_AA", "No AA", "No anti aliasing will be applied to output mesh map textures"),
    ("2X", "2xAA", "Mesh maps will be rendered at 2x scale and then scaled down to effectively apply anti-aliasing"),
    ("4X", "4xAA", "Mesh maps will be rendered at 4x scale and then scaled down to effectively apply anti-aliasing")
]

MESH_MAP_UPSCALE_MULTIPLIER = [
    ("NO_UPSCALE", "No Upscale", "All mesh maps will be baked at the pixel resolution defined in this materials texture set"),
    ("1_75X", "1.75x Upscale", "All mesh maps will be baked at 0.75 of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution"),
    ("2X", "2x Upscale", "All mesh maps will be baked at half of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution"),
    ("4X", "4x Upscale", "All mesh maps will be baked at a quarter of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution"),
    ("8X", "8x Upscale", "All mesh maps will be baked at 1 eighth of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution")
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

class MATLAYER_mesh_map_anti_aliasing(PropertyGroup):
    normals_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Normal Map Anti Aliasing", description="Anti aliasing for output normal maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    ambient_occlusion_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Ambient Occlusion Anti Aliasing", description="Anti aliasing for output ambient occlusion maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    curvature_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Curvature Anti Aliasing", description="Anti aliasing for output curvature maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    thickness_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Thickness Anti Aliasing", description="Anti aliasing for output thickness maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    world_space_normals_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="World Space Normals Anti Aliasing", description="Anti aliasing for output world space normal maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    #----------------------------- FILE MANAGEMENT PROPERTIES -----------------------------#

    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=True,
        description="Saves all imported textures to the 'Layers' folder. This helps provided a constant external folder for saving images used in layers which helps keep your files consistent."
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

    #----------------------------- MESH MAP BAKING PROPERTIES -----------------------------#

    mesh_map_anti_aliasing: PointerProperty(type=MATLAYER_mesh_map_anti_aliasing, name="Mesh Map Anti Aliasing")

    mesh_map_upscaling_multiplier: EnumProperty(
        items=MESH_MAP_UPSCALE_MULTIPLIER,
        name="Mesh Map Upscale Multiplier",
        description="Bakes the mesh map at a smaller resolution, then upscales the mesh map image to match the texture set resolution. Baking at a lower resolution and upscaling allows mesh maps to bake much faster, but with lower quality and accuracy, however a small amount of blurring caused by upscaling mesh map images can result in better mesh maps in some cases",
        default='1_75X'
    )

    mesh_map_quality: EnumProperty(
        items=MESH_MAP_BAKING_QUALITY, 
        name="Mesh Map Quality", 
        description="Bake quality",
        default='RECOMMENDED_QUALITY'
    )

    cage_mode: EnumProperty(
        items=MESH_MAP_CAGE_MODE,
        name="Cage Mode",
        description="Mode to define if a cage is used for mesh map baking, and if the cage is created automatically, or manually defined",
        default='AUTO_CAGE'
    )

    cage_upscale: FloatProperty(
        name="Cage Upscale",
        description="Upscales a duplicate of the low poly mesh by the specified amount to use as a cage for mesh map baking", 
        default=0.01, 
        min=0.0,
        max=0.1
    )

    uv_padding: IntProperty(
        name="UV Padding",
        description="Amount of padding in pixels to extend the baked data out of UV islands. This ensures there is no visible seams between UV splits",
        default=32,
        min=4,
        max=64
    )

    relative_to_bounding_box: BoolProperty(
        name="Relative to Bounding Box",
        description="If true, the sampling radius and cage upscaling used in mesh map baking will be multiplied by the average size of the active objects bounding box",
        default=True
    )

    bake_normals: BoolProperty(
        name="Bake Normal", 
        description="Toggle for baking normal maps for baking as part of the batch baking operator", 
        default=True
    )

    bake_ambient_occlusion: BoolProperty(
        name="Bake Ambient Occlusion", 
        description="Toggle for baking ambient occlusion as part of the batch baking operator", 
        default=True
    )

    bake_curvature: BoolProperty(
        name="Bake Curvature", 
        description="Toggle for baking curvature as part of the batch baking operator", 
        default=True
    )

    bake_thickness: BoolProperty(
        name="Bake Thickness", 
        description="Toggle for baking thickness as part of the batch baking operator", 
        default=True
    )

    bake_world_space_normals: BoolProperty(
        name="Bake World Space Normals", 
        description="Toggle for baking world space normals as part of the batch baking operator", 
        default=True
    )

    occlusion_samples: IntProperty(
        name="Occlusion Samples", 
        description="Number of rays to trace for occlusion shader evaluation. Higher values slightly increase occlusion quality at the cost of increased bake time. In most cases the default value is ideal", 
        default=64, 
        min=1, 
        max=128, 
        update=update_occlusion_samples
    )
    
    occlusion_distance: FloatProperty(
        name="Occlusion Distance", 
        description="Occlusion distance between polygons. Lower values results in less occlusion. In most cases the default value is ideal",
        default=1.0,
        min=0.1,
        max=1.0,
        update=update_occlusion_distance
    )

    occlusion_intensity: FloatProperty(
        name="Occlusion Contrast",
        description="Occlusion contrast. Higher values result in more intense occlusion shadows",
        default=2.0,
        min=0.1,
        max=10.0,
        update=update_occlusion_intensity
    )

    local_occlusion: BoolProperty(
        name="Local Occlusion",
        description="When off, other objects within the scene will contribute occlusion to the output maps",
        default=True,
        update=update_local_occlusion
    )

    bevel_radius: FloatProperty(
        name="Bevel Radius",
        description="Radius of the sharp edges baked into the curvature map",
        default=0.001,
        soft_min=0.001,
        soft_max=0.01,
        step=0.1,
        precision=3,
        update=update_bevel_radius
    )

    bevel_samples: IntProperty(
        name="Bevel Samples",
        description="Number of rays to trace per shader evaluation for curvature bevel (sharp edges) samples. Higher samples results in sharper edges",
        default=2,
        min=2,
        max=16,
        update=update_bevel_samples
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
        default=True)

    #----------------------------- DRAWING -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_main_operations")
        layout.prop(self, "log_sub_operations")