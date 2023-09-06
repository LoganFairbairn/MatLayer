# This file handles the matlayer user interface.

import bpy
import bpy.utils.previews       # Imported for loading texture previews as icons.
from ..core import material_layers
from ..core import blender_addon_utils

class MATLAYER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    draw_counter = 0

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layers = bpy.context.scene.matlayer_layers
            item_index = layers.find(item.name)
            layer_node = material_layers.get_material_layer_node('LAYER', item_index)

            # Draw the hide layer toggle button.
            row = layout.row(align=True)
            row.ui_units_x = 1
            if blender_addon_utils.get_node_active(layer_node):
                operator = row.operator("matlayer.toggle_hide_layer", text="", emboss=False, icon='HIDE_OFF')
                operator.layer_index = item_index

            else:
                operator = row.operator("matlayer.toggle_hide_layer", text="", emboss=False, icon='HIDE_ON')
                operator.layer_index = item_index

            # Draw the layer name.
            if layer_node:
                row = layout.row()
                row.ui_units_x = 3
                row.prop(layer_node, "label", text="", emboss=False)

            # Layer opacity and blending mode (for the selected material channel).
            selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
            opacity_layer_node = material_layers.get_material_layer_node('OPACITY', item_index, material_channel_name=selected_material_channel.upper())
            mix_layer_node = material_layers.get_material_layer_node('MIX', item_index, material_channel_name=selected_material_channel.upper())
            if mix_layer_node:
                row = layout.row(align=True)
                row.ui_units_x = 2

                split = layout.split()
                col = split.column(align=True)
                col.ui_units_x = 1.6
                col.scale_y = 0.5
                col.prop(opacity_layer_node.inputs[0], "default_value", text="", emboss=True)
                col.prop(mix_layer_node, "blend_type", text="")
