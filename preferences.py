# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty, CollectionProperty

ADDON_NAME = __package__

BIT_DEPTH = [
    ("EIGHT", "8-bit", "8-bit depth is the standard color bit depth for games"),
    ("THIRTY_TWO", "32-bit", "32-bit uses more memory in RGB channels, but will result in less color banding (not visible on old monitors)")
]

NORMAL_MAP_MODE = [
    ("OPEN_GL", "OpenGL", "Normal maps will be exported in Open GL format (same as they are in Blender)"),
    ("DIRECTX", "DirectX", "Exported normal maps will have their green channel automatically inverted so they export in Direct X format")
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
    ("PNG", "png", "Exports the selected material channel in png texture format"),
    ("JPG", "jpg", "Exports the selected material channel in jpg texture format"),
    ("TARGA", "tga", "Exports the selected material channel in targa texture format"),
    ("EXR", "exr", "Exports the selected material channel in open exr texture format")
]

class MATLAYER_texture_export_settings(PropertyGroup):
    name_format: StringProperty(default="T_/MaterialName_C")

    r_input_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name="Input R")
    r_pack_input_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='R', name="R")
    r_pack_output_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='R', name="R")

    g_input_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name="Input G")
    g_pack_input_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='G', name="G")
    g_pack_output_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='G', name="G")

    b_input_texture: EnumProperty(items=EXPORT_CHANNELS, default='COLOR', name="Input B")
    b_pack_input_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='B', name="B")
    b_pack_output_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='B', name="B")

    a_input_texture: EnumProperty(items=EXPORT_CHANNELS, default='NONE', name="Input A")
    a_pack_input_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='A', name="A")
    a_pack_output_color_channel: EnumProperty(items=PACKING_COLOR_CHANNELS, default='A', name="A")

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
        name="Logging",
        default=True,
        description="Prints all major functions this add-on runs in Blenders terminal. This is useful for debugging purposes, specifically checking which functions are being called and verifying the function call order is correct."
    )

    #----------------------------- USER INTERFACE PROPERTIES -----------------------------#

    ui_y_scale: FloatProperty(
        name="Interface Y Scale",
        default=1.4,
        description="Y scale modifier for the user interface. Can be used to help make interface elements larger so they are easier to click, and to help keep the interface less cluttered."
    )

    #----------------------------- EXPORTING PROPERTIES -----------------------------#

    export_template_name: StringProperty(default="Unreal Engine 4 (Metallic, Packed)")

    padding: IntProperty(name="Padding", default=16)

    export_channels: CollectionProperty(type=MATLAYER_texture_export_settings)

    delete_unpacked_images: BoolProperty(default=True, description="Deletes unpacked image textures after packing")

    normal_map_mode: EnumProperty(items=NORMAL_MAP_MODE, default='OPEN_GL')

    #----------------------------- MISC -----------------------------#
    
    organize_nodes: BoolProperty(
        name="Organize Nodes",
        default=True,
        description="Organizes nodes created with this add-on. It's useful in some cases to toggle this off to be able to organize shader nodes for add-on development testing."
    )

    #----------------------------- DRAWING -----------------------------#
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_delete_unused_images")
        #layout.prop(self, "save_imported_textures")
        layout.prop(self, "organize_nodes")
        layout.prop(self, "logging")