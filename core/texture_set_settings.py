# This file contains settings and functions the users texture set.

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty, PointerProperty, FloatVectorProperty, EnumProperty

# Available texture resolutions for texture sets.
TEXTURE_SET_RESOLUTIONS = [
    ("FIVE_TWELVE", "512", ""), 
    ("ONEK", "1024", ""),
    ("TWOK", "2048", ""),
    ("FOURK", "4096", ""),
]

def update_match_image_resolution(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return
    
    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

#----------------------------- UPDATE GLOBAL MATERIAL CHANNEL TOGGLES (mute / unmute material channels for ALL layers) -----------------------------#

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_width:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_height:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            return 10

class GlobalMaterialChannelToggles(PropertyGroup):
    '''A boolean toggle for each material channel to toggle it off / on for all layers.'''
    color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the color material channel for this layer")
    subsurface_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the subsurface material channel for this layer")
    metallic_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the metallic material channel for this layer")
    specular_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the specular material channel for this layer")
    roughness_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the roughness material channel for this layer")
    emission_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the emission material channel for this layer")
    normal_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the normal material channel for this layer")
    height_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the height material channel for this layer")
    alpha_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the alpha material channel for this layer")

class MATLAYER_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Width", description="Image width in pixels for the new image.", default='TWOK', update=update_image_width)
    image_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Height", description="Image height in pixels for the new image.", default='TWOK')
    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)
    thirty_two_bit: BoolProperty(name="32 Bit Color", description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients. On monitors (generally older or cheap ones) that don't support this color depth there will be no visual difference", default=True)
    global_material_channel_toggles: PointerProperty(type=GlobalMaterialChannelToggles, description="Toggles for each material channel that toggle them on / off for all layers.")
    auto_update_properties: BoolProperty(name="Auto Update Properties", default=True, description="If true, changing texture set settings will trigger automatic updates.")