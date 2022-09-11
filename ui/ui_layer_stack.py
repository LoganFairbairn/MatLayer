# This file handles the coater user interface.

import bpy
from ..layers.nodes import material_channel_nodes
from ..layers.nodes import layer_nodes

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        #self.use_filter_reverse = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
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
            selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
            texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, item.layer_stack_array_index, context)
            if texture_node:
                row.prop(texture_node.outputs[0], "default_value", text="")

            # TODO: If the layer has a mask, draw a preview.



            # Debug drawing.
            layout.prop(item, "layer_stack_array_index", text="", emboss=False)

            
            # Draw the layer's name.
            row = layout.row(align=True)
            row.ui_units_x = 4
            row.prop(item, "name", text="", emboss=False)




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
