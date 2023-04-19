# This module contains general utility functions for this add-on.

import bpy

def set_valid_mode():
    '''Verifies texture or object mode is being used. This should be used to avoid attempting to run functions in the wrong mode which may throw errors.'''
    if (bpy.context.object.mode != 'TEXTURE_PAINT' and bpy.context.object.mode != 'OBJECT'):
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')

def set_valid_material_shading_mode(context):
    '''Verifies the user is using material or rendered shading mode and corrects the shading mode if they are using a different mode. This allows users to visually see the changes they to the material make when calling select operators.'''
    if context.space_data.type == 'VIEW_3D':
        if context.space_data.shading.type != 'MATERIAL' and context.space_data.shading.type != 'RENDERED':
            context.space_data.shading.type = 'MATERIAL'