# This file contains texture set settings.

import bpy

def update_match_image_resolution(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

class COATER_texture_set_settings(bpy.types.PropertyGroup):
    image_width: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Image Width",
        description="Image size for the new image.",
        default='FIVE_TWELVE',
        update=update_image_width
    )

    image_height: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Image Height",
        description="Image size for the new image.",
        default='FIVE_TWELVE'
    )

    match_image_resolution: bpy.props.BoolProperty(name="Match Image Resoltion", description="Match the image resoltion", default=True, update=update_match_image_resolution)

    thirty_two_bit: bpy.props.BoolProperty(name="32 Bit", description="Create images with 32 bit color depth.", default=False)