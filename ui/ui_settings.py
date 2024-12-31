# User interface for the shaders tab.

import bpy
from bpy.types import Menu
from .. import preferences

def draw_texture_setting_ui(layout):
    '''Draws addon texture settings.'''
    texture_set_settings = bpy.context.scene.rymat_texture_set_settings
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    # Split the UI into a two column layout.
    split = layout.split(factor=0.4)
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

    # Split the UI into a two column layout.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    # Draw the raw texture folder preference.
    row = first_column.row()
    row.label(text="Raw Texture Folder")
    row = second_column.row(align=True)
    row.prop(bpy.context.scene, "rymat_raw_textures_folder", text="")
    row.operator("rymat.set_raw_texture_folder", text="", icon='FOLDER_REDIRECT')
    row.operator("rymat.open_raw_texture_folder", text="", icon='FILE_FOLDER')

    # Draw other texture management settings.
    row = first_column.row()
    row.label(text="Thirty Two Bit Textures")
    row = second_column.row()
    row.prop(addon_preferences, "thirty_two_bit", text="")

    row = first_column.row()
    row.label(text="Save Imported Textures")
    row = second_column.row()
    row.prop(addon_preferences, "save_imported_textures", text="")

    row = first_column.row()
    row.label(text="Auto-save Images")
    row = second_column.row()
    row.prop(addon_preferences, "auto_save_images", text="")

    row = first_column.row()
    row.label(text="Auto-save Image Interval")
    row = second_column.row()
    row.prop(addon_preferences, "image_auto_save_interval", text="")

def draw_shader_setting_ui(layout):
    '''Draws shader setting user interface for this add-on.'''
    # Split the UI into a two column layout.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    # Draw options to edit the selected shader preset.
    row = first_column.row()
    row.label(text="Shader Preset")
    row = second_column.row(align=True)
    row.menu("RYMAT_MT_shader_sub_menu", text="Select Shader")
    row.operator("rymat.new_shader", text="", icon='ADD')
    row.operator("rymat.save_shader", text="", icon='FILE_TICK')
    row.operator("rymat.create_shader_from_nodetree", text="", icon='NODETREE')
    row.operator("rymat.delete_shader", text="", icon='TRASH')

    # Draw the selected shader, and operators to change or edit the shader.
    shader_info = bpy.context.scene.rymat_shader_info
    row = first_column.row()
    row.label(text="Shader Node")
    row = second_column.row(align=True)
    row.prop(shader_info, "shader_node_group", text="")

    # Draw shader channels.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()
    row = first_column.row()
    row.label(text="SHADER CHANNELS")
    row.scale_y = 1.5
    row = second_column.row(align=True)
    row.alignment = 'RIGHT'
    row.scale_x = 1.5
    row.scale_y = 1.5
    row.operator("rymat.add_shader_channel", text="", icon='ADD')
    row.operator("rymat.delete_shader_channel", text="", icon='TRASH')
    row = layout.row(align=True)
    row.template_list("RYMAT_UL_shader_channel_list", "Shader Channels", bpy.context.scene.rymat_shader_info, "material_channels", bpy.context.scene, "rymat_shader_channel_index", sort_reverse=False)

    # Draw properties for the selected shader channel.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    selected_shader_channel_index = bpy.context.scene.rymat_shader_channel_index

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
        row.label(text="Default Value")
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

class ShaderSubMenu(Menu):
    bl_idname = "RYMAT_MT_shader_sub_menu"
    bl_label = "Shader Sub Menu"

    def draw(self, context):
        layout = self.layout
        shaders = bpy.context.scene.rymat_shader_list
        for shader in shaders:
            op = layout.operator("rymat.set_shader", text=shader.name)
            op.shader_name = shader.name

class RYMAT_UL_shader_channel_list(bpy.types.UIList):
    '''Draws the shader channel list'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        layout.label(text=item.name)

class RYMAT_UL_global_shader_property_list(bpy.types.UIList):
    '''Draws a list of the global properties for the selected shader.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        layout.label(text=item.name)
