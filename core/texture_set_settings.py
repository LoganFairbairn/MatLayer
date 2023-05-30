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

def update_color_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.color_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('COLOR', True)
        material_channels.connect_material_channel(context, 'COLOR')
        export_settings.export_base_color = True
    else:
        material_channels.set_material_channel_node_active_state('COLOR', False)
        material_channels.disconnect_material_channel(context, 'COLOR')
        export_settings.export_base_color = False

def update_subsurface_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.subsurface_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('SUBSURFACE', True)
        material_channels.connect_material_channel(context, "SUBSURFACE")
        export_settings.export_subsurface = True
    else:
        material_channels.set_material_channel_node_active_state('SUBSURFACE', False)
        material_channels.disconnect_material_channel(context, "SUBSURFACE")
        export_settings.export_subsurface = False

def update_subsurface_color_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return
    
    export_settings = context.scene.matlayer_export_settings
    if self.subsurface_color_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('SUBSURFACE_COLOR', True)
        material_channels.connect_material_channel(context, "SUBSURFACE_COLOR")
        export_settings.export_subsurface_color = True
    else:
        material_channels.set_material_channel_node_active_state('SUBSURFACE_COLOR', False)
        material_channels.disconnect_material_channel(context, "SUBSURFACE_COLOR")
        export_settings.export_subsurface_color = False

def update_metallic_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return
    
    export_settings = context.scene.matlayer_export_settings
    if self.metallic_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('METALLIC', True)
        material_channels.connect_material_channel(context, "METALLIC")
        export_settings.export_metallic = True
    else:
        material_channels.set_material_channel_node_active_state('METALLIC', False)
        material_channels.disconnect_material_channel(context, "METALLIC")
        export_settings.export_metallic = False

def update_specular_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.specular_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('SPECULAR', True)
        material_channels.connect_material_channel(context, "SPECULAR")
        export_settings.export_specular = True
    else:
        material_channels.set_material_channel_node_active_state('SPECULAR', False)
        material_channels.disconnect_material_channel(context, "SPECULAR")
        export_settings.export_specular = False

def update_roughness_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.roughness_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('ROUGHNESS', True)
        material_channels.connect_material_channel(context, "ROUGHNESS")
        export_settings.export_roughness = True
    else:
        material_channels.set_material_channel_node_active_state('ROUGHNESS', False)
        material_channels.disconnect_material_channel(context, "ROUGHNESS")
        export_settings.export_roughness = False

def update_normal_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.normal_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('NORMAL', True)
        material_channels.connect_material_channel(context, "NORMAL")
        export_settings.export_normals = True
    else:
        material_channels.set_material_channel_node_active_state('NORMAL', False)
        material_channels.disconnect_material_channel(context, "NORMAL")
        export_settings.export_normals = False

def update_height_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.height_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('HEIGHT', True)
        material_channels.connect_material_channel(context, "HEIGHT")
        export_settings.export_height = True
    else:
        material_channels.set_material_channel_node_active_state('HEIGHT', False)
        material_channels.disconnect_material_channel(context, "HEIGHT")
        export_settings.export_height = False

def update_emission_channel_toggle(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    export_settings = context.scene.matlayer_export_settings
    if self.emission_channel_toggle == True:
        material_channels.set_material_channel_node_active_state('EMISSION', True)
        material_channels.connect_material_channel(context, 'EMISSION')
        export_settings.export_emission = True
    else:
        material_channels.set_material_channel_node_active_state('EMISSION', False)
        material_channels.disconnect_material_channel(context, 'EMISSION')
        export_settings.export_emission = False

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
            # Error here, return 10 to make it apparent.
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
            # Error here, return 10 to make it apparent.
            return 10

def get_active_material_channel_count():
    '''Returns the number of active material channels.'''
    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings
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
    height_channel_toggle: BoolProperty(default=False, description="Click to toggle on / off the height material channel for this layer", update=update_height_channel_toggle)

class MATLAYER_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Width", description="Image width in pixels for the new image.", default='TWOK', update=update_image_width)
    image_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Height", description="Image height in pixels for the new image.", default='TWOK')
    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)
    thirty_two_bit: BoolProperty(name="32 Bit Color", description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients. On monitors (generally older or cheap ones) that don't support this color depth there will be no visual difference", default=True)
    global_material_channel_toggles: PointerProperty(type=GlobalMaterialChannelToggles, description="Toggles for each material channel that toggle them on / off for all layers.")
    auto_update_properties: BoolProperty(name="Auto Update Properties", description="If true, changing texture set settings will trigger automatic updates.")