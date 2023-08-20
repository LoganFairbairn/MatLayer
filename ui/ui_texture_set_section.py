import bpy
from .import ui_section_tabs

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    SCALE_Y = 1.4
    texture_set_settings = context.scene.matlayer_texture_set_settings

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

    # Draw global material channel toggles.
    layout.label(text="MATERIAL CHANNELS")
    material_channel_list = get_material_channel_list()
    for material_channel_name in material_channel_list:
        row = layout.row()
        row.scale_y = SCALE_Y
        material_channel_name_text = material_channel_name.replace('_', ' ')
        row.prop(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle", text=material_channel_name_text, toggle=1)

    # Draw additional settings.
    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(texture_set_settings, "thirty_two_bit")