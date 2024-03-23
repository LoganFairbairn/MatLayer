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
    row.prop(shader_info, "group_node_name", text="")
    row.menu("MATLAYER_MT_shader_sub_menu", text="Load Shader")

    # Draw global properties for the shader.
    layout.label(text="Global Properties:")
    for property in shader_info.global_properties:
        split = layout.split(factor=0.5)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row()
        row.prop(property, "name", text="")

        active_object = bpy.context.active_object
        if active_object: 
            active_material = active_object.active_material
            if active_material:
                matlayer_shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
                if matlayer_shader_node:
                    shader_property = matlayer_shader_node.inputs.get(property.name)
                    if shader_property:
                        row = second_column.row()
                        row.prop(shader_property, "default_value", text="")
                    else:
                        row = second_column.row()
                        row.label(text="Shader Property Invalid")
            else:
                row = second_column.row()
                row.label(text="No active material.")
        else:
            row = second_column.row()
            row.label(text="No object selected.")
        

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

    # Draw export channels for the shader.
    layout.label(text="Export Channels:")
    for channel in shader_info.export_channels:
        row = layout.row()
        row.prop(channel, "name", text="")
    
class ShaderSubMenu(Menu):
    bl_idname = "MATLAYER_MT_shader_sub_menu"
    bl_label = "Shader Sub Menu"

    def draw(self, context):
        layout = self.layout
        shaders = bpy.context.scene.matlayer_shader_list
        for shader in shaders:
            op = layout.operator("matlayer.set_shader", text=shader.name)
            op.shader_name = shader.name