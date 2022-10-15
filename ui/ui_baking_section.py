# This files handles drawing baking section user interface.

import bpy
from .import ui_section_tabs

def draw_baking_section_ui(self, context):
    '''Draws the baking section user interface'''
    ui_section_tabs.draw_section_tabs(self, context)

    layout = self.layout
    baking_settings = context.scene.coater_baking_settings

    # Draw bake button.
    row = layout.row()
    row.operator("coater.bake")
    row.scale_y = 2.0

    # Draw baking types.
    scale_y = 1.4

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_ambient_occlusion", text="")
    row.prop_enum(baking_settings, "bake_type", 'AMBIENT_OCCLUSION')
    row.operator("coater.bake_ambient_occlusion", text="", icon='RENDER_STILL')

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "bake_curvature", text="")
    row.prop_enum(baking_settings, "bake_type", 'CURVATURE')
    row.operator("coater.bake_curvature", text="", icon='RENDER_STILL')

    #row = layout.row()
    #row.scale_y = scale_y
    #row.prop(baking_settings, "bake_thickness", text="")
    #row.prop_enum(baking_settings, "bake_type", 'THICKNESS')
    #row.operator("coater.bake_curvature", text="", icon='RENDER_STILL')


    # Draw global bake settings.
    layout.label(text="Global Bake Settings:")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_settings, "output_quality", text="")

    split = layout.split()
    col = split.column()
    col.ui_units_x = 1
    col.scale_y = scale_y
    col.prop(baking_settings, "output_width", text="")

    col = split.column()
    col.ui_units_x = 0.1
    col.scale_y = scale_y
    if baking_settings.match_bake_resolution:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="LOCKED")

    else:
        col.prop(baking_settings, "match_bake_resolution", text="", icon="UNLOCKED")

    col = split.column()
    col.ui_units_x = 2
    col.scale_y = scale_y
    if baking_settings.match_bake_resolution:
        col.enabled = False
        
    col.prop(baking_settings, "output_height", text="")

    row = layout.row()
    row.scale_y = scale_y
    
    row.prop(bpy.data.scenes["Scene"].render.bake, "margin", slider=True)

    #----------------------------- Draw ambient occlusion settings. -----------------------------#
    if baking_settings.bake_type == 'AMBIENT_OCCLUSION':
        layout.label(text="Ambient Occlusion Bake Settings:")
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

    #----------------------------- Draw curvature settings. -----------------------------#
    if baking_settings.bake_type == 'CURVATURE':
        layout.label(text="Curvature Bake Settings:")

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


    #----------------------------- Draw thickness settings. -----------------------------#
    if baking_settings.bake_type == 'THICKNESS':
        layout.label(text="Thickness Bake Settings")

    #----------------------------- Draw existing mesh maps that exist within the blend file. -----------------------------#
    layout.label(text="MESH MAPS: ")

    active_object = context.active_object

    row = layout.row()
    row.scale_y = scale_y
    if bpy.data.images.get(active_object.name + "_AO") != None:
        layout.label(text=active_object.name + "_AO")
    
    row = layout.row()
    row.scale_y = scale_y
    if bpy.data.images.get(active_object.name + "_Curvature") != None:
        layout.label(text=active_object.name + "_Curvature")

    row = layout.row()
    row.scale_y = scale_y
    if bpy.data.images.get(active_object.name + "_Thickness") != None:
        layout.label(text=active_object.name + "_Thickness")