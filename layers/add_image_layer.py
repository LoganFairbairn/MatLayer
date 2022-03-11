import bpy
from bpy.types import Operator
import random
import os       # For saving layer images.
from .import add_layer_slot
from .import create_channel_group_node
from .import coater_material_functions
from .import link_layers
from .import create_layer_nodes
from .import organize_layer_nodes
from .import set_material_shading
from .import coater_node_info
from .import image_file_handling

class COATER_OT_add_image_layer(Operator):
    '''Adds an empty image layer to the layer stack.'''
    bl_idname = "coater.add_image_layer"
    bl_label = "Add Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an empty image layer to the layer stack"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        coater_material_functions.ready_coater_material(context)
        create_channel_group_node.create_channel_group_node(context)
        add_layer_slot.add_layer_slot(context)
        create_layer_nodes.create_layer_nodes(context, 'IMAGE_LAYER')
        organize_layer_nodes.organize_layer_nodes(context)
        link_layers.link_layers(context)
        set_material_shading.set_material_shading(context)

        # Update the layer's type.
        layers[layer_index].type = 'IMAGE_LAYER'

        return {'FINISHED'}

class COATER_OT_add_layer_image(Operator):
    '''Creates a image and adds it to the selected image layer'''
    bl_idname = "coater.add_layer_image"
    bl_label = "Add Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a image and adds it to the selected image layer"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        

        # Assign the new image a unique name.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_name = layer_name + "_" + image_file_handling.get_random_image_id()

        while bpy.data.images.get(image_name) != None:
            image_name = layer_name + "_" + image_file_handling.get_random_image_id()

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

        group_node = coater_node_info.get_channel_node_group(context)
        color_node_name = layers[layer_index].color_node_name
        color_node = group_node.nodes.get(color_node_name)

        if (color_node != None):
            color_node.image = bpy.data.images[image_name]
        
        return {'FINISHED'}

class COATER_OT_delete_layer_image(Operator):
    '''Deletes the current layer image from Blender's data'''
    bl_idname = "coater.delete_layer_image"
    bl_label = "Delete Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the current layer image from Blender's data"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        group_node = coater_node_info.get_channel_node_group(context)
        color_node_name = layers[layer_index].color_node_name
        color_node = group_node.nodes.get(color_node_name)

        if (color_node != None):
            layer_image = color_node.image

            if layer_image != None:
                bpy.data.images.remove(layer_image)
        
        return {'FINISHED'}