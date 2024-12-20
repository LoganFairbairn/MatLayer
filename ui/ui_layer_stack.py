# This file handles the matlayer user interface.

import bpy
from bpy.types import Menu
import bpy.utils.previews       # Imported for loading texture previews as icons.
from ..core import material_layers
from ..core import blender_addon_utils

class LayerBlendingModeSubMenu(Menu):
    bl_idname = "MATLAYER_MT_layer_blending_mode_sub_menu"
    bl_label = "Layer Blending Mode Sub Menu"

    def draw(self, context):
        layer_index = int(context.layer_node.name)
        layout = self.layout

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Mix")
        operator.blending_mode = 'MIX'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Darken")
        operator.blending_mode = 'DARKEN'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Multiply")
        operator.blending_mode = 'MULTIPLY'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Color Burn")
        operator.blending_mode = 'BURN'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Lighten")
        operator.blending_mode = 'LIGHTEN'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Screen")
        operator.blending_mode = 'SCREEN'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Color Dodge")
        operator.blending_mode = 'DODGE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Add")
        operator.blending_mode = 'ADD'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Overlay")
        operator.blending_mode = 'OVERLAY'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Soft Light")
        operator.blending_mode = 'SOFT_LIGHT'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Linear Light")
        operator.blending_mode = 'LINEAR_LIGHT'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Difference")
        operator.blending_mode = 'DIFFERENCE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Exclusion")
        operator.blending_mode = 'EXCLUSION'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Subtract")
        operator.blending_mode = 'SUBTRACT'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Divide")
        operator.blending_mode = 'DIVIDE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Hue")
        operator.blending_mode = 'HUE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Saturation")
        operator.blending_mode = 'SATURATION'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Color")
        operator.blending_mode = 'COLOR'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Value")
        operator.blending_mode = 'VALUE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Normal Map Combine")
        operator.blending_mode = 'NORMAL_MAP_COMBINE'
        operator.layer_index = layer_index

        operator = layout.operator("matlayer.set_layer_blending_mode", text="Normal Map Detail")
        operator.blending_mode = 'NORMAL_MAP_DETAIL'
        operator.layer_index = layer_index

class MATLAYER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layers = bpy.context.scene.matlayer_layers
            item_index = layers.find(item.name)
            layer_node = material_layers.get_material_layer_node('LAYER', item_index)

            if layer_node:

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
                row = layout.row()
                row.ui_units_x = 2
                row.prop(layer_node, "label", text="", emboss=False)

                # Layer opacity and blending mode for the selected material channel.
                selected_material_channel_name = bpy.context.scene.matlayer_layer_stack.selected_material_channel
                opacity_layer_node = material_layers.get_material_layer_node(
                    'OPACITY', 
                    item_index, 
                    channel_name=selected_material_channel_name
                )

                mix_layer_node = material_layers.get_material_layer_node(
                    'MIX', 
                    item_index, 
                    channel_name=selected_material_channel_name
                )

                if mix_layer_node:
                    row = layout.row(align=True)
                    row.ui_units_x = 5

                    split = layout.split()
                    col = split.column(align=True)
                    col.ui_units_x = 1.6
                    col.scale_y = 0.5
                    col.prop(opacity_layer_node.inputs[0], "default_value", text="", emboss=True)

                    col.context_pointer_set("layer_node", layer_node)
                    blending_mode = material_layers.get_layer_blending_mode(item_index)
                    blending_mode_label = blending_mode.replace('_', ' ')
                    blending_mode_label = blender_addon_utils.capitalize_by_space(blending_mode_label)
                    col.menu('MATLAYER_MT_layer_blending_mode_sub_menu', text=blending_mode_label)
