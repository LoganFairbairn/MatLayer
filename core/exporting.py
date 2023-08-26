import os
import numpy
import bpy
from bpy.types import Operator, PropertyGroup, Menu
from bpy.props import BoolProperty, StringProperty, IntProperty
from ..core import baking
from ..core import texture_set_settings
from .. import preferences


#----------------------------- EXPORT SETTINGS -----------------------------#


class MATLAYER_exporting_settings(PropertyGroup):
    export_folder: StringProperty(default="", description="Path to folder location where exported texture are saved. If empty, an export folder will be created next to your .blend file and exported textures will be automatically saved there.", name="Export Folder Path")
    export_base_color: BoolProperty(default=True, name="Export Base Color", description="Include the base color in batch exporting")
    export_subsurface: BoolProperty(default=False, name="Export Subsurface", description="Include the subsurface in batch exporting")
    export_subsurface_color: BoolProperty(default=False, name="Export Subsurface Color", description="Include the subsurface color in batch exporting")
    export_metallic: BoolProperty(default=True, name="Export Metallic", description="Include the metallic in batch exporting")
    export_specular: BoolProperty(default=False, name="Export Specular", description="Include the specular in batch exporting")
    export_roughness: BoolProperty(default=True, name="Export Roughness", description="Include the roughness in batch exporting")
    export_normals: BoolProperty(default=True, name="Export Normals", description="Include the normals in batch exporting")
    export_height: BoolProperty(default=False, name="Export Height", description="Include the height in batch exporting")
    export_emission: BoolProperty(default=False, name="Export Emission", description="Include the emission in batch exporting")
    export_ambient_occlusion: BoolProperty(default=False, name="Export Ambient Occlusion", description="Exports the ambient occlusion mesh map")


#----------------------------- EXPORT FUNCTIONS -----------------------------#


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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.name_format = "T_/MaterialName_SSC"
                new_channel.input_textures.r_texture = 'SUBSURFACE_COLOR'
                new_channel.input_textures.g_texture = 'SUBSURFACE_COLOR'
                new_channel.input_textures.b_texture = 'SUBSURFACE_COLOR'
                new_channel.input_textures.a_texture = 'NONE'

                new_channel = export_textures.add()
                new_channel.name_format = "T_/MaterialName_ORM"
                new_channel.input_textures.r_texture = 'AMBIENT_OCCLUSION'
                new_channel.input_textures.g_texture = 'ROUGHNESS'
                new_channel.input_textures.b_texture = 'METALLIC'
                new_channel.input_textures.a_texture = 'NONE'

                new_channel = export_textures.add()
                new_channel.name_format = "T_/MaterialName_NDX"
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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
                new_channel.input_textures.a_texture = 'OPACITY'

                new_channel = export_textures.add()
                new_channel.name_format = "T_/MaterialName_S"
                new_channel.input_textures.r_texture = 'SPECULAR'
                new_channel.input_textures.g_texture = 'SPECULAR'
                new_channel.input_textures.b_texture = 'SPECULAR'
                new_channel.input_textures.a_texture = 'NONE'

                new_channel = export_textures.add()
                new_channel.name_format = "T_/MaterialName_NDXO"
                new_channel.input_textures.r_texture = 'NORMAL'
                new_channel.input_textures.g_texture = 'NORMAL'
                new_channel.input_textures.b_texture = 'NORMAL'
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

def bake_material_channel(material_channel_name, export_image_name, thirty_two_bit, self, context):
    '''Bakes the defined material channel to an image texture (stores it in Blender's data). Returns true if baking was successful.'''

    # Verify the selected object can be baked from.
    if baking.verify_bake_object(self) == False:
        return
    
    # Verify the material can be baked from.
    if matlayer_materials.verify_material(context) == False:
        return
    
    # Ensure there is a material on the active object.
    if bpy.context.active_object.active_material == None:
        self.report({'INFO'}, "Selected object doesn't have an active material.")
        return
    
    # Force save all textures (unsaved texture will not bake to textures properly).
    for image in bpy.data.images:
        if image.filepath != '' and image.is_dirty and image.has_data:
            image.save()

    # Isolate the material channel.
    if material_channel_name != 'NORMAL':
        material_channels.isolate_material_channel(True, material_channel_name, context)

    # Create a new image to bake to.
    export_image = internal_utils.create_image(export_image_name,
                                               texture_set_settings.get_texture_width(),
                                               texture_set_settings.get_texture_height(),
                                               False,
                                               thirty_two_bit)

    # Create a temporary image texture node to bake to.
    material_nodes = context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.new('ShaderNodeTexImage')
    image_node.image = export_image
    image_node.select = True
    material_nodes.active = image_node

    # Cache the render engine so we can reset it after baking with Cycles.
    original_render_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_selected_to_active = False
    if material_channel_name == 'NORMAL':
        bpy.ops.object.bake(type='NORMAL')
    else:
        bpy.ops.object.bake(type='EMIT')

    # Reset the render engine.
    bpy.context.scene.render.engine = original_render_engine

    # Delete the image texture node, it's no longer needed.
    material_nodes.remove(image_node)

    # De-isolate the material channel.
    if material_channel_name != 'NORMAL':
        material_channels.isolate_material_channel(False, material_channel_name, context)

    logging.log("Baked the {channel_name} material channel to an image texture.".format(channel_name=material_channel_name))

    return export_image

def bake_export_textures(self, context):
    '''Bakes all textures based on the list of defined textures to export.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    # Create a list of textures to bake based on the list of defined textures to export.
    material_channels_to_bake = []
    for export_texture in addon_preferences.export_textures:
        for key in export_texture.input_textures.__annotations__.keys():
            input_texture_channel = getattr(export_texture.input_textures, key)
            if input_texture_channel not in material_channels_to_bake:
                material_channels_to_bake.append(input_texture_channel)
    logging.log("Baking channels: " + str(material_channels_to_bake))

    # Bake a texture for each material channel that requires baking.
    for material_channel_name in material_channels_to_bake:

        # Skip baking for mesh maps and some other specific types.
        match material_channel_name:
            case 'AMBIENT_OCCLUSION':
                continue
            case 'CURVATURE':
                continue
            case 'THICKNESS':
                continue
            case 'BASE_NORMALS':
                continue
            case 'OPACITY':
                continue
            case 'NONE':
                continue

        # Skip baking for material channels that are toggled off in the texture set settings.
        texture_set_settings = context.scene.matlayer_texture_set_settings
        material_channel_enabled = getattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle")
        if not material_channel_enabled:
            logging.log("Skipped baking for disabled material channel {channel_name}.".format(channel_name=material_channel_name))
            continue

        # Bake material channel to a texture (always bake material channels to 32-bit images).
        temp_material_channel_image_name = "ML_{channel_name}".format(channel_name=material_channel_name)
        bake_material_channel(material_channel_name, temp_material_channel_image_name, True, self, context)

    return True

def format_export_image_name(texture_name_format):
    '''Properly formats the name for an export image based on the selected texture export template and the provided material channel.'''
    material_name = bpy.context.active_object.material_slots[0].name        # TODO: Takes the first material name, but in the future, taking the name of the material being baked will be ideal.
    mesh_name = bpy.context.active_object.name

    # Replace key words in the texture name format.
    image_name = texture_name_format.replace("/MaterialName", material_name)
    image_name = image_name.replace("/MeshName", mesh_name)
    
    return image_name

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
    packed_image = internal_utils.create_image(image_name,
                                            image_width=w,
                                            image_height=h,
                                            alpha_channel=has_alpha,
                                            thirty_two_bit=use_thirty_two_bit,
                                            data=True)
    packed_image.file_format = file_format
    packed_image.filepath = "{0}/{1}.{2}".format(export_path, image_name, file_format.lower())
    packed_image.pixels.foreach_set(output_pixels)
    packed_image.save()

    return packed_image

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

def delete_unpacked_images():
    '''Deletes all textures that were packed into images.'''
    print("Placeholder...")

def channel_pack_textures():
    '''Creates channel packed textures using pre-baked textures.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    # Cycle through all defined export textures and channel pack them.
    for export_texture in addon_preferences.export_textures:

        # Get the baked images that will be used in channel packing based on the defined input texture.
        input_images = []
        for key in export_texture.input_textures.__annotations__.keys():
            texture_channel = getattr(export_texture.input_textures, key)

            match texture_channel:
                case 'AMBIENT_OCCLUSION':
                    meshmap_name = baking.get_meshmap_name('AMBIENT_OCCLUSION')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'CURVATURE':
                    meshmap_name = baking.get_meshmap_name('CURVATURE')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'THICKNESS':
                    meshmap_name = baking.get_meshmap_name('THICKNESS')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'BASE_NORMALS':
                    meshmap_name = baking.get_meshmap_name('NORMAL')
                    image = bpy.data.images.get(meshmap_name)
                    input_images.append(image)

                case 'OPACITY':
                    input_images.append(None)       # Not implemented, append None for now.

                case 'NONE':
                    input_images.append(None)

                case 'ROUGHNESS':
                    image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
                    input_images.append(image)

                    # Convert (invert) roughness to a smoothness map based on settings.
                    if addon_preferences.roughness_mode == 'SMOOTHNESS':
                        invert_image(image, True, True, True, False)

                case 'NORMAL':
                    image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
                    input_images.append(image)

                    # Invert normal map G values if exporting for DirectX based on settings.
                    if addon_preferences.normal_map_mode == 'DIRECTX':
                        invert_image(image, False, True, False, False)

                case _:
                    # Get required baked images for packing using their temp name.
                    image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
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

    # Delete temporary baked input textures, they are no longer needed because they are packed into new textures now.
    for key in export_texture.input_textures.__annotations__.keys():
        texture_channel = getattr(export_texture.input_textures, key)
        match texture_channel:
            case 'AMBIENT_OCCLUSION':
                meshmap_name = baking.get_meshmap_name('AMBIENT_OCCLUSION')
                image = bpy.data.images.get(meshmap_name)
                input_images.append(image)

            case 'CURVATURE':
                meshmap_name = baking.get_meshmap_name('CURVATURE')
                image = bpy.data.images.get(meshmap_name)
                input_images.append(image)

            case 'THICKNESS':
                meshmap_name = baking.get_meshmap_name('THICKNESS')
                image = bpy.data.images.get(meshmap_name)
                input_images.append(image)

            case 'BASE_NORMALS':
                meshmap_name = baking.get_meshmap_name('NORMAL')
                image = bpy.data.images.get(meshmap_name)
                input_images.append(image)

            case 'OPACITY':
                input_images.append(None)       # Not implemented, append None for now.

            case 'NONE':
                input_images.append(None)

            case 'ROUGHNESS':
                image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
                input_images.append(image)

                # Convert (invert) roughness to a smoothness map based on settings.
                if addon_preferences.roughness_mode == 'SMOOTHNESS':
                    invert_image(image, True, True, True, False)

            case 'NORMAL':
                image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
                input_images.append(image)

                # Invert normal map G values if exporting for DirectX based on settings.
                if addon_preferences.normal_map_mode == 'DIRECTX':
                    invert_image(image, False, True, False, False)

            case _:
                # Get required baked images for packing using their temp name.
                image = bpy.data.images.get("ML_{material_channel}".format(material_channel=texture_channel))
                input_images.append(image)

#----------------------------- EXPORT OPERATORS -----------------------------#


class MATLAYER_OT_export(Operator):
    bl_idname = "matlayer.export"
    bl_label = "Batch Export"
    bl_description = "Bakes all checked and active material channels to textures in succession and saves all baked images to a texture folder. Note that this function (especially on slower computers, or when using a CPU for rendering) can take a few minutes"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        # Verify the selected object can be baked from.
        if baking.verify_bake_object(self) == False:
            return {'FINISHED'}
        
        # Verify the material can be baked from.
        if matlayer_materials.verify_material(context) == False:
            return {'FINISHED'}
        
        bake_export_textures(self, context)
        channel_pack_textures()

        self.report({'INFO'}, "Finished exporting textures, more information can be found in the Blender console (On Windows: Window -> Toggle System Console).")
        return {'FINISHED'}

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