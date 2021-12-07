# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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


