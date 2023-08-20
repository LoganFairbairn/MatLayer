# This file handles the matlayer user interface.

import bpy
import bpy.utils.previews       # Imported for loading texture previews as icons.

def draw_layer_hidden_icon(layout, item):
    row = layout.row(align=True)
    row.ui_units_x = 1
    if item.hidden == True:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

    elif item.hidden == False:
        row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

def draw_decal_icon(layout, item):
    if item.type == 'DECAL':
        row = layout.row(align=True)
        row.ui_units_x = 1
        row.label(text="", icon='OUTLINER_OB_FONT')

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
    #mix_layer_node = layer_nodes.get_layer_node("MIX-LAYER", selected_material_channel, item.layer_stack_array_index, context)
    #if mix_layer_node:
    #    col.prop(mix_layer_node, "blend_type", text="")

class MATLAYER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            selected_material_channel = context.scene.matlayer_layer_stack.selected_material_channel

            if context.active_object.active_material:
                draw_layer_hidden_icon(layout, item)
                draw_decal_icon(layout, item)
                draw_layer_name(layout, item)
                draw_layer_blending(layout, item, selected_material_channel, context)