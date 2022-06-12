from cgitb import text
import os
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
from ..layers.nodes import layer_nodes
from ..layers.nodes import update_layer_nodes

class COATER_OT_import_color_image(Operator, ImportHelper):
    '''Imports a color image to use for the selected layer.'''
    bl_idname = "coater.import_color_image"
    bl_label = "Import Color Image"
    bl_description = "Opens a menu that allows the user to import a color image."

    input1: bpy.props.StringProperty()

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
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.input1, selected_layer_index, context)
        if texture_node:
            texture_node.image = bpy.data.images[image_name]

        # TODO: Set the textures color space automatically based on which material channel the texture was imported to.
        
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

            update_layer_nodes.update_layer_nodes(context)
        
        return {'FINISHED'}
