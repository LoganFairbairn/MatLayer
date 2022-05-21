# This file contains settings for the users texture set.

import bpy
from ..layers.nodes import material_channel_nodes

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

def update_color_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.color_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "BASECOLOR", False)
    else:
        material_channel_nodes.mute_material_channel(context, "BASECOLOR", True)
        
def update_metallic_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.metallic_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "METALLIC", False)
    else:
        material_channel_nodes.mute_material_channel(context, "METALLIC", True)

def update_roughness_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.roughness_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "ROUGHNESS", False)
    else:
        material_channel_nodes.mute_material_channel(context, "ROUGHNESS", True)

def update_normal_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.normal_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "NORMAL", False)
    else:
        material_channel_nodes.mute_material_channel(context, "NORMAL", True)

def update_height_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.height_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "HEIGHT", False)
    else:
        material_channel_nodes.mute_material_channel(context, "HEIGHT", True)

def update_scattering_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.scattering_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "SCATTERING", False)
    else:
        material_channel_nodes.mute_material_channel(context, "SCATTERING", True)

def update_emission_channel_toggle(self, context):
    texture_set_settings = context.scene.coater_texture_set_settings

    if texture_set_settings.emission_channel_toggle == True:
        material_channel_nodes.mute_material_channel(context, "EMISSION", False)
    else:
        material_channel_nodes.mute_material_channel(context, "EMISSION", True)

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

    layer_folder: bpy.props.StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: bpy.props.BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be synced", default=True, update=update_match_image_resolution)
    thirty_two_bit: bpy.props.BoolProperty(name="32 Bit", description="When toggled on, images created using Coater will be created with 32 bit color depth. Images will take up more memory, but will have significantly less banding from gradients", default=True)
    pack_images: bpy.props.BoolProperty(name="Pack Images", description="When toggled on, images created with Coater will be automatically packed into the Blender file", default=False)

    # Material Channel Toggles (for turning on / off unrequired channels)
    color_channel_toggle: bpy.props.BoolProperty(default=True, update=update_color_channel_toggle)
    metallic_channel_toggle: bpy.props.BoolProperty(default=True, update=update_metallic_channel_toggle)
    roughness_channel_toggle: bpy.props.BoolProperty(default=True, update=update_roughness_channel_toggle)
    normal_channel_toggle: bpy.props.BoolProperty(default=True, update=update_normal_channel_toggle)
    height_channel_toggle: bpy.props.BoolProperty(default=True, update=update_height_channel_toggle)
    scattering_channel_toggle: bpy.props.BoolProperty(default=True, update=update_scattering_channel_toggle)
    emission_channel_toggle: bpy.props.BoolProperty(default=True, update=update_emission_channel_toggle)