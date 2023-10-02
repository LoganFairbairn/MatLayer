import os
import numpy
import bpy
from bpy.types import Operator, Menu
from bpy.props import StringProperty, IntProperty
from ..core import mesh_map_baking
from ..core import texture_set_settings as tss
from ..core import debug_logging
from ..core import blender_addon_utils
from ..core import material_layers
from .. import preferences


#----------------------------- CHANNEL PACKING / IMAGE EDITING FUNCTIONS -----------------------------#


def format_baked_material_channel_name(material_name, material_channel_name):
    '''Properly formats the baked material channel name.'''
    return "ML_{0}_{1}".format(material_name, material_channel_name.capitalize())

def enumerate_color_channel(color_channel):
    '''Returns an interger value for the provided color channel.'''
    match color_channel:
        case 'R':
            return 0
        
        case 'G':
            return 1
        
        case 'B':
            return 2
        
        case 'A':
            return 3

def channel_pack(input_textures, input_packing, output_packing, image_name_format, color_bit_depth, file_format):
    '''Channel packs the provided images into RGBA channels of a single image. Accepts None.'''

    # Create an array of output pixels using the first valid input texture.
    # Initialize full size empty arrays to avoid using dynamic arrays (caused by appending) which is much much slower.
    output_pixels = None
    source_pixels = None
    for channel_index in range(0, 4):
        image = input_textures[channel_index]
        if image:
            w, h = image.size
            source_pixels = numpy.empty(w * h * 4, dtype=numpy.float32)
            output_pixels = numpy.ones(w * h * 4, dtype=numpy.float32)

    # Cycle through and pack RGBA channels.
    for channel_index in range(0, 4):
        image = input_textures[channel_index]
        if image:

            # Break if provided images are not the same size.
            assert image.size[:] == (w, h), "Images must be the same size."

            # Copy the source image R pixels (source pixels 0 = R, 1 = G, 2 = B, 3 = A) to the output image pixels for each channel.
            # Skip 4 elements using extended slice because there are 4 elements in each pixel (RGBA).
            image.pixels.foreach_get(source_pixels)
            output_pixels[output_packing[channel_index]::4] = source_pixels[input_packing[channel_index]::4]
            
        else:
            # If an alpha image is not provided, alpha is 1.0.
            if channel_index == 3:
                output_pixels[channel_index::4] = 1.0

            # If an image other than alpha is not provided, channel is 0.0.
            else:
                output_pixels[channel_index::4] = 0.0
        
    # If an alpha image is provided create an image with alpha.
    has_alpha = False
    if input_textures[3] != None:
        has_alpha = True

    # Translate bit depth to a boolean from an enum.
    use_thirty_two_bit = False
    match color_bit_depth:
        case 'EIGHT':
            use_thirty_two_bit = False
        case 'THIRTY_TWO':
            use_thirty_two_bit = True

    # Create a folder to save / export packed images to.
    export_path = os.path.join(bpy.path.abspath("//"), "Textures")
    if os.path.exists(export_path) == False:
        os.mkdir(export_path)

    # Create image using the packed pixels.
    image_name = format_export_image_name(image_name_format)
    packed_image = blender_addon_utils.create_data_image(image_name,
                                                         image_width=w,
                                                         image_height=h,
                                                         alpha_channel=has_alpha,
                                                         thirty_two_bit=use_thirty_two_bit,
                                                         data=True,
                                                         delete_existing=True)
    packed_image.file_format = file_format
    packed_image.filepath = "{0}/{1}.{2}".format(export_path, image_name, file_format.lower())
    packed_image.pixels.foreach_set(output_pixels)
    packed_image.save()
    blender_addon_utils.save_image(packed_image, file_format, 'EXPORT_TEXTURE')

    return packed_image

def invert_image(image, invert_r = False, invert_g = False, invert_b = False, invert_a = False):
    '''Inverts specified color channels of the provided image.'''
    pixels = numpy.empty(len(image.pixels), dtype=numpy.float32)
    image.pixels.foreach_get(pixels)
    if invert_r: 
        pixels[0::4] = 1 - pixels[0::4]
    if invert_g: 
        pixels[1::4] = 1 - pixels[1::4]
    if invert_b: 
        pixels[2::4] = 1 - pixels[2::4]
    if invert_a: 
        pixels[3::4] = 1 - pixels[3::4]
    image.pixels.foreach_set(pixels)

def channel_pack_textures(material_name):
    '''Creates channel packed textures using pre-baked textures.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    active_object = bpy.context.active_object

    # Cycle through all defined export textures and channel pack them.
    for export_texture in addon_preferences.export_textures:

        # Compile an array of baked images that will be used in channel packing based on the defined input texture...
        # ... and perform image alterations to select channels (normal / roughness / smoothness).
        input_images = []
        for key in export_texture.input_textures.__annotations__.keys():
            texture_channel = getattr(export_texture.input_textures, key)

            match texture_channel:
                case 'AMBIENT_OCCLUSION':
                    meshmap_name = mesh_map_baking.get_meshmap_name(active_object.name, 'AMBIENT_OCCLUSION')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'CURVATURE':
                    meshmap_name = mesh_map_baking.get_meshmap_name(active_object.name, 'CURVATURE')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'THICKNESS':
                    meshmap_name = mesh_map_baking.get_meshmap_name(active_object.name, 'THICKNESS')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'BASE_NORMALS':
                    meshmap_name = mesh_map_baking.get_meshmap_name(active_object.name, 'NORMAL')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'ROUGHNESS':
                    image_name = format_baked_material_channel_name(material_name, texture_channel)
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Convert (invert) roughness to a smoothness map based on settings.
                    if addon_preferences.roughness_mode == 'SMOOTHNESS':
                        invert_image(image, True, True, True, False)

                case 'NORMAL':
                    image_name = format_baked_material_channel_name(material_name, texture_channel)
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Invert normal map G values if exporting for DirectX based on settings.
                    if addon_preferences.normal_map_mode == 'DIRECTX':
                        invert_image(image, False, True, False, False)

                case 'NORMAL_HEIGHT':
                    image_name = format_baked_material_channel_name(material_name, 'NORMAL')
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Invert normal map G values if exporting for DirectX based on settings.
                    if addon_preferences.normal_map_mode == 'DIRECTX':
                        invert_image(image, False, True, False, False)

                case 'NONE':
                    input_images.append(None)

                case _:
                    image_name = format_baked_material_channel_name(material_name, texture_channel)
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

        # Don't attempt to pack an image if there are no baked images.
        if all(image is None for image in input_images):
            continue

        input_packing_channels = []
        for key in export_texture.input_rgba_channels.__annotations__.keys():
            color_channel_index = enumerate_color_channel(getattr(export_texture.input_rgba_channels, key))
            input_packing_channels.append(color_channel_index)

        output_packing_channels = []
        for key in export_texture.output_rgba_channels.__annotations__.keys():
            color_channel_index = enumerate_color_channel(getattr(export_texture.output_rgba_channels, key))
            output_packing_channels.append(color_channel_index)

        # Channel pack baked material channels / textures.
        channel_pack(
            input_textures=input_images,
            input_packing=input_packing_channels,
            output_packing=output_packing_channels,
            image_name_format=export_texture.name_format,
            color_bit_depth=export_texture.bit_depth,
            file_format=export_texture.image_format
        )

    # Delete temp material channel bake images, they are no longer needed because they are packed into new textures now.
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:
        temp_material_channel_image_name = format_baked_material_channel_name(material_name, material_channel_name)
        temp_material_channel_image = bpy.data.images.get(temp_material_channel_image_name)
        if temp_material_channel_image:
            bpy.data.images.remove(temp_material_channel_image)


#----------------------------- EXPORTING FUNCTIONS -----------------------------#


def format_export_image_name(texture_name_format):
    '''Properly formats the name for an export image based on the selected texture export template and the provided material channel.'''
    material_name = bpy.context.active_object.material_slots[0].name        # TODO: Takes the first material name, but in the future, taking the name of the material being baked will be ideal.
    mesh_name = bpy.context.active_object.name

    # Replace key words in the texture name format.
    image_name = texture_name_format.replace("/MaterialName", material_name)
    image_name = image_name.replace("/MeshName", mesh_name)
    
    return image_name

def get_texture_channel_bake_list():
    '''Returns a list of material channels required to be baked as defined in the texture export settings.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    material_channels_to_bake = []
    for export_texture in addon_preferences.export_textures:
        for key in export_texture.input_textures.__annotations__.keys():
            input_texture_channel = getattr(export_texture.input_textures, key)
            if input_texture_channel not in material_channels_to_bake:
                if input_texture_channel != 'NONE':
                    material_channels_to_bake.append(input_texture_channel)
    debug_logging.log("Baking channels: {0}".format(material_channels_to_bake))
    return material_channels_to_bake

def set_export_template(export_template_name):
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    export_textures = addon_preferences.export_textures
    export_textures.clear()
    addon_preferences.export_template_name = export_template_name

    match export_template_name:
        case 'PBR Metallic Roughness':
            addon_preferences.roughness_mode = 'ROUGHNESS'
            addon_preferences.normal_map_mode = 'OPEN_GL'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Color"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Metallic"
            new_channel.input_textures.r_texture = 'METALLIC'
            new_channel.input_textures.g_texture = 'METALLIC'
            new_channel.input_textures.b_texture = 'METALLIC'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Roughness"
            new_channel.input_textures.r_texture = 'ROUGHNESS'
            new_channel.input_textures.g_texture = 'ROUGHNESS'
            new_channel.input_textures.b_texture = 'ROUGHNESS'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Normal"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Emission"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'PBR Specular Glossiness':
            addon_preferences.roughness_mode = 'ROUGHNESS'
            addon_preferences.normal_map_mode = 'OPEN_GL'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Color"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Specular"
            new_channel.input_textures.r_texture = 'SPECULAR'
            new_channel.input_textures.g_texture = 'SPECULAR'
            new_channel.input_textures.b_texture = 'SPECULAR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Glossiness"
            new_channel.input_textures.r_texture = 'ROUGHNESS'
            new_channel.input_textures.g_texture = 'ROUGHNESS'
            new_channel.input_textures.b_texture = 'ROUGHNESS'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Normal"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "/MaterialName_Emission"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unity URP Metallic':
            addon_preferences.normal_map_mode = 'OPEN_GL'
            addon_preferences.roughness_mode = 'SMOOTHNESS'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_MS"
            new_channel.input_textures.r_texture = 'METALLIC'
            new_channel.input_textures.g_texture = 'METALLIC'
            new_channel.input_textures.b_texture = 'METALLIC'
            new_channel.input_textures.a_texture = 'ROUGHNESS'
            new_channel.input_rgba_channels.a_color_channel = 'R'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_N"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unity URP Specular':
            addon_preferences.normal_map_mode = 'OPEN_GL'
            addon_preferences.roughness_mode = 'SMOOTHNESS'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_MG"
            new_channel.input_textures.r_texture = 'SPECULAR'
            new_channel.input_textures.g_texture = 'SPECULAR'
            new_channel.input_textures.b_texture = 'SPECULAR'
            new_channel.input_textures.a_texture = 'ROUGHNESS'
            new_channel.input_rgba_channels.a_color_channel = 'R'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_N"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unity HDRP Metallic':
            addon_preferences.normal_map_mode = 'OPEN_GL'
            addon_preferences.roughness_mode = 'SMOOTHNESS'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_MAG"
            new_channel.input_textures.r_texture = 'METALLIC'
            new_channel.input_textures.g_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.b_texture = 'NONE'
            new_channel.input_textures.a_texture = 'ROUGHNESS'
            new_channel.input_rgba_channels.a_color_channel = 'R'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_N"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unity HDRP Specular':
            addon_preferences.normal_map_mode = 'OPEN_GL'
            addon_preferences.roughness_mode = 'SMOOTHNESS'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_S"
            new_channel.input_textures.r_texture = 'SPECULAR'
            new_channel.input_textures.g_texture = 'SPECULAR'
            new_channel.input_textures.b_texture = 'SPECULAR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_MAG"
            new_channel.input_textures.r_texture = 'METALLIC'
            new_channel.input_textures.g_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.b_texture = 'NONE'
            new_channel.input_textures.a_texture = 'ROUGHNESS'
            new_channel.input_rgba_channels.a_color_channel = 'R'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_N"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unreal Engine 4':
            addon_preferences.roughness_mode = 'ROUGHNESS'
            addon_preferences.normal_map_mode = 'DIRECTX'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_SS"
            new_channel.input_textures.r_texture = 'SUBSURFACE'
            new_channel.input_textures.g_texture = 'SUBSURFACE'
            new_channel.input_textures.b_texture = 'SUBSURFACE'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_ORM"
            new_channel.input_textures.r_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.g_texture = 'ROUGHNESS'
            new_channel.input_textures.b_texture = 'METALLIC'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_NDX"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'Unreal Engine 4 Subsurface (Packed)':
            addon_preferences.roughness_mode = 'ROUGHNESS'
            addon_preferences.normal_map_mode = 'DIRECTX'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'SUBSURFACE'
            new_channel.input_rgba_channels.a_color_channel = 'R'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_ORM"
            new_channel.input_textures.r_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.g_texture = 'ROUGHNESS'
            new_channel.input_textures.b_texture = 'METALLIC'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_NDX"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_E"
            new_channel.input_textures.r_texture = 'EMISSION'
            new_channel.input_textures.g_texture = 'EMISSION'
            new_channel.input_textures.b_texture = 'EMISSION'
            new_channel.input_textures.a_texture = 'NONE'

        case 'CryEngine':
            addon_preferences.roughness_mode = 'ROUGHNESS'
            addon_preferences.normal_map_mode = 'DIRECTX'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_C"
            new_channel.input_textures.r_texture = 'COLOR'
            new_channel.input_textures.g_texture = 'COLOR'
            new_channel.input_textures.b_texture = 'COLOR'
            new_channel.input_textures.a_texture = 'ALPHA'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_S"
            new_channel.input_textures.r_texture = 'SPECULAR'
            new_channel.input_textures.g_texture = 'SPECULAR'
            new_channel.input_textures.b_texture = 'SPECULAR'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_NDXO"
            new_channel.input_textures.r_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.g_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.b_texture = 'NORMAL_HEIGHT'
            new_channel.input_textures.a_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_rgba_channels.a_color_channel = 'R'

        case 'Mesh Maps':
            addon_preferences.normal_map_mode = 'OPEN_GL'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_AmbientOcclusion"
            new_channel.input_textures.r_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.g_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.b_texture = 'AMBIENT_OCCLUSION'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_Curvature"
            new_channel.input_textures.r_texture = 'CURVATURE'
            new_channel.input_textures.g_texture = 'CURVATURE'
            new_channel.input_textures.b_texture = 'CURVATURE'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_Thickness"
            new_channel.input_textures.r_texture = 'THICKNESS'
            new_channel.input_textures.g_texture = 'THICKNESS'
            new_channel.input_textures.b_texture = 'THICKNESS'
            new_channel.input_textures.a_texture = 'NONE'

            new_channel = export_textures.add()
            new_channel.name_format = "T_/MaterialName_BaseNormals"
            new_channel.input_textures.r_texture = 'BASE_NORMALS'
            new_channel.input_textures.g_texture = 'BASE_NORMALS'
            new_channel.input_textures.b_texture = 'BASE_NORMALS'
            new_channel.input_textures.a_texture = 'NONE'

def bake_material_channel(material_channel_name, single_texture_set=False):
    '''Bakes the defined material channel to an image texture (stores it in Blender's data). Returns true if baking was successful.'''

    # We can always bake for the normal + height channel.
    if material_channel_name != 'NORMAL_HEIGHT':

        # Ensure the material channel name provided is valid to bake.
        if material_channel_name not in material_layers.MATERIAL_CHANNEL_LIST:
            debug_logging.log("Can't bake invalid material channel: {0}".format(material_channel_name))
            return ""

        # Skip baking for material channels that are toggled off in the texture set settings.
        if not tss.get_material_channel_active(material_channel_name):
            debug_logging.log("Skipped baking for globally disabled material channel: {channel_name}.".format(channel_name=material_channel_name))
            return ""

    # Force save all textures (unsaved textures will not bake properly).
    blender_addon_utils.force_save_all_textures()

    # Define a background color for new bake textures.
    background_color = (0.0, 0.0, 0.0, 1.0)
    if material_channel_name == 'NORMAL' or material_channel_name == 'NORMAL_HEIGHT':
        background_color = (0.735337, 0.735337, 1.0, 1.0)

    # Normal + height material channel combines height information into the normal map.
    # Convert the name used in exported textures for the normal + height material channel to normal.
    export_channel_name = material_channel_name
    if material_channel_name == 'NORMAL_HEIGHT':
        export_channel_name = 'NORMAL'

    # For baking multiple materials to a texture set
    if single_texture_set:
        material_name = bpy.context.active_object.material_slots[0].material.name
        image_name = format_baked_material_channel_name(material_name, export_channel_name)
        export_image = bpy.data.images.get(image_name)
        if not export_image:
            export_image = blender_addon_utils.create_image(
                new_image_name=image_name,
                image_width=tss.get_texture_width(),
                image_height=tss.get_texture_height(),
                base_color=background_color,
                generate_type='BLANK',
                alpha_channel=False,
                thirty_two_bit=True,
                add_unique_id=False,
                delete_existing=True
            )

    # For baking individual materials to textures, create new images to bake to.
    else:
        image_name = format_baked_material_channel_name(bpy.context.active_object.active_material.name, export_channel_name)
        export_image = blender_addon_utils.create_image(
            new_image_name=image_name,
            image_width=tss.get_texture_width(),
            image_height=tss.get_texture_height(),
            base_color=background_color,
            generate_type='BLANK',
            alpha_channel=False,
            thirty_two_bit=True,
            add_unique_id=False,
            delete_existing=True
        )

    # Add the baking image to the preset baking texture node (included in the default material setup).
    material_nodes = bpy.context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.get('BAKE_IMAGE')
    image_node.image = export_image
    image_node.select = True
    material_nodes.active = image_node
    blender_addon_utils.set_texture_paint_image(export_image)

    # Set baking settings required for baking material channels.
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_selected_to_active = False

    # Bake normals directly from the principled BSDF shader when baking normal + height mixes.
    if material_channel_name == 'NORMAL_HEIGHT':
        bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')

    # Isolate when baking single material channels.
    else:
        material_layers.isolate_material_channel(material_channel_name)
        bpy.ops.object.bake('INVOKE_DEFAULT', type='EMIT')

    return export_image.name

def add_bake_texture_nodes():
    '''Adds a bake texture node to all materials in all material slots on the active object.'''

    # Adding a placeholder image to the bake image nodes stops Blender from throwing annoying 'no active image' warnings when baking'.
    placeholder_image = blender_addon_utils.create_data_image("ML_Placeholder", image_width=32, image_height=32)

    active_object = bpy.context.active_object
    for material_slot in active_object.material_slots:
        if material_slot.material:
            bake_texture_node = material_slot.material.node_tree.nodes.new('ShaderNodeTexImage')
            bake_texture_node.name = 'BAKE_IMAGE'
            bake_texture_node.label = bake_texture_node.name
            bake_texture_node.image = placeholder_image
            bake_texture_node.select = True
            material_slot.material.node_tree.nodes.active = bake_texture_node

def remove_bake_texture_nodes():
    '''Removes image texture nodes for baking from all materials in all material slots on the active object.'''
    placeholder_image = bpy.data.images.get('ML_Placeholder')
    if placeholder_image:
        bpy.data.images.remove(placeholder_image)

    active_object = bpy.context.active_object
    for material_slot in active_object.material_slots:
        if material_slot.material:
            bake_texture_node = material_slot.material.node_tree.nodes.get('BAKE_IMAGE')
            if bake_texture_node:
                material_slot.material.node_tree.nodes.remove(bake_texture_node)


#----------------------------- EXPORT OPERATORS -----------------------------#


class MATLAYER_OT_export(Operator):
    bl_idname = "matlayer.export"
    bl_label = "Export"
    bl_description = "Bakes material channels to textures then channel packs based on export settings and finally saves all export textures folder"

    _timer = None
    _total_materials_to_bake = 0
    _texture_channel_index = -1
    _texture_channels_to_bake = []
    _mesh_map_channels_to_bake = []
    _original_render_engine_name = ""
    _bake_image_name = ""

    # Users must have an object selected to call this operator.
    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':

            # Detect when baking is finished...
            if not bpy.app.is_job_running('OBJECT_BAKE'):

                # If an image was baked, pack it in the blend files data.
                bake_image = bpy.data.images.get(self._bake_image_name)
                if bake_image != None:
                    bake_image.pack()
                    debug_logging.log("Baked - (texture channel - active material): {0} - {1}".format(self._bake_image_name, bpy.context.active_object.active_material.name))
                
                # Start baking the next material channel.
                addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
                self._bake_image_name = ""
                if self._texture_channel_index < len(self._texture_channels_to_bake) - 1:
                    self._texture_channel_index += 1
                    if addon_preferences.export_mode == 'SINGLE_TEXTURE_SET':
                        self._bake_image_name = bake_material_channel(self._texture_channels_to_bake[self._texture_channel_index], single_texture_set=True)
                    else:
                        self._bake_image_name = bake_material_channel(self._texture_channels_to_bake[self._texture_channel_index], single_texture_set=False)

                else:
                    # If all of the textures are baked for the active material, move to baking the next material.
                    if bpy.context.active_object.active_material_index + 1 < self._total_materials_to_bake:
                        debug_logging.log("Completed baking textures for material: {0}".format(bpy.context.active_object.active_material.name))
                        material_layers.show_layer()

                        # Channel pack baked textures after baking textures for each material if not baking to a single texture set.
                        if addon_preferences.export_mode != 'SINGLE_TEXTURE_SET':
                            channel_pack_textures(bpy.context.active_object.active_material.name)

                        bpy.context.active_object.active_material_index += 1
                        while blender_addon_utils.verify_addon_material(bpy.context.active_object.active_material) == False and bpy.context.active_object.active_material_index + 1 < self._total_materials_to_bake:
                            debug_logging.log("Skipped exporting texture set for invalid material (not created with this add-on): {0}".format(bpy.context.active_object.active_material.name))
                            bpy.context.active_object.active_material_index += 1

                        material_layers.refresh_layer_stack()
                        self._texture_channel_index = -1

                    else:
                        material_layers.show_layer()

                        # Channel pack for the first material if baking to a single texture set.
                        if addon_preferences.export_mode == 'SINGLE_TEXTURE_SET':
                            channel_pack_textures(bpy.context.active_object.material_slots[0].material.name)

                        # Channel pack for the active material otherwise.
                        else:
                            channel_pack_textures(bpy.context.active_object.active_material.name)

                        self.finish(context)
                        return {'FINISHED'}
                
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Verify the object can be baked to.
        if blender_addon_utils.verify_bake_object(self, check_active_material=True) == False:
            return {'FINISHED'}
        
        # Get the number of materials to bake and export.
        addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
        match addon_preferences.export_mode:
            case 'ONLY_ACTIVE_MATERIAL':
                debug_logging.log("Starting exporting for only the active material...")
                self._total_materials_to_bake = 1
                bpy.context.scene.render.bake.use_clear = True

            case 'EXPORT_ALL_MATERIALS':
                debug_logging.log("Starting exporting for all materials as individual texture sets...")
                self._total_materials_to_bake = len(bpy.context.active_object.material_slots)
                bpy.context.active_object.active_material_index = 0
                bpy.context.scene.render.bake.use_clear = True

            case 'SINGLE_TEXTURE_SET':
                debug_logging.log("Starting exporting for all materials to a single texture set...")
                self._total_materials_to_bake = len(bpy.context.active_object.material_slots)
                bpy.context.active_object.active_material_index = 0
                bpy.context.scene.render.bake.use_clear = False
        
        # Compile a list of material channels that require baking based on settings.
        self._texture_channels_to_bake = get_texture_channel_bake_list()

        # If there are no texture channels to bake, channel pack and finish.
        if len(self._texture_channels_to_bake) <= 0:
            debug_logging.log_status("No texture channels to bake.", self, type='INFO')
            return {'FINISHED'}
        
        # Add texture nodes to bake to.
        add_bake_texture_nodes()

        # Remember the original render engine so we can reset it after baking.
        self._original_render_engine_name = bpy.context.scene.render.engine

        # Add a timer to provide periodic timer events.
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        # Baking will start automatically when the timer hits the first event.
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Remove the timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        bpy.context.scene.render.engine = self._original_render_engine_name
        remove_bake_texture_nodes()
        material_layers.refresh_layer_stack()
        self.report({'INFO'}, "Exporting textures was manually cancelled.")

    def finish(self, context):
        # Remove the timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        bpy.context.scene.render.engine = self._original_render_engine_name
        remove_bake_texture_nodes()
        material_layers.refresh_layer_stack()
        self.report({'INFO'}, "Exporting textures finished successfully.")

class MATLAYER_OT_set_export_template(Operator):
    bl_idname = "matlayer.set_export_template"
    bl_label = "Set Export Template"
    bl_description = "Sets an export template"

    export_template_name: StringProperty(default="Error")
    
    def execute(self, context):
        set_export_template(self.export_template_name)
        return {'FINISHED'}

class MATLAYER_OT_save_export_template(Operator):
    bl_idname = "matlayer.save_export_template"
    bl_label = "Save Export Template"
    bl_description = "Saves the current export template. If a template with the same name already exists, it will be overwritten"
    
    def execute(self, context):
        # TODO: Save the template if it exists.
        return {'FINISHED'}

class MATLAYER_OT_add_export_texture(Operator):
    bl_idname = "matlayer.add_export_texture"
    bl_label = "Add Export Texture"
    bl_description = "Adds an additional texture to the export texture list"
    
    def execute(self, context):
        addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
        addon_preferences.export_textures.add()
        return {'FINISHED'}

class MATLAYER_OT_remove_export_texture(Operator):
    bl_idname = "matlayer.remove_export_texture"
    bl_label = "Remove Export Texture"
    bl_description = "Removes the related texture from the export texture list"

    export_texture_index: IntProperty(default=0)
    
    def execute(self, context):
        addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
        addon_preferences.export_textures.remove(self.export_texture_index)
        return {'FINISHED'}

class ExportTemplateMenu(Menu):
    bl_idname = "MATLAYER_MT_export_template_menu"
    bl_label = "Export Template Menu"
    bl_description = "Contains options to set a specific export template"

    def draw(self, context):
        layout = self.layout

        template_name = 'PBR Metallic Roughness'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'PBR Specular Glossiness'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unity URP Metallic'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unity URP Specular'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unity HDRP Metallic'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unity HDRP Specular'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unreal Engine 4'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name

        template_name = 'Unreal Engine 4 Subsurface (Packed)'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name 

        template_name = 'CryEngine'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name 

        template_name = 'Mesh Maps'
        op = layout.operator("matlayer.set_export_template", text=template_name)
        op.export_template_name = template_name 

        # TODO: Draw custom export templates.

class MATLAYER_OT_open_export_folder(Operator):
    bl_idname = "matlayer.open_export_folder"
    bl_label = "Open Export Folder"
    bl_description = "Opens the folder containing exported textures in your systems file explorer"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        export_path = os.path.join(bpy.path.abspath("//"), "Textures")
        if os.path.exists(export_path):
            os.startfile(export_path)
        else:
            self.report({'ERROR'}, "Export folder doesn't exist. Export textures folder will be automatically created for you.")
        return {'FINISHED'}