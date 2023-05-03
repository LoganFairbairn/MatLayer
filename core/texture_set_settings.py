# This file contains settings and functions the users texture set.

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty, PointerProperty, FloatVectorProperty, EnumProperty
from ..core import material_channels

# Available texture resolutions for texture sets.
TEXTURE_SET_RESOLUTIONS = [
    ("FIVE_TWELVE", "512", ""), 
    ("ONEK", "1024", ""),
    ("TWOK", "2048", ""),
    ("FOURK", "4096", ""),
    ]

def update_match_image_resolution(self, context):
    texture_set_settings = context.scene.matlay_texture_set_settings

    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    texture_set_settings = context.scene.matlay_texture_set_settings

    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

#----------------------------- UPDATE GLOBAL MATERIAL CHANNEL TOGGLES (mute / unmute material channels for ALL layers) -----------------------------#

def update_color_channel_toggle(self, context):
    if self.color_channel_toggle == True:
        material_channels.connect_material_channel(context, "COLOR")
    else:
        material_channels.disconnect_material_channel(context, "COLOR")

def update_subsurface_channel_toggle(self, context):
    if self.subsurface_channel_toggle == True:
        material_channels.connect_material_channel(context, "SUBSURFACE")
    else:
        material_channels.disconnect_material_channel(context, "SUBSURFACE")

def update_subsurface_color_channel_toggle(self, context):
    if self.subsurface_color_channel_toggle == True:
        material_channels.connect_material_channel(context, "SUBSURFACE_COLOR")
    else:
        material_channels.disconnect_material_channel(context, "SUBSURFACE_COLOR")

def update_metallic_channel_toggle(self, context):
    if self.metallic_channel_toggle == True:
        material_channels.connect_material_channel(context, "METALLIC")
    else:
        material_channels.disconnect_material_channel(context, "METALLIC")

def update_specular_channel_toggle(self, context):
    if self.specular_channel_toggle == True:
        material_channels.connect_material_channel(context, "SPECULAR")
    else:
        material_channels.disconnect_material_channel(context, "SPECULAR")

def update_roughness_channel_toggle(self, context):
    if self.roughness_channel_toggle == True:
        material_channels.connect_material_channel(context, "ROUGHNESS")
    else:
        material_channels.disconnect_material_channel(context, "ROUGHNESS")

def update_normal_channel_toggle(self, context):
    if self.normal_channel_toggle == True:
        material_channels.connect_material_channel(context, "NORMAL")
    else:
        material_channels.disconnect_material_channel(context, "NORMAL")

def update_height_channel_toggle(self, context):
    if self.height_channel_toggle == True:
        material_channels.connect_material_channel(context, "HEIGHT")
    else:
        material_channels.disconnect_material_channel(context, "HEIGHT")

def update_emission_channel_toggle(self, context):
    if self.emission_channel_toggle == True:
        material_channels.connect_material_channel(context, "EMISSION")
    else:
        material_channels.disconnect_material_channel(context, "EMISSION")

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.matlay_texture_set_settings.image_width:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            # Error here, return 10 to make it apparent.
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.matlay_texture_set_settings.image_height:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            # Error here, return 10 to make it apparent.
            return 10

def get_active_material_channel_count():
    '''Returns the number of active material channels.'''
    texture_set_settings = bpy.context.scene.matlay_texture_set_settings
    number_of_active_material_channels = 0
    for material_channel_name in material_channels.get_material_channel_list():
        attribute_name = material_channel_name.lower() + "_channel_toggle"
        if getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None):
            number_of_active_material_channels += 1
    return number_of_active_material_channels

class GlobalMaterialChannelToggles(PropertyGroup):
    '''A boolean toggle for each material channel to toggle it off / on for all layers.'''
    color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the color material channel for this layer", update=update_color_channel_toggle)
    subsurface_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the subsurface material channel for this layer", update=update_subsurface_channel_toggle)
    subsurface_color_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the subsurface color material channel for this layer.", update=update_subsurface_color_channel_toggle)
    metallic_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the metallic material channel for this layer", update=update_metallic_channel_toggle)
    specular_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the specular material channel for this layer.", update=update_specular_channel_toggle)
    roughness_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the roughness material channel for this layer", update=update_roughness_channel_toggle)
    emission_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the emission material channel for this layer", update=update_emission_channel_toggle)
    normal_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the normal material channel for this layer", update=update_normal_channel_toggle)
    height_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the height material channel for this layer", update=update_height_channel_toggle)

class MATLAY_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Width", description="Image width in pixels for the new image.", default='TWOK', update=update_image_width)
    image_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Height", description="Image height in pixels for the new image.", default='TWOK')
    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)
    thirty_two_bit: BoolProperty(name="32 Bit Color", description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients. On monitors (generally older or cheap ones) that don't support this color depth there will be no visual difference", default=True)
    global_material_channel_toggles: PointerProperty(type=GlobalMaterialChannelToggles, description="Toggles for each material channel that toggle them on / off for all layers.")