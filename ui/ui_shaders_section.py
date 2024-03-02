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
    row.scale_y = 1.4
    row.label(text="Shader: ")
    row = second_column.row(align=True)
    row.scale_y = 1.4
    menu_label = shader_info.name
    menu_label = menu_label.replace('ML_', '')
    row.prop(shader_info, "name", text="")
    row.menu("MATLAYER_MT_shader_sub_menu", text="Load Shader")

    # Draw the shader author.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Author: ")
    row = second_column.row()
    row.scale_y = 1.4
    row.prop(shader_info, "author", text="")

    # Draw the shader description.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Description: ")
    row = second_column.row()
    row.scale_y = 1.4
    row.prop(shader_info, "description", text="")

    # Draw the name of the group node used for the shader.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Group Node Name: ")
    row = second_column.row()
    row.scale_y = 1.4
    row.prop(shader_info, "group_node_name", text="")

    # Draw all the material channels for the selected shader.
    layout.label(text="Shader Material Channels:")
    for channel in shader_info.material_channels:
        layout.prop(channel, "name", text="")

class ShaderSubMenu(Menu):
    bl_idname = "MATLAYER_MT_shader_sub_menu"
    bl_label = "Shader Sub Menu"

    def draw(self, context):
        layout = self.layout
        shaders = bpy.context.scene.matlayer_shader_list
        for shader in shaders:
            op = layout.operator("matlayer.set_shader", text=shader.name)
            op.shader_name = shader.name