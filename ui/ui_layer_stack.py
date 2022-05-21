# This file handles the coater user interface.

import bpy
from ..layers.nodes import material_channel_nodes

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

            # TODO: Draw masked icon if the layer is masked.
            #if item.mask_node_name != "":
            #    row.label(text="", icon="MOD_MASK")

            # Draw the layer's name.
            row.prop(item, "name", text="", emboss=False)

            # Draw layer's opacity.
            split = layout.split()
            col = split.column(align=True)
            col.ui_units_x = 1.6
            col.scale_y = 0.5
            col.prop(item, "opacity", text="", emboss=True)

            # Draw mix layer.
            material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")
            mix_layer_node = material_channel_node.node_tree.nodes.get(item.mix_layer_node_name)
            if mix_layer_node:
                col.prop(mix_layer_node, "blend_type", text="")