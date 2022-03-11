import bpy
from .import ui_section_tabs
from .import ui_baking_section

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    scale_y = 1.4
    texture_set_settings = context.scene.coater_texture_set_settings
    layout.label(text="TEXTURE SET SETTINGS:")

    split = layout.split()
    col = split.column()
    col.scale_y = scale_y
    col.prop(texture_set_settings, "image_width", text="")

    col = split.column()
    col.scale_y = scale_y
    if texture_set_settings.match_image_resolution:
        col.prop(texture_set_settings, "match_image_resolution", text="", icon="LOCKED")

    else:
        col.prop(texture_set_settings, "match_image_resolution", text="", icon="UNLOCKED")

    col = split.column()
    col.scale_y = scale_y
    if texture_set_settings.match_image_resolution:
        col.enabled = False

    col.prop(texture_set_settings, "image_height", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "thirty_two_bit")
    row.prop(texture_set_settings, "pack_images")

    # TODO: Draw material channels.
    layout.label(text="MATERIAL CHANNELS: ")
    