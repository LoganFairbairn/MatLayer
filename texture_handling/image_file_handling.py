# This file provides functions to assist with importing, saving, or editing image files / textures made with this add-on.

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
import random
import os                                           # For saving layer images.
from ..import layer_nodes

def get_layer_folder_path():
    '''Returns the save location for the layer images.'''
    layer_image_folder = bpy.path.abspath("//" + 'Layers')
    if not os.path.exists(layer_image_folder):
        os.mkdir(layer_image_folder)
    return layer_image_folder

def save_layer_image(image_name):
    '''Saves the given layer image to the designated folder for layer textures.'''
    image = bpy.data.images[image_name]
    image.filepath = get_layer_folder_path() + "/" + image_name + ".png"
    image.file_format = 'PNG'
    if image:
        if image.is_dirty:
            image.save()
    else:
        print("Error: Layer image being saved doesn't exist.")

def get_image_name(layer_name):
    '''Returns the image name'''
    bpy.context.scene.coater_layers
    layer_index = bpy.context.scene.coater_layer_stack.layer_index

def rename_layer_texture(image_name, new_name):
    '''Renames the given layer texture in blender's data and in external saved folders to the new name.'''
    # TODO: Implement re-naming for layer textures.
    print("placeholder")

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

class COATER_OT_add_layer_image(Operator):
    '''Creates a image and adds it to the selected image layer'''
    bl_idname = "coater.add_layer_image"
    bl_label = "Add Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a image and adds it to the selected image layer"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Assign the new image the layer name + a random image id number.
        # TODO: Investigate for a better way to grab a unique id number for the image here.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_name = layer_name + "_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = layer_name + "_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        # TODO: Use a match case statement here?
        texture_set_settings = context.scene.coater_texture_set_settings
        image_width = 128
        if texture_set_settings.image_width == 'FIVE_TWELVE':
            image_width = 512
        if texture_set_settings.image_width == 'ONEK':
            image_width = 1024
        if texture_set_settings.image_width == 'TWOK':
            image_width = 2048
        if texture_set_settings.image_width == 'FOURK':
            image_width = 4096

        image_height = 128
        if texture_set_settings.image_height == 'FIVE_TWELVE':
            image_height = 512
        if texture_set_settings.image_height == 'ONEK':
            image_height = 1024
        if texture_set_settings.image_height == 'TWOK':
            image_height = 2048
        if texture_set_settings.image_height == 'FOURK':
            image_height = 4096

        image = bpy.ops.image.new(name=image_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(0.0, 0.0, 0.0, 0.0),
                                  alpha=True,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)
        
        # Save the image to an external folder.
        save_layer_image(image_name)

        # Add the new image to the selected layer.
        selected_layer_index = context.scene.coater_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)
        if texture_node:
            texture_node.image = bpy.data.images[image_name]
        
        return {'FINISHED'}

class COATER_OT_delete_layer_image(Operator):
    '''Deletes the current layer image from Blender's data'''
    bl_idname = "coater.delete_layer_image"
    bl_label = "Delete Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the current layer image from Blender's data and saved texture files. If you want to unlink the image from the texture node without deleting the image, use the 'x' button inside the image texture block"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        selected_layer_index = context.scene.coater_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)

        if texture_node.image:
            bpy.data.images.remove(texture_node.image )
        
        return {'FINISHED'}
    
class COATER_OT_import_texture(Operator, ImportHelper):
    '''Imports a texture to use for the selected layer.'''
    bl_idname = "coater.import_texture"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import an texture file."

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        selected_layer_index = context.scene.coater_layer_stack.layer_index

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
        match self.material_channel:
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

class COATER_OT_import_mask_image(Operator, ImportHelper):
    '''Imports an image to use as a mask for the selected layer.'''
    bl_idname = "coater.import_mask_image"
    bl_label = "Import Mask Image"
    bl_description = "Opens a menu that allows the user to import an image to use as a mask"
    
    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        bpy.ops.image.open(filepath=self.filepath)
        
        group_node = layer_nodes.get_channel_node_group(context)
        mask_node = group_node.nodes.get(layers[layer_index].mask_node_name)

        if mask_node != None:
            mask_image = bpy.data.images[image_name]
            mask_node.image = mask_image

            layer_nodes.update_layer_nodes(context)
        
        return {'FINISHED'}
