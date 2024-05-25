import bpy
from . import ui_section_tabs

def draw_ui_settings_tab(self, context):
    ui_section_tabs.draw_section_tabs(self, context)

    layout = self.layout
    scale_y = 1.4

    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = scale_y
    row.label(text="Engine")
    row = second_column.row()
    row.scale_y = scale_y
    row.prop(bpy.context.scene.render, 'engine', text="")

    row = first_column.row()
    row.scale_y = scale_y
    row.label(text="View Transform")
    row = second_column.row()
    row.scale_y = scale_y
    row.prop(bpy.context.scene.view_settings, "view_transform", text="")

    # Draw HDRI Settings
    hdri_node_tree = bpy.data.node_groups.get('ML_HDRI')
    if hdri_node_tree:
        hdri_texture_node = hdri_node_tree.nodes.get('HDRI_TEXTURE')
        if hdri_texture_node:
            row = first_column.row()
            row.scale_y = 7
            row.label(text="HDRI")
            
            row = second_column.row()
            row.template_ID_preview(hdri_texture_node, "image", open="image.open")

        hdri_world = bpy.data.worlds.get('HDRIWorld')
        if hdri_world:
            hdri_node = hdri_world.node_tree.nodes.get('HDRI')
            if hdri_node:
                row = first_column.row()
                row.scale_y = scale_y
                row.label(text="Background Color")
                row = second_column.row()
                row.scale_y = scale_y
                row.prop(hdri_node.inputs[0], "default_value", text="")

                row = first_column.row()
                row.scale_y = scale_y
                row.label(text="Environment Rotation")
                row = second_column.row()
                row.scale_y = scale_y
                row.prop(hdri_node.inputs.get('Environment Rotation'), "default_value", text="", index=2, slider=True)

                row = first_column.row()
                row.scale_y = scale_y
                row.label(text="Environment Blur")
                row = second_column.row()
                row.scale_y = scale_y
                row.prop(hdri_node.inputs.get('Environment Blur'), "default_value", text="", slider=True)

                row = first_column.row()
                row.scale_y = scale_y
                row.label(text="Environment Exposure")
                row = second_column.row()
                row.scale_y = scale_y
                row.prop(hdri_node.inputs.get('Environment Exposure'), "default_value", text="", slider=True)

    # EEVEE Settings
    if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
        row = first_column.row()
        row.scale_y = scale_y
        row.label(text="EEVEE Viewport Samples")
        row = second_column.row()
        row.scale_y = scale_y
        row.prop(bpy.context.scene.eevee, "taa_samples", text="")

        row = first_column.row()
        row.scale_y = scale_y
        row.label(text="Bloom")
        row = second_column.row()
        row.scale_y = scale_y
        row.prop(bpy.context.scene.eevee, 'use_bloom', text="")

        # Ambient Occlusion
        row = first_column.row()
        row.scale_y = scale_y
        row.label(text="Ambient Occlusion")
        row = second_column.row()
        row.scale_y = scale_y
        row.prop(bpy.context.scene.eevee, 'use_gtao', text="")

        # Screenspace Reflections
        row = first_column.row()
        row.scale_y = scale_y
        row.label(text="Screen Space Reflections")
        row = second_column.row()
        row.scale_y = scale_y
        row.prop(bpy.context.scene.eevee, 'use_ssr', text="")