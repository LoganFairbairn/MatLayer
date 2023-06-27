import os
import numpy
import bpy
from bpy.types import Operator, PropertyGroup, Image
from bpy.props import BoolProperty, StringProperty, EnumProperty, PointerProperty
from ..core import material_channels
from ..core import baking
from ..core import texture_set_settings
from ..core import matlayer_materials
from .. import preferences

#----------------------------- EXPORT SETTINGS -----------------------------#

class MATLAYER_exporting_settings(PropertyGroup):
    texture_name_export_format: StringProperty(default="[MaterialName]_[MaterialChannel]", name="Texture Name Export Format", description="Name format used for exported textures. Key words include MaterialName, MaterialChannel, MaterialChannelAbbreviation, ActiveObjectName")
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

def format_export_image_name(material_channel_name):
    '''Properly formats the name for an export image based on the selected texture export template and the provided material channel.'''
    image_name = ""
    active_object = bpy.context.active_object
    if not active_object:
        return image_name
    
    active_material = active_object.active_material
    if not active_material:
        return image_name

    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.texture_export_template:
        case 'PBR_METALLIC_ROUGHNESS':
            image_name = "{0}_{1}".format(active_material.name, material_channel_name)

        case _:
            material_channel_abreviation = ""
            match material_channel_name:
                case 'COLOR':
                    material_channel_abreviation = 'C'
                case 'SUBSURFACE':
                    material_channel_abreviation = 'SS'
                case 'SUBSURFACE_COLOR':
                    material_channel_abreviation = 'SSC'
                case 'METALLIC':
                    material_channel_abreviation = 'M'
                case 'SPECULAR':
                    material_channel_abreviation = 'S'
                case 'ROUGHNESS':
                    material_channel_abreviation = 'R'
                case 'EMISSION':
                    material_channel_abreviation = 'E'
                case 'NORMAL':
                    material_channel_abreviation = 'N'
                case 'HEIGHT':
                    material_channel_abreviation = 'H'
                case 'ORM':
                    material_channel_abreviation = 'ORM'
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

def channel_pack_exported_images():
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