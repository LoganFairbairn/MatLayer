# This files handles drawing baking section user interface.

import bpy
from .import ui_tabs
from ..core import mesh_map_baking
from ..core import blender_addon_utils

def draw_mesh_map_status(layout, baking_settings):
    '''Draws status and operators for each mesh map type.'''
    layout.label(text="MESH MAPS")

    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    null_meshmap_text = "Not Baked"

    for mesh_map_type in mesh_map_baking.MESH_MAP_TYPES:
        mesh_map_label = mesh_map_type.replace('_', ' ')
        mesh_map_label = blender_addon_utils.capitalize_by_space(mesh_map_label)

        bake_checkbox_property_name = "bake_{0}".format(mesh_map_type.lower())
        row = first_column.row()
        row.prop(baking_settings, bake_checkbox_property_name, text="")
        row.label(text=mesh_map_label)

        row = second_column.row()
        col = row.column()

        if bpy.context.active_object:
            mesh_map_name = mesh_map_baking.get_meshmap_name(bpy.context.active_object.name, mesh_map_type)
            if bpy.data.images.get(mesh_map_name):
                col.label(text=mesh_map_name)
            else:
                col.label(text=null_meshmap_text)
        else:
            col.label(text="No Active Object")

        col = row.column()
        col.scale_x = 0.7
        col.prop(baking_settings.mesh_map_anti_aliasing, mesh_map_type.lower() + "_anti_aliasing", text="")

        col = row.column()
        row = col.row(align=True)
        operator = row.operator("matlayer.preview_mesh_map", text="", icon='MATERIAL_DATA')
        operator.mesh_map_type = mesh_map_type
        row.operator("matlayer.disable_mesh_map_preview", text="", icon='TRACKING_REFINE_BACKWARDS')
        operator = row.operator("matlayer.delete_mesh_map", text="", icon='TRASH')
        operator.mesh_map_name = mesh_map_type

def draw_mesh_map_settings(layout, baking_settings):
    '''Draws general settings for mesh map baking.'''
    row = layout.row()
    row.separator()
    row.scale_y = 2
    layout.label(text="GENERAL SETTINGS")

    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.label(text="High Poly Object")
    row = second_column.row()
    row.prop(baking_settings, "high_poly_object", text="", slider=True)

    row = first_column.row()
    row.label(text="Render Device")
    row = second_column.row()
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    row = first_column.row()
    row.label(text="Upscale")
    row = second_column.row()
    row.prop(baking_settings, "mesh_map_upscaling_multiplier", text="")

    row = first_column.row()
    row.label(text="Mesh Map Quality")
    row = second_column.row()
    row.prop(baking_settings, "mesh_map_quality", text="")

    row = first_column.row()
    row.label(text="Cage Mode")
    row = second_column.row()
    row.prop(baking_settings, "cage_mode", text="")

    match baking_settings.cage_mode:
        case 'NO_CAGE':
            row = first_column.row()
            row.label(text="Cage Extrusion")
            row = second_column.row()
            row.prop(bpy.context.scene.render.bake, "cage_extrusion", text="")

        case 'AUTO_CAGE':
            row = first_column.row()
            row.label(text="Cage Upscale")
            row = second_column.row()
            row.prop(baking_settings, "cage_upscale", text="")

        case 'MANUAL_CAGE':
            row = first_column.row()
            row.label(text="Cage")
            row = second_column.row(align=True)
            row.prop(bpy.context.scene.render.bake, "cage_object", text="")
            row.operator("matlayer.create_baking_cage", text="", icon='ADD')
            row.operator("matlayer.delete_baking_cage", text="", icon='TRASH')

    row = first_column.row()
    row.label(text="UV Padding")
    row = second_column.row()
    row.prop(baking_settings, "uv_padding", text="")

    # Ambient Occlusion Settings
    layout.label(text="AMBIENT OCCLUSION")
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.label(text="Occlusion Samples")
    row = second_column.row()
    row.prop(baking_settings, "occlusion_samples", slider=True, text="")

    row = first_column.row()
    row.label(text="Occlusion Distance")
    row = second_column.row()
    row.prop(baking_settings, "occlusion_distance", slider=True, text="")

    row = first_column.row()
    row.label(text="Occlusion Intensity")
    row = second_column.row()
    row.prop(baking_settings, "occlusion_intensity", slider=True, text="")

    row = first_column.row()
    row.label(text="Local Occlusion")
    row = second_column.row()
    row.prop(baking_settings, "local_occlusion", text="")

    # Curvature Settings
    layout.label(text="CURVATURE")
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.label(text="Bevel Samples")
    row = second_column.row()
    row.prop(baking_settings, "bevel_samples", text="")

    row = first_column.row()
    row.label(text="Bevel Radius")
    row = second_column.row()
    row.prop(baking_settings, "bevel_radius", text="")

    row = first_column.row()
    row.label(text="Relative to Bounding Box")
    row = second_column.row()
    row.prop(baking_settings, "relative_to_bounding_box", text="")

    # Thickness Settings
    layout.label(text="THICKNESS")
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.label(text="Thickness Samples")
    row = second_column.row()
    row.prop(baking_settings, "thickness_samples", text="")

    row = first_column.row()
    row.label(text="Thickness Distance")
    row = second_column.row()
    row.prop(baking_settings, "thickness_distance", text="")

    row = first_column.row()
    row.label(text="Local Thickness")
    row = second_column.row()
    row.prop(baking_settings, "local_thickness", text="")

def draw_baking_tab_ui(self, context):
    '''Draws the baking section user interface'''
    ui_tabs.draw_addon_tabs(self, context)

    layout = self.layout

    if "cycles" not in bpy.context.preferences.addons:
        layout.label(text="Cycles add-on is not enabled.")
        layout.label(text="Enable Cyles from Blender's add-ons in for baking to work.")
        layout.label(text="Edit -> Preferences -> Add-ons -> Cycles Render Engine")
        return

    baking_settings = context.scene.matlayer_baking_settings

    # Draw bake button.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.operator("matlayer.batch_bake", text="Bake Mesh Maps")

    draw_mesh_map_status(layout, baking_settings)
    draw_mesh_map_settings(layout, baking_settings)
