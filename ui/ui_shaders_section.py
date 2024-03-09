# User interface for the shaders tab.

import bpy
from bpy.types import Menu
from .import ui_section_tabs

def draw_ui_shaders_section(self, context):
    '''Draws user interface for the shaders tab.'''

    # Draws tabs for all sections in this add-on.
    ui_section_tabs.draw_section_tabs(self, context)

    shader_info = bpy.context.scene.matlayer_shader_info
    layout = self.layout
    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

    # Draw the shader list.
    row = first_column.row()
    row.label(text="Shader: ")
    row = second_column.row(align=True)
    menu_label = shader_info.name
    menu_label = menu_label.replace('ML_', '')
    row.prop(shader_info, "name", text="")
    row.menu("MATLAYER_MT_shader_sub_menu", text="Load Shader")

    # Draw the shader author.
    row = first_column.row()
    row.label(text="Author: ")
    row = second_column.row()
    row.prop(shader_info, "author", text="")

    # Draw the shader description.
    row = first_column.row()
    row.label(text="Description: ")
    row = second_column.row()
    row.prop(shader_info, "description", text="")

    # Draw the name of the group node used for the shader.
    row = first_column.row()
    row.label(text="Group Node Name: ")
    row = second_column.row()
    row.prop(shader_info, "group_node_name", text="")

    # Draw all the channels for the selected shader.
    layout.label(text="Shader Channels:")
    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.alignment = 'CENTER'
    row.label(text="Channel")

    row = second_column.row()
    split = row.split(factor=0.5)
    first_sub_column = split.column()
    second_sub_column = split.column()

    row = first_sub_column.row()
    row.alignment = 'CENTER'
    row.label(text="Default, Min, Max")

    row = second_sub_column.row()
    col = row.column()
    col.label(text="Type")

    col = row.column()
    col.label(text="Subtype")

    col = row.column()
    col.label(text="Blend")

    for channel in shader_info.material_channels:
        split = layout.split(factor=0.3)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row()
        if channel.default_active:
            row.prop(channel, "default_active", text="", toggle=True, icon='CHECKMARK')
        else:
            row.prop(channel, "default_active", text="", toggle=True)
        row.prop(channel, "name", text="")

        row = second_column.row()
        split = row.split(factor=0.5)
        first_sub_column = split.column()
        second_sub_column = split.column()

        row = first_sub_column.row()
        match channel.socket_type:
            case 'NodeSocketFloat':
                row.prop(channel, "socket_float_default", text="")
                row.prop(channel, "socket_float_min", text="")
                row.prop(channel, "socket_float_max", text="")
            case 'NodeSocketColor':
                row.prop(channel, "socket_color_default", text="")
            case 'NodeSocketVector':
                row.prop(channel, "socket_vector_default", text="")
        
        row = second_sub_column.row()
        row.prop(channel, "socket_type", text="")
        row.prop(channel, "socket_subtype", text="")
        row.prop(channel, "default_blend_mode", text="")

class ShaderSubMenu(Menu):
    bl_idname = "MATLAYER_MT_shader_sub_menu"
    bl_label = "Shader Sub Menu"

    def draw(self, context):
        layout = self.layout
        shaders = bpy.context.scene.matlayer_shader_list
        for shader in shaders:
            op = layout.operator("matlayer.set_shader", text=shader.name)
            op.shader_name = shader.name