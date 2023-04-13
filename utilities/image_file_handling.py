# This file provides functions to assist with importing, saving, or editing image files / textures made with this add-on.

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
import random
import os                                           # For saving layer images.
from ..import layer_nodes

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

class MATLAY_OT_add_layer_image(Operator):
    '''Creates a image within Blender's data and adds it to the selected layer.'''
    bl_idname = "matlay.add_layer_image"
    bl_label = "Add Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a image within Blender's data and adds it to the selected layer"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        layers = context.scene.matlay_layers
        layer_index = context.scene.matlay_layer_stack.layer_index

        # Assign the new image the layer name + a random image id number.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_name = layer_name + "_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = layer_name + "_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        texture_set_settings = context.scene.matlay_texture_set_settings
        match texture_set_settings.image_width:
            case 'FIVE_TWELVE':
                image_width = 512
            case 'ONEK':
                image_width = 1024
            case'TWOK':
                image_width = 2048
            case 'FOURK':
                image_width = 4096
            case _:
                image_width = 2048

        image_height = 128
        match texture_set_settings.image_height:
            case 'FIVE_TWELVE':
                image_height = 512
            case 'ONEK':
                image_height = 1024
            case 'TWOK':
                image_height = 2048
            case 'FOURK':
                image_height = 4096
            case _:
                image_width = 2048

        image = bpy.ops.image.new(name=image_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(0.0, 0.0, 0.0, 0.0),
                                  alpha=True,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)
        
        # TODO: Research automatic packing after image creation is complete.
        # Pack the image into Blender's data.
        # Packing layer images is a fairly optimal and simple method for managing layer images.
        image = bpy.data.images[image_name]
        image.pack()

        # Add the new image to the selected layer.
        selected_layer_index = context.scene.matlay_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)
        if texture_node:
            texture_node.image = bpy.data.images[image_name]

        # Select the new texture for painting.
        context.scene.tool_settings.image_paint.canvas = texture_node.image
        
        return {'FINISHED'}

class MATLAY_OT_import_texture(Operator, ImportHelper):
    '''Imports a texture to use for the selected layer.'''
    bl_idname = "matlay.import_texture"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import an texture file."

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        # Open a window to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]
        bpy.ops.image.open(filepath=self.filepath)

        # Put the selected image into the texture node of the currently selected layer.
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)
        image = bpy.data.images[image_name]
        if texture_node:
            texture_node.image = image

        # For specific material channels, imported textures automatically have their color space corrected.
        match self.material_channel_name:
            case 'COLOR':
                image.colorspace_settings.name = 'sRGB'

            case 'METALLIC':
                image.colorspace_settings.name = 'Non-Color'

            case 'ROUGHNESS':
                image.colorspace_settings.name = 'Non-Color'

            case 'NORMAL':
                image.colorspace_settings.name = 'Non-Color'

            case 'HEIGHT':
                image.colorspace_settings.name = 'Non-Color'
        
            case 'EMISSION':
                image.colorspace_settings.name = 'sRGB'

            case 'SCATTERING':
                image.colorspace_settings.name = 'sRGB'

        return {'FINISHED'}

class MATLAY_OT_delete_layer_image(Operator):
    '''Deletes the current layer image from Blender's data'''
    bl_idname = "matlay.delete_layer_image"
    bl_label = "Delete Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the current layer image from Blender's data and saved texture files. If you want to unlink the image from the texture node without deleting the image, use the 'x' button inside the image texture block"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        selected_layer_index = context.scene.matlay_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)
        if texture_node:
            if texture_node.image:
                bpy.data.images.remove(texture_node.image)
        return {'FINISHED'}