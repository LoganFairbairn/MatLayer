# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty

ADDON_NAME = __package__

TEXTURE_EXPORT_TEMPLATES = [
    ("PBR_METALLIC_ROUGHNESS", "PBR Metallic Roughness", "Exports all textures for a standard PBR metallic / roughness setup. Does not channel pack textures"),
    ("UNITY_METALLIC", "Unity (Metallic)", "Channel packs and exports textures for a standard Unity shader with a metallic setup. [ R = Metallic, G = Ambient Occlusion, B = None, Alpha = Glossiness ]"),
    ("UNITY_SPECULAR", "Unity (Specular)", "Channel packs and exports textures for a standard Unity shader with a specular setup. [ R = Metallic, G = Ambient Occlusion, B = None, Alpha = Glossiness ]"),
    ("UNREAL_ENGINE", "Unreal Engine", "Channel packs textures in a common method for materials used in Unreal Engine [ R = Occlusion, G = Roughness, B = Metallic ]")
    ]

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

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

    logging: BoolProperty(
        name="Logging",
        default=True,
        description="Prints all major functions this add-on runs in Blenders terminal. This is useful for debugging purposes, specifically checking which functions are being called and verifying the function call order is correct."
    )

    organize_nodes: BoolProperty(
        name="Organize Nodes",
        default=True,
        description="Organizes nodes created with this add-on. It's useful in some cases to toggle this off to be able to organize shader nodes for add-on development testing."
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

    ui_y_scale: FloatProperty(
        name="Interface Y Scale",
        default=1.4,
        description="Y scale modifier for the user interface. Can be used to help make interface elements larger so they are easier to click, and to help keep the interface less cluttered."
    )

    texture_export_template: EnumProperty(items=TEXTURE_EXPORT_TEMPLATES, name="Texture Export Template", description="", default='UNREAL_ENGINE')
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_delete_unused_images")
        #layout.prop(self, "save_imported_textures")
        layout.prop(self, "organize_nodes")
        layout.prop(self, "logging")