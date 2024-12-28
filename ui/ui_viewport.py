import bpy

def draw_viewport_setting_ui(self, context):
    layout = self.layout

    # Use a two column layout.
    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

    # Draw render engine settings.
    row = first_column.row()
    row.label(text="Engine")
    row = second_column.row()
    row.prop(bpy.context.scene.render, 'engine', text="")

    row = first_column.row()
    row.label(text="View Transform")
    row = second_column.row()
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
                row.label(text="Background Color")
                row = second_column.row()
                row.prop(hdri_node.inputs[0], "default_value", text="")

                row = first_column.row()
                row.label(text="Environment Rotation")
                row = second_column.row()
                row.prop(hdri_node.inputs.get('Environment Rotation'), "default_value", text="", index=2, slider=True)

                row = first_column.row()
                row.label(text="Environment Blur")
                row = second_column.row()
                row.prop(hdri_node.inputs.get('Environment Blur'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Environment Exposure")
                row = second_column.row()
                row.prop(hdri_node.inputs.get('Environment Exposure'), "default_value", text="", slider=True)

    # Draw an operator to append the HDRI lighting setup.
    else:
        row = layout.row()
        row.scale_y = 1.5
        row.operator("matlayer.append_hdri_world", text="Append HDRI World")