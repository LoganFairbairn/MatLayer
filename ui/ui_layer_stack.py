# This file handles the matlay user interface.

import os
import bpy
import bpy.utils.previews       # Imported for loading texture previews as icons.
from ..core import layer_nodes
from ..core import material_filters
from ..utilities import image_file_handling

def draw_layer_hidden_icon(layout, item):
    row = layout.row(align=True)
    row.ui_units_x = 1
    if item.hidden == True:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

    elif item.hidden == False:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

def draw_material_channel_preview(layout, item, selected_material_channel, context):
    '''Draws a preview of what the material will look like for the selected material channel.'''
    row = layout.row(align=True)
    row.ui_units_x = 0.8
    preview_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, item.layer_stack_array_index, context)

    # Draw layer material preview for the selected material channel.
    row = layout.row(align=True)
    row.ui_units_x = 0.8

    # TODO: Update this to show a proper texture preview for the texture used in the layer.
    # Load the texture preview as an icon using the blender utility preview module https://docs.blender.org/api/current/bpy.utils.previews.html
    '''
    layer_folder_path = image_file_handling.get_layer_folder_path()
    if "preview_icon" not in context.scene.preview_icons:
        context.scene.preview_icons.load("preview_icon", os.path.join(layer_folder_path, "Layer_70280.png"), 'IMAGE')
    layer_preview_icon = context.scene.preview_icons["preview_icon"]
    row.use_property_decorate = False
    row.template_icon(icon_value=layer_preview_icon.icon_id,scale=1)
    '''

    row.operator("matlay.open_material_layer_settings", icon='RENDERLAYERS', text="", emboss=False)

def draw_layer_mask_preview(layout):
    '''Draws a preview of the mask for each layer (if one is used) within the layer stack.'''
    row = layout.row(align=True)
    row.ui_units_x = 0.8
    row.operator("matlay.open_mask_settings", icon='MOD_MASK', text="", emboss=False)

def draw_layer_name(layout, item):
    row = layout.row(align=True)
    row.ui_units_x = 3
    row.prop(item, "name", emboss=False)

def draw_layer_blending(layout, item, selected_material_channel, context):
    '''Draws the layer opacity and blend mode.'''

    # Draw layer's opacity.
    row = layout.row(align=True)
    row.ui_units_x = 2

    split = layout.split()
    col = split.column(align=True)
    col.ui_units_x = 1.6
    col.scale_y = 0.5
    col.prop(item, "opacity", text="", emboss=True)

    # Draw the layer's blend mode.
    mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", selected_material_channel, item.layer_stack_array_index, context)
    if mix_layer_node:
        col.prop(mix_layer_node, "blend_type", text="")

class MATLAY_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

            if context.active_object.active_material:
                draw_layer_hidden_icon(layout, item)
                #draw_material_channel_preview(layout, item, selected_material_channel, context)
                #draw_layer_mask_preview(layout)
                draw_layer_name(layout, item)
                draw_layer_blending(layout, item, selected_material_channel, context)