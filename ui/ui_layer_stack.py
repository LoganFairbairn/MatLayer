# This file handles the coater user interface.

import bpy
from ..layers import layer_nodes
from ..layers.layer_filters import material_layer_filter_exists

def select_layer_filter(layer_index, context):
    context.scene.coater_layer_stack.layer_index = layer_index
    context.scene.coater_layer_stack.layer_properties_tab = "MATERIAL"

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
            texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, item.layer_stack_array_index, context)

            # Don't draw layer information for layers with muted material channels.
            if item.color_channel_toggle == False and selected_material_channel == "COLOR":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.metallic_channel_toggle == False and selected_material_channel == "METALLIC":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.roughness_channel_toggle == False and selected_material_channel == "ROUGHNESS":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.normal_channel_toggle == False and selected_material_channel == "NORMAL":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.height_channel_toggle == False and selected_material_channel == "HEIGHT":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.scattering_channel_toggle == False and selected_material_channel == "SCATTERING":
                row = layout.row(align=False)
                row.label(text="muted")

            elif item.emission_channel_toggle == False and selected_material_channel == "EMISSION":
                row = layout.row(align=False)
                row.label(text="muted")

            else:
                # Draw the layer hide icon.
                row = layout.row(align=True)
                row.ui_units_x = 1
                if item.hidden == True:
                    row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

                elif item.hidden == False:
                    row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

                # TODO: Update the texture preview to draw based on selected material channel. 
                # Draw the texture preview.
                row = layout.row(align=True)
                row.ui_units_x = 0.8

                # Useful debug drawing values.
                #layout.prop(item, "layer_stack_array_index", text="", emboss=False)
                #layout.prop(item, "id", text="", emboss=False)
                #layout.prop(item, "cached_frame_name", text="", emboss=False)
                
                # Draw the layer's name.
                row = layout.row(align=True)
                row.ui_units_x = 4
                row.prop(item, "name", text="", emboss=False)

                # Draw the layer filter button.
                if material_layer_filter_exists(item.layer_stack_array_index, context):
                    row = layout.row(align=True)
                    row.prop_enum(context.scene.coater_layer_stack, "layer_properties_tab", 'MATERIAL_FILTERS', text="", icon='FILTER')

                # TODO: If the material layer has a mask, draw a button.


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
