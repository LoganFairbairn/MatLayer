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
        return context.scene.coater_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        self.report({'INFO'}, "Layer Properties Edited")

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        layout.label("Layer Properties")
