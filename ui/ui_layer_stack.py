# This file handles the coater user interface.

import os
import bpy
import bpy.utils.previews       # Imported for loading texture previews as icons.
from ..texture_handling import image_file_handling
from ..layers import layer_nodes
from ..layers.layer_filters import material_layer_filter_exists

def draw_layer_hidden_icon(layout, item):
    row = layout.row(align=True)
    row.ui_units_x = 1
    if item.hidden == True:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

    elif item.hidden == False:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

# TODO: Do I need this? What the fuck is this?
def select_layer_filter(layer_index, context):
    context.scene.coater_layer_stack.layer_index = layer_index
    context.scene.coater_layer_stack.layer_properties_tab = "MATERIAL"

def draw_material_channel_preview(layout, item, selected_material_channel, context):
    '''Draws a preview of what the material will look like for the selected material channel.'''
    row = layout.row(align=True)
    row.ui_units_x = 0.8
    preview_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, item.layer_stack_array_index, context)

    # Draw the layer preview based on the node type.
    match preview_node.type:
        case 'VALUE':
            match selected_material_channel:
                case "COLOR":
                    row.prop(item, "color_layer_color_preview", text="")

                case "METALLIC":
                    row.prop(item, "metallic_layer_color_preview", text="")

                case "ROUGHNESS":
                    row.prop(item, "roughness_layer_color_preview", text="")

                case "NORMAL":
                    row.prop(item, "normal_layer_color_preview", text="")

                case "HEIGHT":
                    row.prop(item, "height_layer_color_preview", text="")

                case "EMISSION":
                    row.prop(item, "emission_layer_color_preview", text="")

                case "SCATTERING":
                    row.prop(item, "scattering_layer_color_preview", text="")
        
        case 'RGB':
            match selected_material_channel:
                case "COLOR":
                    row.prop(item, "color_layer_color_preview", text="")

                case "METALLIC":
                    row.prop(item, "metallic_layer_color_preview", text="")

                case "ROUGHNESS":
                    row.prop(item, "roughness_layer_color_preview", text="")

                case "NORMAL":
                    row.prop(item, "normal_layer_color_preview", text="")

                case "HEIGHT":
                    row.prop(item, "height_layer_color_preview", text="")

                case "EMISSION":
                    row.prop(item, "emission_layer_color_preview", text="")

                case "SCATTERING":
                    row.prop(item, "scattering_layer_color_preview", text="")

        case 'TEX_IMAGE':
            # TODO: Update this to show a proper texture preview for the texture used in the layer.
            # Load the texture preview as an icon using the blender utility preview module https://docs.blender.org/api/current/bpy.utils.previews.html
            layer_folder_path = image_file_handling.get_layer_folder_path()
            if "preview_icon" not in context.scene.preview_icons:
                context.scene.preview_icons.load("preview_icon", os.path.join(layer_folder_path, "Layer_70280.png"), 'IMAGE')
            layer_preview_icon = context.scene.preview_icons["preview_icon"]
            row.use_property_decorate = False
            row.template_icon(icon_value=layer_preview_icon.icon_id,scale=1)

        case 'TEX_NOISE':
            # TODO: Update this to show a texture preview.
            row.prop(preview_node, "color", text="")

        case 'TEX_MUSGRAVE':
            # TODO: Update this to show a texture preview.
            row.prop(preview_node, "color", text="")

        case 'TEX_VORONOI':
            # TODO: Update this to show a texture preview.
            row.prop(preview_node, "color", text="")

        case _:
            # Show an error icon if a preview for the node type doesn't exist.
            row.template_icon(2, scale=1)

def draw_layer_mask_preview(layout, item, selected_material_channel, context):
    '''Draws a preview of the mask for each layer (if one is used) within the layer stack.'''
    if item.masked:
        row = layout.row(align=True)
        row.ui_units_x = 0.8
        row.operator("coater.open_mask_settings", icon='MOD_MASK', text="", emboss=False)

def draw_layer_name(layout, item):
    row = layout.row(align=True)
    row.ui_units_x = 3
    row.prop(item, "name", text="", emboss=False)

def draw_debug_values(layout, item):
    '''Draws helpful debugging values for each layer.'''
    layout.prop(item, "layer_stack_array_index", text="", emboss=False)
    layout.prop(item, "id", text="", emboss=False)
    layout.prop(item, "cached_frame_name", text="", emboss=False)

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

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            selected_material_channel = context.scene.coater_layer_stack.selected_material_channel

            if context.active_object.active_material:
                draw_layer_hidden_icon(layout, item)
                draw_material_channel_preview(layout, item, selected_material_channel, context)
                draw_layer_mask_preview(layout, item, selected_material_channel, context)
                #draw_debug_values(layout, item)
                draw_layer_name(layout, item)
                draw_layer_blending(layout, item, selected_material_channel, context)