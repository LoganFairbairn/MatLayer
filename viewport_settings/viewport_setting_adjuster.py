# This module contains functions to quickly change viewport settings to better suit material editing.

import bpy

def set_material_shading(context):
    if context.space_data.type == 'VIEW_3D':
        context.space_data.shading.type = 'MATERIAL'