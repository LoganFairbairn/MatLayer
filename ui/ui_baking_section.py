# This files handles drawing baking section user interface.

import bpy
from .import ui_section_tabs
from ..core import baking

def draw_ambient_occlusion_settings(layout, baking_settings, scale_y):
    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_intensity", slider=True)
    
    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_samples", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_local")
    row.prop(baking_settings, "ambient_occlusion_inside")

def draw_curvature_settings(layout, baking_settings, scale_y):
    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "curvature_edge_radius", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "curvature_edge_intensity", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_intensity", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_samples", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "ambient_occlusion_local")
    row.prop(baking_settings, "ambient_occlusion_inside")

def draw_thickness_settings(layout, baking_settings, scale_y):
    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "thickness_samples", slider=True)

def draw_normal_settings(layout, baking_settings, scale_y):
    row = layout.row()
    row.scale_y = 1.4
    row.prop(bpy.data.scenes["Scene"].render.bake, "cage_extrusion", slider=True)

    row = layout.row()
    row.scale_y = 1.4
    row.prop(bpy.data.scenes["Scene"].render.bake, "max_ray_distance", slider=True)

def draw_baking_section_ui(self, context):
    '''Draws the baking section user interface'''
    ui_section_tabs.draw_section_tabs(self, context)

    layout = self.layout
    baking_settings = context.scene.matlayer_baking_settings
    scale_y = 1.4

    #----------------------------- BAKE SETTINGS -----------------------------#

    row = layout.row()
    row.scale_y = 1.4

    col = row.split()
    col.prop(baking_settings, "output_width", text="Bake Size")

    col = row.split()
    if baking_settings.match_bake_resolution:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="LOCKED")

    else:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="UNLOCKED")

    col = row.split()
    if baking_settings.match_bake_resolution:
        col.enabled = False
    col.prop(baking_settings, "output_height", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "high_poly_object", slider=True)

    if "cycles" in bpy.context.preferences.addons:
        row = layout.row()
        row.scale_y = scale_y
        row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")
        row.prop(baking_settings, "output_quality", text="")

    #----------------------------- MESH MAPS -----------------------------#

    row = layout.row()
    row.separator()
    row = layout.row()
    row.separator()
    layout.label(text="MESH MAPS: ")

    # Draw bake button.
    row = layout.row()
    row.operator("matlayer.bake")
    row.scale_y = 2.0

    split = layout.split()
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_ambient_occlusion", text="")
    row.label(text="Ambient Occlusion: ")
    row = first_column.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_curvature", text="")
    row.label(text="Curvature: ")
    row = first_column.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_thickness", text="")
    row.label(text="Thickness: ")
    row = first_column.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_normals", text="")
    row.label(text="Normal: ")

    null_meshmap_text = "Not Baked"

    row = second_column.row()
    ao_meshmap_name = baking.get_meshmap_name('AMBIENT_OCCLUSION')
    if bpy.data.images.get(ao_meshmap_name):
        row.label(text=ao_meshmap_name)
    else:
        row.label(text=null_meshmap_text)
    row.operator("matlayer.bake_ambient_occlusion", text="", icon='RENDER_STILL')
    row.operator("matlayer.delete_ao_map", text="", icon='TRASH')
    row.scale_y = scale_y

    row = second_column.row()
    curvature_meshmap_name = baking.get_meshmap_name('CURVATURE')
    if bpy.data.images.get(curvature_meshmap_name):
        row.label(text=curvature_meshmap_name)
    else:
        row.label(text=null_meshmap_text)
    row.operator("matlayer.bake_curvature", text="", icon='RENDER_STILL')
    row.operator("matlayer.delete_curvature_map", text="", icon='TRASH')
    row.scale_y = scale_y

    row = second_column.row()
    thickness_meshmap_name = baking.get_meshmap_name('THICKNESS')
    if bpy.data.images.get(thickness_meshmap_name):
        row.label(text=thickness_meshmap_name)
    else:
        row.label(text=null_meshmap_text)
    row.operator("matlayer.bake_thickness", text="", icon='RENDER_STILL')
    row.operator("matlayer.delete_thickness_map", text="", icon='TRASH')
    row.scale_y = scale_y

    row = second_column.row()
    normal_meshmap_name = baking.get_meshmap_name('NORMAL')
    if bpy.data.images.get(normal_meshmap_name):
        row.label(text=normal_meshmap_name)
    else:
        row.label(text=null_meshmap_text)
    row.operator("matlayer.bake_normals", text="", icon='RENDER_STILL')
    row.operator("matlayer.delete_normal_map", text="", icon='TRASH')
    row.scale_y = scale_y


    #----------------------------- ADVANCED SETTINGS -----------------------------#

    row = layout.row()
    row.separator()
    row = layout.row()
    row.separator()
    layout.label(text="ADVANCED SETTINGS")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].render.bake, "margin", slider=True)

    if baking_settings.high_poly_object != None:
        row = layout.row()
        row.scale_y = scale_y
        row.prop(baking_settings, "cage_extrusion", slider=True)
        row = layout.row()
        row.scale_y = scale_y
        row.prop(bpy.data.scenes["Scene"].render.bake, "max_ray_distance", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_type", text="Bake Settings For")

    match baking_settings.bake_type:
        case 'AMBIENT_OCCLUSION':
            draw_ambient_occlusion_settings(layout, baking_settings, scale_y)

        case 'CURVATURE':
            draw_curvature_settings(layout, baking_settings, scale_y)

        case 'THICKNESS':
            draw_thickness_settings(layout, baking_settings, scale_y)

        case 'NORMAL':
            draw_normal_settings(layout, baking_settings, scale_y)