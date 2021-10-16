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

class COATER_OT_add_mask_menu(bpy.types.Operator):
    '''Opens a menu of mask types that can be added to the selected layer.'''
    bl_label = ""
    bl_idname = "coater.add_mask_menu"
    bl_description = "Opens a menu of mask types that can be added to the selected layer"

    mask_type: bpy.props.EnumProperty(
        items=[('IMAGE_MASK', "Image Mask", "Adds a layer filled with an image assigned to it."),
               ('COLOR_MASK', "Color Mask", "Adds a layer filled with a solid color.")],
        name="",
        description="Type of the layer",
        default='IMAGE_MASK',
        options={'HIDDEN'}
    )

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        if self.mask_type == "COLOR_MASK":
            self.report({'INFO'}, "COLOR MASK")

        elif self.mask_type == "IMAGE_MASK":
            self.report({'INFO'}, "IMAGE MASK")
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mask_type")
