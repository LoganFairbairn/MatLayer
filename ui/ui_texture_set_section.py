import bpy
from bpy.types import Menu
from .import ui_section_tabs
from ..core.material_layers import MATERIAL_CHANNEL_LIST
from ..core import texture_set_settings as tss
from ..core import blender_addon_utils
from .. import preferences

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    texture_set_settings = context.scene.matlayer_texture_set_settings
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    #----------------------------- TEXTURE SET SETTINGS -----------------------------#

    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

    # Draw the raw texture folder setting.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Raw Texture Folder: ")
    row = second_column.row(align=True)
    row.scale_y = 1.4
    row.prop(bpy.context.scene, "matlayer_raw_textures_folder", text="")
    row.operator("matlayer.set_raw_texture_folder", text="", icon='FOLDER_REDIRECT')
    row.operator("matlayer.open_raw_texture_folder", text="", icon='FILE_FOLDER')

    # Draw texture size setting.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Texture Size: ")
    row = second_column.row()
    row.scale_y = 1.4
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
    
    # Draw the shader settings.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Shader: ")
    row = second_column.row()
    row.scale_y = 1.4
    menu_label = bpy.context.scene.matlayer_shader
    menu_label = menu_label.replace('ML_', '')
    row.menu("MATLAYER_MT_shader_sub_menu", text=menu_label)

    # Draw 32-bit color depth setting.
    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Thirty Two Bit Depth: ")
    row = second_column.row()
    row.scale_y = 1.4
    row.prop(addon_preferences, "thirty_two_bit")

    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:
            if blender_addon_utils.verify_addon_material(active_object.active_material):

                # Draw global material channel toggles.
                layout.label(text="MATERIAL CHANNELS")
                row = layout.row()
                row.scale_y = 1.4
                row_count = 0
                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    channel_name = material_channel_name.replace('-', ' ')
                    channel_name = blender_addon_utils.capitalize_by_space(channel_name)

                    if material_channel_name == 'DISPLACEMENT':
                        channel_name += (' (Cycles only)')

                    if tss.get_material_channel_active(material_channel_name):
                        operator = row.operator("matlayer.toggle_texture_set_material_channel", text=channel_name, depress=True)
                    else:
                        operator = row.operator("matlayer.toggle_texture_set_material_channel", text=channel_name)
                    operator.material_channel_name = material_channel_name

                    row_count += 1
                    if row_count >= 2:
                        row = layout.row()
                        row.scale_y = 1.4
                        row_count = 0
            else:
                layout.label(text="Active material isn't created with this add-on, or the format isn't valid.")
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
        op = layout.operator("matlayer.set_shader", text="Principled BSDF")
        op.shader = 'ML_BSDF'
        op = layout.operator("matlayer.set_shader", text="RyShade")
        op.shader = 'ML_RYSHADE'