# Draws the add layer menu popup interface.

import bpy
from bpy.types import Operator

class COATER_OT_add_layer_menu(Operator):
    '''Opens a menu of layer types that can be added the the layer stack.'''
    bl_label = ""
    bl_idname = "coater.add_layer_menu"
    bl_description = "Opens a menu of layer types that can be added to the layer stack"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=200)

    # Draws the properties in the popup.
    def draw(self, context):
        layer_settings = context.scene.coater_layer_settings
        scale_y = 1.4

        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = scale_y
        col.operator("coater.add_image_layer", icon='IMAGE_DATA')
        col.operator("coater.add_empty_image_layer", icon='IMAGE_DATA')
        col.operator("coater.add_color_layer", icon='COLOR')
        col.operator("coater.add_group_layer", icon='GROUP_UVS')

        split = layout.split()
        col = split.column()
        col.scale_y = scale_y
        col.prop(layer_settings, "image_width", text="")

        col = split.column()
        col.scale_y = scale_y
        if layer_settings.match_image_resolution:
            col.prop(layer_settings, "match_image_resolution", text="", icon="LOCKED")

        else:
            col.prop(layer_settings, "match_image_resolution", text="", icon="UNLOCKED")

        col = split.column()
        col.scale_y = scale_y
        if layer_settings.match_image_resolution:
            col.enabled = False

        col.prop(layer_settings, "image_height", text="")

        row = layout.row()
        row.scale_y = scale_y
        row.prop(layer_settings, "thirty_two_bit")

