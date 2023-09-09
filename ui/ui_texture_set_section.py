import bpy
from .import ui_section_tabs
from ..core.material_layers import MATERIAL_CHANNEL_LIST
from ..core import texture_set_settings as tss

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    SCALE_Y = 1.4
    texture_set_settings = context.scene.matlayer_texture_set_settings

    # Draw global material channel toggles.
    layout.label(text="MATERIAL CHANNELS")
    for material_channel_name in MATERIAL_CHANNEL_LIST:
        row = layout.row()
        row.scale_y = SCALE_Y
        if tss.get_material_channel_active(material_channel_name):
            operator = row.operator("matlayer.toggle_texture_set_material_channel", text=material_channel_name.capitalize(), depress=True)
        else:
            operator = row.operator("matlayer.toggle_texture_set_material_channel", text=material_channel_name.capitalize())
        operator.material_channel_name = material_channel_name
    
    row = layout.row()
    row.scale_y = SCALE_Y

    col = row.split()
    col.label(text="Texture Size: ")
    
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

    # Draw additional settings.
    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(texture_set_settings, "thirty_two_bit")