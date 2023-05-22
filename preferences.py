# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty

ADDON_NAME = __package__

TEXTURE_NAME_EXPORT_FORMAT = [
    #("CUSTOM", "Custom", "Export textures with a custom name"),
    ("STANDARD", "Standard", "Export textures with a commonly used naming format"),
    ("UE_UNITY", "Unreal Engine / Unity", "Export textures with the standard Unreal Engine / Unity naming format"),
    ]

TEXTURE_NAME_PREFIX_MODE = [
    ("CUSTOM", "Custom", "Export textures with a custom prefix."),
    ("OBJECT_NAME", "Object Name", "Use the active (selected) object's name as the prefer for texture names.")
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

    texture_name_export_format: EnumProperty(
        items=TEXTURE_NAME_EXPORT_FORMAT, 
        name="Texture Name Export Format",
        description="The naming format used to export textures."
    )

    texture_name_export_prefix_mode: EnumProperty(
        items=TEXTURE_NAME_PREFIX_MODE,
        default='OBJECT_NAME',
        name="Texture Name Export Prefix Mode",
        description="The prefix used in exported textures."
    )

    ui_y_scale: FloatProperty(
        name="Interface Y Scale",
        default=1.4,
        description="Y scale modifier for the user interface. Can be used to help make interface elements larger so they are easier to click, and to help keep the interface less cluttered."
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_delete_unused_images")
        #layout.prop(self, "save_imported_textures")
        layout.prop(self, "organize_nodes")