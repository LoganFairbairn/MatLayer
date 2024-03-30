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
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    # Draw the selected shader, and a list of other available shaders.
    row = first_column.row()
    row.label(text="Shader")
    row.scale_y = 1.4
    row = second_column.row(align=True)
    row.scale_x = 2
    row.scale_y = 1.4
    menu_label = shader_info.name
    menu_label = menu_label.replace('ML_', '')
    row.prop(bpy.context.scene, "matlayer_shader_group_node", text="")
    row.menu("MATLAYER_MT_shader_sub_menu", text="Load Shader")
    row.operator("matlayer.save_shader", text="", icon='FILE_TICK')
    row.operator("matlayer.create_shader_from_nodetree", text="", icon='NODETREE')
    row.operator("matlayer.delete_shader", text="", icon='TRASH')

    # Draw global properties for the shader.
    split = layout.split(factor=0.25)
    first_column = split.column()
    row.scale_y = 1.4
    second_column = split.column()
    row = first_column.row()
    row.label(text="Global Shader Properties")
    row = second_column.row(align=True)
    row.scale_x = 2
    row.scale_y = 1.4
    row.alignment = 'RIGHT'
    row.operator("matlayer.add_global_shader_property", text="", icon='ADD')
    row.operator("matlayer.delete_global_shader_property", text="", icon='TRASH')
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_global_shader_property_list", "Global Shader Properties", bpy.context.scene.matlayer_shader_info, "global_properties", bpy.context.scene, "matlayer_selected_global_shader_property_index", sort_reverse=False)

    selected_global_shader_property_index = bpy.context.scene.matlayer_selected_global_shader_property_index
    if selected_global_shader_property_index > -1 and selected_global_shader_property_index < len(shader_info.global_properties):
        global_shader_property = shader_info.global_properties[selected_global_shader_property_index]
        split = layout.split(factor=0.25)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row()
        row.label(text="Property Name")
        row = second_column.row()
        row.prop(global_shader_property, "name", text="")

        row = first_column.row()
        row.label(text="Value")
        row = second_column.row()
        active_object = bpy.context.active_object
        if active_object: 
            active_material = active_object.active_material
            if active_material:
                matlayer_shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
                if matlayer_shader_node:
                    shader_property = matlayer_shader_node.inputs.get(global_shader_property.name)
                    if shader_property:
                        row.prop(shader_property, "default_value", text="")
                    else:
                        row.label(text="Shader Property Invalid")
                else:
                    row.label(text="No Valid Shader Node")
            else:
                row.label(text="No Active Material")
        else:
            row.label(text="No Object Selected")

    # Draw all the channels for the selected shader.
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Shader Channels")
    row = second_column.row(align=True)
    row.alignment = 'RIGHT'
    row.scale_x = 2
    row.scale_y = 1.4
    row.operator("matlayer.add_shader_channel", text="", icon='ADD')
    row.operator("matlayer.delete_shader_channel", text="", icon='TRASH')
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_shader_channel_list", "Shader Channels", bpy.context.scene.matlayer_shader_info, "material_channels", bpy.context.scene, "matlayer_selected_shader_index", sort_reverse=False)

    # Draw properties for the selected shader channel.
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    selected_shader_channel_index = bpy.context.scene.matlayer_selected_shader_index

    if selected_shader_channel_index > -1 and selected_shader_channel_index < len(shader_info.material_channels):
        selected_shader_channel = shader_info.material_channels[selected_shader_channel_index]

        row = first_column.row()
        row.label(text="Channel Name")
        row = second_column.row()
        row.prop(selected_shader_channel, "name", text="")

        row = first_column.row()
        row.label(text="Default Active")
        row = second_column.row()
        if selected_shader_channel.default_active:
            row.prop(selected_shader_channel, "default_active", text="", toggle=True, icon='CHECKMARK')
        else:
            row.prop(selected_shader_channel, "default_active", text="", toggle=True)

        row = first_column.row()
        row.label(text="Socket Type")
        row = second_column.row()
        row.prop(selected_shader_channel, "socket_type", text="")

        row = first_column.row()
        row.label(text="Socket Sub Type")
        row = second_column.row()
        row.prop(selected_shader_channel, "socket_subtype", text="")

        row = first_column.row()
        row.label(text="Default")
        row = second_column.row()
        match selected_shader_channel.socket_type:
            case 'NodeSocketFloat':
                row.prop(selected_shader_channel, "socket_float_default", text="")
                row.prop(selected_shader_channel, "socket_float_min", text="")
                row.prop(selected_shader_channel, "socket_float_max", text="")
            case 'NodeSocketColor':
                row.prop(selected_shader_channel, "socket_color_default", text="")
            case 'NodeSocketVector':
                row.prop(selected_shader_channel, "socket_vector_default", text="")

        row = first_column.row()
        row.label(text="Default Blend Mode")
        row = second_column.row()
        row.prop(selected_shader_channel, "default_blend_mode", text="")
    
class ShaderSubMenu(Menu):
    bl_idname = "MATLAYER_MT_shader_sub_menu"
    bl_label = "Shader Sub Menu"

    def draw(self, context):
        layout = self.layout
        shaders = bpy.context.scene.matlayer_shader_list
        for shader in shaders:
            op = layout.operator("matlayer.set_shader", text=shader.name)
            op.shader_name = shader.name

class MATLAYER_UL_shader_channel_list(bpy.types.UIList):
    '''Draws the shader channel list'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        layout.label(text=item.name)

class MATLAYER_UL_global_shader_property_list(bpy.types.UIList):
    '''Draws a list of the global properties for the selected shader.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        layout.label(text=item.name)