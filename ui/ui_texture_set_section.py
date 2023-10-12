import bpy
from .import ui_section_tabs
from ..core.material_layers import MATERIAL_CHANNEL_LIST
from ..core import texture_set_settings as tss
from ..core import blender_addon_utils

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    texture_set_settings = context.scene.matlayer_texture_set_settings

    #----------------------------- TEXTURE SET SETTINGS -----------------------------#

    split = layout.split(factor=0.3)
    first_column = split.column()
    second_column = split.column()

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

    row = first_column.row()
    row.scale_y = 1.4
    row.label(text="Thirty Two Bit Depth: ")
    row = second_column.row()
    row.scale_y = 1.4
    row.prop(texture_set_settings, "thirty_two_bit")

    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:
            if blender_addon_utils.verify_addon_material(active_object.active_material):

                # Draw global material channel toggles.
                layout.label(text="MATERIAL CHANNELS")
                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    row = layout.row()
                    row.scale_y = 1.4
                    if tss.get_material_channel_active(material_channel_name):
                        operator = row.operator("matlayer.toggle_texture_set_material_channel", text=material_channel_name.capitalize(), depress=True)
                    else:
                        operator = row.operator("matlayer.toggle_texture_set_material_channel", text=material_channel_name.capitalize())
                    operator.material_channel_name = material_channel_name
            else:
                layout.label(text="Active material isn't created with this add-on, or the format isn't valid.")
        else:
            layout.label(text="No active material.")
    else:
        layout.label(text="No active object.")
    