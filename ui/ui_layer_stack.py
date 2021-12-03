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
            row = layout.row()
            if item.hidden == True:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.hidden == False:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

            # Draw an icon to represent the layer's type
            row = layout.row(align=True)
            if item.layer_type == 'IMAGE_LAYER':
                row.label(text="", icon="IMAGE_DATA")

            elif item.layer_type == 'COLOR_LAYER':
                row.label(text="", icon="COLOR")

            # Draw masked icon if the layer is masked.
            if item.mask_node_name != "":
                row = layout.row()
                row.label(text="", icon="MOD_MASK")

            # Draw the layer's name.
            row.prop(item, "layer_name", text="", emboss=False)

