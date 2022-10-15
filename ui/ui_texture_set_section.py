import bpy
from .import ui_section_tabs

def draw_texture_set_section_ui(self, context):
    '''Draws the layer section UI.'''
    ui_section_tabs.draw_section_tabs(self, context)

    # Draw texture set settings.
    layout = self.layout
    scale_y = 1.4
    texture_set_settings = context.scene.coater_texture_set_settings

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "layer_folder")

    split = layout.split(align=True)

    col = split.column(align=True)
    col.scale_y = scale_y
    col.label(text="Size: ")

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

    # Draw material channel toggles.
    layout.label(text="MATERIAL CHANNELS")
    
    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "color_channel_toggle", text="Color", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "metallic_channel_toggle", text="Metallic", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "roughness_channel_toggle", text="Roughness", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "normal_channel_toggle", text="Normal", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "height_channel_toggle", text="Height", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "scattering_channel_toggle", text="Scattering", toggle=1)

    row = layout.row()
    row.scale_y = scale_y
    row.prop(texture_set_settings, "emission_channel_toggle", text="Emission" , toggle=1)
    