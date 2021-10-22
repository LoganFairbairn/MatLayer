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

import bpy

# Opens a menu containing all adjustable properties for the layer.
class COATER_OT_edit_layer_properties(bpy.types.Operator):
    '''Opens a menu of properties for the selected layer.'''
    bl_label = ""
    bl_idname = "coater.edit_layer_properties"
    bl_description = "Opens a menu of layer properties for the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    # Draws the properties in the popup.
    def draw(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        layout = self.layout
        row = layout.row()
        row.label(text="Layer Properties")

        # Image Layer Properties
        if(layers[layer_index].layer_type == 'IMAGE_LAYER'):
            row = layout.row(align=True)
            row.template_ID(layers[layer_index], "color_image", open="color_image.open")

        # Color Layer Properties
        if(layers[layer_index].layer_type == 'COLOR_LAYER'):
            row = layout.row()
            row.prop(layers[layer_index], "color")

            
