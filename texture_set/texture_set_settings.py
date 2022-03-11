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

def update_pack_images(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.pack_images:
        bpy.ops.file.autopack_toggle()

class COATER_texture_set_settings(bpy.types.PropertyGroup):
    image_width: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Image Width",
        description="Image size for the new image.",
        default='TWOK',
        update=update_image_width
    )

    image_height: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Image Height",
        description="Image size for the new image.",
        default='TWOK'
    )

    match_image_resolution: bpy.props.BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be synced", default=True, update=update_match_image_resolution)

    thirty_two_bit: bpy.props.BoolProperty(name="32 Bit", description="When toggled on, images created using Coater will be created with 32 bit color depth. Images will take up more memory, but will have significantly less banding from gradients", default=False)

    pack_images: bpy.props.BoolProperty(name="Pack Images", description="When toggled on, images created with Coater will be automatically packed into the Blender file", default=False)