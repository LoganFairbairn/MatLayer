import os
import numpy
import bpy
from bpy.types import Operator, PropertyGroup, Menu
from bpy.props import BoolProperty, StringProperty, IntProperty
from ..core import material_channels
from ..core import baking
from ..core import texture_set_settings
from ..core import matlayer_materials
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

def get_material_channel_abbreviation(material_channel_name):
    '''Returns an abbreviation for the material channel name.'''
    match material_channel_name:
        case 'COLOR':
            return 'C'
        case 'SUBSURFACE':
            return 'SS'
        case 'SUBSURFACE_COLOR':
            return 'SSC'
        case 'METALLIC':
            return 'M'
        case 'SPECULAR':
            return 'S'
        case 'ROUGHNESS':
            return 'R'
        case 'EMISSION':
            return 'E'
        case 'NORMAL':
            return 'N'
        case 'HEIGHT':
            return 'H'
        case 'ORM':
            return 'ORM'

def format_export_image_name(material_channel_name):
    '''Properly formats the name for an export image based on the selected texture export template and the provided material channel.'''
    image_name = ""
    active_object = bpy.context.active_object
    if not active_object:
        return image_name
    
    active_material = active_object.active_material
    if not active_material:
        return image_name

    # TODO: Return an export name for the image based on the name format defined.


    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.texture_export_template:
        case 'PBR_METALLIC_ROUGHNESS':
            image_name = "{0}_{1}".format(active_material.name, material_channel_name)

        case _:
            material_channel_abreviation = get_material_channel_abbreviation(material_channel_name)
            image_name = "T_{0}_{1}".format(active_material.name, material_channel_abreviation)
    return image_name

def channel_pack(r_image, g_image, b_image, a_image):
    '''Channel packs the provided images into RGBA channels of a single image. Accepts None.'''

    # Store input images into an array so they can be cycled through easily.
    packing_images = [r_image, g_image, b_image, a_image]

    # Cycle through RGBA channels.
    output_pixels = None
    for i in range(0, 4):
        image = packing_images[i]
        if image:

            # Initialize full size empty arrays to avoid using dynamic arrays (caused by appending) which is much much slower.
            if output_pixels is None:
                w, h = image.size
                source_pixels = numpy.empty(w * h * 4, dtype=numpy.float32)
                output_pixels = numpy.ones(w * h * 4, dtype=numpy.float32)

            # Break if provided images are not the same size.
            assert image.size[:] == (w, h), "Images must be the same size."

            # Copy the source image R pixels to the output image pixels for each channel.
            image.pixels.foreach_get(source_pixels)
            output_pixels[i::4] = source_pixels[0::4]
            
        else:
            # If an alpha image is not provided, alpha is 1.0.
            if i == 3:
                output_pixels[i::4] = 1.0

            # If an image other than alpha is not provided, channel is 0.0.
            else:
                output_pixels[i::4] = 0.0
        
    # If an alpha image is provided create an image with alpha.
    has_alpha = False
    if a_image:
        has_alpha = True

    # Create image using the packed pixels.
    packed_image = bpy.data.images.new("Packed Image", w, h, alpha=has_alpha, float_buffer=True, is_data=True)
    packed_image.pixels.foreach_set(output_pixels)
    packed_image.pack()

    return packed_image

def channel_pack_exported_images(delete_unpacked=True):
    '''Channel packs exported images for the selected object based on the selected texture export preset.'''

    roughness_tex_name = format_export_image_name('ROUGHNESS')
    metallic_tex_name = format_export_image_name('METTALIC')
    ao_tex_name = baking.get_meshmap_image_name('AMBIENT_OCCLUSION')

    roughness_tex = bpy.data.images.get(roughness_tex_name + ".png")
    metallic_tex = bpy.data.images.get(metallic_tex_name + ".png")
    ao_tex = bpy.data.images.get(ao_tex_name + ".png")

    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.texture_export_template:
        case 'UNITY_METALLIC':
            packed_image = channel_pack(roughness_tex, metallic_tex, None, ao_tex)
            packed_image.name = format_export_image_name('ORM')
        case 'UNITY_SPECULAR':
            packed_image = channel_pack(roughness_tex, metallic_tex, None, ao_tex)
            packed_image.name = format_export_image_name('ORM')
        case 'UNREAL_ENGINE':
            packed_image = channel_pack(ao_tex, roughness_tex, metallic_tex, None)
            packed_image.name = format_export_image_name('ORM')

    # TODO: Delete saved unpacked images after packing.
    
def create_export_image(export_image_name):
    '''Creates an image in Blender's data to bake to and export.'''
    export_image = bpy.data.images.get(export_image_name)
    if export_image != None:
        bpy.data.images.remove(export_image)
    export_image = bpy.ops.image.new(name=export_image_name, 
                                     width=texture_set_settings.get_texture_width(), 
                                     height=texture_set_settings.get_texture_height(), 
                                     color=(0.0, 0.0, 0.0, 1.0), 
                                     alpha=False, 
                                     generated_type='BLANK', 
                                     float=False, 
                                     use_stereo_3d=False, 
                                     tiled=False)
    return bpy.data.images[export_image_name]

def bake_and_export_material_channel(material_channel_name, context, self):
    '''Bakes the material channel to a texture and saves the output image to a folder.'''

    # Validate the material channel name.
    if not material_channels.validate_material_channel_name(material_channel_name):
        return

    # Validate the material channel is toggled on in the texture set settings.
    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings
    if not getattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle"):
        self.report({'INFO'}, "The {0} material channel is disabled in the texture set settings and will not be exported.".format(material_channel_name))
        return

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

    # Create a new image in Blender's data and image node.
    export_image_name = format_export_image_name(material_channel_name)
    export_image = create_export_image(export_image_name)

    # Create a folder for the exported texture files.
    export_path = os.path.join(bpy.path.abspath("//"), "Textures")
    if os.path.exists(export_path) == False:
        os.mkdir(export_path)

    export_image.filepath = export_path + "/" + export_image_name + ".png"
    export_image.file_format = 'PNG'

    material_nodes = context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.new('ShaderNodeTexImage')
    image_node.image = export_image
    image_node.select = True
    material_nodes.active = image_node

    # Cache the render engine so we can reset it after baking.
    original_render_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_selected_to_active = False
    if material_channel_name == 'NORMAL':
        bpy.ops.object.bake(type='NORMAL')
    else:
        bpy.ops.object.bake(type='EMIT')

    # Reset the render engine.
    bpy.context.scene.render.engine = original_render_engine
    
    # Save the image.
    if export_image:
        if export_image.is_dirty:
            export_image.save()
        else:
            self.report({'INFO'}, "Exported image pixel data wasn't updated during baking.".format(export_path))

    # Delete the image node.
    material_nodes.remove(image_node)

    # The exported image is already saved to a folder, so it's no longer needed in blend data, remove it.
    bpy.data.images.remove(export_image)

    # De-isolate the material channel.
    if material_channel_name != 'NORMAL':
        material_channels.isolate_material_channel(False, material_channel_name, context)

    self.report({'INFO'}, "Finished exporting textures. You can find any exported textures in {0}".format(export_path))

class MATLAYER_OT_channel_pack(Operator):
    bl_idname = "matlayer.channel_pack"
    bl_label = "Channel Pack"
    bl_description = "Channel packs textures based on the selected texture export template (experimental)"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        channel_pack_exported_images()
        return {'FINISHED'}

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
    
        if bpy.context.scene.matlayer_export_settings.export_base_color:
            bake_and_export_material_channel('COLOR', context, self)
        if bpy.context.scene.matlayer_export_settings.export_subsurface:
            bake_and_export_material_channel('SUBSURFACE', context, self)
        if bpy.context.scene.matlayer_export_settings.export_subsurface_color:
            bake_and_export_material_channel('SUBSURFACE_COLOR', context, self)
        if bpy.context.scene.matlayer_export_settings.export_metallic:
            bake_and_export_material_channel('METALLIC', context, self)
        if bpy.context.scene.matlayer_export_settings.export_specular:
            bake_and_export_material_channel('SPECULAR', context, self)
        if bpy.context.scene.matlayer_export_settings.export_roughness:
            bake_and_export_material_channel('ROUGHNESS', context, self)
        if bpy.context.scene.matlayer_export_settings.export_normals:
            bake_and_export_material_channel('NORMAL', context, self)
        if bpy.context.scene.matlayer_export_settings.export_height:
            bake_and_export_material_channel('HEIGHT', context, self)
        if bpy.context.scene.matlayer_export_settings.export_emission:
            bake_and_export_material_channel('EMISSION', context, self)

        channel_pack_exported_images()
        return {'FINISHED'}

def set_export_template(export_template_name):
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        export_channels = addon_preferences.export_channels
        export_channels.clear()
        addon_preferences.export_template_name = export_template_name

        match export_template_name:
            case 'PBR Metallic Roughness':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Color"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Metallic"
                new_channel.r_input_texture = 'METALLIC'
                new_channel.g_input_texture = 'METALLIC'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'METALLIC'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Roughness"
                new_channel.r_input_texture = 'ROUGHNESS'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'ROUGHNESS'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Normal"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NORMAL'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Emission"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'EMISSION'

            case 'PBR Specular Glossiness':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Color"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Specular"
                new_channel.r_input_texture = 'SPECULAR'
                new_channel.g_input_texture = 'SPECULAR'
                new_channel.b_input_texture = 'SPECULAR'
                new_channel.a_input_texture = 'SPECULAR'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Glossiness"
                new_channel.r_input_texture = 'ROUGHNESS'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'ROUGHNESS'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Normal"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NORMAL'

                new_channel = export_channels.add()
                new_channel.name_format = "/MaterialName_Emission"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'EMISSION'

            case 'Unity URP Metallic':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_MG"
                new_channel.r_input_texture = 'METALLIC'
                new_channel.g_input_texture = 'METALLIC'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_N"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'Unity URP Specular':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_MG"
                new_channel.r_input_texture = 'SPECULAR'
                new_channel.g_input_texture = 'SPECULAR'
                new_channel.b_input_texture = 'SPECULAR'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_N"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'Unity HDRP Metallic':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_MAG"
                new_channel.r_input_texture = 'METALLIC'
                new_channel.g_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.b_input_texture = 'NONE'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_N"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'Unity HDRP Specular':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_S"
                new_channel.r_input_texture = 'SPECULAR'
                new_channel.g_input_texture = 'SPECULAR'
                new_channel.b_input_texture = 'SPECULAR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_MAG"
                new_channel.r_input_texture = 'METALLIC'
                new_channel.g_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.b_input_texture = 'NONE'
                new_channel.a_input_texture = 'ROUGHNESS'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_N"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'Unreal Engine 4':
                addon_preferences.normal_map_mode = 'DIRECTX'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_SS"
                new_channel.r_input_texture = 'SUBSURFACE'
                new_channel.g_input_texture = 'SUBSURFACE'
                new_channel.b_input_texture = 'SUBSURFACE'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_SSC"
                new_channel.r_input_texture = 'SUBSURFACE_COLOR'
                new_channel.g_input_texture = 'SUBSURFACE_COLOR'
                new_channel.b_input_texture = 'SUBSURFACE_COLOR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_ORM"
                new_channel.r_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_NDX"
                new_channel.r_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'Unreal Engine 4 Subsurface (Packed)':
                addon_preferences.normal_map_mode = 'DIRECTX'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'SUBSURFACE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_ORM"
                new_channel.r_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_NDX"
                new_channel.r_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.g_input_texture = 'ROUGHNESS'
                new_channel.b_input_texture = 'METALLIC'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_E"
                new_channel.r_input_texture = 'EMISSION'
                new_channel.g_input_texture = 'EMISSION'
                new_channel.b_input_texture = 'EMISSION'
                new_channel.a_input_texture = 'NONE'

            case 'CryEngine':
                addon_preferences.normal_map_mode = 'DIRECTX'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_C"
                new_channel.r_input_texture = 'COLOR'
                new_channel.g_input_texture = 'COLOR'
                new_channel.b_input_texture = 'COLOR'
                new_channel.a_input_texture = 'OPACITY'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_S"
                new_channel.r_input_texture = 'SPECULAR'
                new_channel.g_input_texture = 'SPECULAR'
                new_channel.b_input_texture = 'SPECULAR'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_NDXO"
                new_channel.r_input_texture = 'NORMAL'
                new_channel.g_input_texture = 'NORMAL'
                new_channel.b_input_texture = 'NORMAL'
                new_channel.a_input_texture = 'AMBIENT_OCCLUSION'

            case 'Mesh Maps':
                addon_preferences.normal_map_mode = 'OPEN_GL'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_AmbientOcclusion"
                new_channel.r_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.g_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.b_input_texture = 'AMBIENT_OCCLUSION'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_Curvature"
                new_channel.r_input_texture = 'CURVATURE'
                new_channel.g_input_texture = 'CURVATURE'
                new_channel.b_input_texture = 'CURVATURE'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_Thickness"
                new_channel.r_input_texture = 'THICKNESS'
                new_channel.g_input_texture = 'THICKNESS'
                new_channel.b_input_texture = 'THICKNESS'
                new_channel.a_input_texture = 'NONE'

                new_channel = export_channels.add()
                new_channel.name_format = "T_/MaterialName_BaseNormals"
                new_channel.r_input_texture = 'BASE_NORMALS'
                new_channel.g_input_texture = 'BASE_NORMALS'
                new_channel.b_input_texture = 'BASE_NORMALS'
                new_channel.a_input_texture = 'NONE'

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
        addon_preferences.export_channels.add()
        return {'FINISHED'}

class MATLAYER_OT_remove_export_texture(Operator):
    bl_idname = "matlayer.remove_export_texture"
    bl_label = "Remove Export Texture"
    bl_description = "Removes the related texture from the export texture list"

    export_texture_index: IntProperty(default=0)
    
    def execute(self, context):
        addon_preferences = context.preferences.addons[preferences.ADDON_NAME].preferences
        addon_preferences.export_channels.remove(self.export_texture_index)
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