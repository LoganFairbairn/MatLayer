# This files handles drawing baking section user interface.

import bpy
from .import ui_section_tabs

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
    layout.label(text="Normal Bake Settings")

def draw_baking_section_ui(self, context):
    '''Draws the baking section user interface'''
    ui_section_tabs.draw_section_tabs(self, context)

    layout = self.layout
    baking_settings = context.scene.matlay_baking_settings

    # Draw bake button.
    row = layout.row()
    row.operator("matlay.bake")
    row.scale_y = 2.0

    # Draw baking types.
    scale_y = 1.4

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_ambient_occlusion", text="")
    row.label(text="Ambient Occlusion")
    row.operator("matlay.bake_ambient_occlusion", text="", icon='RENDER_STILL')
    row.operator("matlay.delete_ao_map", icon='TRASH', text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_curvature", text="")
    row.label(text="Curvature")
    row.operator("matlay.bake_curvature", text="", icon='RENDER_STILL')
    row.operator("matlay.delete_curvature_map", icon='TRASH', text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_thickness", text="")
    row.label(text="Thickness")
    row.operator("matlay.bake_thickness", text="", icon='RENDER_STILL')
    row.operator("matlay.delete_thickness_map", icon='TRASH', text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_normals", text="")
    row.label(text="Normal")
    row.operator("matlay.bake_normals", text="", icon='RENDER_STILL')
    row.operator("matlay.delete_normal_map", icon='TRASH', text="")

    #----------------------------- BAKE SETTINGS -----------------------------#

    row = layout.row()
    row.scale_y = 1.4

    col = row.split()
    col.prop(baking_settings, "output_width", text="")

    col = row.split()
    if baking_settings.match_bake_resolution:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="LOCKED")

    else:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="UNLOCKED")

    col = row.split()
    col.prop(baking_settings, "output_height", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "high_poly_object", slider=True)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")
    row.prop(baking_settings, "output_quality", text="")


    #----------------------------- ADVANCED SETTINGS -----------------------------#

    if not baking_settings.show_advanced_settings:
        row = layout.row()
        row.scale_x = 10000
        row.prop(baking_settings, "show_advanced_settings", icon='TRIA_DOWN', text="")

    if baking_settings.show_advanced_settings:
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
        row.prop(baking_settings, "bake_type")

        match baking_settings.bake_type:
            case 'AMBIENT_OCCLUSION':
                draw_ambient_occlusion_settings(layout, baking_settings, scale_y)

            case 'CURVATURE':
                draw_curvature_settings(layout, baking_settings, scale_y)

            case 'THICKNESS':
                draw_thickness_settings(layout, baking_settings, scale_y)

            case 'NORMAL':
                draw_normal_settings(layout, baking_settings, scale_y)

        row = layout.row()
        row.scale_x = 10000
        row.prop(baking_settings, "show_advanced_settings", icon='TRIA_UP', text="")