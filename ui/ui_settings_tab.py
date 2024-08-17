# User interface for the shaders tab.

import bpy
from bpy.types import Menu
from .import ui_tabs
from ..core import texture_set_settings as tss
from ..core import blender_addon_utils as bau

MATERIAL_SETUP_TABS = [
    ("SHADER_CHANNELS", "Shader Channels", ""),
    ("GLOBAL_SHADER_PROPERTIES", "Shader Properties", ""),
    ("ACTIVE_CHANNELS", "Active Channels", "")
]

def draw_texture_settings(layout):
    '''Draws addon texture settings.'''
    texture_set_settings = bpy.context.scene.matlayer_texture_set_settings

    # Split the UI into a two column layout.
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    # Draw texture size setting.
    row = first_column.row()
    row.label(text="Texture Size ")
    row = second_column.row()
    col = row.split()
    col.prop(texture_set_settings, "image_width", text="")

    col = row.split()
    if texture_set_settings.match_image_resolution:
        col.prop(texture_set_settings, "match_image_resolution", text="", icon="LOCKED")
    else:
        col.prop(texture_set_settings, "match_image_resolution", text="", icon="UNLOCKED")

    col = row.split()
    if texture_set_settings.match_image_resolution:
        col.enabled = False
    col.prop(texture_set_settings, "image_height", text="")

def draw_settings_tab(self, context):
    '''Draws user interface for the setup tab.'''

    # Draws tabs for all sections in this add-on.
    ui_tabs.draw_addon_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    draw_texture_settings(layout)

    # Split the UI into a two column layout.
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    # Draw the selected shader, and operators to change or edit the shader.
    shader_info = bpy.context.scene.matlayer_shader_info
    row = first_column.row()
    row.label(text="Shader")
    row = second_column.row(align=True)
    menu_label = shader_info.name
    menu_label = menu_label.replace('ML_', '')
    row.prop(shader_info, "shader_node_group", text="")
    row.menu("MATLAYER_MT_shader_sub_menu", text="", icon='FILE_PARENT')
    row.operator("matlayer.new_shader", text="", icon='ADD')
    row.operator("matlayer.save_shader", text="", icon='FILE_TICK')
    row.operator("matlayer.create_shader_from_nodetree", text="", icon='NODETREE')
    row.operator("matlayer.delete_shader", text="", icon='TRASH')

    # Draw material setup tabs.
    row = layout.row(align=True)
    row.scale_y = 1.25
    row.prop_enum(bpy.context.scene, "matlayer_material_setup_tabs", 'SHADER_CHANNELS')
    row.prop_enum(bpy.context.scene, "matlayer_material_setup_tabs", "GLOBAL_SHADER_PROPERTIES")
    row.prop_enum(bpy.context.scene, "matlayer_material_setup_tabs", 'ACTIVE_CHANNELS')

    match bpy.context.scene.matlayer_material_setup_tabs:
        case 'SHADER_CHANNELS':
            split = layout.split(factor=0.25)
            first_column = split.column()
            second_column = split.column()
            row = first_column.row()
            row.label(text="Shader Channels")
            row.scale_y = 1.5
            row = second_column.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.operator("matlayer.add_shader_channel", text="", icon='ADD')
            row.operator("matlayer.delete_shader_channel", text="", icon='TRASH')
            row = layout.row(align=True)
            row.template_list("MATLAYER_UL_shader_channel_list", "Shader Channels", bpy.context.scene.matlayer_shader_info, "material_channels", bpy.context.scene, "matlayer_selected_shader_index", sort_reverse=False)

            # Draw properties for the selected shader channel.
            split = layout.split(factor=0.3)
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

                if selected_shader_channel.socket_type != 'NodeSocketColor':
                    row = first_column.row()
                    row.label(text="Socket Sub Type")
                    row = second_column.row()
                    row.prop(selected_shader_channel, "socket_subtype", text="")

                row = first_column.row()
                row.label(text="Default")
                row = second_column.row()
                match selected_shader_channel.socket_type:
                    case 'NodeSocketFloat':
                        if selected_shader_channel.socket_subtype == 'FACTOR':
                            row.prop(selected_shader_channel, "socket_float_default", text="", slider=True)
                        else:
                            row.prop(selected_shader_channel, "socket_float_default", text="")

                        row = first_column.row()
                        row.label(text="Min Value")
                        row = second_column.row()
                        row.prop(selected_shader_channel, "socket_float_min", text="")

                        row = first_column.row()
                        row.label(text="Max Value")
                        row = second_column.row()
                        row.prop(selected_shader_channel, "socket_float_max", text="")
                    case 'NodeSocketColor':
                        row.prop(selected_shader_channel, "socket_color_default", text="")
                    case 'NodeSocketVector':
                        row.prop(selected_shader_channel, "socket_vector_default", text="")

                row = first_column.row()
                row.label(text="Default Blend Mode")
                row = second_column.row()
                row.prop(selected_shader_channel, "default_blend_mode", text="")
        
        case 'GLOBAL_SHADER_PROPERTIES':
            split = layout.split(factor=0.25)
            first_column = split.column()
            second_column = split.column()
            row = first_column.row()
            row.label(text="Global Shader Properties")
            row.scale_y = 1.5
            row = second_column.row(align=True)
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.alignment = 'RIGHT'
            row.operator("matlayer.add_global_shader_property", text="", icon='ADD')
            row.operator("matlayer.delete_global_shader_property", text="", icon='TRASH')
            row = layout.row(align=True)
            row.template_list("MATLAYER_UL_global_shader_property_list", "Global Shader Properties", bpy.context.scene.matlayer_shader_info, "global_properties", bpy.context.scene, "matlayer_selected_global_shader_property_index", sort_reverse=False)

            selected_global_shader_property_index = bpy.context.scene.matlayer_selected_global_shader_property_index
            if selected_global_shader_property_index > -1 and selected_global_shader_property_index < len(shader_info.global_properties):
                global_shader_property = shader_info.global_properties[selected_global_shader_property_index]
                split = layout.split(factor=0.3)
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
        
        case 'ACTIVE_CHANNELS':
            active_object = bpy.context.active_object
            if active_object:
                if active_object.active_material:
                    if bau.verify_addon_material(active_object.active_material):

                        # Draw global material channel toggles.
                        row = layout.row()
                        row.scale_y = 1.5
                        row.label(text="Active Material Channels")
                        row = layout.row()
                        row_count = 0

                        shader_info = bpy.context.scene.matlayer_shader_info
                        for channel in shader_info.material_channels:

                            if tss.get_material_channel_active(channel.name):
                                operator = row.operator("matlayer.toggle_texture_set_material_channel", text=channel.name, depress=True)
                            else:
                                operator = row.operator("matlayer.toggle_texture_set_material_channel", text=channel.name)
                            operator.material_channel_name = channel.name

                            row_count += 1
                            if row_count >= 2:
                                row = layout.row()
                                row_count = 0
                    else:
                        bau.print_aligned_text(layout, "Active material isn't created with this add-on, or the format is not valid.", alignment='CENTER')
                else:
                    layout.label(text="No active material.")
                    layout.label(text="Add a material layer to see texture set settings.")
            else:
                layout.label(text="No active object.")
                layout.label(text="Select an object with a MatLayer material applied")
                layout.label(text="to see texture set settings.")

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