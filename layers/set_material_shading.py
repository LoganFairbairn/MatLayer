import bpy

def set_material_shading(context):
    if context.space_data.type == 'VIEW_3D':
        context.space_data.shading.type = 'MATERIAL'