# This module contains general utility functions for this add-on.

import bpy

def set_valid_mode():
    '''Verifies texture or object mode is being used. This should be used to avoid attempting to run functions in the wrong mode which may throw errors.'''
    if (bpy.context.object.mode != 'TEXTURE_PAINT' and bpy.context.object.mode != 'OBJECT'):
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')

# TODO: Change this to switch out of shaded / wireframe mode to material or rendered preview.
def set_material_shading(context):
    '''Sets the material preview mode to material.'''
    if context.space_data.type == 'VIEW_3D':
        context.space_data.shading.type = 'MATERIAL'