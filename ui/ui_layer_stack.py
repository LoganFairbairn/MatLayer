# This file handles the coater user interface.

import bpy
from ..layers import coater_node_info

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Draw the layer hide icon.
            row = layout.row(align=True)
            row.ui_units_x = 4
            
            if item.hidden == True:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.hidden == False:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

            # Draw an icon to represent the layer's type
            if item.type == 'IMAGE_LAYER':
                row.label(text="", icon="IMAGE_DATA")

            elif item.type == 'COLOR_LAYER':
                row.label(text="", icon="COLOR")

            # Draw masked icon if the layer is masked.
            if item.mask_node_name != "":
                row.label(text="", icon="MOD_MASK")

            # Draw the layer's name.
            row.prop(item, "name", text="", emboss=False)

            # Draw the layers opacity and blend mode.
            split = layout.split()
            col = split.column(align=True)
            col.ui_units_x = 1.6
            col.scale_y = 0.5
            col.prop(item, "opacity", text="", emboss=True)

            mix_node = coater_node_info.get_self_node(item, context, 'MIX')
            col.prop(mix_node, "blend_type", text="")


