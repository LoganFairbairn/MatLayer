# This file contains functions and properties related to exporting textures from this add-on.

import os
import time
import numpy
import json
import copy
from pathlib import Path
from bpy.utils import resource_path
import bpy
from bpy.types import Operator, Menu, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty, CollectionProperty
from ..core import mesh_map_baking
from ..core import texture_set_settings as tss
from ..core import debug_logging
from ..core import blender_addon_utils as bau
from ..core import material_layers
from ..core import image_utilities
from ..core import shaders
from ..preferences import ADDON_NAME


default_output_texture = {
    "export_name_format": "/MeshName_Color",
    "export_image_format": "PNG",
    "export_colorspace": "SRGB",
    "export_bit_depth": "EIGHT",
    "pack_textures": ["COLOR", "COLOR", "COLOR", "NONE"],
    "input_pack_channels": ["R", "G", "B", "A"],
    "output_pack_channels": ["R", "G", "B", "A"]
}

default_export_template_json = {
    "name": "Default Export Template",
    "roughness_map_mode": "ROUGHNESS",
    "normal_map_mode": "OPEN_GL",
    "output_textures": [
        {
            "export_name_format": "/MeshName_Color",
            "export_image_format": "PNG",
            "export_colorspace": "SRGB",
            "export_bit_depth": "EIGHT",
            "pack_textures": [
            "COLOR",
            "COLOR",
            "COLOR",
            "NONE"
            ],
            "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ],
            "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ]
        },
        {
            "export_name_format": "/MeshName_Metallic",
            "export_image_format": "PNG",
            "export_colorspace": "NON_COLOR",
            "export_bit_depth": "EIGHT",
            "pack_textures": [
            "METALLIC",
            "METALLIC",
            "METALLIC",
            "NONE"
            ],
            "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ],
            "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ]
        },
        {
            "export_name_format": "/MeshName_Roughness",
            "export_image_format": "PNG",
            "export_colorspace": "NON_COLOR",
            "export_bit_depth": "EIGHT",
            "pack_textures": [
            "ROUGHNESS",
            "ROUGHNESS",
            "ROUGHNESS",
            "NONE"
            ],
            "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ],
            "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ]
        },
        {
            "export_name_format": "/MeshName_Normal",
            "export_image_format": "PNG",
            "export_colorspace": "NON_COLOR",
            "export_bit_depth": "EIGHT",
            "pack_textures": [
            "NORMAL_HEIGHT",
            "NORMAL_HEIGHT",
            "NORMAL_HEIGHT",
            "NONE"
            ],
            "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ],
            "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ]
        },
        {
            "export_name_format": "/MeshName_Emission",
            "export_image_format": "PNG",
            "export_colorspace": "NON_COLOR",
            "export_bit_depth": "EIGHT",
            "pack_textures": [
            "EMISSION",
            "EMISSION",
            "EMISSION",
            "NONE"
            ],
            "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ],
            "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
            ]
        }
    ]
}

default_json_file = {
  "export_templates": [
    {
      "name": "PBR Metallic Roughness",
      "roughness_map_mode": "ROUGHNESS",
      "normal_map_mode": "OPEN_GL",
      "output_textures": [
        {
          "export_name_format": "/MeshName_Color",
          "export_image_format": "PNG",
          "export_colorspace": "SRGB",
          "export_bit_depth": "EIGHT",
          "pack_textures": [
            "COLOR",
            "COLOR",
            "COLOR",
            "NONE"
          ],
          "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ],
          "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ]
        },
        {
          "export_name_format": "/MeshName_Metallic",
          "export_image_format": "PNG",
          "export_colorspace": "NON_COLOR",
          "export_bit_depth": "EIGHT",
          "pack_textures": [
            "METALLIC",
            "METALLIC",
            "METALLIC",
            "NONE"
          ],
          "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ],
          "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ]
        },
        {
          "export_name_format": "/MeshName_Roughness",
          "export_image_format": "PNG",
          "export_colorspace": "NON_COLOR",
          "export_bit_depth": "EIGHT",
          "pack_textures": [
            "ROUGHNESS",
            "ROUGHNESS",
            "ROUGHNESS",
            "NONE"
          ],
          "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ],
          "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ]
        },
        {
          "export_name_format": "/MeshName_Normal",
          "export_image_format": "PNG",
          "export_colorspace": "NON_COLOR",
          "export_bit_depth": "EIGHT",
          "pack_textures": [
            "NORMAL_HEIGHT",
            "NORMAL_HEIGHT",
            "NORMAL_HEIGHT",
            "NONE"
          ],
          "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ],
          "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ]
        },
        {
          "export_name_format": "/MeshName_Emission",
          "export_image_format": "PNG",
          "export_colorspace": "NON_COLOR",
          "export_bit_depth": "EIGHT",
          "pack_textures": [
            "EMISSION",
            "EMISSION",
            "EMISSION",
            "NONE"
          ],
          "input_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ],
          "output_pack_channels": [
            "R",
            "G",
            "B",
            "A"
          ]
        }
      ]
    }
  ]
}

BIT_DEPTH = [
    ("EIGHT", "8-bit", "8-bit depth is the standard color bit depth for games"),
    ("THIRTY_TWO", "32-bit", "32-bit uses more memory in RGB channels, but will result in less color banding (not visible on old monitors)")
]

NORMAL_MAP_MODE = [
    ("OPEN_GL", "OpenGL", "Normal maps will be exported in Open GL format (same as they are in Blender)"),
    ("DIRECTX", "DirectX", "Exported normal maps will have their green channel automatically inverted so they export in Direct X format")
]

ROUGHNESS_MODE = [
    ("ROUGHNESS", "Roughness", "Roughness will be exported as is."),
    ("SMOOTHNESS", "Smoothness", "Roughness textures will be converted (inverted) to smoothness textures before exporting / packing. This supports some software which uses smoothness maps (e.g. Unity).")
]

RGBA_PACKING_CHANNELS = [
    ("R", "R", "Red Channel"),
    ("G", "G", "Green Channel"),
    ("B", "B", "Blue Channel"),
    ("A", "A", "Alpha Channel")
]

TEXTURE_EXPORT_FORMAT = [
    ("PNG", "png", "Exports the selected material channel in png texture format. This is a non-compressed format, and generally a good default"),
    ("JPEG", "jpg", "Exports the selected material channel in JPG texture format. This is a compressed format, which could be used for textures applied to models that will be shown in a web browser"),
    ("TARGA", "tga", "Exports the selected material channel in TARGA texture format"),
    ("OPEN_EXR", "exr", "Exports the selected material channel in open exr texture format")
]

EXPORT_MODE = [
    ("ONLY_ACTIVE_MATERIAL", "Only Active Material", "Export only the active material to a texture set"),
    ("EXPORT_ALL_MATERIALS", "Export All Materials", "Exports every object on the active material as it's own texture set"),
    ("SINGLE_TEXTURE_SET", "Single Texture Set", "Bakes all materials in all texture slots on the active object to 1 texture set. Separating the final material into separate smaller materials assigned to different parts of the mesh and then baking them to a single texture set can be efficient for workflow, and can reduce shader compilation time while editing")
]

# Available colorspace settings for exported textures.
IMAGE_COLORSPACE_SETTINGS = [
    ("SRGB", "sRGB", ""),
    ("NON_COLOR", "Non-Color", "")
]

# List of channels that should be baked using normal baking instead of the default emission baking.
NORMAL_BAKE_CHANNELS = [
    'NORMAL',
    'NORMAL_HEIGHT'
]


#----------------------------- CHANNEL PACKING / IMAGE EDITING FUNCTIONS -----------------------------#


def format_baked_material_channel_name(material_name, material_channel_name):
    '''Properly formats the baked material channel name.'''
    return "ML_{0}_{1}".format(material_name.replace('_', ''), material_channel_name.capitalize())

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

def channel_pack(pack_textures, input_packing, output_packing, image_name_format, color_bit_depth, file_format, export_colorspace):
    '''Channel packs the provided images into RGBA channels of a single image. Accepts None.'''

    # Create an array of output pixels using the first valid input texture.
    # Initialize full size empty arrays to avoid using dynamic arrays (caused by appending) which is much much slower.
    output_pixels = None
    source_pixels = None
    for channel_index in range(0, 4):
        image = pack_textures[channel_index]
        if image:
            w, h = image.size
            source_pixels = numpy.empty(w * h * 4, dtype=numpy.float32)
            output_pixels = numpy.ones(w * h * 4, dtype=numpy.float32)

    # Cycle through and pack RGBA channels.
    for channel_index in range(0, 4):
        image = pack_textures[channel_index]
        if image:

            # All packed images must be the same size for packing.
            # In some rare cases textures being packed could be different resolutions.
            # If this is the case, we'll re-scale the mesh maps to match the current texture set resolution so channel packing can occur.
            if image.size[0] != w or image.size[1] != h:
                image.scale(tss.get_texture_width(), tss.get_texture_height())
                debug_logging.log("Re-scaled {0} to match the texture set resolution for channel packing.".format(image.name))

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
    if pack_textures[3] != None:
        has_alpha = True

    # Translate bit depth to a boolean from an enum.
    use_thirty_two_bit = False
    match color_bit_depth:
        case 'EIGHT':
            use_thirty_two_bit = False
        case 'THIRTY_TWO':
            use_thirty_two_bit = True

    # Create an image using the packed pixels and save them to the disk.
    image_name = format_export_image_name(image_name_format)
    packed_image = bau.create_data_image(
        image_name,
        image_width=w,
        image_height=h,
        alpha_channel=has_alpha,
        thirty_two_bit=use_thirty_two_bit,
        data=True,
        delete_existing=True
    )

    # Define the colorspace for the packed image.
    match export_colorspace:
        case 'SRGB':
            packed_image.colorspace_settings.name = 'Linear Rec.709'
        case 'NON_COLOR':
            packed_image.colorspace_settings.name = 'sRGB'

    # Define a file format, filepath and then save the channel packed image.
    file_extension = bau.get_image_file_extension(file_format)
    export_path = bau.get_texture_folder_path(folder='EXPORT_TEXTURES')
    packed_image.file_format = file_format
    packed_image.filepath = "{0}/{1}.{2}".format(export_path, image_name, file_extension)
    packed_image.pixels.foreach_set(output_pixels)
    packed_image.save()
   
    # Save the packed image to a folder in the correct color space (note that the image must be saved already before the color space is shifted to sRGB otherwise the output will be blank).
    match export_colorspace:
        case 'SRGB':
            output_colorspace = 'sRGB'
        case 'NON_COLOR':
            output_colorspace = 'Non-Color'
    bau.save_image(packed_image, file_format, 'EXPORT_TEXTURE', colorspace=output_colorspace)

    return packed_image

def invert_image(image, invert_r = False, invert_g = False, invert_b = False, invert_a = False):
    '''Inverts specified color channels of the provided image.'''
    if image:
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
    else:
        debug_logging.log("Error: No image provided to invert.")

def channel_pack_textures(texture_set_name):
    '''Creates channel packed textures using pre-baked textures.'''
    texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
    active_object = bpy.context.active_object

    # Cycle through all defined export textures and channel pack them.
    for export_texture in texture_export_settings.export_textures:

        # Compile an array of baked images that will be used in channel packing based on the defined input texture...
        # ... and perform image alterations to select channels (normal / roughness / smoothness).
        input_images = []
        for key in export_texture.pack_textures.__annotations__.keys():
            texture_channel = getattr(export_texture.pack_textures, key)

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

                case 'WORLD_SPACE_NORMALS':
                    meshmap_name = mesh_map_baking.get_meshmap_name(active_object.name, 'WORLD_SPACE_NORMALS')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'ROUGHNESS':
                    image_name = format_baked_material_channel_name(texture_set_name, texture_channel)
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Convert (invert) roughness to a smoothness map based on settings.
                    if texture_export_settings.roughness_mode == 'SMOOTHNESS':
                        invert_image(image, True, True, True, False)

                case 'NORMAL':
                    image_name = format_baked_material_channel_name(texture_set_name, texture_channel)
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Invert normal map G values if exporting for DirectX based on settings.
                    if texture_export_settings.normal_map_mode == 'DIRECTX':
                        invert_image(image, False, True, False, False)

                case 'NORMAL_HEIGHT':
                    image_name = format_baked_material_channel_name(texture_set_name, 'NORMAL')
                    image = bpy.data.images.get(image_name)
                    input_images.append(image)

                    # Invert normal map G values if exporting for DirectX based on settings.
                    if texture_export_settings.normal_map_mode == 'DIRECTX':
                        invert_image(image, False, True, False, False)

                case 'NONE':
                    input_images.append(None)

                case _:
                    image_name = format_baked_material_channel_name(texture_set_name, texture_channel)
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
            pack_textures=input_images,
            input_packing=input_packing_channels,
            output_packing=output_packing_channels,
            image_name_format=export_texture.name_format,
            color_bit_depth=export_texture.bit_depth,
            file_format=export_texture.image_format,
            export_colorspace=export_texture.colorspace
        )

    # Delete temp material channel bake images, they are no longer needed because they are packed into new textures now.
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        temp_material_channel_image_name = format_baked_material_channel_name(texture_set_name, channel.name )
        temp_material_channel_image = bpy.data.images.get(temp_material_channel_image_name)
        if temp_material_channel_image:
            bpy.data.images.remove(temp_material_channel_image)

    debug_logging.log("Channel packed textures.")


#----------------------------- EXPORTING FUNCTIONS -----------------------------#


def format_export_image_name(texture_name_format):
    '''Properly formats the name for an export image based on the selected texture export template and the provided material channel.'''
    material_name = bpy.context.active_object.active_material.name
    mesh_name = bpy.context.active_object.name

    # Replace specific key words in the texture name format.
    image_name = texture_name_format.replace("/MaterialName", material_name)
    image_name = image_name.replace("/MeshName", mesh_name)
    
    return image_name

def get_texture_channel_bake_list():
    '''Returns a list of material channels required to be baked as defined in the texture export settings.'''
    texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
    material_channels_to_bake = []
    for export_texture in texture_export_settings.export_textures:
        for key in export_texture.pack_textures.__annotations__.keys():
            input_texture_channel = getattr(export_texture.pack_textures, key)
            if input_texture_channel not in material_channels_to_bake:
                if input_texture_channel != 'NONE':
                    material_channels_to_bake.append(input_texture_channel)
    
    # Normal map data bakes blank if they are baked before other maps, it's unclear why.
    # Bake all normal maps first to avoid this error.
    if 'NORMAL-HEIGHT-MIX' in material_channels_to_bake:
        material_channels_to_bake.insert(0, material_channels_to_bake.pop(material_channels_to_bake.index('NORMAL-HEIGHT-MIX')))

    if 'NORMAL' in material_channels_to_bake:
        material_channels_to_bake.insert(0, material_channels_to_bake.pop(material_channels_to_bake.index('NORMAL')))

    debug_logging.log("Baking channels: {0}".format(material_channels_to_bake))
    return material_channels_to_bake

def set_export_template(export_template_name):
    '''Applies the export template settings stored in the specified export template from the export template json file.'''
    # TODO: BPY context isn't available here if this is called on scene load.
    texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
    jdata = read_export_template_data()
    export_templates = jdata['export_templates']
    for template in export_templates:
        if template['name'] == export_template_name:
            texture_export_settings.export_template_name = template['name']
            texture_export_settings.roughness_mode = template['roughness_map_mode']
            texture_export_settings.normal_map_mode = template['normal_map_mode']
            texture_export_settings.export_textures.clear()
            for texture in template['output_textures']:
                export_texture = texture_export_settings.export_textures.add()
                export_texture.name_format = texture['export_name_format']
                export_texture.image_format = texture['export_image_format']
                export_texture.bit_depth = texture['export_bit_depth']
                export_texture.colorspace = texture['export_colorspace']

                enum_items = get_shader_channel_enum_items()
                export_texture.pack_textures.r_texture = bau.get_valid_enum(enum_items, texture['pack_textures'][0], 'NONE')
                export_texture.pack_textures.g_texture = bau.get_valid_enum(enum_items, texture['pack_textures'][1], 'NONE')
                export_texture.pack_textures.b_texture = bau.get_valid_enum(enum_items, texture['pack_textures'][2], 'NONE')
                export_texture.pack_textures.a_texture = bau.get_valid_enum(enum_items, texture['pack_textures'][3], 'NONE')
                export_texture.input_rgba_channels.r_color_channel = texture['input_pack_channels'][0]
                export_texture.input_rgba_channels.g_color_channel = texture['input_pack_channels'][1]
                export_texture.input_rgba_channels.b_color_channel = texture['input_pack_channels'][2]
                export_texture.input_rgba_channels.a_color_channel = texture['input_pack_channels'][3]
                export_texture.output_rgba_channels.r_color_channel = texture['output_pack_channels'][0]
                export_texture.output_rgba_channels.g_color_channel = texture['output_pack_channels'][1]
                export_texture.output_rgba_channels.b_color_channel = texture['output_pack_channels'][2]
                export_texture.output_rgba_channels.a_color_channel = texture['output_pack_channels'][3]

            debug_logging.log("Applied export template: {0}".format(export_template_name))
            return
    
    debug_logging.log("Error export template was not found in the json file and can't be applied")
    return

def bake_material_channel(material_channel_name, single_texture_set=False):
    '''Bakes the defined material channel to an image texture and stores it in Blender's data. Returns true if baking was successful.'''

    # Ensure the material channel name provided is valid to bake.
    static_channel_list = shaders.get_static_shader_channel_list()
    if material_channel_name not in static_channel_list:
        debug_logging.log("Can't bake invalid material channel: {0}".format(material_channel_name))
        return ""

    # Skip baking for material channels that are toggled off in the texture set settings.
    if not tss.get_material_channel_active(material_channel_name):
        debug_logging.log("Skipped baking for disabled material channel: {channel_name}.".format(channel_name=material_channel_name))
        return ""

    # Define a background color for new bake textures.
    background_color = (0.0, 0.0, 0.0, 1.0)
    if material_channel_name == 'NORMAL' or material_channel_name == 'NORMAL_HEIGHT':
        background_color = (0.735337, 0.735337, 1.0, 1.0)

    # Normal + height material channel combines height information into the normal map.
    # Convert the name used in exported textures for the normal + height material channel to normal.
    export_channel_name = material_channel_name
    if material_channel_name == 'NORMAL_HEIGHT':
        export_channel_name = 'NORMAL'

    # For baking multiple materials to a single texture set use one image that uses the name of the active object.
    if single_texture_set:
        object_name = bpy.context.active_object.name.replace('_', '')
        image_name = format_baked_material_channel_name(object_name, export_channel_name)
        export_image = bpy.data.images.get(image_name)
        if export_image == None:
            export_image = bau.create_image(
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
            image_utilities.set_image_colorspace_by_material_channel(export_image, material_channel_name)

    # For baking individual materials to textures, create new images to bake to for each material.
    else:
        material_name = bpy.context.active_object.active_material.name.replace('_', '')
        image_name = format_baked_material_channel_name(material_name, export_channel_name)
        export_image = bau.create_image(
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
        image_utilities.set_image_colorspace_by_material_channel(export_image, material_channel_name)

    # Add the baking image to the preset baking texture node (included in the default material setup).
    material_nodes = bpy.context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.get('BAKE_IMAGE')
    image_node.image = export_image
    image_node.select = True
    material_nodes.active = image_node
    bau.set_texture_paint_image(export_image)

    # For baking channels output from the shader node, connect them to an emission node then bake.
    output_channels = []
    active_material = bpy.context.active_object.active_material
    shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
    if shader_node:
        for i in range(1, len(shader_node.outputs)):
            static_channel = bau.format_node_channel_name(shader_node.outputs[i].name)
            output_channels.append(static_channel)

    if material_channel_name in output_channels:
        active_node_tree = bpy.context.active_object.active_material.node_tree
        emission_node = active_node_tree.nodes.get('EMISSION')
        shader_node = active_node_tree.nodes.get('MATLAYER_SHADER')
        material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')
        bau.safe_node_link(shader_node.outputs.get(material_channel_name), emission_node.inputs[0], active_node_tree)
        bau.safe_node_link(emission_node.outputs[0], material_output.inputs[0], active_node_tree)
    
    # For all other material channels, use the isolate material channel function, then bake.
    else:
        material_layers.isolate_material_channel(material_channel_name)

    # Trigger either emission or normal baking based on the material channel name.
    if material_channel_name in NORMAL_BAKE_CHANNELS:
        bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')
    else:
        bpy.ops.object.bake('INVOKE_DEFAULT', type='EMIT')

    return export_image.name

def add_bake_texture_nodes():
    '''Adds a bake texture node to all materials in all material slots on the active object.'''

    # Adding a placeholder image to the bake image nodes stops Blender from throwing annoying and incorrect 'no active image' warnings when baking'.
    placeholder_image = bau.create_data_image("ML_Placeholder", image_width=32, image_height=32)

    active_object = bpy.context.active_object
    for material_slot in active_object.material_slots:
        if material_slot.material:
            bake_texture_node = material_slot.material.node_tree.nodes.new('ShaderNodeTexImage')
            bake_texture_node.name = 'BAKE_IMAGE'
            bake_texture_node.label = bake_texture_node.name
            bake_texture_node.image = placeholder_image
            bake_texture_node.select = True
            material_slot.material.node_tree.nodes.active = bake_texture_node

            # Link the export UV map to the bake texture node.
            export_uv_map_node = material_layers.get_material_layer_node('EXPORT_UV_MAP')
            if export_uv_map_node:
                material_slot.material.node_tree.links.new(export_uv_map_node.outputs[0], bake_texture_node.inputs[0])

            # Select the export UV map, otherwise Blender will still bake to the original UV map.
            export_uv_map_name = export_uv_map_node.uv_map
            export_uv_map_data = active_object.data.uv_layers.get(export_uv_map_name)
            if export_uv_map_data:
                export_uv_map_data.active = True

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

def read_export_template_data():
    '''Reads json data from the export template file. Creates a new export template json file if one does not exist.'''
    template_folder_path = str(Path(resource_path('USER')) / "scripts/addons" / ADDON_NAME / "json_data")
    if not os.path.exists(template_folder_path):
        os.mkdir(template_folder_path)

    # If the export template doesn't exist, create a new default one.
    templates_json_path = os.path.join(template_folder_path, "export_templates.json")
    if os.path.exists(templates_json_path):
        json_file = open(templates_json_path, "r")
        jdata = json.load(json_file)
        json_file.close()
    else:
        with open(templates_json_path,"w") as f:
            json.dump(default_json_file, f)
        
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
        texture_export_settings.export_template_name = "PBR Metallic Roughness"
        read_export_template_names()

    return jdata

def save_export_template_data(json_data):
    '''Saves the specified json data to the export template file.'''
    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / ADDON_NAME / "json_data" / "export_templates.json")
    json_file = open(templates_path, "w")
    json.dump(json_data, json_file)
    json_file.close()
    
def read_export_template_names():
    '''Reads all of the export template names from the json file into Blender memory (to avoid reading json data in a draw call).'''
    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / ADDON_NAME / "json_data" / "export_templates.json")
    json_file = open(templates_path, "r")
    jdata = json.load(json_file)
    json_file.close()
    export_templates = jdata['export_templates']
    cached_template_names = bpy.context.scene.matlayer_export_templates
    cached_template_names.clear()
    for template in export_templates:
        cached_template = cached_template_names.add()
        cached_template.name = template['name']
    debug_logging.log("Updated export templates.")

def get_shader_channel_enum_items(scene=None, context=None):
    '''Returns an enum list of current shader channels that can be used in RGBA channel packing.'''
    items = []

    # Add a 'NONE' ENUM option for when no texture needs to be channel packed in an RGBA channel.
    items += [("NONE", "None", "None")]

    # Add an ENUM option for all shader channels.
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        items += [(
            bau.format_node_channel_name(channel.name),
            channel.name,
            ""
        )]

    # Add ENUM options for all output pins on the shader node the user can bake from.
    active_material = bpy.context.active_object.active_material
    shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
    if shader_node:
        for i in range(1, len(shader_node.outputs)):
            static_socket_name = bau.format_node_channel_name(shader_node.outputs[i].name)
            items += [(static_socket_name, shader_node.outputs[i].name, '')]
    
    return items


#----------------------------- EXPORT OPERATORS -----------------------------#


class MATLAYER_pack_textures(PropertyGroup):
    r_texture: EnumProperty(items=get_shader_channel_enum_items, name='R Texture')
    g_texture: EnumProperty(items=get_shader_channel_enum_items, name='G Texture')
    b_texture: EnumProperty(items=get_shader_channel_enum_items, name='B Texture')
    a_texture: EnumProperty(items=get_shader_channel_enum_items, name='A Texture')

class MATLAYER_RGBA_pack_channels(PropertyGroup):
    r_color_channel: EnumProperty(items=RGBA_PACKING_CHANNELS, default='R', name="R")
    g_color_channel: EnumProperty(items=RGBA_PACKING_CHANNELS, default='G', name="G")
    b_color_channel: EnumProperty(items=RGBA_PACKING_CHANNELS, default='B', name="B")
    a_color_channel: EnumProperty(items=RGBA_PACKING_CHANNELS, default='A', name="A")

class MATLAYER_texture_export_settings(PropertyGroup):
    '''Settings that define how a texture is exported from this add-on.'''
    name_format: StringProperty(name="Name Format", default="T_/MaterialName_C", description="Name format for the texture. You can add trigger words that will be automatically replaced upon export to name formats including: '/MaterialName', '/MeshName' ")
    image_format: EnumProperty(items=TEXTURE_EXPORT_FORMAT, default='PNG')
    bit_depth: EnumProperty(items=BIT_DEPTH, default='EIGHT')
    colorspace: EnumProperty(items=IMAGE_COLORSPACE_SETTINGS, default='SRGB')
    pack_textures: PointerProperty(type=MATLAYER_pack_textures, name="Pack Textures")
    input_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Input Pack Channels")
    output_rgba_channels: PointerProperty(type=MATLAYER_RGBA_pack_channels, name="Output Pack Channels")

class MATLAYER_texture_set_export_settings(PropertyGroup):
    '''Settings that define how textures are exported from this add-on.'''
    export_template_name: StringProperty(name="Export Template Name", default="PBR Metallic Roughness")
    export_textures: CollectionProperty(type=MATLAYER_texture_export_settings)
    roughness_mode: EnumProperty(name="Roughness Mode", items=ROUGHNESS_MODE, default='ROUGHNESS')
    normal_map_mode: EnumProperty(name="Normal Map Mode", items=NORMAL_MAP_MODE, default='OPEN_GL')
    export_mode: EnumProperty(name="Export Active Material", items=EXPORT_MODE, description="Exports only the active material using the defined export settings", default='SINGLE_TEXTURE_SET')

class MATLAYER_export_template_names(PropertyGroup):
    name: bpy.props.StringProperty()

class MATLAYER_OT_export(Operator):
    bl_idname = "matlayer.export"
    bl_label = "Export"
    bl_description = "Bakes material channels to textures, packs RGBA channels then saves all textures to the defined folder"

    _timer = None
    _total_materials_to_bake = 0
    _texture_channel_index = -1
    _texture_channels_to_bake = []
    _mesh_map_channels_to_bake = []
    _original_render_engine_name = ""
    _bake_image_name = ""
    _start_bake_time = 0

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
                    if not bake_image.packed_file:
                        bake_image.pack()
                        debug_logging.log("Baked - (texture channel - active material): {0} - {1}".format(self._bake_image_name, bpy.context.active_object.active_material.name))
                
                # Start baking the next material channel.
                texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
                if self._texture_channel_index < len(self._texture_channels_to_bake) - 1:
                    self._texture_channel_index += 1
                    self._bake_image_name = ""
                    if texture_export_settings.export_mode == 'SINGLE_TEXTURE_SET':
                        self._bake_image_name = bake_material_channel(self._texture_channels_to_bake[self._texture_channel_index], single_texture_set=True)
                    else:
                        self._bake_image_name = bake_material_channel(self._texture_channels_to_bake[self._texture_channel_index], single_texture_set=False)

                else:
                    # If all of the textures are baked for the active material...
                    if bpy.context.active_object.active_material_index + 1 < self._total_materials_to_bake:
                        debug_logging.log("Completed baking textures for material: {0}".format(bpy.context.active_object.active_material.name))

                        # Channel pack baked textures after baking each material unless we are baking to a single texture set.
                        if texture_export_settings.export_mode != 'SINGLE_TEXTURE_SET':
                            channel_pack_textures(bpy.context.active_object.active_material.name)

                        # Move to baking the next material.
                        bpy.context.active_object.active_material_index += 1
                        while bau.verify_addon_material(bpy.context.active_object.active_material) == False and bpy.context.active_object.active_material_index + 1 < self._total_materials_to_bake:
                            debug_logging.log("Skipped exporting texture set for invalid material (not created with this add-on): {0}".format(bpy.context.active_object.active_material.name))
                            bpy.context.active_object.active_material_index += 1

                        # Reset the texture channel index so all material channels are baked for the next material.
                        self._texture_channel_index = -1

                        # Link the export UV map for the next material.
                        active_material = bpy.context.active_object.active_material
                        export_uv_map_node = material_layers.get_material_layer_node('EXPORT_UV_MAP')
                        bake_texture_node = active_material.node_tree.nodes.get('BAKE_IMAGE')
                        if export_uv_map_node and bake_texture_node:
                            active_material.node_tree.links.new(export_uv_map_node.outputs[0], bake_texture_node.inputs[0])
                    else:
                        # Channel pack textures.
                        if texture_export_settings.export_mode == 'SINGLE_TEXTURE_SET':
                            channel_pack_textures(bpy.context.active_object.name)
                        else:
                            channel_pack_textures(bpy.context.active_object.active_material.name)
                        
                        # De-isolating materials directly after their finished baking will cause errors.
                        # De-isolate all materials at the end of baking.
                        for i in range(0, len(bpy.context.active_object.material_slots)):
                            bpy.context.active_object.active_material_index = i
                            if bau.verify_addon_material(bpy.context.active_object.material_slots[i].material):
                                material_layers.show_layer()

                        material_layers.refresh_layer_stack()
                        self.finish(context)
                        return {'FINISHED'}
                
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Verify the export folder is valid.
        export_folder = bau.get_texture_folder_path(folder='EXPORT_TEXTURES')
        folder_valid = bau.verify_folder(export_folder)
        if not folder_valid:
            debug_logging.log_status("Define a valid export folder before exporting, or reset the folder path to 'Default'.", self, type='ERROR')
            return {'FINISHED'}
        
        # Verify the object can be baked to.
        if bau.verify_bake_object(self, check_active_material=True) == False:
            return {'FINISHED'}
        
        # To avoid errors don't start baking if there is already a bake job running.
        if bpy.app.is_job_running('OBJECT_BAKE') == True:
            debug_logging.log_status("Bake job already in process, cancel or wait until the bake is finished before starting another.", self)
            return {'FINISHED'}
        
        # Record the starting time before baking.
        self._start_bake_time = time.time()

        # Pause auto updating for add-on properties, they will cause errors while baking.
        bpy.context.scene.pause_auto_updates = True
        
        # Set the viewport shading mode to 'Material' so users can monitor the baking process.
        bpy.context.space_data.shading.type = 'MATERIAL'

        # Compile a list of material channels that require baking based on settings.
        self._texture_channels_to_bake = get_texture_channel_bake_list()

        # Get the number of materials to bake and export.
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
        match texture_export_settings.export_mode:
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

                # Textures aren't cleared when baking to a single texture set.
                # Delete any baked material channel images to ensure they are blank before baking the first material.
                for texture_channel_name in self._texture_channels_to_bake:
                    if texture_channel_name == 'NORMAL_HEIGHT':
                        channel_name = 'NORMAL'
                    else:
                        channel_name = texture_channel_name
                    object_name = bpy.context.active_object.name.replace('_', '')
                    image_name = format_baked_material_channel_name(object_name, channel_name)
                    export_image = bpy.data.images.get(image_name)
                    if export_image:
                        bpy.data.images.remove(export_image)

        # If there are no texture channels to bake, channel pack and finish.
        if len(self._texture_channels_to_bake) <= 0:
            debug_logging.log_status("No texture channels to bake.", self, type='INFO')
            return {'FINISHED'}
        
        # Add texture nodes to bake to.
        add_bake_texture_nodes()

        # Remember the original render engine so we can reset it after baking.
        bpy.context.scene.render.engine = 'CYCLES'
        self._original_render_engine_name = bpy.context.scene.render.engine

        # Apply baking settings for exporting textures.
        baking_settings = bpy.context.scene.matlayer_baking_settings
        bpy.context.scene.render.bake.margin = baking_settings.uv_padding
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.context.scene.cycles.samples = 1

        # Force save all textures (unsaved textures will be cleared and not bake properly).
        bau.force_save_all_textures()

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
        bpy.context.scene.pause_auto_updates = False
        self.report({'INFO'}, "Exporting textures was manually cancelled.")

    def finish(self, context):
        # Remove the timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        bpy.context.scene.render.engine = self._original_render_engine_name
        remove_bake_texture_nodes()
        material_layers.refresh_layer_stack()
        bpy.context.scene.pause_auto_updates = False

        # Log the completion exporting textures.
        end_bake_time = time.time()
        total_bake_time = end_bake_time - self._start_bake_time
        debug_logging.log_status("Exporting texture(s) completed, total bake time: {0} seconds.".format(round(total_bake_time), 1), self, 'INFO')

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
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings

        # Check if the export template json file exists.
        jdata = read_export_template_data()
        template_existed = False
        new_export_template = None
        export_templates = jdata['export_templates']
        for template in export_templates:
            if template['name'] == texture_export_settings.export_template_name:
                new_export_template = template
                template_existed = True

        # If the active template doesn't exist in the json file, create a new one by duplicating defined default json data for export templates.
        if template_existed == False:
            new_export_template = copy.deepcopy(default_export_template_json)

        # Overwrite the properties of the export template with the export properties defined in the user interface.
        new_export_template['name'] = texture_export_settings.export_template_name
        new_export_template['roughness_map_mode'] = texture_export_settings.roughness_mode
        new_export_template['normal_map_mode'] = texture_export_settings.normal_map_mode

        output_textures = new_export_template['output_textures']
        output_textures.clear()
        for export_texture in texture_export_settings.export_textures:
            output_textures.append(copy.deepcopy(default_output_texture))
        output_textures = new_export_template['output_textures']
        for i, export_texture in enumerate(texture_export_settings.export_textures):
            new_export_template['output_textures'][i]['export_name_format'] = export_texture.name_format
            new_export_template['output_textures'][i]['export_image_format'] = export_texture.image_format
            new_export_template['output_textures'][i]['export_colorspace'] = export_texture.colorspace
            new_export_template['output_textures'][i]['export_bit_depth'] = export_texture.bit_depth

            new_export_template['output_textures'][i]['pack_textures'][0] = export_texture.pack_textures.r_texture
            new_export_template['output_textures'][i]['pack_textures'][1] = export_texture.pack_textures.g_texture
            new_export_template['output_textures'][i]['pack_textures'][2] = export_texture.pack_textures.b_texture
            new_export_template['output_textures'][i]['pack_textures'][3] = export_texture.pack_textures.a_texture

            new_export_template['output_textures'][i]['input_pack_channels'][0] = export_texture.input_rgba_channels.r_color_channel
            new_export_template['output_textures'][i]['input_pack_channels'][1] = export_texture.input_rgba_channels.g_color_channel
            new_export_template['output_textures'][i]['input_pack_channels'][2] = export_texture.input_rgba_channels.b_color_channel
            new_export_template['output_textures'][i]['input_pack_channels'][3] = export_texture.input_rgba_channels.a_color_channel

            new_export_template['output_textures'][i]['output_pack_channels'][0] = export_texture.output_rgba_channels.r_color_channel
            new_export_template['output_textures'][i]['output_pack_channels'][1] = export_texture.output_rgba_channels.g_color_channel
            new_export_template['output_textures'][i]['output_pack_channels'][2] = export_texture.output_rgba_channels.b_color_channel
            new_export_template['output_textures'][i]['output_pack_channels'][3] = export_texture.output_rgba_channels.a_color_channel

        # Save the new template to the json file.
        if template_existed:
            debug_logging.log_status("Export template settings updated.", self, type='INFO')
            save_export_template_data(jdata)
        else:
            jdata['export_templates'].append(new_export_template)
            debug_logging.log_status("New custom export template created.", self, type='INFO')
            save_export_template_data(jdata)

        # Update the cached list of export templates.
        read_export_template_names()        
        return {'FINISHED'}

class MATLAYER_OT_delete_export_template(Operator):
    bl_idname = "matlayer.delete_export_template"
    bl_label = "Delete Export Template"
    bl_description = "Deletes the currently selected export template from the json file if it exists"
    
    def execute(self, context):
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings

        # Read the existing export templates from the json data.
        jdata = read_export_template_data()

        # Delete the template if it exists in the json data.
        export_templates = jdata['export_templates']
        for template in export_templates:
            if template['name'] == texture_export_settings.export_template_name:
                template_name = template['name']
                export_templates.remove(template)
                debug_logging.log_status("Deleted template: {0}".format(template_name), self, type='INFO')
                break
        
        save_export_template_data(jdata)        # Write the changes to the json file.
        read_export_template_names()            # Update the cached template names.

        # Apply a different export template.
        if len(export_templates) > 0:
            set_export_template(export_templates[0]['name'])

        return {'FINISHED'}

class MATLAYER_OT_refresh_export_template_list(Operator):
    bl_idname = "matlayer.refresh_export_template_list"
    bl_label = "Refresh Export Template List"
    bl_description = "Updates the list of export templates by reading the export template json file"
    
    def execute(self, context):
        # Update the cached template names.
        read_export_template_names()
        return {'FINISHED'}

class MATLAYER_OT_add_export_texture(Operator):
    bl_idname = "matlayer.add_export_texture"
    bl_label = "Add Export Texture"
    bl_description = "Adds an additional texture to the export texture list"
    
    def execute(self, context):
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
        texture_export_settings.export_textures.add()
        return {'FINISHED'}

class MATLAYER_OT_remove_export_texture(Operator):
    bl_idname = "matlayer.remove_export_texture"
    bl_label = "Remove Export Texture"
    bl_description = "Removes the related texture from the export texture list"

    export_texture_index: IntProperty(default=0)
    
    def execute(self, context):
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
        texture_export_settings.export_textures.remove(self.export_texture_index)
        return {'FINISHED'}

class MATLAYER_OT_set_export_folder(Operator):
    bl_idname = "matlayer.set_export_folder"
    bl_label = "Set Export Folder"
    bl_description = "Opens a file explorer to select the folder where exported textures are saved"
    bl_options = {'REGISTER'}

    directory: StringProperty()

    # Filters for only folders.
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )

    def execute(self, context):
        if not os.path.isdir(self.directory):
            debug_logging.log_status("Invalid directory.", self, type='INFO')
        else:
            context.scene.matlayer_export_folder = self.directory
            debug_logging.log_status("Export folder set to: {0}".format(self.directory), self, type='INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MATLAYER_OT_open_export_folder(Operator):
    bl_idname = "matlayer.open_export_folder"
    bl_label = "Open Export Folder"
    bl_description = "Opens the folder containing exported textures in your systems file explorer"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        matlayer_export_folder_path = bau.get_texture_folder_path(folder='EXPORT_TEXTURES')
        bau.open_folder(matlayer_export_folder_path, self)
        return {'FINISHED'}

class ExportTemplateMenu(Menu):
    bl_idname = "MATLAYER_MT_export_template_menu"
    bl_label = "Export Template Menu"
    bl_description = "Contains options to set a specific export template"

    def draw(self, context):
        layout = self.layout
        cached_template_names = bpy.context.scene.matlayer_export_templates
        for template in cached_template_names:
            op = layout.operator("matlayer.set_export_template", text=template.name)
            op.export_template_name = template.name
