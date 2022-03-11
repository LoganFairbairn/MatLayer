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
    row.prop(baking_settings, "bake_ambient_occlusion", text="")
    row.prop_enum(baking_settings, "bake_type", 'AMBIENT_OCCLUSION')
    row.operator("coater.toggle_ambient_occlusion_preview", text="", icon='NODE_MATERIAL')
    row.operator("coater.bake_ambient_occlusion", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    row = layout.row()
    row.prop(baking_settings, "bake_curvature", text="")
    row.prop_enum(baking_settings, "bake_type", 'CURVATURE')
    row.operator("coater.toggle_curvature_preview", text="", icon='NODE_MATERIAL')
    row.operator("coater.bake_curvature", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    # Draw global bake settings.
    layout.label(text="Global Bake Settings:")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")
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

    # Draw specific bake settings based on selected bake type.
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

    if baking_settings.bake_type == 'CURVATURE':
        layout.label(text="Curvature Bake Settings:")

        row = layout.row()
        row.scale_y = scale_y
        row.prop(baking_settings, "curvature_edge_radius", slider=True)
        row.prop(baking_settings, "curvature_edge_intensity", slider=True)

        # Ambient Occlusion Settings.
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

    # TODO: Draw existing mesh maps.
    layout.label(text="MESH MAPS: ")