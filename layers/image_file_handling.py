# This file provides easy ways to correctly edit and save images made with Coater.

import bpy

def get_image_name(layer_name):
    '''Returns the image name'''
    bpy.context.scene.coater_layers
    layer_index = bpy.context.scene.coater_layer_stack.layer_index

def save_layer_image(image_name):
    '''Saves the given layer image to the designated layer folder.'''
    print("")

def rename_layer_image(image_name, new_name):
    '''Renames the given layer image to the new name.'''
    print("")