# This module contains user preference settings for this add-on.

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty

ADDON_NAME = __package__

def get_addon_package_name():
    '''Returns the add-ons package name (generally used for accessing add-on files with correct file paths).'''
    return ADDON_NAME

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=True, 
        description="Saves all imported textures to the 'Layers' folder. This helps provided a constant external folder for saving images used in layers which helps keep your files consistent."
    )

    layer_texture_folder: StringProperty(
        name="Layer Textures Folder",
        default="",
        description="Folder path where layer textures are saved. If this is blank, all layer textures will be saved to a 'Layer' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    mesh_map_texture_folder: StringProperty(
        name="Mesh Map Textures Folder",
        default="",
        description="Folder path where baked mesh maps are saved. If this is blank, all mesh maps will be saved to a 'MeshMaps' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    exported_textures_folder: StringProperty(
        name="Exported Textures Folder",
        default="",
        description="Folder path where exported textures are saved. If this is blank all exported textures will be saved to a 'Textures' folder next to the saved blend file.",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "save_imported_textures")
        layout.prop(self, "layer_texture_folder")
        layout.prop(self, "mesh_map_texture_folder")
        layout.prop(self, "exported_textures_folder")